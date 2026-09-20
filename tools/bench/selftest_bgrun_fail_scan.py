r"""selftest_bgrun_fail_scan.py - the self-test the round-5 `device-failed` decision demands.

DECISION (docs/violation-decisions.md "## device-failed - 2026-09-17 03:38"): `tools/bgrun.py` adds
`^\s*(?:->\s*)?FAIL\b` to the inner-failure scan for build/diagnostic logs and forces rc=1 on a match;
"self-test on the literal line above", i.e. `tools/bench/diag_stop_condterm_panel.log:15-18`.

WHAT ALREADY EXISTS - checked before writing a line (CLAUDE.md "before creating any new op/tool/recipe"):
  * `tools/bench/probe_bgrun_inner.log` - an EXISTING self-test of the bgrun inner-failure scan, named in
    `tools/logclass.py`'s KNOWN LIMIT note ("shells out to Write-Output and never touches LabVIEW"). Its
    driver is a PowerShell one-liner, not a file, so there is nothing here to extend; this is the same
    IDEA re-run as a checked-in script for the new pattern.
  * `tools/logclass.py:is_review_log` - the ONE definition of "is this log the machinery watching the
    build". Reused, not reimplemented: case D asserts a review-named log is still NOT scanned.
  * `grep -n "^def " tools/gscript.py` - nothing about bgrun or log scanning; this touches no LabVIEW API.
  * `ls tools/bench | grep -i selftest` - no existing selftest_*.py.

NO LABVIEW IS TOUCHED. Every case runs `py tools/bgrun.py` over a throwaway fixture script that only
prints and exits 0; LabVIEW is never started, no .vi is opened, no COM call is made.

PREDICTION CONTRACT
  A  the literal lines of diag_stop_condterm_panel.log:15-19 (one `-> FAIL` gate among PASS lines, plus the
     `SUMMARY 3/4 gates pass` line), from a process that exits 0  =>  bgrun ends rc=1 and writes
     `BGRUN INNER FAILURE`. This is the case that ended rc=0 before the patch.
  B  a PASS-only log, including the passing `=== N pass, 0 fail ===` summary  =>  bgrun ends rc=0 and writes
     no INNER FAILURE line. (Regression guard for STATUS OPEN 6: the summary alternative must still ignore a
     zero count.)
  C  boundary lines that contain the word but are not a gate verdict (`FAILURE COUNT 0`, `-> FAILED to import
     an optional module`, `  failures: 0`)  =>  rc=0. `FAIL\b` requires a word boundary, so FAILED/FAILURE/
     failures do not match; recorded as the pattern's documented behaviour, not as an accident.
  D  case A's exact output written to a log named `peer_*.log`  =>  rc=0, because logclass excludes review
     logs from the scan (a reviewer quoting a gate line is evidence, never the thing under test).

    MATERIAL=1 py tools/bgrun.py --max-min 5 --log tools/bench/selftest_bgrun_fail_scan.log \
        -- py -u tools/bench/selftest_bgrun_fail_scan.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
BGRUN = os.path.join(PROJECT, "tools", "bgrun.py")

# The literal lines of tools/bench/diag_stop_condterm_panel.log:15-19, byte for byte. Kept as a list of
# repr-safe strings so this file never itself contains a bare gate-verdict line at column 0 (the outer
# bgrun scans THIS script's output, so an unguarded copy would fail the run that is testing the scan).
CASE_A = [
    "  PASS  Q1 stop (end) uid 7 wire 6929",
    "  PASS  Q1 stop (end) 2 uid 19587 wire 15230",
    "  " + "-> " + "FAIL  Q2 no panel object carries 3457 or 15229",
    "  PASS  MAIN md5 unchanged   2a78e17c449cacdaf5da389818526859",
    "SUMMARY 3/4 gates pass; failing: ['Q2 no panel object carries 3457 or 15229']",
]
CASE_B = [
    "  PASS  Q1 stop (end) uid 7 wire 6929",
    "  PASS  MAIN md5 unchanged   2a78e17c449cacdaf5da389818526859",
    "SUMMARY 2/2 gates pass",
    "=== selftest fixture: 2 pass, 0 " + "fail ===",
]
CASE_C = [
    "FAIL" + "URE COUNT 0",
    "-> " + "FAIL" + "ED to import an optional module (ignored)",
    "  " + "fail" + "ures: 0",
    "SUMMARY 3/3 gates pass",
]

passes, fails = [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**' + 'FAIL' + '**'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    return ok


def run_case(tmp, tag, lines, logname):
    """Write a fixture that prints `lines` and exits 0, run it under bgrun, return (rc, log text)."""
    fixture = os.path.join(tmp, f"fixture_{tag}.py")
    with open(fixture, "w", encoding="utf-8") as f:
        f.write("import sys\n")
        f.write("for L in %r:\n    print(L, flush=True)\n" % (lines,))
        f.write("sys.exit(0)\n")
    logp = os.path.join(tmp, logname)
    # capture_output: bgrun ECHOES the child's stdout, and echoing a gate-verdict line into THIS
    # process's stdout would be scanned by the OUTER bgrun and fail the run that is testing the scan.
    p = subprocess.run([sys.executable, BGRUN, "--max-min", "2", "--log", logp, "--",
                        sys.executable, "-u", fixture],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    txt = open(logp, encoding="utf-8", errors="replace").read() if os.path.exists(logp) else ""
    return p.returncode, txt


def summarise(txt):
    """(has INNER FAILURE line, the BGRUN END/TIMEOUT line) - sanitised, never the child's own lines.

    The END line itself reads `BGRUN END rc=1 ...`, which is one of the OUTER bgrun's own failure
    patterns - echoing it verbatim would make a PASSING self-test report an inner failure. So `rc=`
    is rewritten to `rc:` before it is printed. The comparison above uses the real return code.
    """
    inner = "BGRUN INNER FAILURE" in txt
    end = next((L.strip() for L in txt.splitlines() if L.startswith(("BGRUN END", "BGRUN TIMEOUT"))), "<none>")
    return inner, end.replace("rc=", "rc:")


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    print(f"bgrun under test: {BGRUN}", flush=True)
    tmp = tempfile.mkdtemp(prefix="bgrun_failscan_")
    try:
        rc, txt = run_case(tmp, "a", CASE_A, "diag_case_a.log")
        inner, end = summarise(txt)
        print(f"  CASE A end line: {end!r}", flush=True)
        gate("A1 a gate-verdict line in a build log forces a non-zero bgrun result",
             rc == 1, f"bgrun returned {rc} (want 1)")
        gate("A2 bgrun records WHY it overrode the child's zero", inner, f"INNER FAILURE line present={inner}")
        gate("A3 the child itself exited zero (so only the scan can have caused A1)",
             "the process itself said 0" in txt, "")

        rc, txt = run_case(tmp, "b", CASE_B, "diag_case_b.log")
        inner, end = summarise(txt)
        print(f"  CASE B end line: {end!r}", flush=True)
        gate("B1 a pass-only build log still ends zero", rc == 0, f"bgrun returned {rc} (want 0)")
        gate("B2 no override line on a pass-only log", not inner, f"INNER FAILURE line present={inner}")

        rc, txt = run_case(tmp, "c", CASE_C, "diag_case_c.log")
        inner, end = summarise(txt)
        print(f"  CASE C end line: {end!r}", flush=True)
        gate("C1 word-boundary lines (…URE/…ED/…ures) do not trip the scan",
             rc == 0 and not inner, f"bgrun returned {rc} (want 0), override={inner}")

        rc, txt = run_case(tmp, "d", CASE_A, "peer_case_d.log")
        inner, end = summarise(txt)
        print(f"  CASE D end line: {end!r}", flush=True)
        gate("D1 a review-named log is still exempt from the scan (logclass)",
             rc == 0 and not inner, f"bgrun returned {rc} (want 0), override={inner}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print("  temp fixtures deleted", flush=True)

    print(f"\n=== selftest_bgrun_fail_scan: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
