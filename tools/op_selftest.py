"""Fleet-wide fault-injection regression: every op must fail LOUDLY, never silently.

Feeds each wrapper a deliberately bad input and asserts the failure is READABLE (an
exception carrying the real LabVIEW error), because this fleet's worst failure mode is
the silent no-op - a clean return with nothing done (Clear Errors sinks, self-edit,
unwired sources have all produced one). Registered as maintenance item 2026-08-29.

Non-destructive by design: every case either targets a nonexistent path or asks for a
bogus terminal/label name, so no fleet VI is modified. Run it whenever an op or wrapper
changes:

    py tools\\op_selftest.py

Exit code 0 = every failure was loud; 1 = at least one silent gap (listed in output).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gscript as g

DUMMY = os.path.join(g.CLAUDEDEV, "OpExitLoop_v0.vi")   # read-only stand-in target
BAD_PATH = os.path.join(g.CLAUDEDEV, "DOES_NOT_EXIST_selftest.vi")

CASES = []


def case(name):
    def deco(fn):
        CASES.append((name, fn))
        return fn
    return deco


def expect_raise(fn, *needles):
    """Run fn. PASS = raised with the expected message (clean error-chain path).
    WARN = raised only because the watchdog dismissed a modal dialog - loud, but the
    fragile path: the op itself popped a dialog instead of returning error data.
    FAIL = returned cleanly - a silent failure path."""
    try:
        fn()
    except Exception as e:
        msg = str(e)
        if "modal dialog" in msg.lower():
            return "WARN", f"loud via watchdog-dismissed dialog (fragile): {msg[:90]}"
        missing = [n for n in needles if n.lower() not in msg.lower()]
        if missing:
            return "WARN", f"raised, but message lacks {missing}: {msg[:90]}"
        return "PASS", msg[:100]
    return "FAIL", "returned CLEANLY - silent failure path"


@case("report: nonexistent target path")
def _(): return expect_raise(lambda: g.report(BAD_PATH, "Node"), "error")

@case("count: nonexistent target path")
def _(): return expect_raise(lambda: g.count(BAD_PATH, "Node"), "error")

@case("wire: bogus source terminal name")
def _(): return expect_raise(
    lambda: g.wire(DUMMY, "SubVI", 0, "bogus_term_selftest", "SubVI", 1, "also_bogus"),
    "5001")

@case("exit_loop: bogus output name")
def _(): return expect_raise(
    lambda: g.exit_loop(DUMMY, 0, ["bogus_term_selftest"], 0), "5001")

@case("wire_indicators: bogus source terminal name")
def _(): return expect_raise(
    lambda: g.wire_indicators(DUMMY, 0, ["bogus_term_selftest"], []), "5001")

@case("wire_indicators: refuses self-edit")
def _(): return expect_raise(
    lambda: g.wire_indicators(g.OP_WIREIND, 0, ["error out"], ["error out"]), "itself")

@case("drop_subvi: nonexistent subVI path")
def _(): return expect_raise(lambda: g.drop_subvi(DUMMY, BAD_PATH, 0, (100, 100)), "error")

@case("for_loop: nonexistent target path")
def _(): return expect_raise(
    lambda: g.for_loop(BAD_PATH, (100, 100), tunnels=[], indexing=[], parallel=0), "error")

@case("delete_by_label: label that matches nothing")
def _():
    import shutil
    scratch = os.path.join(g.CLAUDEDEV, "SCRATCH_selftest_del.vi")
    shutil.copyfile(DUMMY, scratch)
    try:
        return expect_raise(
            lambda: g.delete_by_label(scratch, "bogus_label_selftest"), "nothing")
    finally:
        os.remove(scratch)


def main():
    g.open_panel(DUMMY)
    results = []
    for name, fn in CASES:
        try:
            verdict, detail = fn()
        except Exception as e:            # harness bug, not an op verdict
            verdict, detail = "FAIL", f"selftest harness error: {e}"
        results.append((verdict, name, detail))
        print(verdict, "|", name, "|", detail)
    fails = [r for r in results if r[0] == "FAIL"]
    warns = [r for r in results if r[0] == "WARN"]
    print()
    print(f"{len(results) - len(fails) - len(warns)} PASS / {len(warns)} WARN / "
          f"{len(fails)} FAIL of {len(results)}")
    if warns:
        print("WARN = loud but fragile (dialog + watchdog, or vague message) - backlog:")
        for _, name, detail in warns:
            print("  -", name, "->", detail)
    if fails:
        print("FAIL = SILENT gap (a real error would vanish here):")
        for _, name, detail in fails:
            print("  -", name, "->", detail)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
