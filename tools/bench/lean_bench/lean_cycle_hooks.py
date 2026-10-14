# ---
# labview: close-only (end: quits / force-closes LabVIEW.exe through cycle_runner.labview_close_hook; never opens it)
# hardware: motors (PI + ASI limits only, through tools/motor_gate.py --session start|end; no motion except the gate's
#           own PI reference move at session start)
# ---
"""The lean queue's cycle boundary hooks (user 2026-10-13: "모터 움직임 제한을 위한 훅은 사이클 시작 시점에 걸고, 사이클
종료 시점에 풀리도록"; CLAUDE.md rule 1b: limits SET at every cycle start and RELEASED at every cycle end, each verified by
readback, after a real PI reference move; every cycle ends with LabVIEW CLOSED and verified gone).

  start  py tools/motor_gate.py --session start --status <main STATUS.md>   (limits written, PI reference move, readback)
  end    1. LabVIEW closed and verified gone (cycle_runner.labview_close_hook: COM Quit, then taskkill /F, then tasklist)
         2. py tools/motor_gate.py --session end --status <main STATUS.md>   (limits released, readback, session file gone)
         LabVIEW goes first so no VI can drive a motor once the limits are released, and the COM ports are free.

The rig state is read from the MAIN checkout's STATUS.md (the user's announcements live there, not in this worktree).
The lean session itself may not open or close the motor session (guard_lean refuses it): the limits hold for the whole
cycle. Exit 0 = done and verified; anything else = the queue stops the run (a safety step failed, the user must look).

Shared code CALLED, not copied: tools/motor_gate.py (CLI), tools/cycle_runner.labview_close_hook.
Usage: py tools/bench/lean_bench/lean_cycle_hooks.py start|end --tag <tag>
"""
import json
import os
import subprocess
import sys
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(os.path.dirname(HERE))
ROOT = os.path.dirname(TOOLS)
MAIN_STATUS = os.path.join(os.path.dirname(ROOT), "V6_ParallelLoop", "STATUS.md")
QLOG = os.path.join(HERE, "queue.log")
sys.path.insert(0, TOOLS)


def log(line):
    with open(QLOG, "a", encoding="utf-8") as f:
        f.write("%s\n" % line)
    print(line, flush=True)


def gate(which, tag):
    """motor_gate --session start|end against the MAIN STATUS; its output goes to motor_session_<which>_<tag>_<time>.log
    (time-stamped so a retried tag never overwrites an earlier cycle's record - evaluation 2026-10-14)."""
    out = os.path.join(HERE, "motor_session_%s_%s_%s.log" % (which, tag, time.strftime("%Y%m%d_%H%M%S")))
    with open(out, "w", encoding="utf-8") as f:
        rc = subprocess.call([sys.executable, os.path.join(TOOLS, "motor_gate.py"), "--session", which,
                              "--status", MAIN_STATUS], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, timeout=600)
    tail = [ln.strip() for ln in open(out, encoding="utf-8", errors="replace") if ln.strip()][-3:]
    return rc, out, tail


def main(argv):
    if len(argv) < 1 or argv[0] not in ("start", "end"):
        sys.stderr.write("usage: lean_cycle_hooks.py start|end --tag <tag>\n")
        return 2
    which = argv[0]
    tag = argv[argv.index("--tag") + 1] if "--tag" in argv else "untagged"
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    res = {"hook": which, "tag": tag}
    if which == "end":
        import cycle_runner
        a = types.SimpleNamespace(dry_run=False, dry_cmd=False, no_labview_close=False)
        status_text = open(MAIN_STATUS, encoding="utf-8", errors="replace").read()
        ok, verdict = cycle_runner.labview_close_hook(0, a, os.path.dirname(HERE), QLOG, status_text)
        res["labview"] = verdict
        if not ok:
            res["status"] = "FAIL"
            log("CYCLE-HOOK | %s | %s | end | LabVIEW NOT verified gone: %s - limits NOT released" % (stamp, tag, verdict))
            print("RESULT " + json.dumps(res, ensure_ascii=False))
            return 3
    rc, out, tail = gate(which, tag)
    res.update(gate_rc=rc, gate_log=os.path.relpath(out, ROOT).replace("\\", "/"), gate_tail=tail)
    ok = rc == 0 and any(("SESSION %s OK" % which.upper()) in t for t in tail)
    res["status"] = "PASS" if ok else "FAIL"
    log("CYCLE-HOOK | %s | %s | %s | motor_gate rc=%s | %s | %s"
        % (stamp, tag, which, rc, " / ".join(tail)[:300], res.get("labview", "")))
    print("RESULT " + json.dumps(res, ensure_ascii=False))
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
