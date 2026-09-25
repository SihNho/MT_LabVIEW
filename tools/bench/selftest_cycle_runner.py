r"""Self-test for tools/cycle_runner.py - the loop, the logging and all four stop conditions.

NO LabVIEW, NO agents, NO `claude -p`: every "session" is replaced by `--dry-run` / `--dry-cmd`, and every file
the runner reads or writes lives in a throwaway temp directory, so the project's own STATUS.md and
tools/bench/*.log are untouched.

PREDICTION CONTRACT (7 gates):
  G1  a STATUS.md with a `STOP` line in its head       -> exit 0, no cycle run, runner log says STOP marker
  G2  three cycles whose session CHANGES the NEXT text -> exit 0 after exactly 3 cycles, 3 CYCLE lines logged,
                                                          per-cycle logs cycle_1/2/3.log each with a BGRUN END
  G3  a session that leaves NEXT identical             -> exit 3 after 4 cycles (judgement ladder, card chat-M1b
                                                          2026-09-26: x1 opus high, x2 fable low, x3 fable medium,
                                                          x4 RUNNER STOP), "ladder is exhausted" in the reason
  G4  the same run appends `## RUNNER STOPPED` to STATUS and does not rewrite what was there
  G5  a session that exits non-zero twice              -> exit 3, reason names the repeat
  G6  cycle numbering continues from the runner log    -> a second invocation starts at CYCLE 4
  G7  `limit_wait_s` parses an epoch reset, a clock reset and a bare limit message, and returns None otherwise
Output deliberately avoids the strings bgrun/guard_peer scan for (`rc=<n>`, a line starting with FAIL).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RUNNER = os.path.join(ROOT, "tools", "cycle_runner.py")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import cycle_runner  # noqa: E402

RESULTS = []
STATUS_BODY = """# STATUS (self-test copy)

## Where things stand
nothing real here.

## NEXT
do the first thing.

## Where to look
nowhere.
"""
# A stand-in "session": it rewrites the NEXT section of the STATUS file it is given, the way a real judgement
# session ends its cycle. Written to the temp dir so --dry-cmd can be whitespace-split safely.
# Since session protocol v1 (C7, 2026-09-24) the runner reads `<bench>/next.json`, not the prose: the stand-in also
# writes a valid next/1 there (argv[2] = the bench dir; argv[3] = 'stop' sets stop_requested).
MUTATOR = """import sys, time, json, os
p = sys.argv[1]
b = open(p, encoding='utf-8').read()
b = b.replace('## NEXT\\n', '## NEXT\\nturn %s\\n' % time.time())
open(p, 'w', encoding='utf-8').write(b)
if len(sys.argv) > 2:
    json.dump({"schema": "next/1", "cycle": 1, "act": "self-test act", "task_kind": "build", "plan": None,
               "pass": [], "blocked_by": None, "stop_requested": len(sys.argv) > 3 and sys.argv[3] == 'stop',
               "advances": ["M3"], "note": "turn %s" % time.time()},
              open(os.path.join(sys.argv[2], 'next.json'), 'w', encoding='utf-8'))
print('session done')
"""


def gate(label, ok, detail=""):
    RESULTS.append((label, bool(ok)))
    print("  %-4s %-52s %s" % ("ok" if ok else "BAD", label, detail), flush=True)


def run_runner(*args):
    p = subprocess.run([sys.executable, RUNNER] + list(args), cwd=ROOT, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=900)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def new_case(tmp, name, body=STATUS_BODY):
    d = os.path.join(tmp, name)
    os.makedirs(os.path.join(d, "bench"), exist_ok=True)
    sp = os.path.join(d, "STATUS.md")
    with open(sp, "w", encoding="utf-8") as f:
        f.write(body)
    return sp, os.path.join(d, "bench")


def cycle_lines(bench):
    p = os.path.join(bench, "cycle_runner.log")
    try:
        return [ln for ln in open(p, encoding="utf-8").read().splitlines() if ln.startswith("CYCLE ")]
    except OSError:
        return []


def main():
    tmp = tempfile.mkdtemp(prefix="cycrun_")
    mut = os.path.join(tmp, "mutator.py")
    failer = os.path.join(tmp, "failer.py")
    with open(mut, "w", encoding="utf-8") as f:
        f.write(MUTATOR)
    with open(failer, "w", encoding="utf-8") as f:
        f.write("import sys\nprint('session refused')\nsys.exit(2)\n")
    if " " in tmp or " " in sys.executable:
        # --dry-cmd is whitespace-split by design (self-test only), so a space here would silently mis-run.
        print("  BAD  a path contains a space; this test needs space-free temp and interpreter paths", flush=True)
        return 1
    try:
        # G1 - the user's STOP marker
        sp, bench = new_case(tmp, "stop", STATUS_BODY.replace("# STATUS (self-test copy)",
                                                              "# STATUS (self-test copy)\nSTOP the runner, please"))
        code, out = run_runner("--dry-run", "--cycles", "3", "--status", sp, "--bench-dir", bench)
        gate("G1 STOP marker stops before any cycle",
             code == 0 and not cycle_lines(bench) and "STOP marker" in out, "exit %d" % code)

        # G2 - three cycles that move
        sp, bench = new_case(tmp, "moving")
        code, out = run_runner("--dry-cmd", "%s %s %s %s" % (sys.executable, mut, sp, bench),
                               "--cycles", "3", "--status", sp, "--bench-dir", bench, "--max-min", "2")
        lines = cycle_lines(bench)
        logs_ok = all(os.path.isfile(os.path.join(bench, "cycle_%d.log" % i)) for i in (1, 2, 3))
        ends = sum(1 for i in (1, 2, 3)
                   if "BGRUN END" in open(os.path.join(bench, "cycle_%d.log" % i), encoding="utf-8").read())
        gate("G2 three moving cycles complete", code == 0 and len(lines) == 3 and logs_ok and ends == 3,
             "exit %d, %d CYCLE lines, %d ended" % (code, len(lines), ends))
        # G8 - C1: one valid cycle/1 card per cycle, and the session's prompt starts with `CARD <path>`
        import protocol
        cards_ok = 0
        for i in (1, 2, 3):
            cp = os.path.join(bench, "cards", "cycle_%d.json" % i)
            try:
                c = protocol.load_card(cp, None)
                cards_ok += (c["cycle"] == i and c["errorlist"] is None)
            except (OSError, ValueError):
                pass
        rlog = open(os.path.join(bench, "cycle_runner.log"), encoding="utf-8").read()
        gate("G8 a valid cycle/1 card is written for every cycle", cards_ok == 3 and rlog.count("CYCLE-CARD |") == 3,
             "%d/3 cards valid" % cards_ok)
        gate("G9 next.json is read after every cycle (C7)", rlog.count("next.json read, CHANGED") == 3,
             "%d CHANGED readings" % rlog.count("next.json read, CHANGED"))

        # G10 - stop_requested in next.json stops the runner with exit 0 after that cycle
        sp10, bench10 = new_case(tmp, "stopreq")
        code10, out10 = run_runner("--dry-cmd", "%s %s %s %s stop" % (sys.executable, mut, sp10, bench10),
                                   "--cycles", "3", "--status", sp10, "--bench-dir", bench10, "--max-min", "2")
        gate("G10 next.json stop_requested stops the runner", code10 == 0 and len(cycle_lines(bench10)) == 1
             and "stop_requested" in out10, "exit %d, %d cycles" % (code10, len(cycle_lines(bench10))))

        # G6 - numbering continues from the runner log (same bench dir, fresh invocation)
        code6, _ = run_runner("--dry-cmd", "%s %s %s %s" % (sys.executable, mut, sp, bench),
                              "--cycles", "1", "--status", sp, "--bench-dir", bench, "--max-min", "2")
        lines6 = cycle_lines(bench)
        gate("G6 cycle numbering continues across invocations",
             code6 == 0 and len(lines6) == 4 and lines6[-1].startswith("CYCLE 4 |"),
             lines6[-1][:60] if lines6 else "(none)")

        # G3 + G4 - a session that changes nothing
        sp, bench = new_case(tmp, "stuck")
        code, out = run_runner("--dry-run", "--cycles", "5", "--status", sp, "--bench-dir", bench, "--max-min", "2")
        body = open(sp, encoding="utf-8").read()
        gate("G3 unchanged NEXT four times stops the loop (judgement ladder)",
             code == 3 and len(cycle_lines(bench)) == 4 and "ladder is exhausted" in out,
             "exit %d, %d cycles" % (code, len(cycle_lines(bench))))
        gate("G4 the stop notice is APPENDED to STATUS",
             "## RUNNER STOPPED" in body and body.startswith("# STATUS (self-test copy)")
             and "do the first thing." in body, "STATUS is %d bytes" % len(body))

        # G5 - a session that exits non-zero twice
        sp, bench = new_case(tmp, "failing")
        code, out = run_runner("--dry-cmd", "%s %s" % (sys.executable, failer),
                               "--cycles", "5", "--status", sp, "--bench-dir", bench, "--max-min", "2")
        gate("G5 two non-zero sessions stop the loop",
             code == 3 and "twice in a row" in out, "exit %d, %d cycles" % (code, len(cycle_lines(bench))))

        # G7 - the usage-limit parser
        now = time.time()
        w_epoch = cycle_runner.limit_wait_s('usage limit reached {"resetsAt": %d}' % int(now + 600), now)
        lt = time.localtime(now + 3600)
        w_clock = cycle_runner.limit_wait_s("Claude usage limit reached. Your limit will reset at %d:%02d"
                                            % (lt.tm_hour, lt.tm_min), now)
        w_bare = cycle_runner.limit_wait_s("Error: rate limit", now)
        w_none = cycle_runner.limit_wait_s("session finished normally", now)
        gate("G7 usage-limit waits parse (epoch / clock / bare / none)",
             abs(w_epoch - 720) < 5 and w_clock is not None and 0 < w_clock <= 8 * 3600
             and abs(w_bare - 2400) < 1 and w_none is None,
             "epoch %.0fs, clock %.0fs, bare %.0fs, none %s" % (w_epoch, w_clock or -1, w_bare, w_none))
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
