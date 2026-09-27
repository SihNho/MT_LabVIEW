r"""runner_supervisor.py - when a cycle runner ends ROUTINELY, start the next one (user, 2026-09-28 03:1x:
"러너가 멈추면 자동으로 새 러너 돌려야하는거 아니야?" / "러너가 멈추면 다음 러너를 돌리라니깐").

Routine end = the runner's last `RUNNER STOP` line is the graceful budget stop or `--cycles N exhausted`.
Every other end is a REAL stop and the supervisor exits without relaunching: a STOP marker in STATUS.md, repeated
failure, usage limit, firefighter ceiling, pending user decision, a crash (no RUNNER STOP line), a bgrun TIMEOUT.
Before each relaunch it re-checks STATUS.md for a STOP marker (cycle_runner.stop_marker, the same reader).
A runner that ended routinely in under MIN_LIFE_MIN is treated as a fault (no tight relaunch loop).

It first waits for a runner that is already running (newest tools/bench/cycle_runner_main_*.log without a
`BGRUN END` line), then takes over. Each new runner gets its own log cycle_runner_main_<YYYYmmdd_HHMM>.log, the name
report_gate.py and the runner-cycle-report task already read (newest by mtime).

Launch (from the project root, under bgrun like every long job):
    py tools/bgrun.py --max-min 10080 --log tools/bench/runner_supervisor.log -- py -u tools/runner_supervisor.py
Self-test (no launch): py tools/runner_supervisor.py --selftest
"""
import glob, os, re, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(ROOT, "tools", "bench")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import cycle_runner as CR                                                   # noqa: E402  (stop_marker only)

RUNNER_ARGS = ["--cycles", "0", "--budget-min", "480"]    # the user's 8 h rotation; a fresh runner after each
BGRUN_MAX_MIN = "720"                                     # CLAUDE.md: well above budget + the longest cycle
MIN_LIFE_MIN = 30
POLL_S = 60
ROUTINE = re.compile(r"RUNNER STOP \|[^|]*\| (graceful: --budget-min|--cycles \d+ exhausted)")


def say(msg):
    print("SUPERVISOR | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg), flush=True)


def newest_log():
    logs = glob.glob(os.path.join(BENCH, "cycle_runner_main_*.log"))
    return max(logs, key=os.path.getmtime) if logs else None


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def verdict(log_text):
    """-> ('routine'|'real'|'running', reason line)."""
    lines = log_text.splitlines()
    if not any(l.startswith("BGRUN END") for l in lines):
        return "running", ""
    stops = [l for l in lines if l.startswith("RUNNER STOP")]
    if not stops:
        return "real", "no RUNNER STOP line (crash or bgrun TIMEOUT): " + (lines[-1] if lines else "")
    last = stops[-1]
    return ("routine" if ROUTINE.match(last) else "real"), last


def status_stop():
    return CR.stop_marker(read(os.path.join(ROOT, "STATUS.md")))


def launch():
    log = os.path.join(BENCH, "cycle_runner_main_%s.log" % time.strftime("%Y%m%d_%H%M"))
    cmd = [sys.executable, os.path.join(ROOT, "tools", "bgrun.py"), "--max-min", BGRUN_MAX_MIN, "--log", log, "--",
           "py", os.path.join(ROOT, "tools", "cycle_runner.py")] + RUNNER_ARGS
    say("LAUNCH %s" % os.path.relpath(log, ROOT))
    t0 = time.time()
    rc = subprocess.run(cmd, cwd=ROOT).returncode
    return log, rc, (time.time() - t0) / 60.0


def main():
    log = newest_log()
    life = None
    while True:
        if log:
            while verdict(read(log))[0] == "running":
                time.sleep(POLL_S)
            kind, why = verdict(read(log))
            say("runner ended (%s): %s" % (kind, why))
            if kind != "routine":
                say("EXIT - real stop, not relaunching")
                return 0
            if life is not None and life < MIN_LIFE_MIN:
                say("EXIT - routine end after only %.1f min (< %d): treated as a fault" % (life, MIN_LIFE_MIN))
                return 3
        mark = status_stop()
        if mark:
            say("EXIT - STATUS.md carries a STOP marker: %s" % mark)
            return 0
        log, rc, life = launch()
        say("bgrun rc=%s after %.1f min" % (rc, life))


def selftest():
    ok = 0
    cases = [("x\nRUNNER STOP | t | graceful: --budget-min 480 exceeded (529 min elapsed); ...\nBGRUN END rc=0", "routine"),
             ("RUNNER STOP | t | --cycles 8 exhausted\nBGRUN END rc=0", "routine"),
             ("RUNNER STOP | t | STATUS.md carries a STOP marker: STOP x\nBGRUN END rc=0", "real"),
             ("RUNNER STOP | t | same failure two cycles running\nBGRUN END rc=0", "real"),
             ("CYCLE 1 | ...\nBGRUN TIMEOUT\nBGRUN END rc=-9", "real"),
             ("CYCLE 1 | ...", "running")]
    for text, want in cases:
        got = verdict(text)[0]
        ok += got == want
        print("%s want=%s got=%s" % ("PASS" if got == want else "FAIL", want, got))
    print("STATUS stop marker now:", status_stop())
    print("SELFTEST %d/%d" % (ok, len(cases)))
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
