r"""replay_c6_protocol.py - REPLAY PROOF for session protocol v1 C6 (bgrun body scan removed; the RESULT line decides).
NO LABVIEW. Reads tools/bench/*.log only.

For every bgrun run whose START lies in 2026-09-23 18:00 .. 2026-09-24 08:00 (cycles 68-73):
  OLD verdict = what bgrun wrote (`BGRUN END rc!=0` or TIMEOUT; the inner-failure scan is in that rc).
  NEW verdict = what bgrun decides now: TIMEOUT, or the PROCESS exit code (rc, or 0 when the END line says
                "(inner failure; the process itself said 0)"), or a failing RESULT line. Historical runs print none, so
                the RESULT line is DERIVED: stagekit's from its `=== GATES: n pass / m fail` line
                (protocol.stagekit_result_from_gates); motor_gate's from its sender's `RESULT: REJECTED|NOT at target`
                / `FAIL: motor_gate exit N` lines (each such line = one motor_gate call that now prints RESULT FAIL).
  Review logs and Jev commands are excluded from RESULT reading exactly as bgrun excludes them.
Plus the motor rejection replay: tools/bench/pi_testmove_20260923e.log (13:30, outside the window) by the same rule.

PREDICTION: false failures removed include device_value_a/b, dryrun_l7_r_address and rc=2 self-test cases; every
stage_d1_l7_* failure and the motor replay are still caught; real failures newly missed = 0 (each old-fail/new-pass
run is LISTED with its first scanned line so the classification can be checked by hand).
"""
import glob
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import logclass  # noqa: E402
import protocol as P  # noqa: E402
import bgrun  # noqa: E402

T0 = time.mktime(time.strptime("2026-09-23 18:00:00", "%Y-%m-%d %H:%M:%S"))
T1 = time.mktime(time.strptime("2026-09-24 08:00:00", "%Y-%m-%d %H:%M:%S"))
MOTOR_RE = re.compile(r"^RESULT:\s*(?:REJECTED\b|NOT at target\b)|^FAIL: motor_gate exit", re.M)
INNER_RE = re.compile(r"^BGRUN INNER FAILURE:.*?first:\s*(.*)$", re.M)


def judge(path, seg, cmdline):
    end = P.BGRUN_END_RE.findall(seg)
    timeout = bool(P.BGRUN_TIMEOUT_RE.search(seg))
    if not end and not timeout:
        return None
    rc = int(end[-1]) if end else None
    old = timeout or bool(rc)
    endline = next((l for l in seg.splitlines() if l.startswith("BGRUN END")), "")
    proc_rc = 0 if "(inner failure" in endline else rc
    cmd = cmdline.split("min:", 1)[-1].split()
    exempt = logclass.is_review_log(path) or bgrun.is_jev_command(cmd)
    derived = None
    if not exempt:
        derived = P.stagekit_result_from_gates(seg)
        if "motor_gate.py" in cmdline and MOTOR_RE.search(seg):
            derived = P.make_result(0, len(MOTOR_RE.findall(seg)), MOTOR_RE.search(seg).group(0))
    new = timeout or bool(proc_rc) or (derived is not None and P.result_failed(derived))
    inner = (INNER_RE.search(seg).group(1) if INNER_RE.search(seg) else endline)[:110]
    return {"log": os.path.basename(path), "start": cmdline[12:31], "old": old, "new": new, "rc": rc,
            "proc_rc": proc_rc, "derived": derived, "inner": inner}


def main():
    res = []
    for p in sorted(glob.glob(os.path.join(HERE, "*.log"))):
        text = open(p, encoding="utf-8", errors="replace").read()
        for ts, cmdline, seg in P.segments(text):
            if ts is not None and T0 <= ts <= T1:
                r = judge(p, seg, cmdline)
                if r:
                    res.append(r)
    pm = os.path.join(HERE, "pi_testmove_20260923e.log")
    ts, cmdline, seg = P.last_segment(open(pm, encoding="utf-8", errors="replace").read())
    motor = judge(pm, seg, cmdline)
    removed = [r for r in res if r["old"] and not r["new"]]
    caught = [r for r in res if r["old"] and r["new"]]
    added = [r for r in res if not r["old"] and r["new"]]
    print("runs judged: %d  old-fail: %d  new-fail: %d" % (len(res), sum(r["old"] for r in res),
                                                          sum(r["new"] for r in res)))
    print("\n--- FALSE FAILURES REMOVED (old FAIL -> new PASS): %d" % len(removed))
    for r in removed:
        print("  %s  %-44s rc=%s first-scanned: %s" % (r["start"], r["log"], r["rc"], r["inner"]))
    print("\n--- STILL CAUGHT (old FAIL, new FAIL): %d" % len(caught))
    for r in caught:
        why = ("RESULT(derived) %s/%s" % (r["derived"]["gates"]["pass"], r["derived"]["gates"]["fail"])
               if r["derived"] and P.result_failed(r["derived"]) else "exit rc=%s" % r["proc_rc"])
        print("  %s  %-44s %s" % (r["start"], r["log"], why))
    print("\n--- NEWLY FAILING (old PASS, new FAIL): %d" % len(added))
    for r in added:
        print("  %s  %-44s %s" % (r["start"], r["log"], r["derived"]))
    l7 = [r for r in res if r["log"].startswith("stage_d1_l7_") and r["old"]]
    l7_missed = [r["log"] for r in l7 if not r["new"]]
    print("\n--- stage_d1_l7_* old failures: %d, still caught: %d, missed: %s" % (
        len(l7), len(l7) - len(l7_missed), l7_missed or "none"))
    print("--- motor rejection replay pi_testmove_20260923e.log: old %s new %s derived %s" % (
        motor["old"], motor["new"], motor["derived"]))
    print(P.result_line(P.make_result(2 - bool(l7_missed) - (not motor["new"]),
                                      bool(l7_missed) + (not motor["new"]),
                                      ("l7 missed %s" % l7_missed) if l7_missed else
                                      (None if motor["new"] else "motor replay not caught"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
