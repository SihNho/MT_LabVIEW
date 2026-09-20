r"""selftest_audit_cost_window.py - OPEN 52: does `audit_cycle`'s cost window clip each RUN by its own
`BGRUN START`/`END` stamps, instead of counting a whole log because the FILE's mtime lands in the window?
Pure Python, reads only; touches no LabVIEW, creates nothing outside %TEMP%.

PRIOR ART CHECKED BEFORE WRITING THIS (CLAUDE.md, material brief):
  - `ls tools/bench/selftest_*.py` -> bgrun_fail_scan, cycle_runner, cycle_runner_ff, guard_cycle_fixed,
    guard_cycle_rerun, guard_session, motor_gate2, stamp_window. NONE of them touches audit_cycle's cost lines:
    `selftest_stamp_window.py` tests guard_cycle.stamp() and the retrospective's WINDOW BOUNDS (which window is
    chosen), never what is summed inside one. So this file is new and does not duplicate it.
  - `audit_cycle.py` already has an import-time `_self_test()` (COST_RE round-4 device); it is extended with two
    one-line assertions of the same property, and the full cases live here.

THE FAULT UNDER TEST (cycle-26 retrospective, `VIOLATION: device-failed`, 3rd occurrence): a log file's mtime is
its LAST write, so `tools/bench/cycle_12.log` - a firefighter run that STARTED 2026-09-18 13:30:03 - was inside
the 13:49..14:03 window by mtime alone, and its 1199 s and $13.7777 were reported as cycle-26 cost
(`archive/peer/2026-09-18-retrospective-cycle26.md:116,130`).

PREDICTION CONTRACT - each line is PASS/FAIL on its own, no judgement:

  T1 before-window   : a run wholly BEFORE the window contributes 0 runs, 0 s, $0.
  T2 inside-window   : a run wholly INSIDE the window contributes 1 run, its seconds and its cost.
  T3 mtime-trap      : a real FILE whose mtime is forced INSIDE the window while its `BGRUN START` is BEFORE it is
                       EXCLUDED - the actual bug. Checked through audit_cycle's own accumulator expression, not
                       only through window_runs(), so the fix is tested where the numbers are produced.
  T4 no-bgrun-lines  : a log with NO `BGRUN START`/`END` line at all is returned WHOLE (the documented fallback):
                       it carries no run stamps, its mtime is its only timestamp, and that is what selected it.
                       So a `COST:` line in such a file is still counted - unchanged from before the repair.
  T5 after-window    : a run that starts AFTER the window ends is excluded too (the other end of the clip).
  T6 real-data       : on the REAL `tools/bench/cycle_12.log` and the REAL cycle-26 window (13:49..14:03), OLD
                       (whole file) vs NEW (window_runs) wall-clock and cost, side by side. EXPECT new = 0 s / $0.

  py tools/bench/selftest_audit_cost_window.py
"""
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import audit_cycle as ac          # noqa: E402  (its import-time _self_test() runs here too)

SECS_RE = re.compile(r"BGRUN (?:END rc=\d+|TIMEOUT killed) after (\d+)s")
RESULTS = []


def check(label, ok, detail):
    RESULTS.append((label, bool(ok), detail))
    print(("  PASS  " if ok else "  FAIL  ") + label + " : " + detail, flush=True)


def ts(s):
    return time.mktime(time.strptime(s, "%Y-%m-%d %H:%M:%S"))


WIN = (ts("2026-09-18 13:49:00"), ts("2026-09-18 14:03:00"))       # cycle 26's real window


def run_log(start, secs, cost):
    """One bgrun run, in bgrun.py's exact output form (bgrun.py:111,183)."""
    return ("BGRUN START %s limit 20.0 min: py -u tools/recipes/x.py\n"
            "COST: $%.4f  in 48 / out 1731 / cache-create 1 / cache-read 2  (%ds, 14 turn(s))\n"
            "BGRUN END rc=0 after %ds\n" % (start, cost, secs, secs))


def tally(segments):
    """EXACTLY what audit_cycle's C3/C4 loops do with the segments they are given."""
    secs = sum(int(m.group(1)) for s in segments for m in SECS_RE.finditer(s))
    cost = sum(float(m.group(1) or m.group(2)) for s in segments for m in ac.COST_RE.finditer(s))
    return len(segments), secs, cost


def t1_t2_t5():
    before = run_log("2026-09-18 13:30:03", 1199, 13.7777)
    inside = run_log("2026-09-18 13:55:00", 60, 1.0)
    after = run_log("2026-09-18 14:30:00", 30, 2.5)
    n, s, c = tally(ac.window_runs(before, *WIN))
    check("T1 before-window excluded", (n, s, c) == (0, 0, 0.0),
          "run 13:30:03 (+1199 s, $13.7777) vs window 13:49..14:03 -> runs %d, %d s, $%.4f" % (n, s, c))
    n, s, c = tally(ac.window_runs(inside, *WIN))
    check("T2 inside-window included", (n, s, round(c, 4)) == (1, 60, 1.0),
          "run 13:55:00 (+60 s, $1.0000) -> runs %d, %d s, $%.4f" % (n, s, c))
    n, s, c = tally(ac.window_runs(after, *WIN))
    check("T5 after-window excluded", (n, s, c) == (0, 0, 0.0),
          "run 14:30:00 (+30 s, $2.5000) -> runs %d, %d s, $%.4f" % (n, s, c))
    # both in one file: only the second survives, which is the multi-run case a session log actually is
    n, s, c = tally(ac.window_runs(before + inside + after, *WIN))
    check("T2b mixed file keeps only the in-window run", (n, s, round(c, 4)) == (1, 60, 1.0),
          "three runs in one file -> runs %d, %d s, $%.4f" % (n, s, c))


def t3():
    """THE ACTUAL BUG: mtime inside the window, BGRUN START before it."""
    tmp = os.environ.get("TEMP") or HERE
    p = os.path.join(tmp, "_open52_mtime_trap.log")
    with open(p, "w", encoding="utf-8") as f:
        f.write(run_log("2026-09-18 13:30:03", 1199, 13.7777))
    inside_mtime = ts("2026-09-18 13:50:02")                  # exactly where cycle_12.log's mtime sat
    os.utime(p, (inside_mtime, inside_mtime))
    selected = WIN[0] <= os.path.getmtime(p) <= WIN[1]        # the file-level selection audit_cycle does
    body = ac.read(p)
    old_n, old_s, old_c = tally([body])                       # pre-repair: the whole file counted
    new_n, new_s, new_c = tally(ac.window_runs(body, *WIN))    # post-repair
    os.remove(p)
    check("T3 mtime-trap excluded", selected and (new_n, new_s, new_c) == (0, 0, 0.0),
          "file mtime 13:50:02 selects it=%s; OLD %d s / $%.4f  ->  NEW %d s / $%.4f"
          % (selected, old_s, old_c, new_s, new_c))


def t4():
    """The documented fallback, stated as an assertion so nobody has to guess what it does."""
    body = "STALL: pid 1234 unresponsive 31 s\nCOST: $0.5000  in 1 / out 1\n"
    segs = ac.window_runs(body, *WIN)
    n, s, c = tally(segs)
    check("T4 no-bgrun-lines returned whole", segs == [body] and (n, s, round(c, 4)) == (1, 0, 0.5),
          "a log with no BGRUN START/END keeps the OLD mtime-based treatment (whole body, its $0.5000 still "
          "counted): runs %d, %d s, $%.4f" % (n, s, c))


def t6():
    """REAL DATA - the exact file and window the cycle-26 retrospective used."""
    p = os.path.join(ROOT, "tools", "bench", "cycle_12.log")
    if not os.path.isfile(p):
        check("T6 real-data cycle_12.log", False, "file missing: " + p)
        return
    body = ac.read(p)
    mt = os.path.getmtime(p)
    start = ac.BGRUN_START_RE.search(body)
    old_n, old_s, old_c = tally([body])
    new_n, new_s, new_c = tally(ac.window_runs(body, *WIN))
    detail = ("BGRUN START %s, file mtime %s, window 13:49:00..14:03:00 -> selected by mtime=%s | "
              "OLD whole-file %d min %d s / $%.4f | NEW %d run(s) %d min %d s / $%.4f"
              % (start.group(1) if start else "?",
                 time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mt)),
                 WIN[0] <= mt <= WIN[1], old_s // 60, old_s % 60, old_c, new_n, new_s // 60, new_s % 60, new_c))
    check("T6 real-data cycle_12.log excluded", (new_n, new_s, new_c) == (0, 0, 0.0), detail)


def main():
    print("=== OPEN 52 self-test: audit_cycle cost-window run clipping ===", flush=True)
    t1_t2_t5()
    t3()
    t4()
    t6()
    n_ok = sum(1 for _, ok, _ in RESULTS if ok)
    print("\nSELFTEST %d pass / %d fail" % (n_ok, len(RESULTS) - n_ok), flush=True)
    return 0 if n_ok == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
