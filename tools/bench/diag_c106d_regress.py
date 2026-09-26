r"""diag_c106d_regress.py - card 106-4: regression sweep of every self-test that imports guard_bash or audit_cycle
(grep of tools/bench/selftest_*.py), after the 106-4 edits. Prediction: each ends rc 0 / RESULT PASS, or, where it
fails, the failing gate is unrelated to stop_gate / drop_jev_ledgers / a1_bypass / a3_unreviewed (checked by hand).
Each runs as a subprocess with a 90 s cap; prints rc + the last RESULT line (or the last 3 lines) per test.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

TESTS = ["selftest_bgrun_reap.py", "selftest_guard_session.py", "selftest_prerun_diag.py", "selftest_audit_c7.py",
         "selftest_protocol_wiring.py", "selftest_stage_prerun_headcmp_79-6.py", "selftest_launch_gate.py",
         "selftest_retry_cap.py", "selftest_next_gate_jev.py", "selftest_motor_fail_exit.py",
         "selftest_motor_gate2.py", "selftest_audit_c4c_split.py", "selftest_audit_cost_window.py"]
ok = bad = 0
fails = []
for t in TESTS:
    try:
        r = subprocess.run([sys.executable, "-u", os.path.join(HERE, t)], cwd=ROOT, capture_output=True, text=True,
                           timeout=90, encoding="utf-8", errors="replace")
        out = (r.stdout or "") + (r.stderr or "")
        rc = r.returncode
    except subprocess.TimeoutExpired:
        out, rc = "TIMEOUT", -1
    res = [l for l in out.splitlines() if l.startswith("RESULT ")]
    fl = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")]
    print("TEST %-40s code %s  %s" % (t, rc, (res[-1] if res else " | ".join(out.strip().splitlines()[-3:]))[:220]))
    for l in fl[:6]:
        print("     " + l[:220])
    if rc == 0:
        ok += 1
    else:
        bad += 1
        fails.append(t)
print(protocol.result_line(protocol.make_result(ok, bad, fails[0] if fails else None)))
