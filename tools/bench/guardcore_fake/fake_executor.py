# ---
# labview: none
# hardware: none
# ---
"""fake_executor.py - card chat-X2 step 4: the COMMON EXECUTOR PATH (guard_bash launch gates, stage_prerun.check_launch,
tools/bgrun.py) against SENTINEL targets only. Nothing here starts LabVIEW, opens a port or calls a motor script: the
forbidden commands are JUDGED (guardcore.judge -> the existing guards), and the only processes actually started are
`py -c` sleepers that write marker files under tools/bench/guardcore_fake/.

PREDICTION CONTRACT:
  E1 bypass - a LabVIEW-scoped script started WITHOUT bgrun (foreground, no timeout) is refused;
  E2 bypass - the same backgrounded without bgrun is refused;
  E3 the stage launch gate (stage_prerun.check_launch) refuses a stage script it has no dry/prerun record for;
  E4 inline COM / serial in a command is refused;
  E5 a run past its deadline: bgrun --max-min 0.05 kills the sleeper - log ends `BGRUN TIMEOUT`, the sleeper's END
     marker is never written;
  E6 a concurrent run: the EXECUTOR does NOT refuse a second run started beside a live one (predicted GAP - both
     sleepers write their START marker); the command-level screen guardcore R4 does refuse a LabVIEW-scoped launch
     while LabVIEW runs (probe forced).
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
TOOLS = os.path.dirname(BENCH)
ROOT = os.path.dirname(TOOLS)
for d in (os.path.join(TOOLS, "hooks"), TOOLS):
    if d not in sys.path:
        sys.path.insert(0, d)
os.environ.setdefault("GUARDCORE_LOG", os.path.join(BENCH, "guardcore_fixtures", "fake_executor_judge.log"))
import guardcore      # noqa: E402
import adapt_claude   # noqa: E402
import protocol       # noqa: E402
import stage_prerun   # noqa: E402

SH = "PowerShell" if os.name == "nt" else "Bash"
LVCMD = "py -u tools/bench/guardcore_fake/sentinel_lv.py"


def judge_shell(cmd, timeout=None, bg=False):
    ti = {"command": cmd}
    if timeout is not None:
        ti["timeout"] = timeout
    if bg:
        ti["run_in_background"] = True
    return guardcore.judge(adapt_claude.to_event({"tool_name": SH, "tool_input": ti, "session_id": "gc_fake_exec",
                                                  "cwd": ROOT}), probe=lambda: False)


def sleeper(tag, secs):
    m = os.path.join(HERE, "marker_%s" % tag).replace("\\", "/")
    return [sys.executable, "-u", "-c",
            "import time;open(r'%s_start.txt','w').write('s');time.sleep(%d);open(r'%s_end.txt','w').write('e')"
            % (m, secs, m)]


def bgrun(tag, max_min, secs):
    log = os.path.join(HERE, "fake_exec_%s.log" % tag)
    for f in (log, os.path.join(HERE, "marker_%s_start.txt" % tag), os.path.join(HERE, "marker_%s_end.txt" % tag)):
        if os.path.exists(f):
            os.remove(f)
    p = subprocess.Popen([sys.executable, os.path.join(TOOLS, "bgrun.py"), "--max-min", str(max_min), "--log", log,
                          "--"] + sleeper(tag, secs), cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return p, log


def main():
    ok = bad = 0
    first = None

    def gate(label, cond, detail=""):
        nonlocal ok, bad, first
        ok, bad = (ok + 1, bad) if cond else (ok, bad + 1)
        first = first or (None if cond else label)
        print("GATE %s %s | %s" % ("PASS" if cond else "FAIL", label, str(detail)[:300].replace("\n", " ")))

    v, why = judge_shell(LVCMD)
    gate("E1 LabVIEW-scoped script without bgrun (foreground) refused", v == "deny", why)
    v, why = judge_shell("py -u tools/bench/guardcore_fake/sentinel_lv.py --material", bg=True)
    gate("E2 same, backgrounded without bgrun, refused", v == "deny", why)
    ok_l, why_l = stage_prerun.check_launch("py -u tools/recipes/stage_gc_fake_never_exists.py")
    gate("E3 stage launch gate refuses a stage script without records", not ok_l, why_l)
    v, why = judge_shell("py -c \"import serial; serial.Serial('COM99')\"", timeout=10000)
    gate("E4 inline serial refused", v == "deny", why)

    p, log = bgrun("timeout", 0.05, 30)            # 3 s deadline, 30 s sleeper
    p.wait(timeout=90)
    txt = open(log, encoding="utf-8", errors="replace").read() if os.path.exists(log) else ""
    gate("E5 bgrun kills a run past --max-min (BGRUN TIMEOUT)", "BGRUN TIMEOUT" in txt,
         [ln for ln in txt.splitlines() if ln.startswith("BGRUN")])
    gate("E5 the killed run never reached its END marker",
         not os.path.exists(os.path.join(HERE, "marker_timeout_end.txt")))

    p1, log1 = bgrun("conc1", 1, 6)
    time.sleep(2)
    p2, log2 = bgrun("conc2", 1, 6)
    p1.wait(timeout=90)
    p2.wait(timeout=90)
    both = all(os.path.exists(os.path.join(HERE, "marker_%s_start.txt" % t)) for t in ("conc1", "conc2"))
    gate("E6 GAP (predicted): bgrun does NOT refuse a second run beside a live one", both,
         "both sleepers started" if both else "second refused")
    ev = adapt_claude.to_event({"tool_name": SH, "session_id": "gc_fake_exec", "cwd": ROOT, "tool_input": {
        "command": "py tools/bgrun.py --material --max-min 1 --log tools/bench/guardcore_fake/x.log -- " + LVCMD,
        "timeout": 20000}})
    gate("E6 command-level screen guardcore R4 refuses a LabVIEW launch while LabVIEW runs",
         bool(guardcore.concurrency_ban(ev, probe=lambda: True)), guardcore.concurrency_ban(ev, probe=lambda: True))
    print(protocol.result_line(protocol.make_result(ok, bad, first)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
