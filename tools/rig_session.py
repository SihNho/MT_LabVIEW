# ---
# labview: read
# hardware: motor
# ---
# labview = close-only at the end (cycle_runner.labview_close_hook: COM Quit, taskkill, tasklist); never opens or edits.
# hardware = PI + ASI limits through tools/motor_gate.py --session start|end only; any motion inside the wrapped command
# goes through motor_gate.py itself (this file sends nothing to a device).
"""rig_session.py - one rig job OUTSIDE the lean queue (chat checks, one-off cards) under the shared rig lock
(user 2026-10-21, debate riglock-v6 item 8; G:\\Codes\\rig\\riglock.py):

  1. acquire the lock (holder V6-chat, this process's pid) - refused: experiment / another live holder / stale / error
  2. motor_gate --session start (limits set, PI reference move, readback)        [skipped with --no-motor-session]
  3. run the command with RIGLOCK_TOKEN in its environment (its motor commands go through motor_gate --execute,
     which checks the lock); every 30 s ask riglock.permitted - if the user declared an experiment (or the lock is
     lost) the command's process tree is killed
  4. cleanup, ALWAYS, also after a kill or a failure: LabVIEW closed and verified gone, then motor_gate --session end
     (limits released + readback) - the rig back at its initial condition (user item 9)
  5. cleanup verified -> release the lock; cleanup FAILED -> the lock is KEPT (exit 3) so the next user sees it

The guards still apply: the wrapped command is a normal command (guard_bash checks the Bash line that contains it), and
nothing here bypasses motor_gate. Run it like any LabVIEW / motor job, backgrounded through bgrun:
  py tools/bgrun.py --max-min 20 --log tools/bench/<name>.log -- py -u tools/rig_session.py --purpose "<why>" --max-min 15 -- <command ...>
Exit: 0 ok; 2 lock refused (nothing touched); 3 cleanup failed (lock kept); 4 command failed or was stopped (cleanup ok,
lock released). Last line: RESULT {...}.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATUS = os.path.join(ROOT, "STATUS.md")
LOGDIR = os.path.join(HERE, "bench")
sys.path.insert(0, HERE)
import motor_gate                                            # noqa: E402  (RIG_DIR, rig_lock_ok)
sys.path.insert(0, motor_gate.RIG_DIR)
import riglock                                               # noqa: E402

POLL_S = 30


def say(line):
    print("%s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), line), flush=True)


def gate_session(which, env, log_path):
    with open(log_path, "w", encoding="utf-8") as f:
        rc = subprocess.call([sys.executable, os.path.join(HERE, "motor_gate.py"), "--session", which],
                             cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=600)
    tail = [ln.strip() for ln in open(log_path, encoding="utf-8", errors="replace") if ln.strip()][-2:]
    return rc == 0 and any(("SESSION %s OK" % which.upper()) in t for t in tail), tail


def close_labview(log_path):
    import cycle_runner
    a = types.SimpleNamespace(dry_run=False, dry_cmd=False, no_labview_close=False)
    status_text = open(STATUS, encoding="utf-8", errors="replace").read()
    return cycle_runner.labview_close_hook(0, a, LOGDIR, log_path, status_text)


def kill_tree(p):
    subprocess.call(["taskkill", "/T", "/F", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        p.wait(60)
    except subprocess.TimeoutExpired:
        pass


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--max-min", type=float, default=15.0)
    ap.add_argument("--no-motor-session", action="store_true", help="camera-only job: no motor_gate session")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args(argv)
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    if not cmd:
        ap.error("no command after --")
    res = {"purpose": a.purpose, "cmd": " ".join(cmd)[:200]}
    stamp = time.strftime("%Y%m%d_%H%M%S")

    try:
        token = riglock.acquire("V6-chat", a.purpose, pid=os.getpid())
    except (riglock.Refused, OSError, RuntimeError, TimeoutError) as e:
        res.update(status="REFUSED", why=str(e))
        say("RIGLOCK refused - nothing touched: %s" % e)
        print("RESULT " + json.dumps(res, ensure_ascii=False))
        return 2
    say("RIGLOCK acquired (V6-chat, pid %d)" % os.getpid())
    env = dict(os.environ, RIGLOCK_TOKEN=token)
    cmd_rc, stopped, started = None, "", False

    try:
        if not a.no_motor_session:
            started = True
            ok, tail = gate_session("start", env, os.path.join(LOGDIR, "rig_session_start_%s.log" % stamp))
            say("motor session start: %s %s" % ("OK" if ok else "FAILED", " / ".join(tail)))
            if not ok:
                stopped = "motor session start failed"
        if not stopped:
            p = subprocess.Popen(cmd, cwd=ROOT, env=env)
            t_end = time.time() + a.max_min * 60
            while True:
                try:
                    cmd_rc = p.wait(POLL_S)
                    break
                except subprocess.TimeoutExpired:
                    pass
                if not riglock.permitted(token, motor_gate.RIG_STATES_OK):
                    stopped = "rig lock no longer permits work (experiment declared or lock lost)"
                elif time.time() > t_end:
                    stopped = "time limit %.0f min" % a.max_min
                if stopped:
                    say("stopping the command: %s" % stopped)
                    kill_tree(p)
                    break
    finally:
        # cleanup ALWAYS: LabVIEW gone, then limits released (user item 9 - back to the initial condition)
        lv_ok, lv_why = close_labview(os.path.join(LOGDIR, "rig_session_labview_%s.log" % stamp))
        say("LabVIEW close: %s %s" % ("OK" if lv_ok else "FAILED", lv_why))
        end_ok, end_tail = True, []
        if started:
            end_ok, end_tail = gate_session("end", env, os.path.join(LOGDIR, "rig_session_end_%s.log" % stamp))
            say("motor session end: %s %s" % ("OK" if end_ok else "FAILED", " / ".join(end_tail)))
        clean = lv_ok and end_ok
        if clean:
            riglock.release(token)
            say("RIGLOCK released")
        else:
            say("RIGLOCK KEPT - cleanup not verified; the user must look before anyone uses the rig")

    res.update(cmd_rc=cmd_rc, stopped=stopped or None, labview=lv_why, limits_released=end_ok if started else None,
               lock="released" if clean else "KEPT")
    rc = 3 if not clean else (4 if (stopped or cmd_rc) else 0)
    res["status"] = {0: "PASS", 3: "CLEANUP-FAILED", 4: "COMMAND-FAILED"}[rc]
    print("RESULT " + json.dumps(res, ensure_ascii=False))
    return rc


if __name__ == "__main__":
    sys.exit(main())
