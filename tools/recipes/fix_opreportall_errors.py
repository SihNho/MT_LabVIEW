"""fix_opreportall_errors.py - stop OpReportAll_v0 popping a modal dialog, and find out what really errors.

THE DEFECT, caught by the acceptance test rather than by inspection. On class `Diagram` the op raised:

    Error 1055 occurred at Property Node in OpReportAll_v0.vi
    LabVIEW: (Hex 0x41F) Object reference is invalid.

and, because BOTH property nodes inside the loop have an UNWIRED `error out`, LabVIEW's automatic error handling
turned that into a MODAL DIALOG. A reporting op must never do that: the fleet's watchdog costs 8 s per dialog,
and an op that blocks is worse than an op that is merely slow - this is the same failure shape that made
`net_map`'s docstring warn of "one 8 s dialog per node" until OpNetInfo_v1 fixed it the same way.

Note what the error is NOT. It is not "a Diagram has no Position" (that would be 1057/1058, a bad property for
the class). 1055 is an INVALID REFERENCE, so some reference in the chain is dead or empty - most likely the
`Owner` of the top-level diagram, which is the one object in the traversal with nothing above it.

TWO THINGS ARE DONE HERE, and they are deliberately separate:

  1. `set_auto_error_handling(False)` - the op can no longer pop a dialog. This is the standing fleet treatment
     for an op whose property nodes error by design (OpNetInfo_v1, OpFPLabels_v0, OpTunnelInd_v0 all carry it).

  2. MEASURE what the silenced error costs. Silencing an error is only legitimate if the results are still
     right, so this re-runs the `Diagram` comparison against report() and prints both, row for row. If the rows
     match, the error was harmless and the op is a drop-in for Diagram too. If they do not, that is recorded as
     a LIMITATION of report_all rather than hidden - report() stays the path for that class.

  py tools/bgrun.py --max-min 20 --log tools/bench/fix_opreportall_errors.log -- py -u tools/recipes/fix_opreportall_errors.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

OP = os.path.join(g.CLAUDEDEV, "OpReportAll_v0.vi")
SMALL_SRC = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi")
SMALL = os.path.join(g.CLAUDEDEV, "SCRATCH_reportall_diag.vi")
g._run.__defaults__ = (6.0, 300.0)


def main():
    g._lv = None

    print("== 1. silence automatic error handling on OpReportAll_v0", flush=True)
    g.open_panel(OP)
    time.sleep(0.8)
    before = g.exec_state(OP)
    g.set_auto_error_handling(OP, False)
    print(f"   ExecState {before} -> {g.exec_state(OP)}", flush=True)
    g.save(OP)
    print("   saved", flush=True)

    print("\n== 2. rebuild a small scratch target and re-run the Diagram comparison", flush=True)
    try:
        g.close_panel(SMALL)
        time.sleep(0.3)
    except Exception:
        pass
    if os.path.exists(SMALL):
        try:
            os.remove(SMALL)
        except OSError:
            pass
    shutil.copyfile(SMALL_SRC, SMALL)
    g.open_panel(SMALL)
    time.sleep(0.8)

    rc = 0
    for cls in ("Diagram", "Node"):
        print(f"\n---- class {cls!r} ----", flush=True)
        try:
            t0 = time.time()
            new = g.report_all(SMALL, cls)
            t_new = time.time() - t0
            print(f"   report_all: {len(new)} rows in {t_new:.2f} s  (no dialog)", flush=True)
        except Exception as e:
            print(f"   report_all STILL FAILS: {str(e)[:240]}", flush=True)
            rc = 2
            continue
        old = g.report(SMALL, cls)
        print(f"   report    : {len(old)} rows", flush=True)
        print("   report_all rows:", flush=True)
        for r in new:
            print("      ", (r["uid"], r["class"], r["pos"], r["owner"]), flush=True)
        print("   report rows:", flush=True)
        for r in old:
            print("      ", (r["uid"], r["class"], r["pos"], r["owner"]), flush=True)
        same = (len(new) == len(old) and all(
            (a["uid"], a["class"], tuple(a["pos"]), a["owner"]) ==
            (b["uid"], b["class"], tuple(b["pos"]), b["owner"]) for a, b in zip(new, old)))
        print(f"   -> {'IDENTICAL' if same else 'DIFFERENT - report_all is NOT a drop-in for this class'}",
              flush=True)
        if not same:
            rc = 3

    try:
        g.close_panel(SMALL)
        time.sleep(0.3)
        os.remove(SMALL)
        print("\nscratch target deleted", flush=True)
    except Exception as e:
        print("\ncleanup:", str(e)[:120], flush=True)

    print("\nVERDICT:", "the dialog is gone and the rows agree" if rc == 0 else
          "see above - the limitation is recorded, not hidden", flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
