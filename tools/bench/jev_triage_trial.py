r"""jev_triage_trial.py - MEASURE insertion #2 of docs/jev-integration-plan.md (failure-log triage) on the
hand-labelled set tools/bench/jev_triage_set.json.

PREDICTION CONTRACT (written before the run):
  T1  every item in the set resolves to a summary (jev.summarise_failure returns non-None)   -> 40/40
  T2  every call returns an answer with a choice and a probability dict                      -> 40/40
  T3  accuracy vs the hand labels                                                            -> REPORTED, not gated
  T4  mean confidence (the winning option's probability)                                     -> REPORTED
  T5  the ledger (tools/bench/jev_usage.jsonl) gains exactly one line per call               -> +40
  A confusion matrix and the full disagreement list are printed; nothing here is a pass/fail of Jev.

PRIOR ART CHECKED BEFORE WRITING: tools/jev.py already owns key handling, retries, the ledger, the unknown band
and summarise_failure (ported from tools/bench/jev_trial.py, the measured 40-pair same-failure-class trial); this
file adds only the question text and the scoring, and calls nothing else. No LabVIEW, no COM, no recipe.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import jev  # noqa: E402
from jev_triage_q import CLASSES, TRIAGE_Q  # noqa: E402

SET = os.path.join(HERE, "jev_triage_set.json")
OUT = os.path.join(HERE, "jev_triage_trial.json")


def main():
    doc = json.load(open(SET, encoding="utf-8"))
    items = doc["items"]
    print("=== jev_triage_trial  %d item(s) from %s" % (len(items), os.path.basename(SET)))
    print("=== classes: %s" % ", ".join(CLASSES))
    rows, no_summary, no_answer = [], [], []
    t_all = time.time()
    for i, it in enumerate(items):
        path = os.path.join(HERE, it["log"])
        s = jev.summarise_failure(path)
        if not s:
            no_summary.append(it["log"])
            print("  MISS %-34s no summary" % it["log"])
            continue
        t0 = time.time()
        resp, err = jev.ask({"log": s}, {"kind": TRIAGE_Q}, purpose="triage-trial")
        dt = time.time() - t0
        if err:
            no_answer.append((it["log"], err))
            print("  ERR  %-34s %s" % (it["log"], err[:80]))
            continue
        choice, probs = jev.choice(resp, "kind")
        p = None
        if isinstance(probs, dict) and choice in probs:
            try:
                p = float(probs[choice])
            except (TypeError, ValueError):
                p = None
        if choice is None:
            no_answer.append((it["log"], "no choice in response"))
            print("  ERR  %-34s no choice in response" % it["log"])
            continue
        ok = (choice == it["label"])
        rows.append({"log": it["log"], "truth": it["label"], "jev": choice, "p": p,
                     "probs": probs, "latency_s": round(dt, 3), "ok": ok, "why": it["why"]})
        print("  %-4s %-34s truth=%-16s jev=%-16s p=%s  %.2fs" % (
            "OK" if ok else "DIFF", it["log"], it["label"], choice,
            ("%.2f" % p) if p is not None else "?", dt))
        sys.stdout.flush()

    n = len(rows)
    acc = sum(1 for r in rows if r["ok"]) / n if n else 0.0
    ps = [r["p"] for r in rows if r["p"] is not None]
    meanp = sum(ps) / len(ps) if ps else 0.0
    print("\n=== GATE T1 every item produced a summary: %d/%d %s" % (
        len(items) - len(no_summary), len(items), "PASS" if not no_summary else "FAIL " + str(no_summary)))
    print("=== GATE T2 every call answered with a choice: %d/%d %s" % (
        n, len(items) - len(no_summary), "PASS" if not no_answer else "FAIL " + str(no_answer[:3])))
    print("=== T3 ACCURACY vs the hand labels: %d/%d = %.1f %%" % (sum(1 for r in rows if r["ok"]), n, 100 * acc))
    print("=== T4 MEAN CONFIDENCE (winning option's probability): %.3f" % meanp)
    print("=== T5 total wall %.1f s, mean %.2f s/call" % (time.time() - t_all, (time.time() - t_all) / max(n, 1)))

    print("\n=== CONFUSION MATRIX  (rows = my label, columns = Jev)")
    print("    %-18s %s" % ("", "".join("%-17s" % c for c in CLASSES)))
    for c in CLASSES:
        line = "".join("%-17d" % sum(1 for r in rows if r["truth"] == c and r["jev"] == d) for d in CLASSES)
        print("    %-18s %s  (n=%d)" % (c, line, sum(1 for r in rows if r["truth"] == c)))

    print("\n=== DISAGREEMENTS (%d)" % sum(1 for r in rows if not r["ok"]))
    for r in rows:
        if not r["ok"]:
            print("  - %-34s mine=%-16s jev=%-16s p=%s" % (
                r["log"], r["truth"], r["jev"], ("%.2f" % r["p"]) if r["p"] is not None else "?"))
            print("      my reason: %s" % r["why"][:160])

    json.dump({"set": os.path.basename(SET), "n": n, "accuracy": acc, "mean_confidence": meanp,
               "no_summary": no_summary, "no_answer": no_answer, "rows": rows},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n=== readings -> %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
