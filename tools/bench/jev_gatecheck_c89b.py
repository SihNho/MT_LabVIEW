"""READ-ONLY check: is any failing log left ARMING tools/hooks/guard_peer.py against the next build?

PRIOR ART: this calls guard_peer's OWN functions (`newest_failing_log`, `failure_names`, `newest_bound_peer`,
`same_row_review`) - it re-implements nothing and writes nothing. Deliberately does NOT call `main()`, because
main()'s Jev discharge/ladder branches WRITE citation lines into review files and jev_gate.log; a check must not
change the thing it checks.

PREDICTION CONTRACT
  G1 newest_failing_log() returns None, OR returns a log for which newest_bound_peer()/same_row_review() finds a
     binding accepted review  => the gate is CLEAR for the next build
  G2 tools/bench/diag_c89_wirebirth.log is NOT the armed log (its LAST run passed 45/0)

Touches no LabVIEW. Jev-prefixed, so exempt from the material and failed-prediction gates (user 2026-09-22).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "hooks"))

import guard_peer                                  # noqa: E402


def main():
    failing = guard_peer.newest_failing_log()
    if not failing:
        print("G1 newest_failing_log -> None")
        print("RESULT: GATE CLEAR - no failing log inside 6 h arms guard_peer.")
        return 0
    path, mtime, text = failing
    rel = os.path.relpath(path, ROOT)
    print("G1 newest_failing_log -> %s" % rel)
    print("   first failure line : %s" % next(
        (ln.strip() for ln in text.splitlines() if guard_peer.FAILURE_RE.search(ln)), "(none)")[:180])
    names = guard_peer.failure_names(path, text)
    print("   names it must be reviewed under: %s" % ", ".join(sorted(names)))
    hit, rejected = guard_peer.newest_bound_peer(mtime, names)
    if hit:
        print("   bound review : %s  (ANSWERED, adversary)" % os.path.basename(hit))
        print("RESULT: GATE CLEAR - the loop on that log is closed by an archived review.")
        return 0
    if rejected:
        print("   NOT accepted : %s" % "; ".join(rejected))
    sr = guard_peer.same_row_review(path, text)
    if sr:
        print("   RULE-SAME-ROW would release it: %s (age %d min)" % (os.path.basename(sr[0]), int(round(sr[2]))))
        print("RESULT: GATE CLEAR via RULE-SAME-ROW (no new review owed).")
        return 0
    print("RESULT: GATE ARMED - that log still owes an adversarial review.")

    wb = os.path.join(HERE, "diag_c89_wirebirth.log")
    print("G2 armed log is diag_c89_wirebirth.log? %s" % (os.path.abspath(path) == os.path.abspath(wb)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
