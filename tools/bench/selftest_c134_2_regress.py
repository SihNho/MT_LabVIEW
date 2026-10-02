r"""selftest_c134_2_regress - card 134-2 steps 1-3: the EXISTING dry/prerun/launch/stagesim self-tests and c125_1_offline_measure.py
after the gate-B edit of tools/stagesim.py (fs_border_gate, simulate) and the dry_rule edit of tools/stage_prerun.py (check_launch,
write_record). OFFLINE (each child is an offline self-test). Copy of selftest_c134_1_a4.py's runner + c134_1_dry/_fsmap/c134_2_gates,
chat_p3, prerun_diag (dry records), stagesim selftest. No guard_bash.py.new is staged, so selftest_launch_gate installs nothing.
PREDICTION: every child exits 0 and its last RESULT line says PASS.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/selftest_c134_2_regress.log -- py -u tools/bench/selftest_c134_2_regress.py"""
import json, os, subprocess, sys, time                                                       # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                          # noqa: E402
TESTS = [["tools/bench/selftest_c134_2_gates.py"], ["tools/bench/selftest_c134_1_dry.py"], ["tools/bench/selftest_c134_1_fsmap.py"],
         ["tools/bench/selftest_dry_c130_5.py"], ["tools/bench/selftest_stage_prerun_stageplan.py"],
         ["tools/bench/selftest_chat_p3.py"], ["tools/bench/selftest_prerun_diag.py"], ["tools/stagesim.py", "selftest"],
         ["tools/bench/selftest_stage_prerun_c128.py"], ["tools/bench/selftest_stage_prerun_c128b.py"], ["tools/bench/selftest_c133_6_fr.py"],
         ["tools/bench/selftest_stage_prerun_c103.py"], ["tools/bench/selftest_stage_prerun_c106c.py"],
         ["tools/bench/selftest_stage_prerun_c106e.py"], ["tools/bench/selftest_stage_prerun_c114d.py"],
         ["tools/bench/selftest_stage_prerun_graphload.py"], ["tools/bench/c125_1_offline_measure.py"]]
if os.path.exists(os.path.join(ROOT, "tools", "hooks", "guard_bash.py.new")):
    print("  STOP  a guard_bash.py.new is staged; selftest_launch_gate (via stageplan) would install it", flush=True)
    sys.exit(2)
res, fails = [], []
for t in TESTS:
    p = os.path.join(ROOT, t[0])
    if not os.path.isfile(p):
        print("  SKIP  {0} (missing)".format(t), flush=True)
        continue
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, "-u", p] + t[1:], cwd=ROOT, capture_output=True, text=True, timeout=600)
        out, rc = r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        out, rc = "TIMEOUT", -9
    rl = [ln for ln in out.splitlines() if ln.startswith("RESULT ")]
    st = json.loads(rl[-1][7:]).get("status") if rl else None
    ok = rc == 0 and st == "PASS"
    res.append(ok)
    ff = [ln[:300] for ln in out.splitlines() if "FAIL" in ln or "Error" in ln][:4]
    print("  {0}  {1} rc={2} result={3} {4:.0f}s {5}".format("PASS" if ok else "FAIL", " ".join(t), rc, rl[-1][7:180] if rl else None,
                                                          time.time() - t0, "" if ok else ff), flush=True)
    if not ok:
        fails.append(" ".join(t))
print(P.result_line(P.make_result(res.count(True), res.count(False), fails[0] if fails else None)), flush=True)
sys.exit(1 if fails else 0)
