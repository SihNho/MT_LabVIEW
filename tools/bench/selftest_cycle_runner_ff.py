"""Self-test of cycle_runner's FIREFIGHTER trigger (2026-09-18). Dry: no claude session, no LabVIEW.
PREDICTION (user model table 2026-09-27, card chat-N4: the firefighter is ONE Opus 5.5 max cycle, then STOP): with a
stand-in session that writes a failing bgrun log for tools/recipes/build_fake_v0.py every cycle, the runner logs
FAILED-RECIPES for cycles 1-2, FIREFIGHTER cycle 3 (claude-opus-5-5/max, rung 1 of 1), then RUNNER STOP asking the
user after cycle 3 - no cycle 4. With a stand-in that fails only in cycles 1-2, cycle 3 is the firefighter, it
clears, no STOP and cycle 4 runs as a normal cycle.
Usage: py tools/bench/selftest_cycle_runner_ff.py            (as the runner's --dry-cmd it is called with a mode)"""
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUNNER = os.path.join(ROOT, "tools", "cycle_runner.py")

if len(sys.argv) > 1 and sys.argv[1] in ("fail", "fail2", "samegate", "newestpass", "otherpass"):
    bench = os.environ["FF_BENCH"]
    cnt_path = os.path.join(bench, "count.txt")
    c = int(open(cnt_path).read() or 0) + 1 if os.path.exists(cnt_path) else 1
    open(cnt_path, "w").write(str(c))
    if sys.argv[1] in ("newestpass", "otherpass"):
        # retrospective-cycle88 device-failed: the recipe fails every cycle, then a NEWER run is written.
        # newestpass: the newer run of the SAME recipe (same command identity, extra --graph arg) PASSES -> no
        # firefighter, ever. otherpass: the newer passing run is a DIFFERENT recipe -> the failure stands, ff fires.
        with open(os.path.join(bench, "build_fake_v0_run%d.log" % c), "w") as f:
            f.write("BGRUN START 2026-09-18 00:00:00 limit 1.0 min: py tools/recipes/build_fake_v0.py\n"
                    "**FAIL B4 [OUT Tunnel] ExecState 0 at uid #77\nBGRUN END rc=1 after 1s\n")
        time.sleep(0.05)
        later = "build_fake_v0.py --graph g.json" if sys.argv[1] == "newestpass" else "build_other_v0.py"
        with open(os.path.join(bench, "later_pass_run%d.log" % c), "w") as f:
            f.write("BGRUN START 2026-09-18 00:00:01 limit 1.0 min: py -u tools/recipes/%s\n"
                    "RESULT {\"schema\":\"result-line/1\",\"status\":\"PASS\",\"gates\":{\"pass\":8,\"fail\":0},"
                    "\"first_fail\":null,\"artefacts\":[]}\nBGRUN END rc=0 after 1s\n" % later)
    elif sys.argv[1] == "samegate":
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
    # session protocol v1 (C7, 2026-09-24): the runner's "NEXT moved" test reads <bench>/next.json, not the prose
    import json
    with open(os.path.join(bench, "next.json"), "w", encoding="utf-8") as f:
        json.dump({"schema": "next/1", "cycle": c, "act": "ff self-test cycle %d" % c, "task_kind": "build",
                   "stop_requested": False, "advances": ["M3"]}, f)
    time.sleep(1.1)
    sys.exit(0)

ok = 0
MODES = (("fail", 4, True, True), ("fail2", 4, True, False), ("samegate", 4, True, True),
         # 2026-09-26 (retrospective-cycle88 device-failed): newest run of the same recipe PASSED -> no firefighter;
         # a newer passing run of ANOTHER recipe clears nothing -> the ladder runs to the STOP as in `fail`
         ("newestpass", 4, False, False), ("otherpass", 4, True, True))
for mode, cycles, want_ff, want_stop in MODES:
    bench = tempfile.mkdtemp(prefix="ffbench_")
    status = os.path.join(bench, "STATUS.md")
    open(status, "w", encoding="utf-8").write("## NEXT\nx\n")
    env = dict(os.environ, FF_BENCH=bench)
    r = subprocess.run([sys.executable, RUNNER, "--cycles", str(cycles), "--bench-dir", bench, "--status", status,
                        # --dry-cmd is whitespace-split: relative path, cwd=ROOT (the project path has spaces)
                        "--dry-cmd", "py tools/bench/selftest_cycle_runner_ff.py %s" % mode],
                       capture_output=True, text=True, env=env, cwd=ROOT)
    log = open(os.path.join(bench, "cycle_runner.log"), encoding="utf-8").read()
    got_ff = "FIREFIGHTER |" in log and "cycle 3 runs as claude-opus-5-5/max (rung 1 of 1)" in log
    got_stop = ("user's judgement is requested" in log and "cycle 4 runs" not in log
                and "CYCLE-CARD | " in log and "cycle 4 | wrote" not in log)
    if "fable" in log:
        print("FAIL: a fable model appeared in a firefighter self-test (the table has no fable rung for it)")
        got_ff = False
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
    if mode == "newestpass" and "FAILED-RECIPES" in log and "build_fake" in log:
        print("FAIL: newestpass - a superseded failure was still listed under FAILED-RECIPES")
        ok -= res
        res = False
    if not res:
        print(log)
N = len(MODES)
print("%d/%d PASS" % (ok, N))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
print(protocol.result_line(protocol.make_result(ok, N - ok, None if ok == N else "%d/%d modes" % (ok, N))))
sys.exit(0 if ok == N else 1)
