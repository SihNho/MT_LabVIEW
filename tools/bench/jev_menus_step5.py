r"""STEP 5 measurement + the real M3a-4 decision record. NO LabVIEW - wiki/graph JSONs on disk + Jev over HTTPS.

    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/jev_menus_step5.log -- py -u tools/bench/jev_menus_step5.py [--dry]

PREDICTION CONTRACT (written before the run):
  M0  bed md5 in the wiki == 0b84595245dd650c0e8fd3f57104782c; S1 wiki loads; no LabVIEW process is touched
  M1  labelled sets written: pair >= 20 items (>= 9 positives), op >= 20, risk == 28 (8 + 20), chain >= 10 positive links
  M2  every labelled item gets a Jev answer (n_ok >= 1 of 5) - a missing key or HTTP failure FAILS this gate
  M3  per menu: acc@0.5, Brier, confusion, threshold sweep written to tools/bench/jev_menu_<name>_result.json;
      thresholds written to tools/bench/jev_menu_thresholds.json; a menu below 80 % or n < 20 -> acts: false
  M4  E: decision_m3a4.json written with 11 intents, one decision each; action in {wire, llm, skip}; NOTHING wired
  PREDICTED VALUES (desk-derived before the run, stated so a miss is visible):
      candidates generator on the bed, replace=False: rows 1731/1893/2819/3947/4833/7388/9635/11232/23502/23540
      have ZERO legal pairs (their S1 sink is occupied by a live source) and 7337 has exactly ONE (#11263 outer
      'VISA out' -> #4334 inner, a half-wire sink, scope cousins, 2 borders) - measured in the exploration run.
      Jev accuracies: not predicted (that is what is being measured).

PRIOR ART CHECKED: tools/bench/jev_trial.py / jev_triage_trial.py (the measure-then-threshold pattern: acc, Brier,
sweep), tools/bench/diag_vigraph_check.py (graph load), tools/jev_rowcheck.py. No step-5 set existed.
"""
import concurrent.futures as cf
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import jev  # noqa: E402
import jev_candidates as JC  # noqa: E402
import jev_chain as CH  # noqa: E402
import jev_pairs as JP  # noqa: E402
import vigraph as V  # noqa: E402

BED_MD5 = "0b84595245dd650c0e8fd3f57104782c"
DRY = "--dry" in sys.argv
WORKERS = 4
N = {"pass": 0, "fail": 0}
T0 = time.time()


def gate(label, ok, detail=""):
    N["pass" if ok else "fail"] += 1
    print("  {0}  {1}{2}".format("PASS" if ok else "FAIL", label, (" | " + str(detail)[:500]) if detail else ""),
          flush=True)


def fact(s):
    print("  FACT  " + s, flush=True)


def dump(name, obj):
    p = os.path.join(HERE, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, default=str)
    return p


# S1 severed rows: (wire, S1 src node, S1 dst node). Endpoints: tools/bench/vigraph_check.log G2g lines.
S1_ROWS = [(1731, 4344, 48), (1893, 3447, 48), (2819, 3560, 48), (3947, 4274, 48), (4833, 3529, 48),
           (7337, 11263, 4334), (7388, 48, 11348), (9635, 9641, 9623), (11232, 48, 11220)]
# S3b rows: docs/m3a1-severed-rows.md s3 (#10407 t0 / t2); graph ends = the bed's edges #23499 -> #10429 outer,
# #23523 -> #10978 outer (graph_diff_s1_bed edges_added).
S3B_ROWS = [(23502, 23499, 10429, "#10407 t0 ''"), (23540, 23523, 10978, "#10407 t2 'index'")]


def s1_endpoints(A, B, wire):
    ks = V.wire_terminals(A, wire)
    src = [k for k in ks if A["rows"][k]["is_source"]][0]
    snk = [k for k in ks if not A["rows"][k]["is_source"]][0]
    bs, ms = JC.map_key(B, src, A)
    bd, md = JC.map_key(B, snk, A)
    return src, snk, bs, bd, (ms, md)


def intents(A, B):
    out = []
    for w, s, d in S1_ROWS:
        src, snk, bs, bd, how = s1_endpoints(A, B, w)
        out.append({"id": w, "src": s, "dst": d, "src_hint": A["rows"][src]["term_name"],
                    "dst_hint": A["rows"][snk]["term_name"], "s1_src": src, "s1_sink": snk,
                    "true_src": bs, "true_dst": bd, "key_map": how,
                    "line": "restore the S1 connection of severed wire {0}: node #{1} ({2}) output {3!r} -> node "
                            "#{4} ({5}) input {6!r}".format(w, s, A["cls"].get(s), A["rows"][src]["term_name"], d,
                                                            A["cls"].get(d), A["rows"][snk]["term_name"])})
    for w, s, tun, doc in S3B_ROWS:
        src = V.terminals(B, node=s, is_source=True)[0]
        snk = V.terminals(B, node=tun, cls="OuterTerminal", is_source=False)[0]
        out.append({"id": w, "src": s, "dst": {"structure": 10407}, "src_hint": B["rows"][src]["term_name"],
                    "dst_hint": B["rows"][snk]["term_name"], "s1_src": None, "s1_sink": None,
                    "true_src": src, "true_dst": snk, "key_map": "bed edge (row created in S3b; S1 has none)",
                    "line": "restore severed wire {0}: Local node #{1} output {2!r} -> CaseStructure #10407 input "
                            "{3} (docs/m3a1-severed-rows.md s3)".format(w, s, B["rows"][src]["term_name"], doc)})
    return out


# ------------------------------------------------------------------------------------------------ labelled sets
def pair_set(A, B, ints):
    items = []
    for it in ints:
        c = JC.candidates(B, dict(it, replace=True))
        for p in c["pairs"]:
            lab = (p["src"]["key"] == it["true_src"] and p["dst"]["key"] == it["true_dst"])
            items.append({"intent_id": it["id"], "line": it["line"], "cand": p, "label": lab})
    return items


# op history (tools/bench/build_d1_m3a1.log:3120-3281, build_d1_m3a2.log:143/207,
# build_d1_m3a3b_rowD_clean.log:96, diag_c64_s3b_row1.log:183, diag_c65_s3b_row2.log:198,
# diag_s58_boolwire.log:151). (src uid, src term class, dst uid, dst term class, dst name or None, op, source)
OP_HISTORY = [
    (11263, "OuterTerminal", 23868, "InnerTerminal", None, "wire_sr", "build_d1_m3a1.log:3120 RightIn reg0"),
    (2017, "OuterTerminal", 23895, "InnerTerminal", None, "wire_sr", "build_d1_m3a1.log:3138 RightIn reg1"),
    (23880, "InnerTerminal", 48, "Terminal", "VISA resource name", "wire_sr", "build_d1_m3a1.log:3156 LeftIn reg0"),
    (23909, "InnerTerminal", 48, "Terminal", "In position", "wire_sr", "build_d1_m3a1.log:3174 LeftIn reg1"),
    (24035, "InnerTerminal", 9623, "OuterTerminal", None, "connect_from_wire", "build_d1_m3a1.log:3194 [5]"),
    (24018, "InnerTerminal", 12673, "OuterTerminal", None, "connect_from_wire", "build_d1_m3a1.log:3281 [5b]"),
    (4194, "Terminal", 23880, "OuterTerminal", None, "connect_from_wire", "build_d1_m3a2.log:143 ROW A"),
    (3974, "Terminal", 23909, "OuterTerminal", None, "connect_from_wire", "build_d1_m3a2.log:207 ROW B"),
    (23868, "OuterTerminal", 7468, "Terminal", None, "fs_inner_tunnel_connect", "build_d1_m3a3b_rowD_clean.log:96"),
    (23499, "Terminal", 10429, "OuterTerminal", None, "connect_nested", "diag_c64_s3b_row1.log:183"),
    (23523, "Terminal", 10978, "OuterTerminal", None, "connect_nested", "diag_c65_s3b_row2.log:198"),
    (10686, "ParameterTerminal", 23576, "ControlTerminal", None, "wire_indicators", "diag_s58_boolwire.log:151"),
    (10757, "Terminal", 23541, "ControlTerminal", None, "wire_indicators",
     "INFERRED: S3a's second half, same verb as diag_s58_boolwire.log:151 (not read from its own log)"),
]
# capability-rule rows: labelled from docs/toolkit-capabilities.md rows 67/70 + NAMES.md:278-280, NOT from a run
RULE_PATTERNS = [
    (("SubVI", "Terminal"), ("SubVI", "Terminal"), "connect_nested", 3),
    (("LoopTunnel", "InnerTerminal"), ("SubVI", "Terminal"), "connect_from_wire", 2),
    (("SubVI", "Terminal"), ("FlatSequenceInnerTunnel", "Terminal"), "fs_inner_tunnel_connect", 2),
]


def edge_cand(B, sk, dk):
    s, d = JC.term_row(B, sk), JC.term_row(B, dk)
    rel, borders = JC.scope(B, s["diagram"], d["diagram"])
    return {"row_key": {"src_uid": s["uid"], "src_term": s["term"], "dst_uid": d["uid"], "dst_term": d["term"]},
            "src": s, "dst": d, "sink_state": "occupied", "scope": rel, "borders": borders}


def op_set(B):
    items, used = [], set()
    wires = [(a, b) for k, a, b, _i in B["edges"] if k == "wire"]
    for su, sc, du, dc, dn, op, src in OP_HISTORY:
        hit = [(a, b) for a, b in wires if V.key_parts(a)[0] == su and B["rows"][a]["term_class"] == sc and
               V.key_parts(b)[0] == du and B["rows"][b]["term_class"] == dc and
               (dn is None or B["rows"][b]["term_name"] == dn)]
        if not hit:
            fact("OP history row NOT FOUND in the bed graph: #{0} -> #{1} ({2})".format(su, du, src))
            continue
        a, b = hit[0]
        used.add((a, b))
        items.append({"cand": edge_cand(B, a, b), "label": op, "provenance": "history", "source": src})
    for (scl, stc), (dcl, dtc), op, k in RULE_PATTERNS:
        got = 0
        for a, b in sorted(wires):
            if (a, b) in used:
                continue
            ra, rb = B["rows"][a], B["rows"][b]
            if B["cls"].get(ra["node"]) == scl and ra["term_class"] == stc and B["cls"].get(rb["node"]) == dcl \
                    and rb["term_class"] == dtc:
                items.append({"cand": edge_cand(B, a, b), "label": op, "provenance": "capability-rule",
                              "source": "docs/toolkit-capabilities.md:67/70, NAMES.md:278-280"})
                used.add((a, b))
                got += 1
                if got == k:
                    break
    return items


def risk_set(A, B):
    cd = json.load(open(os.path.join(HERE, "graph_computation_diff_s1_bed_20260923.json"), encoding="utf-8"))
    diff = json.load(open(os.path.join(HERE, "graph_diff_s1_bed_20260923.json"), encoding="utf-8"))
    added = set(int(x["node"]) for x in cd["computation_nodes_added"])
    items = []
    for x in cd["computation_nodes_added"]:
        n = int(x["node"])
        ins = sorted(set(V.show(a) for k, a, b, _i in B["edges"] if k == "wire" and V.key_parts(b)[0] == n))[:4]
        outs = sorted(set(V.show(b) for k, a, b, _i in B["edges"] if k == "wire" and V.key_parts(a)[0] == n))[:4]
        items.append({"change": "node #{0} ({1}) added".format(n, x["class"]),
                      "evidence": {"node_in_original": n in A["cls"], "class": x["class"],
                                   "scheduling_under_assumption_A": False, "inputs_from": ins, "outputs_to": outs,
                                   "listed_by_computation_diff_as": "computation_nodes_added"},
                      "label": True})
    neg = 0
    for k, a, b in sorted(tuple(e) for e in diff["edges_added"]):
        na, nb = V.key_parts(a)[0], V.key_parts(b)[0]
        if na in added or nb in added:
            continue
        eff_b = sorted(V.show(x) for x in V.effective_sources(B, b)) if b in B["rows"] else None
        eff_a = sorted(V.show(x) for x in V.effective_sources(A, b)) if b in A["rows"] else "sink not in original"
        items.append({"change": "{0} edge {1} -> {2}".format(k, V.show(a), V.show(b)),
                      "evidence": {"source_is_scheduling": V.is_scheduling(B, na),
                                   "sink_is_scheduling": V.is_scheduling(B, nb),
                                   "sink_effective_sources_original": eff_a, "sink_effective_sources_now": eff_b,
                                   "computation_diff_rows_whole_vi": len(cd["rows"])},
                      "label": False})
        neg += 1
        if neg == 20:
            break
    return items


CHAIN_ENDS = [(6810, 376), (6810, 5696), (5058, 28233), (5696, 29009), (19093, 26539), (48, 19093),
              (21046, 1779), (28083, 29009), (28180, 28233), (6085, 30306), (5058, 376)]


def chain_set(A):
    scope = CH.subvi_nodes_in_scope(A, 639)
    items = []
    for y, z in CHAIN_ENDS:
        succ = CH.direct_successors(A, y)
        others = [x for x in scope if x not in (y,)]
        pos = [x for x in others if CH.true_next(A, y, z, x)]
        hard = [x for x in others if x in succ and x not in pos]
        rest = [x for x in others if x not in pos and x not in hard][:3]
        for x in pos + hard + rest:
            items.append({"y": y, "z": z, "x": x, "label": x in pos,
                          "kind": "pos" if x in pos else ("hard-neg" if x in hard else "neg")})
    return items


# ------------------------------------------------------------------------------------------------ scoring
def brier(ps, ls):
    return sum((p - (1.0 if l else 0.0)) ** 2 for p, l in zip(ps, ls)) / max(1, len(ps))


def score_binary(items, name):
    ok = [i for i in items if i.get("p") is not None]
    ps, ls = [i["p"] for i in ok], [bool(i["label"]) for i in ok]
    acc = sum((p >= 0.5) == l for p, l in zip(ps, ls)) / max(1, len(ok))
    tp = sum(p >= 0.5 and l for p, l in zip(ps, ls)); fp = sum(p >= 0.5 and not l for p, l in zip(ps, ls))
    fn = sum(p < 0.5 and l for p, l in zip(ps, ls)); tn = sum(p < 0.5 and not l for p, l in zip(ps, ls))
    sweep = []
    for t in [x / 100.0 for x in range(5, 100, 5)]:
        yes = [(p, l) for p, l in zip(ps, ls) if p >= t]
        no = [(p, l) for p, l in zip(ps, ls) if p <= t]
        sweep.append({"t": t, "n_yes": len(yes), "prec_yes": (sum(l for _p, l in yes) / len(yes)) if yes else None,
                      "recall_yes": (sum(l for _p, l in yes) / max(1, sum(ls))),
                      "n_no": len(no), "npv_no": (sum(not l for _p, l in no) / len(no)) if no else None})
    return {"menu": name, "n": len(items), "n_answered": len(ok), "n_pos": sum(ls), "acc@0.5": round(acc, 4),
            "brier": round(brier(ps, ls), 4), "confusion@0.5": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
            "sweep": sweep}


def run_items(items, fn, label):
    t = time.time()
    if DRY:
        return 0
    with cf.ThreadPoolExecutor(WORKERS) as ex:
        futs = {ex.submit(fn, it): it for it in items}
        for f in cf.as_completed(futs):
            it = futs[f]
            try:
                f.result()
            except Exception as e:                                              # noqa: BLE001
                it["err"] = "{0}: {1}".format(type(e).__name__, e)
    fact("{0}: {1} items in {2:.1f}s".format(label, len(items), time.time() - t))
    return time.time() - t


def main():
    print("=== STEP 5 jev menus ({0})".format("DRY" if DRY else "LIVE"), flush=True)
    B = JC.load(JC.BED_KEY)
    A = JC.load(JC.S1_KEY)
    gate("M0 bed wiki md5", B["wiki"]["md5"] == BED_MD5, B["wiki"]["md5"])
    gate("M0b jev key present", DRY or bool(jev.get_key()), "key presence only; value never read out")
    ints = intents(A, B)
    for it in ints:
        fact("INTENT {0}: true {1} -> {2} ({3})".format(it["id"], it["true_src"] and V.show(it["true_src"]),
                                                       it["true_dst"] and V.show(it["true_dst"]), it["key_map"]))
    P, O, R, C = pair_set(A, B, ints), op_set(B), risk_set(A, B), chain_set(A)
    gate("M1a pair set >= 20 items, >= 9 positives", len(P) >= 20 and sum(i["label"] for i in P) >= 9,
         "{0} items, {1} pos".format(len(P), sum(i["label"] for i in P)))
    gate("M1b op set >= 20", len(O) >= 20, "{0} items ({1} history, {2} rule)".format(
        len(O), sum(i["provenance"] == "history" for i in O), sum(i["provenance"] != "history" for i in O)))
    gate("M1c risk set == 28 (8 + 20)", len(R) == 28 and sum(i["label"] for i in R) == 8,
         "{0} items, {1} pos".format(len(R), sum(i["label"] for i in R)))
    gate("M1d chain set >= 10 positive links", sum(i["label"] for i in C) >= 10,
         "{0} items, {1} pos".format(len(C), sum(i["label"] for i in C)))
    for name, s in (("pair", P), ("op", O), ("risk", R), ("chain", C)):
        dump("jev_menu_{0}_set.json".format(name),
             [dict((k, v) for k, v in i.items() if k != "cand") | ({"row": JP.op_state(i["cand"])["row"]}
                                                                  if "cand" in i else {}) for i in s])

    def f_pair(i):
        i["p"], sp, i["err"] = JP.ask_pair(i["line"], i["cand"])
        i["spread"] = (sp or {}).get("spread")

    def f_op(i):
        i["pred"], i["probs"], i["opts"], i["err"] = JP.ask_op(i["cand"])

    def f_risk(i):
        i["p"], sp, i["err"] = JP.ask_risk(i["change"], i["evidence"])

    def f_chain(i):
        i["p"], sp, i["err"] = CH.ask_link(A, i["y"], i["z"], i["x"])

    secs = {}
    for name, s, fn in (("pair", P, f_pair), ("op", O, f_op), ("risk", R, f_risk), ("chain", C, f_chain)):
        secs[name] = run_items(s, fn, name)
    if DRY:
        print("=== STEP 5 DRY: {0} pass / {1} fail".format(N["pass"], N["fail"]))
        return 1 if N["fail"] else 0

    answered = all((i.get("p") is not None) for i in P + R + C) and all(i.get("pred") for i in O)
    gate("M2 every labelled item answered", answered,
         "missing: " + str([(k, sum(1 for i in s if i.get("p") is None and i.get("pred") is None))
                            for k, s in (("pair", P), ("op", O), ("risk", R), ("chain", C))]))
    res = {}
    for name, s in (("pair", P), ("risk", R), ("chain", C)):
        res[name] = score_binary(s, name)
    # op: choice accuracy + confidence sweep
    ok = [i for i in O if i.get("pred")]
    acc = sum(i["pred"] == i["label"] for i in ok) / max(1, len(ok))
    hist = [i for i in ok if i["provenance"] == "history"]
    sweep = []
    for t in [x / 100.0 for x in range(40, 100, 5)]:
        acted = [i for i in ok if (i["probs"] or {}).get(i["pred"], 0) >= t]
        sweep.append({"t": t, "n_acted": len(acted),
                      "acc_acted": (sum(i["pred"] == i["label"] for i in acted) / len(acted)) if acted else None})
    br = sum(sum(((i["probs"] or {}).get(o, 0) - (1.0 if o == i["label"] else 0.0)) ** 2 for o in i["opts"])
             for i in ok) / max(1, len(ok))
    conf = {}
    for i in ok:
        conf.setdefault("{0} -> {1}".format(i["label"], i["pred"]), 0)
        conf["{0} -> {1}".format(i["label"], i["pred"])] += 1
    res["op"] = {"menu": "op", "n": len(O), "n_answered": len(ok), "acc": round(acc, 4),
                 "acc_history": round(sum(i["pred"] == i["label"] for i in hist) / max(1, len(hist)), 4),
                 "n_history": len(hist), "brier_multiclass": round(br, 4), "confusion": conf, "sweep": sweep}

    # thresholds from the curves (rules stated in jev_pairs.py docstring)
    th = {"measured": time.strftime("%Y-%m-%d %H:%M:%S"), "rules": {
        "pair/chain": "act = smallest t whose yes-precision is 1.0 with >= 1 yes; acts iff acc@0.5 >= 0.80 and n >= 20",
        "op": "act = smallest t whose acted-accuracy is 1.0; acts iff acc >= 0.80 and n >= 20",
        "risk": "act (proceed when p_risk <= t) = largest t below every positive's p; acts iff acc@0.5 >= 0.80 and n >= 20"}}
    for name in ("pair", "chain"):
        r = res[name]
        t = next((s["t"] for s in r["sweep"] if s["t"] >= 0.5 and s["n_yes"] and s["prec_yes"] == 1.0), None)
        th[name] = {"act": t if t is not None else 1.01, "acts": bool(r["acc@0.5"] >= 0.80 and r["n"] >= 20 and t),
                    "acc": r["acc@0.5"], "brier": r["brier"], "n": r["n"]}
    t = next((s["t"] for s in res["op"]["sweep"] if s["n_acted"] and s["acc_acted"] == 1.0), None)
    th["op"] = {"act": t if t is not None else 1.01, "acts": bool(res["op"]["acc"] >= 0.80 and len(O) >= 20 and t),
                "acc": res["op"]["acc"], "brier": res["op"]["brier_multiclass"], "n": len(O)}
    pos_p = [i["p"] for i in R if i["label"] and i.get("p") is not None]
    cand_t = [s["t"] for s in res["risk"]["sweep"] if s["t"] <= 0.5 and (not pos_p or s["t"] < min(pos_p))]
    tr = max(cand_t) if cand_t else 0.0
    th["risk"] = {"act": tr, "acts": bool(res["risk"]["acc@0.5"] >= 0.80 and len(R) >= 20 and tr > 0),
                  "acc": res["risk"]["acc@0.5"], "brier": res["risk"]["brier"], "n": len(R)}
    dump("jev_menu_thresholds.json", th)
    for name in ("pair", "op", "risk", "chain"):
        dump("jev_menu_{0}_result.json".format(name), {"result": res[name], "threshold": th[name],
                                                       "items": [dict((k, v) for k, v in i.items() if k != "cand")
                                                                 for i in {"pair": P, "op": O, "risk": R,
                                                                           "chain": C}[name]]})
        fact("MENU {0}: n={1} acc={2} brier={3} act={4} acts={5} | {6}".format(
            name, th[name]["n"], th[name]["acc"], th[name]["brier"], th[name]["act"], th[name]["acts"],
            json.dumps(res[name].get("confusion@0.5") or res[name].get("confusion"))))
    fact("op history-only acc {0} (n={1})".format(res["op"]["acc_history"], res["op"]["n_history"]))
    for i in P:
        if (i["p"] is not None) and ((i["p"] >= 0.5) != i["label"]):
            fact("PAIR MISS {0}: {1} label={2} p={3:.3f}".format(i["intent_id"], JP.op_state(i["cand"])["row"][:160],
                                                                  i["label"], i["p"]))
    for i in O:
        if i.get("pred") and i["pred"] != i["label"]:
            fact("OP MISS {0} -> {1} ({2}) {3}".format(i["label"], i["pred"], i["provenance"],
                                                      JP.op_state(i["cand"])["row"][:140]))
    for i in R:
        if i.get("p") is not None and (i["p"] >= 0.5) != i["label"]:
            fact("RISK MISS label={0} p={1:.3f} {2}".format(i["label"], i["p"], i["change"][:140]))
    for i in C:
        if i.get("p") is not None and (i["p"] >= 0.5) != i["label"]:
            fact("CHAIN MISS {0}->{1} x={2} ({3}) p={4:.3f}".format(i["y"], i["z"], i["x"], i["kind"], i["p"]))
    gate("M3 results + thresholds written", True, th["rules"])

    # ---------------------------------------------------------------------------------------- E: M3a-4 record
    tE = time.time()
    cands, decs = [], []
    for it in ints:
        c = JC.candidates(B, dict(it, replace=False))
        cands.append(c)
        s1_edge = bool(it["true_src"] and it["true_dst"] and any(
            k == "wire" and a == it["true_src"] and b == it["true_dst"] for k, a, b, _i in B["edges"]))
        eff_same = None
        if it["s1_sink"] and it["true_dst"]:
            eff_same = set(V.show(x) for x in V.effective_sources(A, it["s1_sink"])) == \
                set(V.show(x) for x in V.effective_sources(B, it["true_dst"]))
        if not c["pairs"]:
            d = {"row_key": {"src_uid": it["src"], "src_term": it["src_hint"],
                             "dst_uid": it["dst"] if isinstance(it["dst"], int) else it["dst"],
                             "dst_term": it["dst_hint"]},
                 "pair_p": None, "op": None, "op_p": None, "risk_p": None,
                 "action": "skip" if (s1_edge or eff_same) else "llm", "decided_by": "python",
                 "evidence": {"reason": "no legal candidate (every sink of the dst is fed by a live source)",
                              "excluded": c["excluded"], "s1_edge_present_in_bed": s1_edge,
                              "effective_sources_identical_to_s1": eff_same}, "jev_calls": 0}
        else:
            d = JP.decide(it["line"], c, G_orig=A, G_new=B, orig_sink_key=it["s1_sink"], th=th)
            d["evidence"]["s1_edge_present_in_bed"] = s1_edge
            d["evidence"]["effective_sources_identical_to_s1"] = eff_same
        d["intent_id"] = it["id"]
        decs.append(d)
        fact("M3a-4 {0}: {1} pairs, action={2} by {3}, pair_p={4} op={5} op_p={6} risk_p={7} | {8}".format(
            it["id"], len(c["pairs"]), d["action"], d["decided_by"], d["pair_p"], d["op"], d["op_p"], d["risk_p"],
            d["evidence"].get("reason", "")))
    ip = [dict((k, v) for k, v in it.items()) for it in ints]
    p, rec = JP.write_record("m3a4", B["wiki"]["md5"], ip, cands, decs, tE,
                             extra={"note": "STEP 5 record - nothing was wired; step 6 executes 'wire' rows only"})
    acts = {}
    for d in decs:
        acts[d["action"]] = acts.get(d["action"], 0) + 1
    gate("M4 decision_m3a4.json: 11 intents, one decision each, actions valid",
         len(decs) == 11 and all(d["action"] in ("wire", "llm", "skip") for d in decs), acts)
    fact("wrote {0}: actions {1}, jev_calls {2}, {3}".format(os.path.basename(p), acts, rec["jev_calls"],
                                                            rec["cost"]))
    total_calls = sum(1 for _ in open(jev.LEDGER, encoding="utf-8"))
    fact("measurement seconds {0}; total {1:.0f}s; ledger lines now {2}".format(
        dict((k, round(v, 1)) for k, v in secs.items()), time.time() - T0, total_calls))
    print("=== STEP 5: {0} pass / {1} fail".format(N["pass"], N["fail"]), flush=True)
    return 1 if N["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
