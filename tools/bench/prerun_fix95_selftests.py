"""prerun_fix95_selftests - run the existing stage_prerun self-tests and print their RESULT/last lines (card 95-1).
Offline only: every test here stubs COM (stage_prerun dry layer) or reads files; none reaches LabVIEW.
Usage: py -u tools/bench/prerun_fix95_selftests.py <tag>   (tag = before|after)"""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
tag = sys.argv[1] if len(sys.argv) > 1 else "run"
TESTS = [
    ["py", "-u", "tools/bench/selftest_stage_prerun_stageplan.py"],
    ["py", "-u", "tools/bench/selftest_stage_prerun_headcmp_79-6.py"],
    ["py", "-u", "tools/bench/selftest_launch_gate.py"],
    ["py", "-u", "tools/bench/selftest_prerun_diag.py"],
    ["py", "-u", "tools/stage_prerun.py", "--selftest-control-lint"],
]
if len(sys.argv) > 2:
    TESTS.append(["py", "-u", "tools/bench/selftest_stage_prerun_graphload.py"])
env = dict(os.environ, PRERUN_RECORDS=os.path.join(os.environ.get("TEMP", "."), "prerun_fix95_records_%s.jsonl" % tag))
summary = []
for cmd in TESTS:
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=600)
    lines = [l for l in (p.stdout + p.stderr).splitlines() if l.strip()]
    res = [l for l in lines if l.startswith("RESULT") or "PASS" in l[:12] and "/" in l or "self-test" in l.lower()]
    print("=== %s rc=%s" % (" ".join(cmd[2:]), p.returncode))
    for l in lines[-4:]:
        print("   ", l[:300])
    summary.append((" ".join(cmd[2:]), p.returncode, (lines[-1] if lines else "")[:200]))
print("SUMMARY %s" % tag)
for s in summary:
    print("  rc=%s  %s  | %s" % (s[1], s[0], s[2]))
bad = sum(1 for s in summary if s[1] != 0)
print('RESULT {"schema":"result-line/1","status":"%s","gates":{"pass":%d,"fail":%d},"first_fail":%s,"artefacts":[]}'
      % ("PASS" if not bad else "FAIL", len(summary) - bad, bad,
         "null" if not bad else '"%s"' % [s[0] for s in summary if s[1] != 0][0]))
