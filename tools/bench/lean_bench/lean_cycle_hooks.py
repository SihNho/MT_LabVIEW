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
import re
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


PI_TOL_MM = 0.001   # motor_limits.json tolerance
ASI_TOL = 2         # ASI position units; evidence: all 13 cycles 2026-10-13/14 before p64p2 read back EXACTLY equal
POS_AFTER_RE = re.compile(r"position after \(must be unchanged\): X=(-?\d+) Y=(-?\d+)")
READBACK_RE = re.compile(r"VERIFY: commanded=\S+ readback=(-?[\d.Ee+-]+)")
PI_BEFORE_RE = re.compile(r"before: POS\?=1=(-?[\d.Ee+-]+)")


def positions(start_log, end_log):
    """{pi_start, pi_end, asi_start, asi_end} from the cycle's motor_gate logs: PI = the last VERIFY readback after the
    start reference move vs the end session's `before: POS?`; ASI = the `position after` (X, Y) of each. None = unread."""
    def text(p):
        try:
            return open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            return ""
    s, e = text(start_log), text(end_log)
    rb = READBACK_RE.findall(s)
    pe = PI_BEFORE_RE.search(e)
    a0, a1 = POS_AFTER_RE.search(s), POS_AFTER_RE.search(e)
    return {"pi_start": float(rb[-1]) if rb else None, "pi_end": float(pe.group(1)) if pe else None,
            "asi_start": (int(a0.group(1)), int(a0.group(2))) if a0 else None,
            "asi_end": (int(a1.group(1)), int(a1.group(2))) if a1 else None}


def check_positions(p):
    """Evaluation 2026-10-14 change 1 (user "1~6 동의"): an unexpected PI or ASI XY position change over the cycle stops
    the run. -> (ok, why)."""
    if None in (p["pi_start"], p["pi_end"], p["asi_start"], p["asi_end"]):
        return False, "positions unreadable %s" % p
    why = []
    if abs(p["pi_end"] - p["pi_start"]) > PI_TOL_MM:
        why.append("PI %.5f -> %.5f mm" % (p["pi_start"], p["pi_end"]))
    dx, dy = p["asi_end"][0] - p["asi_start"][0], p["asi_end"][1] - p["asi_start"][1]
    if abs(dx) > ASI_TOL or abs(dy) > ASI_TOL:
        why.append("ASI X %d -> %d, Y %d -> %d" % (p["asi_start"][0], p["asi_end"][0], p["asi_start"][1], p["asi_end"][1]))
    return (not why), ("; ".join(why) or "unchanged")


def selftest():
    """Offline, on the recorded logs: p64p3 (13:03-13:07, nothing moved) -> ok; p64p2 (13:13-15:18, the user moved the
    ASI by joystick) -> STOP; a synthetic PI left at 30 mm -> STOP; a missing log -> STOP."""
    ok, n = 0, 0
    cases = [
        ("p64p3 unchanged -> ok", "motor_session_start_p64p3_20261014_130339.log",
         "motor_session_end_p64p3_20261014_130705.log", True),
        ("p64p2 ASI moved -> stop", "motor_session_start_p64p2_20261014_131350.log",
         "motor_session_end_p64p2_20261014_151838.log", False),
        ("missing end log -> stop", "motor_session_start_p64p3_20261014_130339.log", "nope.log", False)]
    for name, s, e, want in cases:
        got, why = check_positions(positions(os.path.join(HERE, s), os.path.join(HERE, e)))
        n += 1
        ok += got == want
        print("%s  %s (%s)" % ("PASS" if got == want else "FAIL", name, why))
    p = positions(os.path.join(HERE, cases[0][1]), os.path.join(HERE, cases[0][2]))
    p["pi_end"] = 30.0
    got, why = check_positions(p)
    n += 1
    ok += got is False
    print("%s  PI left at 30 mm -> stop (%s)" % ("PASS" if got is False else "FAIL", why))
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if ok == n else "FAIL",
                                  "gates": {"pass": ok, "fail": n - ok}, "first_fail": None, "artefacts": []}))
    return 0 if ok == n else 1


def newest(pattern):
    import glob
    hits = glob.glob(os.path.join(HERE, pattern))
    return max(hits, key=os.path.getmtime) if hits else None


def main(argv):
    if argv[:1] == ["selftest"]:
        return selftest()
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
    if which == "end":   # after the release: the cycle's start vs end positions (evaluation change 1)
        start_log = newest("motor_session_start_%s_*.log" % tag)
        pok, pwhy = check_positions(positions(start_log or "", out))
        res["positions"] = pwhy
        if not pok:
            ok = False
            log("POSITION-CHANGE | %s | %s | %s (start %s) - the run stops; limits already released"
                % (stamp, tag, pwhy, os.path.basename(start_log or "-")))
    res["status"] = "PASS" if ok else "FAIL"
    log("CYCLE-HOOK | %s | %s | %s | motor_gate rc=%s | %s | %s"
        % (stamp, tag, which, rc, " / ".join(tail)[:300], res.get("labview", "")))
    print("RESULT " + json.dumps(res, ensure_ascii=False))
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
