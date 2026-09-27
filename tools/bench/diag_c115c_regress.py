"""card 115-3 F2 - the stage_prerun regression set run BEFORE and AFTER the X5 narrowing, OFFLINE (no LabVIEW, no COM).

    py tools/bench/diag_c115c_regress.py <tag>        (tag = before | after)

Existed first: diag_c115a_regress.py (16 children + negative + replay); this is its stage_prerun subset only (the X5
edit touches tools/stage_prerun.py alone): control_path_lint + the 10 selftest_stage_prerun_* children, plus the new
selftest_stage_prerun_c115c.py when it exists. Child logs: tools/bench/selftest_<name>_c115c_<tag>.log.
Prediction contract: tag before -> the failures on record before F1 are whatever this prints (named per child);
tag after -> every child that PASSED before still PASSES (0 new failures) and selftest_stage_prerun_c115c PASSES.
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
TAG = sys.argv[1] if len(sys.argv) > 1 else "before"
RUNS = [("control_path_lint", [PY, "-u", "tools/stage_prerun.py", "--selftest-control-lint"])]
for n in ("stageplan", "c103", "c106c", "c106e", "c110g", "graphload", "headcmp_79-6", "c114", "c114d", "c115a", "c115c"):
    if os.path.exists(os.path.join(HERE, "selftest_stage_prerun_{0}.py".format(n))):
        RUNS.append(("stage_prerun_" + n, [PY, "-u", "tools/bench/selftest_stage_prerun_{0}.py".format(n)]))


def main():
    G = []
    for name, cmd in RUNS:
        log = os.path.join(HERE, "selftest_{0}_c115c_{1}.log".format(name, TAG))
        with open(log, "w", encoding="utf-8") as f:
            rc = subprocess.call(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, timeout=900)
        res = None
        for line in open(log, encoding="utf-8", errors="replace"):
            if line.startswith("RESULT "):
                try:
                    res = json.loads(line[7:])
                except ValueError:
                    res = None
        g = (res or {}).get("gates") or {}
        ok = bool(res) and res.get("status") == "PASS" and g.get("fail") == 0 and rc == 0
        G.append((name, ok))
        print("  {0}  SELFTEST {1}: rc {2} pass {3} fail {4} first_fail {5} ({6})".format(
            "PASS" if ok else "FAIL", name, rc, g.get("pass"), g.get("fail"), (res or {}).get("first_fail"),
            os.path.relpath(log, ROOT)), flush=True)
    n = sum(1 for _l, ok in G if ok)
    first = next((l for l, ok in G if not ok), None)
    print("=== GATES ({0}): {1} pass / {2} fail; failing: {3}".format(TAG, n, len(G) - n, [l for l, ok in G if not ok]))
    print(protocol.result_line(protocol.make_result(n, len(G) - n, first)))
    return 0 if first is None else 1


if __name__ == "__main__":
    sys.exit(main())
