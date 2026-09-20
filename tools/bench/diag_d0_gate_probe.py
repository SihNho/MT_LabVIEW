r"""diag_d0_gate_probe.py - READ-ONLY: the two sides of guard_cycle's freshness comparison.

WHAT ALREADY EXISTS (checked before writing, CLAUDE.md "before creating any new tool"):
  * `tools/hooks/guard_cycle.py` owns `newest_retrospective()` / `newest_build_log()`. No standalone reader
    exists - the only callers are `tools/bench/diag_fstunnel_wirebroken.py:304-314` (a LabVIEW diagnostic that
    prints them as its P9 side-fact, and which opens COM, so it cannot be reused here) and
    `tools/bench/selftest_stamp_window.py:240`, which re-implements a *time-bounded* variant for its own test.
  * So this file imports the gate's own functions and prints nothing of its own invention. No new logic.

TOUCHES NO LabVIEW, no motor, no serial, no camera, no GUI, no COM. Pure filesystem reads.

PREDICTION CONTRACT
  P1 guard_cycle imports cleanly and both helpers return either None or a (path, timestamp) pair.
  P2 newest_retrospective() returns an ANSWERED `archive/peer/*retrospective*.md`.
  P3 newest_build_log() returns a `tools/bench/*.log` classified as a build log by logclass.
  P4 `since` (unreviewed build logs newer than the retrospective) is reported with the span in hours and the
     `overdue` boolean the gate computes from CYCLE_BUILD_BUDGET / CYCLE_HOURS.
  P5 the retrospective gate's own predicate `log and (retro is None or (retro[1] < log[1] and overdue))` is
     printed as a single TRUE/FALSE, so "would the retrospective gate block" is read, not inferred.
"""
import datetime
import glob
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import guard_cycle  # noqa: E402
import logclass     # noqa: E402

FAILS = []


def ts(t):
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


def rel(p):
    try:
        return os.path.relpath(p, ROOT)
    except ValueError:
        return p


def check(label, ok, detail):
    print("%-4s %-8s %s | %s" % ("", "PASS" if ok else "FAIL", label, detail), flush=True)
    if not ok:
        FAILS.append(label)


def main():
    print("=== diag_d0_gate_probe (read-only) ===", flush=True)
    print("ROOT %s" % ROOT, flush=True)
    print("CYCLE_BUILD_BUDGET=%s CYCLE_HOURS=%s MAX_AGE_S=%s"
          % (guard_cycle.CYCLE_BUILD_BUDGET, guard_cycle.CYCLE_HOURS, guard_cycle.MAX_AGE_S), flush=True)

    retro = guard_cycle.newest_retrospective()
    log = guard_cycle.newest_build_log()
    check("P1 helpers returned", True, "retro=%s log=%s" % (retro is not None, log is not None))

    if retro:
        print("RETRO  path  %s" % rel(retro[0]), flush=True)
        print("RETRO  stamp %s (%.0f)" % (ts(retro[1]), retro[1]), flush=True)
        print("RETRO  mtime %s" % ts(os.path.getmtime(retro[0])), flush=True)
    check("P2 newest retrospective found", bool(retro), rel(retro[0]) if retro else "NONE ARCHIVED")

    if log:
        print("BUILD  path  %s" % rel(log[0]), flush=True)
        print("BUILD  mtime %s (%.0f)" % (ts(log[1]), log[1]), flush=True)
        print("BUILD  is_build_log %s" % logclass.is_build_log(log[0]), flush=True)
    check("P3 newest build log found", bool(log), rel(log[0]) if log else "NONE")

    since = [p for p in glob.glob(os.path.join(guard_cycle.BENCH, "*.log"))
             if logclass.is_build_log(p)
             and (retro is None or os.path.getmtime(p) > retro[1])
             and time.time() - os.path.getmtime(p) <= guard_cycle.MAX_AGE_S]
    if retro is None:
        hours = 999.0
    elif len(since) >= 2:
        t = [os.path.getmtime(p) for p in since]
        hours = (max(t) - min(t)) / 3600.0
    else:
        hours = 0.0
    overdue = len(since) >= guard_cycle.CYCLE_BUILD_BUDGET or hours >= guard_cycle.CYCLE_HOURS
    print("SINCE  %d unreviewed build log(s), span %.2f h, overdue=%s" % (len(since), hours, overdue), flush=True)
    for p in sorted(since, key=os.path.getmtime):
        print("SINCE    %s  %s" % (ts(os.path.getmtime(p)), rel(p)), flush=True)
    check("P4 since-set computed", True, "%d logs, %.2f h, overdue=%s" % (len(since), hours, overdue))

    would = bool(log) and (retro is None or (retro[1] < log[1] and overdue))
    print("RETRO-GATE would block: %s   (retro_stamp<build_mtime=%s, overdue=%s)"
          % (would, (retro[1] < log[1]) if (retro and log) else "n/a", overdue), flush=True)
    check("P5 retrospective-gate predicate read", True, "would_block=%s" % would)

    print("=== diag_d0_gate_probe: %d pass, %d fail ===" % (5 - len(FAILS), len(FAILS)), flush=True)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
