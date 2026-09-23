"""Cycle 68: let guard_peer DECIDE on the newest failing log (expected: tools/bench/q_m4_iterlocal.log, run 1's P6d).

PRIOR ART: jev_gatecheck_c89b.py (read-only functions). This one ALSO runs the gate's own decision path
(same_row_review -> jev_gate.jev_ladder -> jev_gate.jev_discharge) exactly as guard_peer.main() orders it, so
the ladder's JEV-LADDER line is written to jev_gate.log like any gate call. Touches no LabVIEW.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
sys.path.insert(0, HERE)
import guard_peer                                  # noqa: E402

failing = guard_peer.newest_failing_log()
if not failing:
    print("RESULT: CLEAR - no failing log arms guard_peer")
    sys.exit(0)
path, mtime, text = failing
print("armed log:", os.path.relpath(path, ROOT))
print("first failure:", next((l.strip() for l in text.splitlines() if guard_peer.FAILURE_RE.search(l)), "")[:200])
names = guard_peer.failure_names(path, text)
hit, rej = guard_peer.newest_bound_peer(mtime, names)
if hit:
    print("RESULT: CLEAR - bound review", os.path.basename(hit))
    sys.exit(0)
sr = guard_peer.same_row_review(path, text)
if sr:
    print("RESULT: CLEAR via RULE-SAME-ROW", os.path.basename(sr[0]))
    sys.exit(0)
import jev_gate                                    # noqa: E402
la, ll = jev_gate.jev_ladder(path, text)
print("ladder:", la, ll)
if la is True:
    print("RESULT: CLEAR via JEV-LADDER")
    sys.exit(0)
if la is None:
    al, jl = jev_gate.jev_discharge(path, text)
    print("discharge:", al, jl)
    if al:
        print("RESULT: CLEAR via JEV discharge")
        sys.exit(0)
print("RESULT: ARMED - a claude/hypothesis review is owed")
