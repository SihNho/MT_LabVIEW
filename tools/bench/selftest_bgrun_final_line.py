r"""selftest_bgrun_final_line.py - does the terminal line REALLY get written on every exit path,
and does wait_logs.py survive a non-cp949 character in the tail it prints?

Covers the two repairs of cycle 36 (2026-09-18), both REPAIRS of existing devices:
  * tools/bgrun.py  - the docstring promised "Always ends by writing BGRUN END / BGRUN TIMEOUT"
    while the file held no try/finally and no atexit (5th occurrence of the OPEN-54 class; four
    START-only logs on disk: diag_fstunnelterm_v2_panelcost, p2_open_copy, prose_cycle25,
    wait_runner_exit).
  * tools/wait_logs.py:75 - UnicodeEncodeError: 'cp949' ... '—' raised out of the DONE print,
    i.e. the waiter crashing at the exact tick it succeeded. Hit by two sessions on 2026-09-18.

PRIOR ART checked before writing (CLAUDE.md "before creating any new op, tool or recipe"):
  * ls tools/bench/*selftest* - 14 self-tests exist; the closest, `selftest_bgrun_fail_scan.py`,
    tests bgrun's INNER-FAILURE regex only and never asserts that a terminal line exists at all.
  * `tools/bench/bgrun_selftest.log` is a 2026-09-05 log of a throwaway probe, not a runnable test.
  * grep "^def " tools/gscript.py - LabVIEW only, nothing relevant. No LabVIEW is touched here.

PREDICTION CONTRACT (each gate FAILs loudly if the observation differs):
  B1 normal exit .......... child rc 0        -> last line matches ^BGRUN END rc=0
  B2 non-zero child rc .... child exits 3     -> last line matches ^BGRUN END rc=3
  B3 runner exception ..... command does not exist (Popen raises inside main) -> last line
                            matches ^BGRUN END and carries "runner exception"; runner rc 125
  B4 timeout .............. child sleeps 20 s, limit 0.02 min -> last line matches ^BGRUN TIMEOUT;
                            runner rc 124
  B5 exactly ONE terminal line in each of the four logs (no double-write by the finalizer)
  C0 control: printing an em-dash to a cp949 stdout DOES raise UnicodeEncodeError in this
     environment (if it does not, W1/W2 prove nothing and this test says so)
  W1 wait_logs on a terminal log whose matched line holds an em-dash, PYTHONIOENCODING=cp949
                            -> rc 0, stdout carries "DONE", no traceback
  W2 wait_logs on a RUNNING log whose tail holds an em-dash -> rc 3, "RUNNING", no traceback

OUTPUT IS SANITISED: every quoted log line has "rc=" rewritten to "rc<eq>" before printing,
because the outer bgrun scans this script's stdout for `rc=<non-zero>` and would otherwise report
its own passing self-test as an inner failure (bgrun.py inner_re; STATUS OPEN 6/8 history).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

# Run 1 of this test PASSED all six bgrun gates and then died in its OWN print, with the exact error it
# was written to check: `UnicodeEncodeError: 'cp949' ... '—'` at the W1 gate, because a child of
# bgrun gets a cp949 stdout and the quoted wait_logs output carries the em-dash. Kept as evidence that
# the class is real and environmental, not specific to wait_logs. Both belts here: reconfigure, and an
# ASCII fold inside safe() so the quoted text can never reach the encoder intact.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
BGRUN = os.environ.get("BGRUN_UNDER_TEST") or os.path.join(PROJECT, "tools", "bgrun.py")   # override: test a candidate copy
WAITER = os.path.join(PROJECT, "tools", "wait_logs.py")
EMDASH = "—"

PASS = 0
FAIL = 0


def safe(s):
    s = str(s).replace("rc=", "rc<eq>")
    return s.encode("ascii", errors="replace").decode("ascii")   # em-dash -> '?', never an encoder error


def gate(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print("  -> PASS %s  %s" % (name, safe(detail)), flush=True)
    else:
        FAIL += 1
        print("  -> FAIL %s  %s" % (name, safe(detail)), flush=True)


def run_bgrun(logp, minutes, cmd):
    p = subprocess.run([sys.executable, BGRUN, "--max-min", str(minutes), "--log", logp, "--"] + cmd,
                       cwd=PROJECT, capture_output=True)
    return p.returncode


def lines(logp):
    with open(logp, "r", encoding="utf-8", errors="replace") as f:
        return [ln.rstrip("\n") for ln in f if ln.strip()]


def terminal_lines(logp):
    return [ln for ln in lines(logp) if ln.startswith("BGRUN END") or ln.startswith("BGRUN TIMEOUT")]


def main():
    tmp = tempfile.mkdtemp(prefix="bgrunfinal_")
    try:
        # ---------------- bgrun: the four exit paths ----------------
        cases = [
            ("B1 normal-exit", 1, [sys.executable, "-c", "print('child ok')"],
             0, r"^BGRUN END rc=0\b", None),
            ("B2 child-rc-nonzero", 1, [sys.executable, "-c", "import sys; sys.exit(3)"],
             3, r"^BGRUN END rc=3\b", None),
            ("B3 runner-exception", 1, ["__no_such_executable_c36__"],
             125, r"^BGRUN END\b", "runner exception"),
            ("B4 timeout", 0.02, [sys.executable, "-c", "import time; time.sleep(20)"],
             124, r"^BGRUN TIMEOUT\b", None),
        ]
        logs = {}
        for name, mins, cmd, want_rc, want_re, want_sub in cases:
            logp = os.path.join(tmp, name.split()[0] + ".log")
            logs[name] = logp
            rc = run_bgrun(logp, mins, cmd)
            ls = lines(logp)
            last = ls[-1] if ls else "<EMPTY LOG>"
            ok = bool(re.match(want_re, last)) and rc == want_rc
            if want_sub:
                ok = ok and (want_sub in last)
            gate(name, ok, "runner exit %d (want %d) | last: %s" % (rc, want_rc, last[:150]))

        multi = [n for n, p in logs.items() if len(terminal_lines(p)) != 1]
        gate("B5 exactly-one-terminal-line", not multi,
             "logs with a count other than 1: %s" % (multi or "none"))

        # ---------------- control: does cp949 stdout really break? ----------------
        env = dict(os.environ, PYTHONIOENCODING="cp949")
        c = subprocess.run([sys.executable, "-c", "print('tail %s here')" % EMDASH],
                           cwd=PROJECT, capture_output=True, env=env)
        ctl = c.returncode != 0 and b"UnicodeEncodeError" in (c.stderr or b"")
        gate("C0 control-cp949-raises", ctl,
             "python -c print(em-dash) under PYTHONIOENCODING=cp949 exit %d" % c.returncode)

        # ---------------- wait_logs: DONE and RUNNING with an em-dash ----------------
        done_log = os.path.join(tmp, "w_done.log")
        with open(done_log, "w", encoding="utf-8") as f:
            f.write("BGRUN START 2026-09-18 00:00:00 limit 5 min: py -u probe.py\n")
            f.write("some %s narrative line\n" % EMDASH)
            f.write("BGRUN END rc=0 after 12s %s done\n" % EMDASH)
        run_log = os.path.join(tmp, "w_running.log")
        with open(run_log, "w", encoding="utf-8") as f:
            f.write("BGRUN START 2026-09-18 00:00:00 limit 5 min: py -u probe.py\n")
            f.write("step 3 %s still working\n" % EMDASH)

        for name, logp, want_rc, want_word in (("W1 wait-DONE-emdash", done_log, 0, "DONE"),
                                               ("W2 wait-RUNNING-emdash", run_log, 3, "RUNNING")):
            w = subprocess.run([sys.executable, WAITER, "--seconds", "1", logp],
                               cwd=PROJECT, capture_output=True, env=env)
            so = (w.stdout or b"").decode("utf-8", errors="replace")
            se = (w.stderr or b"").decode("utf-8", errors="replace")
            ok = (w.returncode == want_rc) and (want_word in so) and ("Traceback" not in se) \
                and ("UnicodeEncodeError" not in se)
            gate(name, ok, "exit %d (want %d) | out: %s | err: %s"
                 % (w.returncode, want_rc, so.strip().replace("\n", " ; ")[:160], se.strip()[:120]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("=== selftest_bgrun_final_line: %d pass, %d fail ===" % (PASS, FAIL), flush=True)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
