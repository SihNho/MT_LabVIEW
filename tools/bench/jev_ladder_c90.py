"""Run THE JEV REVIEW LADDER (docs/jev-integration-plan.md 2차 #1, user-approved 2026-09-22 17:3x) on the
CYCLE-68 failed prediction: the JUDGEMENT session predicted 11 agrees / 0 disagrees / 0 unread over the 11
wires Remove Bad Wires removes, and `tools/bench/diag_c90_live_endpoints.log:99` measured
`{'agrees': 4, 'disagrees': 0, 'unread': 7}`. That run ended `=== GATES: 14 pass / 0 fail` and
`BGRUN END rc=0 after 114s` (:157,:159) - the miss is in a ROW, deliberately not in a gate, so guard_peer's
FAILURE_RE is not armed by it; the review is owed by the RULE, not by the gate.

PRIOR ART CHECKED BEFORE WRITING (CLAUDE.md, "check what already exists"):
  - tools/bench/jev_ladder_c89b.py IS this script for the previous failure. This file is that one with two
    changes only: the LOG, and RUN_INDEX=-1 (this log holds exactly one run, and it is the last).
  - tools/bench/jev_gate.py:368 `jev_ladder` / :342 `ladder_classify` / :231 `jev_discharge` are the ladder
    and the discharge; nothing is reimplemented here.
  - tools/hooks/guard_peer.py:385 `same_row_review` is RULE-SAME-ROW (user 2026-09-22 18:xx); called, not
    re-written.
  - tools/jev_gaterow.py:91 `verdicts_for(logpath, run_index=...)` supplies the per-row verdicts.

PREDICTION CONTRACT
  P1 the Jev key resolves (jev.get_key() truthy)      -> else "no key": the OLD PATH applies (review owed)
  P2 ladder_classify returns a class in jev_gate.LADDER_CLASSES with a float p, or (None, None, None)
  P3 RULE-SAME-ROW: same_row_review() returns None (no ANSWERED adversary review inside 6 h names
     `diag_c90_live_endpoints`) -- if it returns one, that review discharges this failure.
  P4 guard_peer.newest_failing_log() -- this log passed 14/0, so it should NOT arm the gate.

This script touches NO LabVIEW, opens no COM client and writes no VI. Jev scripts are EXEMPT from the
failed-prediction and material gates (user, 2026-09-22 "Jev는 면제").
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, HERE)
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "hooks"))

import jev                                        # noqa: E402
import jev_gate                                   # noqa: E402

LOG = os.path.join(HERE, "diag_c90_live_endpoints.log")
RUN_INDEX = -1


def main():
    print("=== JEV REVIEW LADDER on %s run %d ===" % (os.path.basename(LOG), RUN_INDEX))
    print("exists=%s size=%s" % (os.path.exists(LOG), os.path.getsize(LOG) if os.path.exists(LOG) else "-"))

    import guard_peer
    failing = guard_peer.newest_failing_log()
    if failing:
        print("P4 guard_peer.newest_failing_log -> %s" % os.path.relpath(failing[0], ROOT))
        print("   first failure line: %s" % next(
            (ln.strip() for ln in failing[2].splitlines() if guard_peer.FAILURE_RE.search(ln)), "(none)")[:180])
    else:
        print("P4 guard_peer.newest_failing_log -> None  (NO failing log arms the gate)")

    with open(LOG, "r", encoding="utf-8", errors="replace") as fh:
        whole = fh.read()
    stem = guard_peer.log_script(whole)
    sr = guard_peer.same_row_review(LOG, whole)
    print("P3 RULE-SAME-ROW: script stem=%s -> %s" % (
        stem, "NONE (no accepted review of this script inside 6 h)" if not sr
        else "%s (age %d min)" % (os.path.basename(sr[0]), int(round(sr[2])))))
    if sr:
        print("RESULT: RULE-SAME-ROW discharges it; cite %s. No ladder branch needed." % os.path.basename(sr[0]))
        return 0

    key = bool(jev.get_key())
    print("P1 key_present=%s  LADDER_P=%.2f  DISCHARGE_P=%.2f  samples=%s" % (
        key, jev_gate.LADDER_P, jev_gate.DISCHARGE_P, jev.samples()))
    if not key:
        print("RESULT: no key -> the ladder cannot act; the OLD PATH applies (review owed).")
        return 0

    fs = jev.summarise_failure(LOG, run_index=RUN_INDEX)
    print("failure_summary_len=%d" % (len(fs or "")))
    print("---- failure summary (first 1400 chars) ----")
    print((fs or "")[:1400])
    print("---- end ----")

    try:
        import jev_gaterow
        rows = jev_gaterow.verdicts_for(LOG, run_index=RUN_INDEX)
    except Exception as exc:                       # noqa: BLE001
        rows = ""
        print("gaterow unavailable: %r" % (exc,))
    print("---- gate_rows ----")
    print((rows or "")[:1200])
    print("---- end ----")

    recent_paths = jev_gate.recent_adversary_reviews(jev_gate.N_RECENT_REVIEWS)
    print("recent_adversary_reviews=%d" % len(recent_paths))
    for p in recent_paths:
        print("   %s" % os.path.basename(p))
    recent = "\n".join("- %s" % os.path.basename(p) for p in recent_paths)[:1200]

    cls, p, spread = jev_gate.ladder_classify(fs, rows or "", recent, purpose="c90-material-ladder")
    print("P2 CLASSIFY: class=%s p=%s spread=%s" % (cls, ("%.4f" % p) if p is not None else None, spread))
    if cls is None or p is None:
        print("RESULT: no answer -> the OLD PATH applies (review owed).")
        return 0
    acts = p >= jev_gate.LADDER_P
    print("            acts_at_p>=%.2f -> %s" % (jev_gate.LADDER_P, "ACTS" if acts else "BELOW BAND: old path"))

    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    base = os.path.basename(LOG) + "#run%d" % RUN_INDEX
    if not acts:
        jev_gate.gate_log("JEV-LADDER | %s | %s | %s p=%.3f | below %.2f: old path" % (
            ts, base, cls, p, jev_gate.LADDER_P))
        print("RESULT: BELOW BAND -> old path: review owed.")
    elif cls == "our-script-bug":
        line = "JEV-LADDER | %s | %s | our-script-bug p=%.3f | ALLOW (no machine claim to attack)" % (ts, base, p)
        jev_gate.gate_log(line)
        jev_gate.ladder_allowed_line(base, cls, p, ts)
        print("RESULT: DISCHARGED as our-script-bug - no review bought. Logged: %s" % line)
    elif cls == "already-reviewed-class":
        allow, dline = jev_gate.jev_discharge(LOG, whole)
        line = "JEV-LADDER | %s | %s | already-reviewed-class p=%.3f | %s" % (
            ts, base, p, "ALLOW via discharge" if allow else "BLOCK (no citable review)")
        jev_gate.gate_log(line)
        print("RESULT: already-reviewed-class -> %s" % (dline or line))
    else:
        jev_gate.gate_log("JEV-LADDER | %s | %s | new-problem p=%.3f | BLOCK (review owed)" % (ts, base, p))
        print("RESULT: new-problem -> review owed (buy the Opus hypothesis review).")

    print(json.dumps({"class": cls, "p": p, "spread": spread, "acts": acts,
                      "same_row": None, "gate_armed": bool(failing)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
