"""census_predict - the class-count (census) prediction of a stage plan, COMPUTED from measured samples (card 123-4).

Decision: docs/violation-decisions.md, block "inference-over-measurement - 2026-10-01 13:56". Cycle 122 typed P2b's census
by hand (+1 DigitalNumericConstant; plan_ring_p2b_make.py:82) and the LabVIEW run measured +5
(stage_d1_ring_p2b_scratch_pin.log:171-172). This tool derives each plan row's class delta from
tools/bench/census_samples.json (every sample cites the log lines that measured it) and compares the sum with the
`census` block of the plan's prediction file.

STANDALONE: imports none of stagesim / stagekit / stagexec / gscript (the hook-in to stage_prerun --prerun is card 123-5).
PRIOR ART checked: tools/bench/opmodels/*.json carry per-op `new_objs_by_class` from raw/*.json samples but no log
file:line and none for const_donor / OpConstInd_v0; stage_prerun has no census derivation; plan_ring_p2b_make.py:82 types it.

Usage:  py tools/census_predict.py <plan.json> <pred.json> [--samples tools/bench/census_samples.json] [--json out.json]
Verdict per class: PASS (derived == declared), FAIL (class, derived, declared), CENSUS-UNPREDICTED (some row has no
sample, or the class was never measured). A plan with ANY unpredicted row never PASSes: every class is UNPREDICTED
(an unsampled row may change any class), and the overall verdict is UNPREDICTED.
Overall: PASS / FAIL / UNPREDICTED / UNDECLARED (prediction file has no `census` block). Exit 0 PASS, 1 FAIL,
2 UNPREDICTED, 3 UNDECLARED, 4 usage/input error. Last line: RESULT {...} (result-line/1; UNPREDICTED and UNDECLARED
print status SKIP with gates.fail 0 - never PASS).
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import gateclass as _gateclass                                                     # noqa: E402  card chat-S2
DEFAULT_SAMPLES = os.path.join(ROOT, "tools", "bench", "census_samples.json")


def _load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def md5_of(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def _canon_by_donor(pred):
    """donor uid -> canon, from the prediction file's rows (the plan rows carry no canon)."""
    out = {}
    for r in (pred or {}).get("rows") or []:
        if isinstance(r, dict) and r.get("donor_uid") is not None and r.get("canon"):
            out.setdefault(int(r["donor_uid"]), set()).add(r["canon"])
    return out


def _row_canon(a, canon_by_donor):
    if a.get("canon"):
        return a["canon"]
    d = a.get("donor") or {}
    uid = d.get("uid")
    if uid is None:
        return None
    s = canon_by_donor.get(int(uid)) if isinstance(uid, int) or str(uid).isdigit() else None
    return next(iter(s)) if s and len(s) == 1 else None


def _match_variant(variants, cls, canon, cls_key):
    for v in variants:
        m = v.get("match") or {}
        if m.get(cls_key) == cls and canon in (m.get("canon_in") or []):
            return v
    return None


def resolve_row(a, by_as, samples, canon_by_donor):
    """-> (op_key, variant_name or None, delta dict or None, why)."""
    ops = samples.get("ops") or {}
    op = a.get("op")
    if op == "create" and a.get("prim") == "const_donor":
        key = "create_primitive_nested:const_donor"
        canon = _row_canon(a, canon_by_donor)
        v = _match_variant((ops.get(key) or {}).get("variants") or [], a.get("class"), canon, "class")
        if v is None:
            return key, None, None, "no sample for class %s canon %s" % (a.get("class"), canon)
        return key, v["name"], dict(v["delta"]), "class %s canon %s" % (a.get("class"), canon)
    if op == "create" and a.get("class") == "ControlTerminal" and a.get("indicator") and a.get("born_on"):
        key = "OpConstInd_v0"
        bu = (a.get("born_on") or {}).get("uid")
        k = bu[4:] if isinstance(bu, str) and bu.startswith("new:") else None
        src = by_as.get(k) if k else None
        if src is None or src.get("prim") != "const_donor":
            return key, None, None, "born_on %r is not a const_donor row of this plan" % (bu,)
        canon = _row_canon(src, canon_by_donor)
        v = _match_variant((ops.get(key) or {}).get("variants") or [], src.get("class"), canon, "const_class")
        if v is None:
            return key, None, None, "no sample for born-on %s canon %s" % (src.get("class"), canon)
        return key, v["name"], dict(v["delta"]), "born on %s %s" % (src.get("class"), canon)
    if op == "create" and a.get("class") == "CaseStructure" and a.get("src") is not None and not a.get("label") \
            and a.get("donor_uid") is None and not a.get("prim"):
        # card 123-7: gscript.case_wired (stagexec route 'case_wired'); the variant is whether its selector source is a NEW
        # wire (the source is an output of a node this plan created and no earlier row took it as a source) or a BRANCH
        key = "case_wired"
        src = (a["src"] or {}).get("uid") if isinstance(a["src"], dict) else a["src"]
        fresh = isinstance(src, str) and src.startswith("new:") and src.partition(".")[0][4:] in by_as
        name = "new_wire" if fresh and not _earlier_src_use(a, by_as) else "branch"
        v = next((x for x in (ops.get(key) or {}).get("variants") or [] if x.get("name") == name), None)
        if v is None:
            return key, None, None, "no sample for case_wired variant %s (selector source %r)" % (name, a["src"])
        return key, v["name"], dict(v["delta"]), "case_wired %s" % name
    desc = op if op != "create" else "create:%s%s" % (a.get("class"), (":" + a["prim"]) if a.get("prim") else "")
    return desc, None, None, "no sample for op %s" % desc


def _earlier_src_use(a, by_as):
    """True when an EARLIER row of the plan already used `a['src']` as a source (so case_wired would branch its wire)."""
    for b in by_as.get("__acts__") or []:
        if b is a:
            return False
        if isinstance(b, dict) and b.get("src") == a["src"]:
            return True
    return False


def predict(plan, pred, samples):
    acts = plan.get("actions") or []
    by_as = {a["as"]: a for a in acts if isinstance(a, dict) and a.get("as")}
    by_as["__acts__"] = acts                     # card 123-7: row order, for case_wired's new-wire / branch variant
    cbd = _canon_by_donor(pred)
    measured = set(samples.get("classes_measured") or [])
    rows, derived, unpredicted = [], {}, []
    for i, a in enumerate(acts):
        key, var, delta, why = resolve_row(a, by_as, samples, cbd)
        row = {"k": i + 1, "id": a.get("id"), "op": key, "variant": var, "delta": delta, "why": why}
        if delta is None:
            row["verdict"] = "CENSUS-UNPREDICTED"
            unpredicted.append(row)
        else:
            row["verdict"] = "SAMPLED"
            for c, n in delta.items():
                derived[c] = derived.get(c, 0) + int(n)
        rows.append(row)
    declared = pred.get("census") if isinstance(pred, dict) else None
    classes = sorted(set(derived) | set(declared or {}) | measured)
    per = []
    for c in classes:
        d, x = derived.get(c, 0), (None if declared is None else int((declared or {}).get(c, 0)))
        if unpredicted:
            v = "CENSUS-UNPREDICTED"
        elif c not in measured:
            v = "CENSUS-UNPREDICTED"
        elif x is None:
            v = "CENSUS-UNDECLARED"
        else:
            # card chat-S2 (PD327): a non-semantic class within max(5, 25 % of declared) is SOFT (LOG-only), not FAIL
            cv, rule = _gateclass.count_verdict(c, d, x)
            v = {"ok": "PASS", "log": "SOFT", "stop": "FAIL"}[cv]
        per.append({"class": c, "derived": d, "declared": x, "verdict": v})
        if v == "SOFT":
            per[-1]["rule"] = rule
    if any(p["verdict"] == "FAIL" for p in per):
        overall = "FAIL"
    elif unpredicted:
        overall = "UNPREDICTED"
    elif declared is None:
        overall = "UNDECLARED"
    elif any(p["verdict"] == "CENSUS-UNPREDICTED" for p in per):
        overall = "UNPREDICTED"
    else:
        overall = "PASS"
    return {"rows": rows, "classes": per, "derived": derived, "declared": declared,
            "unpredicted": [r["k"] for r in unpredicted], "overall": overall}


def result_line(rep, artefacts):
    n_fail = sum(1 for p in rep["classes"] if p["verdict"] == "FAIL")
    n_pass = sum(1 for p in rep["classes"] if p["verdict"] == "PASS")
    ov = rep["overall"]
    if ov == "FAIL":
        f = [p for p in rep["classes"] if p["verdict"] == "FAIL"][0]
        ff = "CENSUS FAIL %s derived %+d declared %+d" % (f["class"], f["derived"], f["declared"])
        st = "FAIL"
    elif ov == "UNPREDICTED":
        ff, st = "CENSUS-UNPREDICTED rows %s" % rep["unpredicted"], "SKIP"
        if not rep["unpredicted"]:
            ff = "CENSUS-UNPREDICTED classes %s" % [p["class"] for p in rep["classes"]
                                                     if p["verdict"] == "CENSUS-UNPREDICTED"]
    elif ov == "UNDECLARED":
        ff, st = "CENSUS-UNDECLARED: the prediction file has no census block", "SKIP"
    else:
        ff, st = None, "PASS"
    d = {"schema": "result-line/1", "status": st, "gates": {"pass": n_pass, "fail": n_fail},
         "first_fail": None if ff is None else ff[:200], "artefacts": artefacts}
    return "RESULT " + json.dumps(d, ensure_ascii=True, separators=(",", ":"))


def check_cites(cites, root=ROOT):
    """Every cite {file, line, expect}: `expect` must be a substring of that 1-based line. -> list of problems ([] = all hold)."""
    bad = []
    for c in cites or []:
        p = c["file"] if os.path.isabs(c["file"]) else os.path.join(root, c["file"])
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                lines = f.read().splitlines()
        except OSError as e:
            bad.append("%s: %s" % (c["file"], e))
            continue
        n = int(c["line"])
        if n < 1 or n > len(lines) or c["expect"] not in lines[n - 1]:
            bad.append("%s:%s does not carry %r" % (c["file"], n, c["expect"][:80]))
    return bad


def record_sample(samples_p, op, variant, delta, cites, why="", plan_match=None, route=None, match=None, n=1):
    """Card 123-7 (PD247(e)): record a scratch run's MEASURED class census as a sample. Refuses (ValueError, nothing written)
    when a cite does not hold or the delta is empty / non-integer. Replaces a same-named variant of `op`; adds the delta's
    classes to classes_measured. Returns the variant written."""
    if not delta or not all(isinstance(v, int) for v in delta.values()):
        raise ValueError("record: delta %r must be a non-empty {class: int}" % (delta,))
    if not cites:
        raise ValueError("record: a sample without a cited log line is not a measurement")
    bad = check_cites(cites)
    if bad:
        raise ValueError("record: cite(s) do not hold: %s" % "; ".join(bad))
    S = _load(samples_p)
    o = S.setdefault("ops", {}).setdefault(op, {"variants": []})
    if plan_match:
        o["plan_match"] = plan_match
    if route:
        o["route"] = route
    v = {"name": variant, "delta": dict(delta), "n": int(n), "why": why, "cites": list(cites)}
    if match:
        v["match"] = match
    o["variants"] = [x for x in o.get("variants") or [] if x.get("name") != variant] + [v]
    cm = S.setdefault("classes_measured", [])
    for c in delta:
        if c not in cm:
            cm.append(c)
    with open(samples_p, "w", encoding="utf-8") as f:
        json.dump(S, f, indent=1)
    return v


def main(argv):
    if argv[:1] == ["record"]:
        # record <op> <variant> --delta '{"C":1}' --cites cites.json [--why ..] [--samples ..] [--n N]
        it, kw = iter(argv[3:]), {"samples": DEFAULT_SAMPLES, "why": "", "n": "1"}
        for x in it:
            kw[x.lstrip("-")] = next(it)
        try:
            v = record_sample(kw["samples"], argv[1], argv[2], json.loads(kw["delta"]), _load(kw["cites"]), kw["why"], n=int(kw["n"]))
        except (ValueError, KeyError, OSError, IndexError) as e:
            print("RECORD REFUSED %s" % e)
            print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL", "gates": {"pass": 0, "fail": 1},
                                          "first_fail": ("record refused: %s" % e)[:200], "artefacts": []}))
            return 4
        print("RECORDED %s/%s %s" % (argv[1], argv[2], json.dumps(v["delta"])))
        print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None,
                                      "artefacts": [{"path": kw["samples"].replace("\\", "/"), "md5": md5_of(kw["samples"])}]}))
        return 0
    args, samples_p, out_p = [], DEFAULT_SAMPLES, None
    it = iter(argv)
    for x in it:
        if x == "--samples":
            samples_p = next(it)
        elif x == "--json":
            out_p = next(it)
        else:
            args.append(x)
    if len(args) != 2:
        print(__doc__)
        print('RESULT {"schema":"result-line/1","status":"FAIL","gates":{"pass":0,"fail":1},'
              '"first_fail":"usage: census_predict.py <plan.json> <pred.json>","artefacts":[]}')
        return 4
    plan_p, pred_p = args
    try:
        plan, pred, samples = _load(plan_p), _load(pred_p), _load(samples_p)
    except (OSError, ValueError) as e:
        print("INPUT ERROR %s" % e)
        print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL", "gates": {"pass": 0, "fail": 1},
                                      "first_fail": ("input error: %s" % e)[:200], "artefacts": []}))
        return 4
    print("census_predict  plan %s (%s)  pred %s (%s)  samples %s (%s)" % (
        plan_p, md5_of(plan_p), pred_p, md5_of(pred_p), samples_p, md5_of(samples_p)))
    rep = predict(plan, pred, samples)
    for r in rep["rows"]:
        print("  ROW %2d %-24s %-40s %-8s %-20s %s" % (r["k"], r["id"], r["op"], r["variant"] or "-",
                                                      r["verdict"], json.dumps(r["delta"]) if r["delta"] else r["why"]))
    for p in rep["classes"]:
        print("  CLASS %-24s derived %+4d declared %5s  %s" % (
            p["class"], p["derived"], "-" if p["declared"] is None else "%+d" % p["declared"], p["verdict"]))
        if p["verdict"] == "SOFT":                       # card chat-S2: one soft-log line per LOG-only class
            _gateclass.soft_record("CENSUS %s" % os.path.basename(plan_p), p["class"], p["declared"], p["derived"], p.get("rule"))
    print("CENSUS VERDICT %s%s" % (rep["overall"], ("  unpredicted rows %s" % rep["unpredicted"]) if rep["unpredicted"] else ""))
    arts = []
    if out_p:
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=1)
        arts.append({"path": out_p.replace("\\", "/"), "md5": md5_of(out_p)})
    print(result_line(rep, arts))
    return {"PASS": 0, "FAIL": 1, "UNPREDICTED": 2, "UNDECLARED": 3}[rep["overall"]]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
