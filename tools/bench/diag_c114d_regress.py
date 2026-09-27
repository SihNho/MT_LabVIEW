"""card 114-3 C5 - the regression set for the stagesim / stage_prerun change, OFFLINE (no LabVIEW, no COM).

    py tools/bench/diag_c114d_regress.py

Runs every self-test the two files carry (the same set card 114-1 reported: stagesim selftest + its 3 bench self-tests;
stage_prerun --selftest-control-lint + its 8 bench self-tests) plus the new selftest_stage_prerun_c114d.py, each as a
child with its own log tools/bench/selftest_<name>_c114d.log, and reads ONLY each child's RESULT line (C6).
Prediction contract: every child RESULT status PASS, fail 0; a child with no RESULT line counts as a failure.
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
        ("control_path_lint", [PY, "-u", "tools/stage_prerun.py", "--selftest-control-lint"])]
for n in ("stageplan", "c103", "c106c", "c106e", "c110g", "graphload", "headcmp_79-6", "c114", "c114d"):
    RUNS.append(("stage_prerun_" + n, [PY, "-u", "tools/bench/selftest_stage_prerun_{0}.py".format(n)]))


def main():
    npass, nfail, first, rows = 0, 0, None, []
    for name, cmd in RUNS:
        log = os.path.join(HERE, "selftest_{0}_c114d.log".format(name))
        with open(log, "w", encoding="utf-8") as f:
            rc = subprocess.call(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, timeout=900)
        res = None
        for line in open(log, encoding="utf-8", errors="replace"):
            if line.startswith("RESULT "):
                try:
                    res = json.loads(line[7:])
                except ValueError:
                    res = None
        ok = bool(res) and res.get("status") == "PASS" and (res.get("gates") or {}).get("fail") == 0
        g = (res or {}).get("gates") or {}
        rows.append((name, rc, g.get("pass"), g.get("fail"), (res or {}).get("first_fail")))
        print("SELFTEST {0}: rc {1} pass {2} fail {3} first_fail {4} ({5})".format(
            name, rc, g.get("pass"), g.get("fail"), (res or {}).get("first_fail"), os.path.relpath(log, ROOT)), flush=True)
        if ok:
            npass += 1
        else:
            nfail += 1
            first = first or name
    print(protocol.result_line(protocol.make_result(npass, nfail, first)))
    return 0 if not nfail else 1


if __name__ == "__main__":
    sys.exit(main())
