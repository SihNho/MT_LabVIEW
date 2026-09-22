"""Run THE JEV REVIEW LADDER (docs/jev-integration-plan.md 2차 #1, user-approved 2026-09-22 17:3x) on
the cycle-67 failed prediction `tools/bench/diag_c89_execstate_factorial.log`, and report its 3-way
classification and probability band so the material session knows whether an Opus `hypothesis` review
must be bought.

PRIOR ART CHECKED BEFORE WRITING (CLAUDE.md, "check what already exists"):
  - tools/bench/jev_gate.py:368 `jev_ladder(log_path, failure_text, ...)` ALREADY IS the ladder call
    that tools/hooks/guard_peer.py makes. Nothing new is implemented here; this file only INVOKES it
    on one named log and prints the verdict. LADDER_P = 0.80, consensus over jev.samples() asks.
  - tools/bench/jev_gate.py:231 `jev_discharge` is what the already-reviewed-class branch calls.
  - tools/bench/jev_gate.py:93 `recent_adversary_reviews` supplies the review list.
  - tools/jev_gaterow.py:92 `verdicts_for` supplies the per-row verdicts (advisory input).
  - RULE-SAME-ROW (user 2026-09-22 18:xx) lives in tools/hooks/guard_peer.py; reported separately.

PREDICTION CONTRACT
  P1 the Jev key resolves (jev.get_key() truthy)            -> else the ladder cannot act: report "no key"
  P2 jev_ladder returns one of (True, False, None) with a line or None; it NEVER raises
  P3 the printed classification is one of jev_gate.LADDER_CLASSES, or None when no answer

This script touches NO LabVIEW, opens no COM client, and writes no VI. Jev scripts are EXEMPT from the
failed-prediction and material gates (user, 2026-09-22 "Jev는 면제").
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                     # tools/
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

import jev                                        # noqa: E402
import jev_gate                                   # noqa: E402

LOG = os.path.join(HERE, "diag_c89_execstate_factorial.log")


def main():
    print("=== JEV REVIEW LADDER on %s ===" % os.path.basename(LOG))
    print("exists=%s size=%s" % (os.path.exists(LOG), os.path.getsize(LOG) if os.path.exists(LOG) else "-"))
    key = bool(jev.get_key())
    print("P1 key_present=%s  LADDER_P=%.2f  samples=%s" % (key, jev_gate.LADDER_P, jev.samples()))
    if not key:
        print("RESULT: no key -> the ladder cannot act; the OLD PATH applies (review owed).")
        return 0

    fs = jev.summarise_failure(LOG)
    print("failure_summary_len=%d" % (len(fs or "")))
    print("---- failure summary (first 1200 chars) ----")
    print((fs or "")[:1200])
    print("---- end ----")

    try:
        import jev_gaterow
        rows = jev_gaterow.verdicts_for(LOG)
    except Exception as exc:                       # noqa: BLE001
        rows = ""
        print("gaterow unavailable: %r" % (exc,))
    print("---- gate_rows (first 1200) ----")
    print((rows or "")[:1200])
    print("---- end ----")

    recent = jev_gate.recent_adversary_reviews(jev_gate.N_RECENT_REVIEWS)
    print("recent_adversary_reviews=%d" % len(recent))
    for p in recent:
        print("   %s" % os.path.basename(p))

    # The raw classification (so the band is visible even when the ladder declines to act).
    cls, p, spread = jev_gate.ladder_classify(
        fs, rows or "", "\n".join("- %s" % os.path.basename(x) for x in recent)[:1200],
        purpose="c89-material-ladder")
    print("P3 CLASSIFY: class=%s p=%s spread=%s" % (cls, ("%.4f" % p) if p is not None else None, spread))
    print("            acts_at_p>=%.2f -> %s" % (jev_gate.LADDER_P,
          "ACTS" if (p is not None and p >= jev_gate.LADDER_P) else "BELOW BAND: old path"))

    allow, line = jev_gate.jev_ladder(LOG, "", gate_rows=rows)
    print("P2 LADDER: allow=%r" % (allow,))
    print("P2 LADDER line: %s" % (line,))
    verdict = {True: "DISCHARGED - no review bought",
               False: "BLOCKED by the ladder (no citable review) - review owed",
               None: "LADDER DID NOT ACT - old path: review owed"}[allow]
    print("RESULT: %s" % verdict)
    print(json.dumps({"class": cls, "p": p, "allow": allow}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
