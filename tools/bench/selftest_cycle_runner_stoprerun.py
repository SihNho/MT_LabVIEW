r"""Self-test for tools/cycle_runner.py - a STOP marker in STATUS beats the usage-limit RERUN (card chat-R1).

Why: 2026-10-02 23:50 cycle 141 slept to rerun after a usage-limit message although STATUS already carried the
user's weekly-90 % STOP; the chat added `stop_marker(read(status_path))` checks before and after the sleep
(cycle_runner.py:1488-1505). This test drives that path with NO LabVIEW, NO motors (--no-motor-hooks, and dry-cmd
skips them anyway), NO `claude -p`: the "session" is a stand-in script in a temp dir that prints a usage-limit
message, and STATUS / bench are temp copies. cycle_runner.py itself is not edited.

Existing pieces reused: selftest_cycle_runner.py's pattern (run_runner, new_case, whitespace-free temp paths for
--dry-cmd); cycle_runner.stop_marker / limit_wait_s semantics (STOP at line start in the head; resetsAt epoch).

PREDICTION CONTRACT (4 gates):
  S1  session writes `STOP` into STATUS then prints a limit message (--no-sleep) -> runner log has
      "usage-limit attempt 1: rerun SKIPPED - STATUS carries a STOP marker", no "sleeping", session ran once,
      runner ends with RUNNER STOP (STOP marker), exit 0
  S2  same, no STOP written (control) -> log has "usage-limit attempt 1, non-result; sleeping", no "SKIPPED"
      (the gate discriminates; --no-sleep then breaks, session ran once)
  S3  limit message with resetsAt = now-108 s (wait ~12 s, real sleep); the TEST writes STOP into STATUS once the
      runner logs "sleeping" -> log has "rerun SKIPPED after the wait", session ran exactly once (no attempt 2)
  S4  S3's runner exits 0 and its log carries a RUNNER STOP naming the STOP marker (a HEARTBEAT FINAL follows it)
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RUNNER = os.path.join(ROOT, "tools", "cycle_runner.py")
sys.path.insert(0, os.path.join(ROOT, "tools"))

RESULTS = []
STATUS_BODY = "# STATUS (self-test copy)\n\n## Where things stand\nnothing real here.\n\n## NEXT\ndo the first thing.\n"
# argv: status_path count_file mode   (mode: stop = write STOP then limit msg; plain = limit msg;
#                                       epoch<secs> = limit msg with resetsAt = now - <secs>)
SESSION = """import sys, time
sp, cnt, mode = sys.argv[1], sys.argv[2], sys.argv[3]
open(cnt, 'a').write('x\\n')
if mode == 'stop':
    b = open(sp, encoding='utf-8').read()
    open(sp, 'w', encoding='utf-8').write(b.replace('# STATUS (self-test copy)\\n',
                                                     '# STATUS (self-test copy)\\nSTOP weekly 90 pct (self-test)\\n'))
if mode.startswith('epoch'):
    print('Claude usage limit reached {"resetsAt": %d}' % int(time.time() - int(mode[5:])))
else:
    print('Claude usage limit reached')
"""


def gate(label, ok, detail=""):
    RESULTS.append((label, bool(ok)))
    print("  %-4s %-60s %s" % ("ok" if ok else "BAD", label, detail), flush=True)


def common(sp, bench):
    return ["--cycles", "1", "--status", sp, "--bench-dir", bench, "--max-min", "2",
            "--no-motor-hooks", "--no-errorlist-hook", "--no-labview-close"]


def new_case(tmp, name):
    d = os.path.join(tmp, name)
    os.makedirs(os.path.join(d, "bench"), exist_ok=True)
    sp = os.path.join(d, "STATUS.md")
    with open(sp, "w", encoding="utf-8") as f:
        f.write(STATUS_BODY)
    return sp, os.path.join(d, "bench"), os.path.join(d, "count.txt")


def rlog(bench):
    try:
        return open(os.path.join(bench, "cycle_runner.log"), encoding="utf-8").read()
    except OSError:
        return ""


def runs(cnt):
    try:
        return len(open(cnt).read().splitlines())
    except OSError:
        return 0


def main():
    tmp = tempfile.mkdtemp(prefix="cycstop_")
    sess = os.path.join(tmp, "session.py")
    with open(sess, "w", encoding="utf-8") as f:
        f.write(SESSION)
    if " " in tmp or " " in sys.executable:
        print("  BAD  a path contains a space; --dry-cmd is whitespace-split", flush=True)
        return 1
    try:
        # S1 - STOP written by the session, before the sleep
        sp, bench, cnt = new_case(tmp, "pre")
        p = subprocess.run([sys.executable, RUNNER, "--dry-cmd", "%s %s %s %s stop" % (sys.executable, sess, sp, cnt),
                            "--no-sleep"] + common(sp, bench), cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=300)
        L = rlog(bench)
        gate("S1 STOP before the sleep skips the rerun",
             p.returncode == 0 and "usage-limit attempt 1: rerun SKIPPED - STATUS carries a STOP marker" in L
             and "sleeping" not in L and runs(cnt) == 1 and "STATUS.md carries a STOP marker" in L,
             "exit %d, sessions %d, skipped %s" % (p.returncode, runs(cnt), "rerun SKIPPED" in L))

        # S2 - control: no STOP, the rerun path is taken (then --no-sleep breaks)
        sp, bench, cnt = new_case(tmp, "control")
        p = subprocess.run([sys.executable, RUNNER, "--dry-cmd", "%s %s %s %s plain" % (sys.executable, sess, sp, cnt),
                            "--no-sleep"] + common(sp, bench), cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=300)
        L = rlog(bench)
        gate("S2 control without STOP still takes the rerun path",
             "usage-limit attempt 1, non-result; sleeping" in L and "SKIPPED" not in L and runs(cnt) == 1,
             "exit %d, sessions %d" % (p.returncode, runs(cnt)))

        # S3/S4 - STOP appears DURING the sleep (written by this test once the runner logs 'sleeping')
        sp, bench, cnt = new_case(tmp, "post")
        proc = subprocess.Popen([sys.executable, RUNNER, "--dry-cmd",
                                 "%s %s %s %s epoch108" % (sys.executable, sess, sp, cnt)] + common(sp, bench),
                                cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                encoding="utf-8", errors="replace")
        wrote, t0 = False, time.time()
        while time.time() - t0 < 120 and proc.poll() is None:
            if not wrote and "non-result; sleeping" in rlog(bench):
                b = open(sp, encoding="utf-8").read()
                open(sp, "w", encoding="utf-8").write(b.replace("# STATUS (self-test copy)\n",
                                                                "# STATUS (self-test copy)\nSTOP during sleep\n"))
                wrote = True
            time.sleep(0.5)
        if proc.poll() is None:
            proc.kill()
        out = proc.communicate()[0] or ""
        L = rlog(bench)
        gate("S3 STOP during the sleep skips the rerun after the wait",
             wrote and "rerun SKIPPED after the wait - STATUS carries a STOP marker" in L and runs(cnt) == 1,
             "wrote_stop %s, sessions %d" % (wrote, runs(cnt)))
        last = [ln for ln in L.splitlines() if ln.strip()][-1:] or [""]
        gate("S4 runner then stops on the STOP marker",
             proc.returncode == 0 and "RUNNER STOP" in L and "STOP during sleep" in L,
             "exit %s, last: %s" % (proc.returncode, last[0][:80]))
        if not all(ok for _, ok in RESULTS):
            print("--- runner output (last case) ---\n" + out[-1500:] + "\n--- runner log ---\n" + L[-2500:], flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    good = sum(1 for _, ok in RESULTS if ok)
    print("SUMMARY %d/%d gates pass" % (good, len(RESULTS)), flush=True)
    import protocol
    bad = [lab for lab, ok in RESULTS if not ok]
    print(protocol.result_line(protocol.make_result(good, len(bad), bad[0] if bad else None)), flush=True)
    return 0 if good == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
