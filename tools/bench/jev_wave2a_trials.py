r"""jev_wave2a_trials.py - MEASURE the three 2차 insertions the user approved on 2026-09-22 17:3x
("이거 다 적용해보자"): #6 consensus, #2 gate-row triage, #1 the review ladder.

NO LabVIEW. This reads .log and .md files off disk and, through tools/jev.py ONLY, calls api.typesafe.ai.
No COM, no VISA, no motor, no camera, no GUI, no .vi is opened.

PREDICTION CONTRACT (written before the run):
  A1  the c80 pair answers on both consensus runs                                     -> 2/2
  A2  the two runs' MEAN probabilities differ by <= 0.05, and each run's SPREAD <= 0.15
      (the pair that flapped 0.80 / 0.78 / 0.80 / 0.79 across single calls)            -> GATED
  B1  every labelled gate row is found in its log by its `starts` prefix               -> 68/68
  B2  every found row gets an answer (a class and a mean probability)                  -> 68/68
  B3  accuracy vs the hand labels                                                      -> REPORTED, not gated
  C1  every labelled review resolves to a trigger log AND a run index                  -> 16/16
  C2  every resolved run produces a failure summary                                    -> 16/16
  C3  3-way accuracy vs the hand labels, and the headline the user asked for:
      "the ladder would have skipped N of 16 reviews, of which M would have been WRONG" -> REPORTED
  D   total Jev spend stays under $0.10 (ledger lines x the measured $/call)           -> GATED

WHAT ALREADY EXISTS (checked before writing):
  tools/jev.py (transport, ledger, ask_n, summarise_failure) · tools/bench/jev_gate.py (COVERS_Q, LADDER_Q,
  jev_discharge, recent_adversary_reviews) · tools/bench/jev_gaterow_q.py (GATEROW_Q, fail_rows) ·
  tools/jev_gaterow.py (classify) · tools/bench/jev_trial.py + jev_triage_trial.py (the 1차 trial shape, reused
  verbatim here: gate lines, confusion matrix, disagreement list, JSON readings). Nothing is re-implemented.

NOTHING IS WRITTEN INTO archive/peer/. The ladder cell runs jev_gate.jev_discharge with write=False and with
GATE_LOG redirected, so no citation is appended to any review file and no discharge cache entry is created by a
measurement. The gate-row cell DOES append its `JEV-GATEROW` verdict lines to tools/bench/jev_gate.log, which is
this device's own audit trail.
"""
import json
import os
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
PEER = os.path.join(ROOT, "archive", "peer")
for _p in (TOOLS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import jev                                              # noqa: E402
import jev_gate                                         # noqa: E402
import jev_gaterow                                      # noqa: E402
from jev_gaterow_q import CLASSES as ROW_CLASSES, fail_rows   # noqa: E402

GATEROW_SET = os.path.join(HERE, "jev_gaterow_set.json")
LADDER_SET = os.path.join(HERE, "jev_ladder_set.json")
OUT = os.path.join(HERE, "jev_wave2a_trials.json")
GATELOG = os.path.join(HERE, "jev_gate.log")
USD_PER_CALL = 0.025 / 326.0        # measured 2026-09-22: 326 calls, $0.025 (docs/jev-integration-plan.md)
BUDGET_S = 18 * 60                  # leave room inside the 25-minute bgrun deadline

NPASS = NFAIL = 0
T0 = time.time()


def gate(ok, label, detail=""):
    global NPASS, NFAIL
    if ok:
        NPASS += 1
        print("  PASS  %s  %s" % (label, detail))
    else:
        NFAIL += 1
        print("  FAIL  %s  %s" % (label, detail))
    sys.stdout.flush()


def ledger_lines():
    try:
        with open(jev.LEDGER, encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def out_of_time(why):
    if time.time() - T0 > BUDGET_S:
        print("\n*** BUDGET STOP after %.0f s: %s ***" % (time.time() - T0, why))
        return True
    return False


# ------------------------------------------------------------------ CELL A: #6 consensus on the c80 pair
def cell_a():
    print("\n=== CELL A - #6 CONSENSUS, the pair that flapped (c80_rowd_routeA_r2.log x c80-...-r2.md)")
    logp = os.path.join(HERE, "c80_rowd_routeA_r2.log")
    revp = os.path.join(PEER, "2026-09-22-c80-rowd-routeA-swapped-r2.md")
    fs = jev.summarise_failure(logp)
    rs = jev_gate.summarise_review(revp)
    runs = []
    for k in (1, 2):
        t0 = time.time()
        mean, spread, err = jev.ask_n({"failure": fs, "review": rs},
                                      {"review_covers_failure": jev_gate.COVERS_Q},
                                      n=5, purpose="wave2a-consensus")
        dt = time.time() - t0
        if err or mean is None:
            print("  run %d: ERROR %s" % (k, err))
            runs.append(None)
            continue
        print("  run %d: mean p=%.4f  spread=%.4f  n_ok=%d/%d  values=%s  (%.1f s)" % (
            k, mean, spread["spread"], spread["n_ok"], spread["n"], spread["values"], dt))
        runs.append({"mean": mean, "spread": spread["spread"], "values": spread["values"], "wall_s": round(dt, 1)})
        sys.stdout.flush()
    ok = [r for r in runs if r]
    gate(len(ok) == 2, "A1 both consensus runs answered", "%d/2" % len(ok))
    if len(ok) == 2:
        drift = abs(ok[0]["mean"] - ok[1]["mean"])
        worst = max(r["spread"] for r in ok)
        gate(drift <= 0.05 and worst <= 0.15,
             "A2 run-to-run mean drift <= 0.05 and per-run spread <= 0.15",
             "drift %.4f ; worst spread %.4f" % (drift, worst))
    return {"runs": runs}


# ------------------------------------------------------------------ CELL B: #2 gate-row triage
def cell_b():
    print("\n=== CELL B - #2 GATE-ROW TRIAGE over %s" % os.path.basename(GATEROW_SET))
    doc = json.load(open(GATEROW_SET, encoding="utf-8"))
    items = doc["items"]
    print("=== %d labelled row(s); classes: %s" % (len(items), ", ".join(ROW_CLASSES)))
    cache, rows, missing, noanswer, lines = {}, [], [], [], []
    for it in items:
        if out_of_time("cell B"):
            break
        logp = os.path.join(HERE, it["log"])
        if it["log"] not in cache:
            cache[it["log"]] = fail_rows(logp)
        hit = next((r for r in cache[it["log"]] if r["row"].startswith(it["starts"])), None)
        if hit is None:
            missing.append((it["log"], it["starts"]))
            print("  MISS %-30s %s" % (it["log"], it["starts"][:60]))
            continue
        cls, p, sp = jev_gaterow.classify(hit["state"], purpose="wave2a-gaterow")
        if p is None:
            noanswer.append((it["log"], it["starts"]))
            print("  ERR  %-30s no answer" % it["log"])
            continue
        ok = (cls == it["label"])
        rows.append({"log": it["log"], "label": hit["label"], "truth": it["label"], "jev": cls,
                     "p": p, "spread": sp, "ok": ok, "row": hit["row"][:180], "why": it["why"]})
        line = "JEV-GATEROW | %s | %s | %s p=%.2f" % (it["log"], hit["label"], cls, p)
        lines.append(line)
        print("  %-4s %s   truth=%-16s (spread %.2f)" % ("OK" if ok else "DIFF", line, it["label"], sp or 0.0))
        sys.stdout.flush()
    try:
        with open(GATELOG, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    except OSError:
        pass
    n = len(rows)
    nok = sum(1 for r in rows if r["ok"])
    gate(not missing, "B1 every labelled row was found by its prefix",
         "%d/%d found" % (len(items) - len(missing), len(items)))
    gate(not noanswer, "B2 every found row got an answer", "%d answered" % n)
    print("=== B3 ACCURACY vs the hand labels: %d/%d = %.1f %%" % (nok, n, 100.0 * nok / max(n, 1)))
    conf = [c for c in ROW_CLASSES] + ["unknown"]
    print("\n=== CONFUSION MATRIX (rows = my label, columns = Jev)")
    print("    %-20s%s" % ("", "".join("%-20s" % c for c in conf)))
    for c in ROW_CLASSES:
        line = "".join("%-20d" % sum(1 for r in rows if r["truth"] == c and r["jev"] == d) for d in conf)
        print("    %-20s%s  (n=%d)" % (c, line, sum(1 for r in rows if r["truth"] == c)))
    print("\n=== DISAGREEMENTS (%d)" % (n - nok))
    for r in rows:
        if not r["ok"]:
            print("  - %-28s %-14s mine=%-17s jev=%-17s p=%.2f" % (
                r["log"], r["label"], r["truth"], r["jev"], r["p"]))
            print("      row : %s" % r["row"][:150])
            print("      mine: %s" % r["why"][:150])
    sp = [r["spread"] for r in rows if r["spread"] is not None]
    print("\n=== B4 mean consensus spread over %d rows: %.3f (max %.3f)" % (
        len(sp), sum(sp) / max(len(sp), 1), max(sp) if sp else 0.0))
    return {"n": n, "accuracy": nok / max(n, 1), "rows": rows, "missing": missing, "noanswer": noanswer}


# ------------------------------------------------------------------ CELL C: #1 the review ladder
import re  # noqa: E402

_DATE_RE = re.compile(r"^\-\s*\*\*date:\*\*\s*([\d]{4}-[\d]{2}-[\d]{2} [\d:]{8})", re.M)
_LOG_RE = re.compile(r"([\w.\-]+\.log)")
_RUNSTART_RE = re.compile(r"^BGRUN START (\d{4}-\d\d-\d\d) (\d\d:\d\d:\d\d)", re.M)


def resolve_trigger(review_path):
    """(log basename, run index, review epoch) for one archived review, or (None, None, None)."""
    try:
        body = open(review_path, encoding="utf-8", errors="replace").read().lstrip("\ufeff")
    except OSError:
        return None, None, None
    dm = _DATE_RE.search(body)
    if not dm:
        return None, None, None
    epoch = time.mktime(time.strptime(dm.group(1), "%Y-%m-%d %H:%M:%S"))
    q = body.split("## Answer", 1)[0]
    for name in _LOG_RE.findall(q):
        p = os.path.join(HERE, name)
        if not os.path.exists(p):
            continue
        txt = open(p, encoding="utf-8", errors="replace").read()
        starts = list(_RUNSTART_RE.finditer(txt))
        if not starts:
            continue
        idx = -1
        for i, m in enumerate(starts):
            try:
                t = time.mktime(time.strptime(m.group(1) + " " + m.group(2), "%Y-%m-%d %H:%M:%S"))
            except ValueError:
                continue
            if t <= epoch:
                idx = i
        if idx < 0:
            idx = 0
        if idx == len(starts) - 1:
            idx = -1                       # the last run: keep the normal -1 addressing
        return name, idx, epoch
    return None, None, None


def cell_c():
    print("\n=== CELL C - #1 REVIEW LADDER over %s" % os.path.basename(LADDER_SET))
    doc = json.load(open(LADDER_SET, encoding="utf-8"))
    items = doc["items"]
    # THE DISCHARGE CACHE FOLLOWS GATE_LOG's DIRECTORY (jev_gate.py), so the scratch log must live in a
    # DIFFERENT directory - otherwise this measurement would read the live cache (which already holds a granted
    # discharge for c80_rowd_routeA_r2.log) and report a cache hit as a fresh judgement.
    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="jev_wave2a_")
    old_gatelog = jev_gate.GATE_LOG
    jev_gate.GATE_LOG = os.path.join(tmpdir, "ladder_scratch.log")
    rows, unresolved, nosummary = [], [], []
    try:
        for it in items:
            if out_of_time("cell C"):
                break
            revp = os.path.join(PEER, it["review"])
            name, run, epoch = resolve_trigger(revp)
            if not name:
                unresolved.append(it["review"])
                print("  MISS %-46s no trigger log" % it["review"])
                continue
            logp = os.path.join(HERE, name)
            fs = jev.summarise_failure(logp, run_index=run)
            if not fs:
                nosummary.append(it["review"])
                print("  MISS %-46s no summary for %s run %s" % (it["review"], name, run))
                continue
            grows = jev_gaterow.verdicts_for(logp, run_index=run, max_rows=4, n=2)
            recent = jev_gate.recent_adversary_reviews(jev_gate.N_RECENT_REVIEWS, before=epoch - 1)
            cls, p, sp = jev_gate.ladder_classify(
                fs, grows, "\n".join("- %s" % os.path.basename(x) for x in recent)[:1200],
                purpose="wave2a-ladder", n=5)
            acted, skipped, cited = "block", False, None
            if cls is not None and p is not None and p >= jev_gate.LADDER_P:
                if cls == "our-script-bug":
                    acted, skipped = "allow (script-bug)", True
                elif cls == "already-reviewed-class":
                    allow, dline = jev_gate.jev_discharge(logp, fs, before=epoch - 1, write=False)
                    skipped = bool(allow)
                    acted = "allow via discharge" if allow else "block (no citable review)"
                    cited = dline
                else:
                    acted = "block (new-problem)"
            else:
                acted = "block (unknown band -> old path)"
            ok = (cls == it["label"])
            wrong_skip = skipped and it["label"] == "new-problem"
            rows.append({"review": it["review"], "log": name, "run": run, "truth": it["label"],
                         "jev": cls, "p": p, "spread": sp, "ok": ok, "action": acted,
                         "skipped": skipped, "wrong_skip": wrong_skip, "cited": cited, "why": it["why"]})
            print("  %-4s %-46s %-24s truth=%-22s jev=%-22s p=%s -> %s" % (
                "OK" if ok else "DIFF", it["review"], "%s[run %s]" % (name, run), it["label"],
                cls, ("%.2f" % p) if p is not None else "-", acted))
            sys.stdout.flush()
    finally:
        jev_gate.GATE_LOG = old_gatelog
    n = len(rows)
    nok = sum(1 for r in rows if r["ok"])
    nskip = sum(1 for r in rows if r["skipped"])
    nwrong = sum(1 for r in rows if r["wrong_skip"])
    gate(not unresolved, "C1 every review resolved to a trigger log and run",
         "%d/%d resolved" % (len(items) - len(unresolved), len(items)))
    gate(not nosummary, "C2 every resolved run produced a failure summary", "%d summarised" % n)
    print("=== C3 3-WAY ACCURACY vs the hand labels: %d/%d = %.1f %%" % (nok, n, 100.0 * nok / max(n, 1)))
    print("=== C4 *** THE LADDER WOULD HAVE SKIPPED %d OF %d REVIEWS; %d OF THOSE SKIPS WOULD HAVE BEEN WRONG ***"
          % (nskip, n, nwrong))
    conf = list(jev_gate.LADDER_CLASSES) + ["None"]
    print("\n=== CONFUSION MATRIX (rows = my label, columns = Jev)")
    print("    %-24s%s" % ("", "".join("%-24s" % c for c in conf)))
    for c in jev_gate.LADDER_CLASSES:
        line = "".join("%-24d" % sum(1 for r in rows if r["truth"] == c and (r["jev"] or "None") == d)
                       for d in conf)
        print("    %-24s%s  (n=%d)" % (c, line, sum(1 for r in rows if r["truth"] == c)))
    print("\n=== SKIPS (%d)" % nskip)
    for r in rows:
        if r["skipped"]:
            print("  - %-46s %s p=%.2f  %s%s" % (r["review"], r["jev"], r["p"], r["action"],
                                                 "   *** WRONG ***" if r["wrong_skip"] else ""))
            if r["cited"]:
                print("      cited: %s" % str(r["cited"])[:160])
    print("\n=== DISAGREEMENTS (%d)" % (n - nok))
    for r in rows:
        if not r["ok"]:
            print("  - %-46s mine=%-22s jev=%-22s p=%s" % (
                r["review"], r["truth"], r["jev"], ("%.2f" % r["p"]) if r["p"] is not None else "-"))
            print("      mine: %s" % r["why"][:150])
    return {"n": n, "accuracy": nok / max(n, 1), "skipped": nskip, "wrong_skips": nwrong, "rows": rows,
            "unresolved": unresolved, "nosummary": nosummary}


def main():
    print("=== jev_wave2a_trials - 2차 #6 consensus, #2 gate-row triage, #1 review ladder")
    print("=== NO LabVIEW. Key present: %s ; JEV_SAMPLES=%s (default %d)" % (
        bool(jev.get_key()), os.environ.get("JEV_SAMPLES", "(unset)"), jev.SAMPLES_DEFAULT))
    if not jev.get_key():
        print("  FAIL  PRE no TYPESAFE_API_KEY visible - nothing can be measured")
        return 1
    before = ledger_lines()
    res = {"a": cell_a(), "b": cell_b(), "c": cell_c()}
    calls = ledger_lines() - before
    usd = calls * USD_PER_CALL
    print("\n=== D SPEND: %d ledger line(s) x $%.6f = $%.4f ; wall %.1f s" % (
        calls, USD_PER_CALL, usd, time.time() - T0))
    gate(usd <= 0.10, "D total Jev spend <= $0.10", "$%.4f over %d call(s)" % (usd, calls))
    res["spend"] = {"calls": calls, "usd": round(usd, 4), "wall_s": round(time.time() - T0, 1)}
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("=== readings -> %s" % OUT)
    print("\n=== jev_wave2a_trials: %d pass / %d fail ===" % (NPASS, NFAIL))
    return 0 if NFAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
