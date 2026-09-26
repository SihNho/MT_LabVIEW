r"""diag_c107a_regress.py - card 107-1: regression sweep after the stop_record offline_checker + launched_plan_runs newline
edits. Every self-test that imports stage_prerun (list copied from diag_c106e_regress.py) + the stop_record self-tests
(table, bgrun, eqform, supersession) + selftest_c106d_tools + stage_prerun --selftest-control-lint. Offline: none opens LabVIEW.
Prediction: each ends rc 0. Each runs as a subprocess (cap 400 s); rc + last RESULT line per test. Pattern: diag_c106e_regress.py.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_c107a_regress.log -- py -u tools/bench/diag_c107a_regress.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

TESTS = ["selftest_stoprecord_offline_c107.py", "selftest_stoprecord_table.py", "selftest_stoprecord_bgrun.py",
         "selftest_stoprecord_eqform.py", "selftest_stoprecord_supersession.py", "selftest_c106d_tools.py",
         "selftest_stage_prerun_c106e.py", "selftest_stage_prerun_c106c.py",
         "selftest_stage_prerun_graphload.py", "selftest_stage_prerun_c103.py", "selftest_stage_prerun_stageplan.py",
         "selftest_stage_prerun_headcmp_79-6.py", "selftest_launch_gate.py", "selftest_prerun_diag.py",
         "selftest_retry_cap.py", "selftest_guard_bash_jev.py", "selftest_c103d_hooks.py", "selftest_scratch_verify.py",
         "selftest_stagexec_gate.py", "selftest_c98_compile.py", "selftest_matbench.py", "selftest_protocol_wiring.py"]
ok = bad = 0
fails = []
for t in TESTS:
    try:
        r = subprocess.run([sys.executable, "-u", os.path.join(HERE, t)], cwd=ROOT, capture_output=True, text=True,
                           timeout=400, encoding="utf-8", errors="replace")
        out = (r.stdout or "") + (r.stderr or "")
        rc = r.returncode
    except subprocess.TimeoutExpired:
        out, rc = "TIMEOUT", -1
    res = [l for l in out.splitlines() if l.startswith("RESULT ")]
    fl = [l.strip() for l in out.splitlines() if "FAIL" in l and not l.startswith("RESULT")]
    print("TEST %-40s code %s  %s" % (t, rc, (res[-1] if res else " | ".join(out.strip().splitlines()[-3:]))[:220]), flush=True)
    for l in (fl[:6] if rc else []):
        print("     " + l[:220], flush=True)
    if rc == 0:
        ok += 1
    else:
        bad += 1
        fails.append(t)
r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "stage_prerun.py"), "--selftest-control-lint"], cwd=ROOT,
                   capture_output=True, text=True, timeout=120, encoding="utf-8", errors="replace")
print("TEST %-40s code %s  %s" % ("stage_prerun --selftest-control-lint", r.returncode, (r.stdout or "").strip().splitlines()[-1:]), flush=True)
ok, bad = ok + (r.returncode == 0), bad + (r.returncode != 0)
print(protocol.result_line(protocol.make_result(ok, bad, fails[0] if fails else (None if r.returncode == 0 else "control-lint"))))
