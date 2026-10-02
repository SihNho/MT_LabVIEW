r"""selftest_c134_1_a4 - card 134-1 (a4, PD252(a)): the EXISTING dry/prerun self-tests and c125_1_offline_measure.py after the
dry-rule edit of tools/stage_prerun.py and the census edit of tools/stagekit.py. OFFLINE (each child is an offline self-test).
PREDICTION: every child exits 0 and its last RESULT line says PASS.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/selftest_c134_1_a4.log -- py -u tools/bench/selftest_c134_1_a4.py"""
import json, os, subprocess, sys, time                                                       # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                          # noqa: E402
TESTS = ["selftest_dry_c130_5.py", "selftest_stage_prerun_c128.py", "selftest_stage_prerun_c128b.py", "selftest_c133_6_fr.py",
         "selftest_stage_prerun_c103.py", "selftest_stage_prerun_c106c.py", "selftest_stage_prerun_c106e.py",
         "selftest_stage_prerun_c114d.py", "selftest_stage_prerun_stageplan.py", "selftest_stage_prerun_graphload.py",
         "selftest_prerun_diag.py", "c125_1_offline_measure.py"]
res, fails = [], []
for t in TESTS:
    p = os.path.join(HERE, t)
    if not os.path.isfile(p):
        print("  SKIP  {0} (missing)".format(t), flush=True)
        continue
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, "-u", p], cwd=ROOT, capture_output=True, text=True, timeout=600)
        out, rc = r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        out, rc = "TIMEOUT", -9
    rl = [ln for ln in out.splitlines() if ln.startswith("RESULT ")]
    st = json.loads(rl[-1][7:]).get("status") if rl else None
    ok = rc == 0 and st in ("PASS", None)
    res.append(ok)
    ff = [ln for ln in out.splitlines() if "FAIL" in ln][:3]
    print("  {0}  {1} rc={2} result={3} {4:.0f}s {5}".format("PASS" if ok else "FAIL", t, rc, rl[-1][7:180] if rl else None,
                                                          time.time() - t0, "" if ok else ff), flush=True)
    if not ok:
        fails.append(t)
print(P.result_line(P.make_result(res.count(True), res.count(False), fails[0] if fails else None)), flush=True)
sys.exit(1 if fails else 0)
