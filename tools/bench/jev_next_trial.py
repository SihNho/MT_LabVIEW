r"""jev_next_trial.py - MEASURE insertion #5 of docs/jev-integration-plan.md (NEXT quality) on the hand-labelled
set tools/bench/jev_next_set.json.

PREDICTION CONTRACT (written before the run):
  N1  every item gets a noul probability back                                  -> 25/25
  N2  accuracy with the project's unknown band (>=0.7 GOOD, <=0.3 POOR)        -> REPORTED, not gated
  N3  Brier score against the label (GOOD = 1, POOR = 0)                       -> REPORTED
  N4  mean latency per call                                                    -> REPORTED
  N5  for every item Jev scores <= 0.3, the MISSING_Q answer is printed        -> REPORTED
  ⚠️ THE SET IS IMBALANCED BY CONSTRUCTION: 23 GOOD / 2 POOR (see the set file's `how`). Accuracy therefore
  measures mostly the false-alarm rate on good hand-offs; detection on POOR rests on two items and is anecdotal.

PRIOR ART CHECKED: tools/jev.py owns the transport, the ledger and the unknown band; tools/bench/jev_next_q.py
owns the two question texts, shared with tools/hooks/guard_bash.py:next_gate(). No LabVIEW, no COM.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import jev  # noqa: E402
from jev_next_q import MISSING_Q, NEXT_Q  # noqa: E402

SET = os.path.join(HERE, "jev_next_set.json")
OUT = os.path.join(HERE, "jev_next_trial.json")
MAXCHARS = 6000


def main():
    doc = json.load(open(SET, encoding="utf-8"))
    items = doc["items"]
    print("=== jev_next_trial  %d item(s), %d POOR, from %s" % (len(items), doc["n_poor"], os.path.basename(SET)))
    rows, no_answer = [], []
    t_all = time.time()
    for it in items:
        text = it["text"][:MAXCHARS]
        t0 = time.time()
        resp, err = jev.ask({"next": text}, {"startable": NEXT_Q}, purpose="next-quality-trial")
        dt = time.time() - t0
        if err:
            no_answer.append((it["src"], err))
            print("  ERR  %-52s %s" % (it["src"][:52], err[:70]))
            continue
        p = jev.noul(resp, "startable")
        if p is None:
            no_answer.append((it["src"], "no noul in response"))
            print("  ERR  %-52s no noul in response" % it["src"][:52])
            continue
        v = jev.verdict(p)                     # yes / no / unknown, project band 0.30/0.70
        pred = {"yes": "GOOD", "no": "POOR"}.get(v, "UNKNOWN")
        ok = (pred == it["label"])
        missing = None
        if p <= jev.UNKNOWN_LO:
            mresp, merr = jev.ask({"next": text}, {"missing": MISSING_Q}, purpose="next-missing-trial")
            missing = jev.choice(mresp, "missing")[0] if not merr else "?(%s)" % merr[:30]
        rows.append({"src": it["src"], "truth": it["label"], "p": p, "verdict": v, "pred": pred,
                     "ok": ok, "missing": missing, "truth_missing": it["missing"], "latency_s": round(dt, 3)})
        print("  %-4s %-52s truth=%-4s p=%.3f -> %-7s %s  %.2fs" % (
            "OK" if ok else "DIFF", it["src"][:52], it["label"], p, pred,
            ("missing=" + str(missing)) if missing else "", dt))
        sys.stdout.flush()

    n = len(rows)
    acc = sum(1 for r in rows if r["ok"]) / n if n else 0.0
    brier = sum((r["p"] - (1.0 if r["truth"] == "GOOD" else 0.0)) ** 2 for r in rows) / n if n else 0.0
    lat = sum(r["latency_s"] for r in rows) / n if n else 0.0
    unk = sum(1 for r in rows if r["pred"] == "UNKNOWN")
    poor = [r for r in rows if r["truth"] == "POOR"]
    caught = sum(1 for r in poor if r["pred"] == "POOR")
    false_alarm = sum(1 for r in rows if r["truth"] == "GOOD" and r["pred"] == "POOR")
    print("\n=== GATE N1 every item answered: %d/%d %s" % (n, len(items),
          "PASS" if not no_answer else "FAIL " + str(no_answer[:3])))
    print("=== N2 ACCURACY (unknown band 0.30/0.70 counted as a miss): %d/%d = %.1f %% ; UNKNOWN %d" % (
        sum(1 for r in rows if r["ok"]), n, 100 * acc, unk))
    print("=== N3 BRIER (GOOD = 1): %.4f" % brier)
    print("=== N4 MEAN LATENCY: %.2f s/call ; total wall %.1f s" % (lat, time.time() - t_all))
    print("=== N5 POOR items caught (p <= 0.30): %d/%d ; FALSE ALARMS on GOOD: %d/%d" % (
        caught, len(poor), false_alarm, sum(1 for r in rows if r["truth"] == "GOOD")))
    print("=== p range on GOOD: %.3f .. %.3f ; on POOR: %s" % (
        min([r["p"] for r in rows if r["truth"] == "GOOD"] or [0]),
        max([r["p"] for r in rows if r["truth"] == "GOOD"] or [0]),
        ", ".join("%.3f" % r["p"] for r in poor) or "-"))
    print("\n=== DISAGREEMENTS (%d)" % sum(1 for r in rows if not r["ok"]))
    for r in rows:
        if not r["ok"]:
            print("  - %-52s mine=%-4s p=%.3f -> %s  missing=%s (mine: %s)" % (
                r["src"][:52], r["truth"], r["p"], r["pred"], r["missing"], r["truth_missing"] or "-"))
    json.dump({"set": os.path.basename(SET), "n": n, "accuracy": acc, "brier": brier, "mean_latency_s": lat,
               "unknown": unk, "poor_caught": caught, "false_alarms": false_alarm,
               "no_answer": no_answer, "rows": rows},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n=== readings -> %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
