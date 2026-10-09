# ---
# labview: none
# hardware: none
# ---
"""card 155-a1-1: run the existing stage-tool self-tests (all offline) and print each one's RESULT/summary line.

  py tools/bench/prep_c155_a1_1_suite.py <tag>     (tag = before | after)

Prediction contract: the 'after' run prints the same pass/fail counts per self-test as the 'before' run (taken on the
unedited stagexec 1bab9cf9 / stagesim 78b8d5a1). Each child's full output goes to tools/bench/prep_c155_a1_1_suite_<tag>_<n>.out."""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

TESTS = [("stagexec", ["tools/stagexec.py", "selftest"]), ("stagesim", ["tools/stagesim.py", "selftest"]),
         ("c120_caseshape", ["tools/bench/selftest_c120_caseshape.py", "tools/bench/graph_qrt_pool_20260928.json"]),
         ("case_frame_c124", ["tools/bench/selftest_case_frame_c124.py"]),
         ("stagexec_gate", ["tools/bench/selftest_stagexec_gate.py"]),
         ("stagesim_tunnel_naming", ["tools/bench/selftest_stagesim_tunnel_naming.py"]),
         ("fs_c126", ["tools/bench/selftest_fs_c126.py"]), ("t6_regress", ["tools/bench/selftest_t6_regress.py"])]
tag = sys.argv[1] if len(sys.argv) > 1 else "before"
only = sys.argv[2:]
gates = {"pass": 0, "fail": 0}
for name, cmd in TESTS:
    if only and name not in only:
        continue
    p = subprocess.run([sys.executable, "-u"] + cmd, cwd=ROOT, capture_output=True, text=True, timeout=900,
                       encoding="utf-8", errors="replace")
    out = p.stdout + p.stderr
    with open(os.path.join(HERE, "prep_c155_a1_1_suite_{0}_{1}.out".format(tag, name)), "w", encoding="utf-8") as f:
        f.write(out)
    npass = len(re.findall(r"^\s*(?:GATE )?PASS\b", out, re.M))
    nfail = len(re.findall(r"^\s*(?:GATE )?FAIL\b", out, re.M))
    res = [l for l in out.splitlines() if l.startswith("RESULT") or re.search(r"\b\d+ */ *\d+\b.*(pass|PASS)|SELFTEST|selftest", l)]
    print("SUITE {0} rc={1} PASS-lines={2} FAIL-lines={3} | {4}".format(name, p.returncode, npass, nfail,
                                                                     " || ".join(x[:220] for x in res[-3:])))
    gates["pass" if p.returncode == 0 else "fail"] += 1
print(protocol.result_line({"status": "PASS" if not gates["fail"] else "FAIL", "gates": gates,
                            "first_fail": None if not gates["fail"] else "a self-test rc != 0", "artefacts": []}))
