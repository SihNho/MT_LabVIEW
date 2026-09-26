r"""diag_c106e_regress.py - card 106-5: regression sweep of every self-test that imports stage_prerun (grep of
tools/bench/selftest_*.py) plus selftest_protocol_wiring (edited here), after the 106-5 edits (X10 690 + WARN,
find_graph plan base graph, launched_py newline split). Offline: none of them opens LabVIEW.
Prediction: each ends rc 0 / RESULT PASS. Each runs as a subprocess (cap 400 s); rc + last RESULT line per test.
Pattern copied from tools/bench/diag_c106d_regress.py.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c106e_regress.log -- py -u tools/bench/diag_c106e_regress.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

TESTS = ["selftest_stage_prerun_graphload.py", "selftest_stage_prerun_c103.py", "selftest_stage_prerun_stageplan.py",
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
    fl = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")]
    print("TEST %-40s code %s  %s" % (t, rc, (res[-1] if res else " | ".join(out.strip().splitlines()[-3:]))[:220]), flush=True)
    for l in fl[:6]:
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
