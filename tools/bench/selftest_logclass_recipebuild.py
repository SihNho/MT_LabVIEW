r"""selftest_logclass_recipebuild.py - `tools/logclass.py:is_recipe_build_log`, the Pre-decided 112 repair.

WHAT IS UNDER TEST. `guard_cycle.py`'s retrospective BUDGET SET counted every log in `tools/bench/` that was not
review machinery. On 2026-09-22 09:0x that set held 16 logs whose oldest and newest were `jev_trial.log` (a
model-API trial) and `selftest_guard_peer_jev.log` (a hook self-test): neither builds anything in LabVIEW, and
between them they set BOTH the count and the 8-hour span the gate then called an overdue cycle.

THE REPAIR IS A NEW, SEPARATE PREDICATE, NOT A NARROWING OF `is_build_log` (Pre-decided 112, verbatim): "`is_build_log`
itself is left exactly as it is, because `guard_peer` arms the failed-prediction review off it and a failing
*diagnostic* must keep arming it; narrowing the shared predicate would have silently disarmed that gate." So this
file tests BOTH halves: the new predicate discriminates, and the old one does not move.

PRIOR ART, CHECKED BEFORE A LINE WAS WRITTEN (`grep "^def " tools/logclass.py`, `ls tools/bench/selftest_*.py`):
`tools/bench/selftest_guard_peer_jev.py` (17/0) and `tools/bench/selftest_guard_peer_failre.py` already cover
guard_peer's classifier; neither touches `logclass.is_recipe_build_log`, which did not exist until now. There is
no existing self-test for `tools/logclass.py` at all - this is the first. The real logs used as fixtures are read,
never written.

PREDICTION CONTRACT, WRITTEN BEFORE THE RUN.
  C1  tools/bench/jev_trial.log            is_recipe_build_log False   (command = tools/bench/jev_trial.py)
  C2  tools/bench/selftest_guard_peer_jev.log  False                   (command = tools/bench/selftest_*.py)
  C3  tools/bench/build_d1_m3a3_run2.log   is_recipe_build_log TRUE    (command = py -u tools/recipes/build_d1_m3a3.py)
  C4  all three keep is_build_log TRUE - the shared predicate is untouched
  C5  a log whose PROSE quotes a recipe path but whose command is a bench script -> False (command position only)
  C6  `cp "a.py" "tools/recipes/b.py"` -> False (the interpreter runs cp, not the recipe; STATUS hint 4's shape)
  C7  an APPENDED file (bench run, then a recipe run) -> True; the reverse order -> False (LAST run only)
  C8  a review log (`peer_*`, `retro*`, `cycle_*`) -> False even if its command line names a recipe
  C9  a file with no BGRUN line at all (a watchdog record) -> False
  C10 guard_peer's own self-tests still pass UNCHANGED, run as subprocesses and their tallies read back
Every case is a FAIL if it disagrees. No LabVIEW is touched by this file.
"""
import os
import re
import subprocess
import sys
import tempfile

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                              # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import logclass                                                                    # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
passes, fails = [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    return ok


def fact(line):
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def head(t):
    print("\n---------- %s" % t, flush=True)


def write(tmp, name, body):
    p = os.path.join(tmp, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    return p


BG = "BGRUN START 2026-09-22 08:10:56 limit 50.0 min: %s\n"


def main():
    print("=" * 100, flush=True)
    print("=== selftest_logclass_recipebuild - Pre-decided 112, the cycle gate's budget classifier", flush=True)
    print("=" * 100, flush=True)

    head("[1] THE THREE REAL LOGS Pre-decided 112 NAMES, read off disk")
    real = [("C1 jev_trial.log", "jev_trial.log", False),
            ("C2 selftest_guard_peer_jev.log", "selftest_guard_peer_jev.log", False),
            ("C3 build_d1_m3a3_run2.log", "build_d1_m3a3_run2.log", True)]
    for label, name, want in real:
        p = os.path.join(BENCH, name)
        if not os.path.isfile(p):
            gate("%s the fixture log exists on disk" % label, False, p)
            continue
        cmd = logclass.last_bgrun_command(p)
        got = logclass.is_recipe_build_log(p)
        fact("%s command VERBATIM: %r" % (label, cmd))
        gate("%s is_recipe_build_log is %r" % (label, want), got == want, "got %r" % got)
        gate("C4 %s is_build_log is STILL True - the shared predicate is UNTOUCHED (guard_peer arms the "
             "failed-prediction review off it)" % name, logclass.is_build_log(p) is True,
             "got %r" % logclass.is_build_log(p))

    head("[2] THE SCOPING CASES - the command in COMMAND POSITION, never the filename and never the prose")
    tmp = tempfile.mkdtemp(prefix="logclass_st_")
    cases = [
        ("C5 prose-only mention", "prose_run.log",
         BG % "py -u tools/bench/diag_c77_rowd_addr.py"
         + "the review cites tools/recipes/build_d1_m3a3.py and its FAIL lines verbatim\n", False),
        ("C6 cp into tools/recipes", "copy_run.log",
         BG % 'cp "tools/recipes/a.py" "tools/recipes/b.py"', False),
        ("C6b cp from elsewhere", "copy2_run.log",
         BG % 'cp "a.py" "tools/recipes/b.py"', False),
        ("C7 appended, LAST run is the recipe", "appended_ok.log",
         BG % "py -u tools/bench/jev_trial.py" + "noise\n" + BG % "py -u tools/recipes/build_d1_m3a3.py", True),
        ("C7b appended, LAST run is a bench script", "appended_no.log",
         BG % "py -u tools/recipes/build_d1_m3a3.py" + "noise\n" + BG % "py -u tools/bench/jev_trial.py", False),
        ("C8 a peer transcript whose command names a recipe", "peer_whatever.log",
         BG % "py -u tools/recipes/build_d1_m3a3.py", False),
        ("C8b a cycle-runner session transcript", "cycle_71.log",
         BG % "py -u tools/recipes/build_d1_m3a3.py", False),
        ("C8c a retrospective runner log", "retro.log",
         BG % "py -u tools/recipes/build_d1_m3a3.py", False),
        ("C9 a watchdog record with no BGRUN line", "stall_pid9999.log",
         "STALL: pid 9999 unresponsive\n", False),
        ("C9b a bench log with no BGRUN line at all", "orphan_run.log", "just some text\n", False),
        ("C10a a windows-path recipe command", "winpath_run.log",
         BG % r"py -u tools\recipes\build_d1_m3a3.py", True),
        ("C10b a recipe under an absolute path", "abspath_run.log",
         BG % r"py -u G:\proj\tools\recipes\build_d1_m3a3.py", True),
    ]
    for label, name, body, want in cases:
        p = write(tmp, name, body)
        got = logclass.is_recipe_build_log(p)
        gate("%s -> is_recipe_build_log %r" % (label, want), got == want,
             "got %r ; command %r" % (got, logclass.last_bgrun_command(p)))

    head("[3] THE SHARED PREDICATE DID NOT MOVE - is_build_log on the same fixtures")
    gate("C4b is_build_log still True for a plain bench log", logclass.is_build_log(
        os.path.join(tmp, "prose_run.log")) is True)
    gate("C4c is_build_log still False for a peer transcript", logclass.is_build_log(
        os.path.join(tmp, "peer_whatever.log")) is False)
    gate("C4d is_build_log still False for a watchdog record (guard_peer sees it by its OWN route)",
         logclass.is_build_log(os.path.join(tmp, "stall_pid9999.log")) is False)

    head("[4] GUARD_PEER's OWN SELF-TESTS, RUN UNCHANGED (Pre-decided 112: its classifier is not touched)")
    for st in ("selftest_guard_peer_jev.py", "selftest_guard_peer_failre.py"):
        p = os.path.join(BENCH, st)
        if not os.path.isfile(p):
            gate("C10 %s exists" % st, False, p)
            continue
        try:
            r = subprocess.run([sys.executable, "-u", p], cwd=ROOT, capture_output=True, text=True,
                               timeout=300)
            tail = (r.stdout or "")[-4000:]
            m = re.findall(r"(\d+)\s*pass\s*/\s*(\d+)\s*fail", tail, re.I)
            nfail = int(m[-1][1]) if m else None
            fact("%s rc=%r ; tally %r ; last line %r"
                 % (st, r.returncode, m[-1] if m else None,
                    ([ln for ln in tail.splitlines() if ln.strip()] or [""])[-1][:160]))
            gate("C10 %s still passes UNCHANGED (rc 0 and 0 failures)" % st,
                 r.returncode == 0 and (nfail == 0 or nfail is None),
                 "rc=%r nfail=%r" % (r.returncode, nfail))
        except Exception as e:                                                     # noqa: BLE001
            gate("C10 %s still passes UNCHANGED" % st, False, "%s: %s" % (type(e).__name__, str(e)[:200]))

    head("[5] THE BUDGET, RECOUNTED - what guard_cycle now sees")
    import glob
    import time
    allp = sorted(glob.glob(os.path.join(BENCH, "*.log")))
    old = [p for p in allp if logclass.is_build_log(p)]
    new = [p for p in allp if logclass.is_recipe_build_log(p)]
    fact("tools/bench/*.log total %d ; is_build_log %d ; is_recipe_build_log %d" % (len(allp), len(old), len(new)))
    for p in sorted(new, key=os.path.getmtime):
        fact("  RECIPE BUILD  %s  %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(p))),
                                         os.path.basename(p)))
    gate("C11 the recipe-build set is a STRICT SUBSET of the old set", set(new) <= set(old),
         "%d of %d" % (len(new), len(old)))

    print("\n" + "=" * 100, flush=True)
    print("=== GATES: %d pass / %d fail%s" % (len(passes), len(fails),
                                              ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
