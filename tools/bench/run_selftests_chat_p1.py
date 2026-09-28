r"""run_selftests_chat_p1.py - card chat-P1: every self-test the acceleration items 1-4 can affect, in ONE bgrun.
No LabVIEW, no network (TYPESAFE_API_KEY removed), no motor. Usage: py -u run_selftests_chat_p1.py <tag>
(each test's output goes to tools/bench/selftest_<name>_p1<tag>.log).

WHAT EXISTED: run_selftests_chat_b2.py (same tally shape, a different test list); each self-test below unchanged in
purpose; this file only runs them and tallies. selftest_chat_p1 is the new-case file of this card (absent -> skipped
in the 'before' run).

PREDICTION CONTRACT: every self-test listed exits 0.
"""
import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P  # noqa: E402

TAG = sys.argv[1] if len(sys.argv) > 1 else "run"
FIXED = ["selftest_guard_session", "selftest_protocol", "selftest_protocol_wiring", "selftest_guard_cycle_fixed",
         "selftest_guard_cycle_offline", "selftest_guard_cycle_rerun", "selftest_c103d_hooks", "selftest_launch_gate",
         "selftest_c110_launchgate", "selftest_next_gate_jev", "selftest_cycle_runner", "selftest_cycle_runner_ladder",
         "selftest_audit_c7", "selftest_chat_p1"]
GLOBS = ["selftest_guard_peer_*.py", "selftest_stage_prerun_*.py"]
ENV = {k: v for k, v in os.environ.items() if k != "TYPESAFE_API_KEY"}
PASS, FAIL = [], []


def gate(label, ok, detail=""):
    (PASS if ok else FAIL).append(label)
    print("  %s  %-44s %s" % ("PASS" if ok else "FAIL", label, str(detail)[:160]), flush=True)


def tests():
    out = list(FIXED)
    for g in GLOBS:
        out += sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(HERE, g)))
    return out


def main():
    for t in tests():
        path = os.path.join(HERE, t + ".py")
        if not os.path.isfile(path):
            print("  SKIP  %-44s (file absent)" % t, flush=True)
            continue
        try:
            r = subprocess.run([sys.executable, "-u", path], cwd=ROOT, env=ENV, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=900)
            rc, out = r.returncode, (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired as e:
            rc, out = -9, "TIMEOUT %s" % e
        with open(os.path.join(HERE, "%s_p1%s.log" % (t, TAG)), "w", encoding="utf-8") as f:
            f.write(out)
        tail = [ln for ln in out.strip().splitlines() if ln.strip()][-1:] or [""]
        gate(t, rc == 0, "exit %d | %s" % (rc, tail[0]))
    print("\n=== GATES: %d pass / %d fail%s" % (len(PASS), len(FAIL),
                                                ("; failing: " + ", ".join(FAIL)) if FAIL else ""), flush=True)
    print(P.result_line(P.make_result(len(PASS), len(FAIL), FAIL[0] if FAIL else None)), flush=True)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
