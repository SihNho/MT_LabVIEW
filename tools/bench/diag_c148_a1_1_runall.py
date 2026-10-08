# ---
# labview: none
# hardware: none
# ---
r"""diag_c148_a1_1_runall - card 148-a1-1 step 4: re-run every existing self-test of each file the card edited
(tools/stage_prerun.py, tools/hooks/guard_cycle.py, tools/hooks/guard_write.py, tools/hooks/guard_assign.py) and print
rc + the GATES/pass-fail count line per test. Usage: py -u diag_c148_a1_1_runall.py <tag>.

WHAT EXISTED: no batch runner of self-tests by imported module (grep -l "runall\|run_selftests" tools/bench/*.py: none
for this purpose); each self-test is run as its own plain `py -u` subprocess, exactly as bgrun would run it.

SCOPE: a self-test is RUN only when its own scope header is `labview: none` + `hardware: none` (tools/scope_header.read);
any other header is listed SKIP-HEADER and not run (this card is labview none - fp-55, PD357(d)). No LabVIEW, no COM.
PREDICTION: every RUN test ends rc 0 in the `after` run; a test that is non-zero in `after` is printed FAIL with its
count line; the summary line `RUNALL <tag>: run N, rc0 A, nonzero B, skipped S` closes the log.
"""
import glob
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import scope_header as SH  # noqa: E402
import protocol as P  # noqa: E402

EDITED = re.compile(r"\b(stage_prerun|guard_cycle|guard_write|guard_assign)\b")
COUNT_RE = re.compile(r"(=== .*(?:pass|PASS).*|.*\b\d+\s*(?:pass|PASS)\b.*\b\d+\s*(?:fail|FAIL)\b.*|RESULT \{.*)$")
SELF = os.path.basename(__file__)


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "run"
    tests = []
    for p in sorted(glob.glob(os.path.join(HERE, "selftest_*.py"))):
        try:
            src = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if EDITED.search(src):
            tests.append(p)
    n_run = n_ok = n_bad = n_skip = 0
    bad = []
    for p in tests:
        name = os.path.basename(p)
        h, err = SH.read(p)
        if err or not h or h.get("labview") != "none" or h.get("hardware") != "none":
            n_skip += 1
            print("SKIP-HEADER %s (%s)" % (name, err or "labview %s hardware %s" % (h.get("labview"), h.get("hardware"))),
                  flush=True)
            continue
        t0 = time.time()
        env = dict(os.environ)
        env.pop("CARD_ID", None)
        try:
            cp = subprocess.run([sys.executable, "-u", p], cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=240, env=env)
            rc, out = cp.returncode, (cp.stdout or "") + (cp.stderr or "")
        except subprocess.TimeoutExpired:
            rc, out = "TIMEOUT", ""
        n_run += 1
        lines = [ln.strip() for ln in out.splitlines() if COUNT_RE.match(ln.strip()) and not ln.strip().startswith("RESULT")]
        cnt = lines[-1][:160] if lines else "(no count line)"
        if rc == 0:
            n_ok += 1
            print("RC0  %-52s %5.1fs  %s" % (name, time.time() - t0, cnt), flush=True)
        else:
            n_bad += 1
            bad.append(name)
            fl = [ln.strip() for ln in out.splitlines() if re.match(r"^\s*(?:->\s*)?FAIL\b", ln)][:4]
            print("NONZERO rc=%s %-45s %5.1fs  %s  | %s" % (rc, name, time.time() - t0, cnt,
                                                            " || ".join(x[:140] for x in fl)), flush=True)
    print("RUNALL %s: run %d, rc0 %d, nonzero %d, skipped %d%s" % (tag, n_run, n_ok, n_bad, n_skip,
                                                                    ("; nonzero: " + ", ".join(bad)) if bad else ""), flush=True)
    # PREDICTION per tag: `after` -> nonzero == 0. `before` (the four edited files at their HEAD = card-input bytes) ->
    # exactly the tests carrying this card's new cases are nonzero (they must fail before the fix), every other one rc 0.
    new_cases = {"selftest_c148_prerun_fp.py", "selftest_c148_guard_fp.py", "selftest_guard_cycle_rerun.py",
                 "selftest_guard_cycle_offline.py"}
    ok = (set(bad) == new_cases) if tag == "before" else not bad
    unexpected = sorted(set(bad) ^ new_cases) if tag == "before" else bad
    print("PREDICTION %s: %s%s" % (tag, "MET" if ok else "NOT MET",
                                   "" if ok else " - unexpected: " + ", ".join(unexpected)), flush=True)
    print(P.result_line(P.make_result(1 if ok else 0, 0 if ok else 1, None if ok else "prediction " + tag)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
