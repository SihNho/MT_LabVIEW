r"""diag_delete_error.py - read the error cluster `delete_object` has never looked at.

WHY, and whose idea it is. `tools/bench/diag_save_persists.log` showed one delete on a clean donor copy removing
NOTHING while the op VI's Run returned normally, and I called that a "silent no-op". The peer review
(`archive/peer/2026-09-16-delete-object-noop-failed-prediction.md`) refused that framing at the premise:

  "'the helper VI's Run returned successfully' does NOT prove that Generic.Delete executed without a LabVIEW
   error. Generic.Delete is an Invoke Node with its own error in/error out; if error in.status is already true,
   LabVIEW does not execute the method and merely propagates the error."

And it is right that we would never have seen it: `gscript.delete_object` (tools/gscript.py:1957-1972) sets three
controls, calls `_run`, and **reads no error output at all** - unlike every neighbouring op wrapper, which calls
`_err`. So "no exception" only ever meant "the op VI itself did not crash".

The reviewer's cheapest discriminator is to expose `Generic.Delete`'s exact `error out` and probe the same GObject
reference once without retraversing. Exposing a new terminal means rebuilding the op; **reading the error terminals
it already has costs nothing**, and it decides whether a rebuild is even the right move. So this step is only:
enumerate OpDelete_v0's front panel, run one delete, and read every error-shaped indicator on it.

PREDICTION CONTRACT:
  P1 OpDelete_v0 exposes at least one error-shaped indicator (a cluster named like "error out"/"error").
     If it exposes NONE, the reviewer's mechanism is confirmed as unobservable from here and the fix is to rebuild
     the op with its error wired out - that is the finding, not a failure of this test.
  P2 After a delete that removes nothing, at least one of those indicators carries a NON-ZERO status.
     TRUE  => not a silent no-op; the code is the diagnosis, and "silent structural-edit rejection" is dead.
     FALSE => error out is genuinely clean while nothing was deleted, which is the reviewer's own falsifier and
              points at object-level locking, a wrong method, or a LabVIEW defect.
  P3 The target reports Execution:State idle and is not locked, measured rather than assumed - the reviewer notes
     my earlier ExecState reading only counts if it came from the same in-memory instance.

Scratch discipline: the scratch VI is created and DELETED in the same run. No original is opened, nothing is saved.

  py tools/bgrun.py --max-min 12 --log tools/bench/diag_delete_error.log -- py -u tools/bench/diag_delete_error.py
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import fresh  # noqa: E402

DONOR = os.path.join(g.CLAUDEDEV, "OpWireSource_v5.vi")
SCRATCH = os.path.join(g.CLAUDEDEV, "ScratchDeleteError_v0.vi")
TARGET_UID, TARGET_CLS = 1319, "Property"
OUT = os.path.join(HERE, "diag_delete_error.json")


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    out = {"scratch": SCRATCH, "target_uid": TARGET_UID}
    if not os.path.exists(DONOR):
        print("STOP: donor missing", flush=True)
        return 3
    try:
        if os.path.exists(SCRATCH):
            os.remove(SCRATCH)
        shutil.copy2(DONOR, SCRATCH)
        fresh()
        print(f"copied donor -> {os.path.basename(SCRATCH)}", flush=True)

        print("\n=== P3 is the target editable, measured in THIS instance ===", flush=True)
        out["exec_state"] = g.exec_state(SCRATCH)
        print(f"  ExecState = {out['exec_state']}  (1 = idle/editable)", flush=True)

        before = {o["uid"] for o in g.report_all(SCRATCH, TARGET_CLS)}
        out["present_before"] = TARGET_UID in before
        order = [o["uid"] for o in g.report_all(SCRATCH, TARGET_CLS)]
        if TARGET_UID not in order:
            print(f"STOP: uid {TARGET_UID} is not in the donor copy at all", flush=True)
            return 3
        idx = order.index(TARGET_UID)
        print(f"  uid {TARGET_UID} present={out['present_before']}, traverse index={idx}, "
              f"{TARGET_CLS} count={len(before)}", flush=True)

        print("\n=== P1 what does OpDelete_v0 actually expose? ===", flush=True)
        vi = g.op(g.OP_DELETE)
        # The op VIs in this fleet are built with plain labelled controls; probe the names we know the family uses
        # plus every error spelling seen in the codebase. GetControlValue raises for a name that is not on the panel,
        # so a successful read IS the existence test.
        CANDIDATES = ["error out", "error out 2", "error", "error in (no error)", "error in",
                      "Delete error", "err", "status"]
        found = {}
        for nm in CANDIDATES:
            try:
                found[nm] = vi.GetControlValue(nm)
            except Exception:
                pass
        out["panel_error_terminals"] = sorted(found)
        print(f"  error-shaped terminals present: {sorted(found) or 'NONE'}", flush=True)
        if not found:
            print("  **P1 FAIL** - OpDelete_v0 exposes no error terminal at all, so the Invoke Node's error\n"
                  "  cluster is unobservable from COM. The fix is to rebuild the op with error out wired.",
                  flush=True)

        print("\n=== P2 run one delete and read those terminals ===", flush=True)
        vi.SetControlValue("vi path", SCRATCH)
        vi.SetControlValue("Class Name", TARGET_CLS)
        vi.SetControlValue("index", idx)
        try:
            g._run(vi)
            out["run"] = "returned"
        except Exception as e:
            out["run"] = f"raised {str(e)[:120]}"
        print(f"  Run: {out['run']}", flush=True)

        out["errors"] = {}
        for nm in sorted(found):
            try:
                raw = vi.GetControlValue(nm)
                msg = g._err(vi, nm)
                out["errors"][nm] = {"raw": str(raw)[:200], "decoded": msg}
                print(f"  {nm!r:<22} -> {msg or 'status FALSE (clean)'}   raw={str(raw)[:90]}", flush=True)
            except Exception as e:
                print(f"  {nm!r:<22} -> read raised {str(e)[:60]}", flush=True)

        after = {o["uid"] for o in g.report_all(SCRATCH, TARGET_CLS)}
        out["gone"] = sorted(before - after)
        out["present_after"] = TARGET_UID in after
        print(f"\n  objects that disappeared: {out['gone'] or 'NONE'}   uid {TARGET_UID} still present="
              f"{out['present_after']}", flush=True)

        any_err = any(v.get("decoded") for v in out["errors"].values())
        out["verdict"] = (
            "P2 TRUE - Generic.Delete FAILED WITH AN ERROR that delete_object never read; diagnose that code"
            if any_err and out["present_after"] else
            "deletion actually worked here - the earlier verification was looking at a different object graph"
            if not out["present_after"] else
            "error out is CLEAN and nothing was deleted - the reviewer's own falsifier; object locking, wrong "
            "method, or a LabVIEW defect" if found else
            "UNOBSERVABLE - OpDelete_v0 exposes no error terminal; rebuild it with error out wired")
        print(f"\n=== VERDICT: {out['verdict']} ===", flush=True)
    finally:
        g._lv = None
        try:
            if os.path.exists(SCRATCH):
                os.remove(SCRATCH)
                print(f"  scratch removed: {os.path.basename(SCRATCH)}", flush=True)
        except OSError as e:
            print(f"  could not remove scratch: {e}", flush=True)
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        print(f"wrote {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
