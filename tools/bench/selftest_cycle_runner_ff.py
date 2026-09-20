"""Self-test of cycle_runner's FIREFIGHTER trigger (2026-09-18). Dry: no claude session, no LabVIEW.
PREDICTION: with a stand-in session that writes a failing bgrun log for tools/recipes/build_fake_v0.py every
cycle, the runner logs FAILED-RECIPES for cycles 1-2, FIREFIGHTER cycle 3 (fable/low), FIREFIGHTER cycle 4
(fable/medium), then RUNNER STOP asking the user. With a stand-in that fails only in cycles 1-2, cycle 3 is the
low firefighter, it clears, no escalation and no STOP.
Usage: py tools/bench/selftest_cycle_runner_ff.py            (as the runner's --dry-cmd it is called with a mode)"""
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUNNER = os.path.join(ROOT, "tools", "cycle_runner.py")

if len(sys.argv) > 1 and sys.argv[1] in ("fail", "fail2", "samegate"):
    bench = os.environ["FF_BENCH"]
    cnt_path = os.path.join(bench, "count.txt")
    c = int(open(cnt_path).read() or 0) + 1 if os.path.exists(cnt_path) else 1
    open(cnt_path, "w").write(str(c))
    if sys.argv[1] == "samegate":
        # SAME MISTAKE under a new file name: v1, v2, v3 ... all die at gate B4 with different uids
        with open(os.path.join(bench, "build_fake_v%d_run1.log" % c), "w") as f:
            f.write("BGRUN START 2026-09-18 00:00:00 limit 1.0 min: py tools/recipes/build_fake_v%d.py\n"
                    "**FAIL B4 [OUT Tunnel] ExecState 0 at uid #%d\nBGRUN END rc=1 after 1s\n" % (c, 1000 + c))
    elif sys.argv[1] == "fail" or c <= 2:
        with open(os.path.join(bench, "build_fake_v0_run%d.log" % c), "w") as f:
            f.write("BGRUN START 2026-09-18 00:00:00 limit 1.0 min: py tools/recipes/build_fake_v0.py\nx\nBGRUN END rc=1 after 1s\n")
    # a DIAGNOSTIC that merely names a recipe as an argument must never count (peer finding 2026-09-18)
    with open(os.path.join(bench, "diag_names_recipe_run%d.log" % c), "w") as f:
        f.write("BGRUN START 2026-09-18 00:00:00 limit 1.0 min: py tools/bench/diag_x.py tools/recipes/build_other_v0.py\nx\nBGRUN END rc=1 after 1s\n")
    # a real session changes STATUS NEXT every cycle; without this, stop condition 3 (unchanged NEXT) fires first
    # (peer finding 2026-09-18: the first fix was necessary, not sufficient)
    with open(os.path.join(bench, "STATUS.md"), "a", encoding="utf-8") as f:
        f.write("cycle %d\n" % c)
    time.sleep(1.1)
    sys.exit(0)

ok = 0
for mode, cycles, want_ff, want_stop in (("fail", 4, True, True), ("fail2", 4, True, False),
                                         ("samegate", 4, True, True)):
    bench = tempfile.mkdtemp(prefix="ffbench_")
    status = os.path.join(bench, "STATUS.md")
    open(status, "w", encoding="utf-8").write("## NEXT\nx\n")
    env = dict(os.environ, FF_BENCH=bench)
    r = subprocess.run([sys.executable, RUNNER, "--cycles", str(cycles), "--bench-dir", bench, "--status", status,
                        # --dry-cmd is whitespace-split: relative path, cwd=ROOT (the project path has spaces)
                        "--dry-cmd", "py tools/bench/selftest_cycle_runner_ff.py %s" % mode],
                       capture_output=True, text=True, env=env, cwd=ROOT)
    log = open(os.path.join(bench, "cycle_runner.log"), encoding="utf-8").read()
    got_ff = "FIREFIGHTER |" in log and "fable/low" in log and "cycle 3 runs" in log
    got_stop = "user's judgement is requested" in log and "fable/medium" in log and "cycle 4 runs" in log
    if "build_other_v0" in log:
        print("FAIL: a diagnostic naming a recipe as an argument was counted as a failed recipe")
        got_ff = False
    if mode == "samegate" and "gate:fail b4" not in log:
        print("FAIL: the same-gate signature did not fire although the recipe name changed each cycle")
        got_ff = False
    res = got_ff == want_ff and got_stop == want_stop
    ok += res
    # "runner-exit", not "rc=": bgrun's inner-failure scan reads a literal `rc=3` in output as a failure
    print("%s mode=%s ff=%s stop=%s runner-exit %d" % ("PASS" if res else "FAIL", mode, got_ff, got_stop,
                                                        r.returncode))
    if not res:
        print(log)
print("%d/3 PASS" % ok)
sys.exit(0 if ok == 3 else 1)
