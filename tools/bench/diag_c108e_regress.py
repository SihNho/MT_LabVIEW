"""diag_c108e_regress - card 108-5: the existing self-tests that touch what 108-5 changed (cycle_runner gates_due,
stage_prerun dry UNROUTABLE -> FAIL, protocol result-line SKIP + result_failed, cycle/1 gates_due, drive_legguard /
diag_c104_abba SKIP verdict) run once each, sequentially, offline (none opens LabVIEW; card 108-4 may hold one in parallel,
so LabVIEW presence is logged as a FACT, not gated).
PREDICTION: every listed self-test exits rc 0 with a PASS RESULT line (or, with no RESULT line, rc 0). A failing one is
reported by name with its first_fail; nothing is re-run.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P  # noqa: E402

TESTS = ["selftest_protocol", "selftest_protocol_wiring", "selftest_requires", "selftest_cycle_runner",
         "selftest_cycle_runner_ladder", "selftest_cycle_runner_ff", "selftest_heartbeat", "selftest_leg_guard",
         "selftest_stage_prerun_stageplan", "selftest_stage_prerun_c103", "selftest_stage_prerun_c106c",
         "selftest_stage_prerun_c106e", "selftest_stage_prerun_graphload", "selftest_stage_prerun_headcmp_79-6",
         "selftest_launch_gate", "selftest_prerun_diag", "selftest_stagexec_gate", "selftest_guard_peer_budget",
         "selftest_guard_peer_failre", "selftest_guard_peer_jev", "selftest_guard_peer_ladder",
         "selftest_guard_peer_samerow", "selftest_bgrun_fail_scan",
         "selftest_bgrun_final_line"]
if len(sys.argv) > 1:
    TESTS = sys.argv[1:]


def lv():
    return "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()


res = []
lv0 = lv()
print("LabVIEW running before: %s" % lv0, flush=True)
for t in TESTS:
    p = os.path.join(HERE, t + ".py")
    if not os.path.isfile(p):
        print("  MISSING %s" % t, flush=True)
        res.append((t, False, "missing"))
        continue
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, "-u", p], cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=1200, env=dict(os.environ, MATERIAL="1"))
        rc, out = r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        rc, out = "TIMEOUT", ""
    d = P.parse_result_line(out)
    ok = rc == 0 and (d is None or not P.result_failed(d))
    info = "rc %s %.0fs %s" % (rc, time.time() - t0, (d or {}).get("gates") if d else "no RESULT line")
    if not ok:
        info += " first_fail=%s | tail: %s" % ((d or {}).get("first_fail"), " / ".join(out.strip().splitlines()[-6:])[:900])
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", t, info), flush=True)
    res.append((t, ok, info))
lv1 = lv()
print("LabVIEW running after: %s" % lv1, flush=True)
# NOT a gate: card 108-4 builds in LabVIEW in parallel, so a running LabVIEW here is not evidence about these tests.
print("FACT LabVIEW running before=%s after=%s (card 108-4 runs LabVIEW in parallel)" % (lv0, lv1), flush=True)
bad = [t for t, ok, _ in res if not ok]
print("=== %d pass / %d fail: %s" % (len(res) - len(bad), len(bad), bad), flush=True)
print(P.result_line(P.make_result(len(res) - len(bad), len(bad), bad[0] if bad else None)), flush=True)
sys.exit(1 if bad else 0)
