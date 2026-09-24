r"""selftest_bgrun_jev_exempt.py - the self-test demanded by docs/violation-decisions.md
`## device-failed - 2026-09-24 03:53` (bgrun's inner-failure scan exempts a Jev COMMAND, never a Jev log name).

    py tools/bgrun.py --material --max-min 8 --log tools/bench/selftest_bgrun_jev_exempt.log -- \
        py -u tools/bench/selftest_bgrun_jev_exempt.py [path/to/bgrun_candidate.py]

PRIOR ART: tools/bench/selftest_bgrun_fail_scan.py (same fixture-under-bgrun shape, reused), _final_line.py and
selftest_motor_fail_exit.py - all three are RE-RUN here against the same bgrun under test (env BGRUN_UNDER_TEST),
so a candidate copy is accepted only if every older bgrun self-test still passes on it. No LabVIEW.

PREDICTION CONTRACT
  J1 a command running `.../tools/bench/jev_fixture.py` that prints a gate-verdict FAIL line and `rc=1`, exit 0 -> rc 0
  J2 the same through `.../tools/jev_fixture.py`                                                              -> rc 0
  J3 a Jev command whose process exits 1                                                                      -> rc 1
  N1 a non-Jev command (`tools/recipes/build_fixture.py`) printing the same lines, exit 0                     -> rc 1
  N2 N1 written to a log NAMED `jev_survey.log` (scope is the command, not the filename)                      -> rc 1
  N3 a non-Jev command that merely has a Jev path as an ARGUMENT                                              -> rc 1
  R1..R3 selftest_bgrun_fail_scan / selftest_bgrun_final_line / selftest_motor_fail_exit on the same bgrun   -> rc 0
RE-CUT 2026-09-24 (session protocol v1 C6): the body scan is gone, so the fixture now also prints a failing
`RESULT {...}` line - the only thing bgrun still reads - and the override is recognised by `(RESULT:` on the END line.
The exemption itself is unchanged: a Jev command's quoted RESULT line is not its verdict.
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
BGRUN = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(PROJECT, "tools", "bgrun.py")

LINES = ["  PASS  S1 one row", "  " + "FAIL" + "  S2 quoted from another run's log", "probe ex" + "it=1",
         "RESULT " + '{"schema":"result-line/1","status":"FAIL","gates":{"pass":1,"fail":1},"first_fail":"S2",'
         '"artefacts":[]}']
passes, fails = [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""), flush=True)   # documented emitter (37(i))


def fixture(tmp, rel, code):
    path = os.path.join(tmp, *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("import sys\nfor L in %r:\n    print(L, flush=True)\nsys.exit(%d)\n" % (LINES, code))
    return path


def run(tmp, logname, argv):
    logp = os.path.join(tmp, logname)
    p = subprocess.run([sys.executable, BGRUN, "--max-min", "2", "--log", logp, "--"] + argv,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    txt = open(logp, encoding="utf-8", errors="replace").read() if os.path.exists(logp) else ""
    return p.returncode, "(RESULT:" in txt


def main():
    print("bgrun under test: %s" % BGRUN, flush=True)
    tmp = tempfile.mkdtemp(prefix="bgrun_jev_")
    py = sys.executable
    try:
        jb = fixture(tmp, "tools/bench/jev_fixture.py", 0)
        jt = fixture(tmp, "tools/jev_fixture.py", 0)
        jx = fixture(tmp, "tools/bench/jev_exit1.py", 1)
        nb = fixture(tmp, "tools/recipes/build_fixture.py", 0)
        rc, inner = run(tmp, "diag_j1.log", [py, "-u", jb])
        gate("J1 Jev bench command quoting FAIL ends rc 0", rc == 0 and not inner, "bgrun returned %d, override %s" % (rc, inner))
        rc, inner = run(tmp, "diag_j2.log", [py, "-u", jt])
        gate("J2 Jev tools command quoting FAIL ends rc 0", rc == 0 and not inner, "bgrun returned %d, override %s" % (rc, inner))
        rc, inner = run(tmp, "diag_j3.log", [py, "-u", jx])
        gate("J3 Jev command exiting 1 still ends non-zero", rc == 1, "bgrun returned %d" % rc)
        rc, inner = run(tmp, "diag_n1.log", [py, "-u", nb])
        gate("N1 non-Jev build printing FAIL still ends rc 1", rc == 1 and inner, "bgrun returned %d, override %s" % (rc, inner))
        rc, inner = run(tmp, "jev_survey.log", [py, "-u", nb])
        gate("N2 a Jev-NAMED log does not exempt a non-Jev command", rc == 1 and inner, "bgrun returned %d, override %s" % (rc, inner))
        rc, inner = run(tmp, "diag_n3.log", [py, "-u", nb, jt])
        gate("N3 a Jev path as an ARGUMENT does not exempt", rc == 1 and inner, "bgrun returned %d, override %s" % (rc, inner))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    env = dict(os.environ, BGRUN_UNDER_TEST=BGRUN)
    for tag, name in (("R1", "selftest_bgrun_fail_scan.py"), ("R2", "selftest_bgrun_final_line.py"),
                      ("R3", "selftest_motor_fail_exit.py")):
        p = subprocess.run([py, "-u", os.path.join(HERE, name)], env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=600)
        summ = [L.strip() for L in (p.stdout or "").splitlines() if "pass" in L.lower() and "===" in L]
        gate("%s existing %s passes on this bgrun" % (tag, name), p.returncode == 0,
             "exit %d; %s" % (p.returncode, (summ[-1] if summ else "")[:160]))
    print("\n=== selftest_bgrun_jev_exempt: %d pass, %d fail ===" % (len(passes), len(fails)), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
