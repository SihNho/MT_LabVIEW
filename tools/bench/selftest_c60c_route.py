"""selftest_c60c_route - does c60c_astcheck.py's repaired gate 7 discriminate the two routes BOTH ways?

Touches NO LabVIEW, opens no COM, runs no VI. It writes two tiny fixture scripts into a temp directory
under the session scratchpad, runs tools/bench/c60c_astcheck.py against them as a SUBPROCESS (the way the
fleet actually invokes it, so the module-level argparse is exercised as shipped), and reads gate 7's own
printed row out of stdout.

WHY A SUBPROCESS AND NOT AN IMPORT. c60c_astcheck parses its arguments at module level, so importing it
would parse THIS script's argv. The subprocess also proves the thing that matters operationally: that an
invocation passing only a positional target still selects the `owner` route.

PREDICTION CONTRACT - four cells, all four must hold:
  1 owner  x fixture WITHOUT move_in : gate 7 PASSes   (today's behaviour, unchanged)
  2 owner  x fixture WITH    move_in : gate 7 FAILs    (today's behaviour, unchanged)
  3 movein x fixture WITH    move_in : gate 7 PASSes   (the repair: a legitimate move_in build is no
                                                        longer a false positive)
  4 movein x fixture WITHOUT move_in : gate 7 FAILs    (the repair's other direction: a script claiming
                                                        the movein route and never calling move_in is
                                                        the real defect)
Plus two structural assertions:
  5 the two routes print DIFFERENT gate names, so the cycle runner's "same first failing gate line"
    matcher cannot conflate an owner-route failure with a movein-route failure
  6 cell 1 is reached with NO --route flag at all, i.e. the default really is `owner`

PRIOR ART CHECKED BEFORE WRITING THIS (CLAUDE.md: check what exists first):
  - tools/bench/ already holds selftest_guard_peer_failre.py and tools/bench/selftest_cycle_runner_ff.py,
    both of which drive their tool as a subprocess over fixture files; this follows that shape and adds
    no new helper.
  - no existing selftest covers c60c_astcheck.py at all (glob tools/bench/selftest_*c60c* -> nothing),
    so this is new coverage of an existing tool, not a second copy of one.
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECKER = os.path.join(ROOT, "tools", "bench", "c60c_astcheck.py")

# A fixture that CALLS move_in the way a real movein-route diagnostic does: imported from its real home,
# tools/recipes/build_d1_v0.py:318 (move_in is NOT a tools/gscript.py verb, so `g.move_in` would trip
# gate 4 instead of gate 7 and the cell would prove nothing).
FIXTURE_MOVEIN = '''"""fixture: a diagnostic that legitimately takes the movein route."""
from build_d1_v0 import move_in


def main(g, target):
    move_in(target, 10757, 46, (100, 100))
    move_in(target, 10758, 46, (100, 140))
    return 0
'''

# The same script with the move_in import and calls removed and nothing else changed.
FIXTURE_OWNER = '''"""fixture: a diagnostic that takes the owner route and must not touch move_in."""


def main(g, target):
    g.exec_state(target)
    return 0
'''

GATE7_RE = re.compile(r"^\s{2}(PASS|FAIL)\s{2}(7\[(owner|movein)\][^\n]*)$", re.M)
fails = []


def cell(name, ok, detail=""):
    if not ok:
        fails.append(name)
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""), flush=True)
    return ok


def run_checker(fixture_path, route=None):
    """Returns (verdict, gate_name) read off gate 7's own printed row, or (None, None)."""
    cmd = [sys.executable, CHECKER, fixture_path]
    if route is not None:
        cmd += ["--route", route]
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=120)
    m = GATE7_RE.search(p.stdout)
    if not m:
        print("    (no gate 7 row; rc=%s)\n%s" % (p.returncode, (p.stdout + p.stderr)[-800:]), flush=True)
        return None, None
    return m.group(1), m.group(2)


def main():
    scratch = os.environ.get("CLAUDE_SCRATCHPAD") or tempfile.gettempdir()
    tmp = tempfile.mkdtemp(prefix="c60c_route_", dir=scratch)
    f_move = os.path.join(tmp, "fx_movein.py")
    f_own = os.path.join(tmp, "fx_owner.py")
    with open(f_move, "w", encoding="utf-8") as f:
        f.write(FIXTURE_MOVEIN)
    with open(f_own, "w", encoding="utf-8") as f:
        f.write(FIXTURE_OWNER)
    print("fixtures: %s\n          %s" % (f_move, f_own), flush=True)

    v1, n1 = run_checker(f_own, None)          # no flag at all -> the default must be owner
    v2, n2 = run_checker(f_move, "owner")
    v3, n3 = run_checker(f_move, "movein")
    v4, n4 = run_checker(f_own, "movein")

    cell("1 owner (NO --route flag) x fixture without move_in", v1 == "PASS",
         "expect=pass got=%r gate=%r" % (v1, n1))
    cell("2 owner x fixture with move_in", v2 == "FAIL",
         "expect=fail got=%r gate=%r" % (v2, n2))
    cell("3 movein x fixture with move_in", v3 == "PASS",
         "expect=pass got=%r gate=%r" % (v3, n3))
    cell("4 movein x fixture without move_in", v4 == "FAIL",
         "expect=fail got=%r gate=%r" % (v4, n4))
    cell("5 the two routes print DIFFERENT gate names", bool(n2) and bool(n3) and n2 != n3,
         "owner=%r movein=%r" % (n2, n3))
    cell("6 the no-flag default really is the owner route", bool(n1) and n1.startswith("7[owner]"),
         "%r" % (n1,))

    for p in (f_move, f_own):
        try:
            os.remove(p)
        except OSError:
            pass
    try:
        os.rmdir(tmp)
    except OSError:
        pass
    print("\n=== SELFTEST %d/%d cells%s"
          % (6 - len(fails), 6, ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
