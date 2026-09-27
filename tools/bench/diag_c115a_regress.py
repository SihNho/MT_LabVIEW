"""card 115-1 B2/B3 - the regression set for the stage_prerun X13 + stagesim-pin change, OFFLINE (no LabVIEW, no COM).

    py tools/bench/diag_c115a_regress.py

Existed first: diag_c114d_regress.py (the 14-child set, copied here with the two new children) and diag_c114d_replay.py
(called as a child with tag c115a; it writes only under tools/bench/sim/c114d_c115a/).
FAILURES ON RECORD BEFORE THIS CARD (PD229(c)): none - diag_c114d_regress_r2.log:17 is 14/0 after card 114-4; the earlier
E1 / U3 count-pin fails (diag_c114d_regress.log:5-6, also *_c112a.log / *_c101-4.log) were fixed by 114-4 R2.
Prediction contract:
  R1 all 16 self-test children RESULT PASS, fail 0 (the 14 of diag_c114d_regress_r2.log + selftest_stagesim_pin 10/0 +
     selftest_stage_prerun_c115a 8/0); counts: stagesim 75/0, l2a1_80 13/0, unflip_81 8/0 (E1/U3 stay ONE gate each).
  R2 NEGATIVE (B1 in situ + B2): selftest_stagesim_unflip_81 with SELFTEST_STAGESIM_PASS_FLOOR=999 -> RESULT FAIL, U3's
     stagesim row FAILS and the process exits rc 1 (it exited 0 on failure before: diag_c114d_regress.log:6).
  R3 replays keep their verdicts (= diag_c114d_replay_post2.log:3,7,8): l2b3 final/route PASS/6 new/lost [5174,5336,28392];
     l2b2b final/PASS/5/[]; l2b2a final/PASS/5/[].
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

PY = sys.executable
RUNS = [("stagesim", [PY, "-u", "tools/stagesim.py", "selftest"]),
        ("stagesim_k79", [PY, "-u", "tools/bench/selftest_stagesim_k79.py"]),
        ("stagesim_l2a1_80", [PY, "-u", "tools/bench/selftest_stagesim_l2a1_80.py"]),
        ("stagesim_unflip_81", [PY, "-u", "tools/bench/selftest_stagesim_unflip_81.py"]),
        ("stagesim_pin", [PY, "-u", "tools/bench/selftest_stagesim_pin.py"]),
        ("control_path_lint", [PY, "-u", "tools/stage_prerun.py", "--selftest-control-lint"])]
for n in ("stageplan", "c103", "c106c", "c106e", "c110g", "graphload", "headcmp_79-6", "c114", "c114d", "c115a"):
    RUNS.append(("stage_prerun_" + n, [PY, "-u", "tools/bench/selftest_stage_prerun_{0}.py".format(n)]))
WANT_REPLAY = {"tools/bench/plan_l2b3.json": (True, "PASS", 6, [5174, 5336, 28392]),
               "tools/bench/plan_l2b2b.json": (True, "PASS", 5, []), "tools/bench/plan_l2b2a.json": (True, "PASS", 5, [])}


def child(name, cmd, env=None):
    log = os.path.join(HERE, "selftest_{0}_c115a.log".format(name))
    with open(log, "w", encoding="utf-8") as f:
        rc = subprocess.call(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, timeout=900, env=env)
    res, lines = None, open(log, encoding="utf-8", errors="replace").read().splitlines()
    for line in lines:
        if line.startswith("RESULT "):
            try:
                res = json.loads(line[7:])
            except ValueError:
                res = None
    return rc, res, lines, os.path.relpath(log, ROOT)


def main():
    G = []

    def gate(l, ok, d=""):
        G.append((l, bool(ok)))
        print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", l, str(d)[:400]), flush=True)
    for name, cmd in RUNS:
        rc, res, _l, log = child(name, cmd)
        g = (res or {}).get("gates") or {}
        print("SELFTEST {0}: rc {1} pass {2} fail {3} first_fail {4} ({5})".format(
            name, rc, g.get("pass"), g.get("fail"), (res or {}).get("first_fail"), log), flush=True)
        gate("R1 {0} RESULT PASS fail 0 rc 0".format(name), bool(res) and res.get("status") == "PASS" and g.get("fail") == 0
             and rc == 0, (rc, g))
    env = dict(os.environ, SELFTEST_STAGESIM_PASS_FLOOR="999")
    rc, res, lines, log = child("stagesim_unflip_81_neg", [PY, "-u", "tools/bench/selftest_stagesim_unflip_81.py"], env)
    u3 = [l for l in lines if "U3 stagesim selftest" in l]
    print("NEGATIVE unflip_81 floor 999: rc {0} RESULT {1} U3 {2} ({3})".format(rc, res, u3[:1], log), flush=True)
    gate("R2 negative: floor 999 -> U3 stagesim row FAIL, RESULT FAIL, rc 1", rc == 1 and bool(res) and
         res.get("status") == "FAIL" and u3 and u3[0].lstrip().startswith("FAIL"), (rc, (res or {}).get("gates"), u3[:1]))
    rlog = os.path.join(HERE, "diag_c115a_replay.log")
    with open(rlog, "w", encoding="utf-8") as f:
        rrc = subprocess.call([PY, "-u", "tools/bench/diag_c114d_replay.py", "c115a"], cwd=ROOT, stdout=f,
                              stderr=subprocess.STDOUT, timeout=900)
    got = {}
    for line in open(rlog, encoding="utf-8", errors="replace"):
        if line.startswith("REPLAY "):
            p, _s, js = line[7:].partition(": ")
            d = json.loads(js)
            got[p] = (d.get("final"), d.get("route_check"), d.get("n_new"), d.get("lost"))
    for p, want in WANT_REPLAY.items():
        gate("R3 replay {0} keeps (final, route, n_new, lost) = {1}".format(p, want), got.get(p) == want and rrc == 0,
             (got.get(p), rrc))
    n = sum(1 for _l, ok in G if ok)
    first = next((l for l, ok in G if not ok), None)
    print("=== GATES: {0} pass / {1} fail".format(n, len(G) - n))
    print(protocol.result_line(protocol.make_result(n, len(G) - n, first)))
    return 0 if first is None else 1


if __name__ == "__main__":
    sys.exit(main())
