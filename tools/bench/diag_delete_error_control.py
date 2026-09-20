r"""diag_delete_error_control.py - is OpDelete_v0's `error out` WIRED, or just an indicator nobody writes?

WHY THIS EXISTS, and why the previous run is not enough. `tools/bench/diag_delete_error.log` measured, on an idle
(ExecState 1) fresh copy: one delete removed NOTHING and `error out` read **(False, 0, '')** - clean. That fires the
peer reviewer's own falsifier (`archive/peer/2026-09-16-delete-object-noop-failed-prediction.md`, section 6), which
said it would abandon the error-plumbing explanation exactly if `Delete.error out` came back clean on an idle,
unlocked target in the same application instance.

But a clean read has TWO readings, and choosing between them by argument is the mistake this project keeps making:

  R1 the indicator is wired to `Generic.Delete`'s `error out`, the method really did return no error, and the
     delete genuinely did nothing;
  R2 the indicator is NOT wired (or is written before the Invoke Node), so it holds its default forever and
     `(False, 0, '')` is what it would report no matter what happened.

R2 would make the whole previous run meaningless, so it is tested FIRST and by the cheapest possible means: give
the op inputs that CANNOT succeed and see whether the indicator moves.

  case A  index = 999999          - past the end of the class's object array; Index Array + Delete cannot work
  case B  Class Name = garbage    - a class name Traverse does not know (the same shape as the recorded 1092)

PREDICTION CONTRACT:
  P1 At least one of case A / case B drives `error out` to a NON-ZERO status.
     TRUE  => the indicator is live, so the clean read on the real delete was REAL evidence: R1 holds, the reviewer's
              falsifier stands, and the remaining candidates are object-level locking, a wrong method for this
              class, or a LabVIEW defect.
     FALSE => `error out` never moves for ANY input. R2 holds, the indicator is dead, `diag_delete_error.log` proves
              nothing, and the op must be rebuilt with the Invoke Node's error actually wired out before anything
              else about delete can be claimed.
  P2 Neither control case deletes anything (a sanity check: case A must not delete some OTHER object by accident).

Scratch discipline: the scratch VI is created and DELETED in the same run. No original is opened, nothing is saved.

  py tools/bgrun.py --max-min 12 --log tools/bench/diag_delete_error_control.log -- py -u tools/bench/diag_delete_error_control.py
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
SCRATCH = os.path.join(g.CLAUDEDEV, "ScratchDeleteCtl_v0.vi")
CLS = "Property"
OUT = os.path.join(HERE, "diag_delete_error_control.json")


def attempt(vi, tag, cls, index):
    vi.SetControlValue("vi path", SCRATCH)
    vi.SetControlValue("Class Name", cls)
    vi.SetControlValue("index", index)
    ran = "returned"
    try:
        g._run(vi)
    except Exception as e:
        ran = f"raised {str(e)[:100]}"
    raw = None
    try:
        raw = vi.GetControlValue("error out")
    except Exception as e:
        raw = f"READ FAILED {str(e)[:60]}"
    msg = g._err(vi, "error out")
    print(f"  [{tag}] Class={cls!r} index={index}  Run: {ran}\n"
          f"        error out -> {msg or 'status FALSE (clean)'}   raw={str(raw)[:90]}", flush=True)
    return {"tag": tag, "cls": cls, "index": index, "run": ran, "raw": str(raw)[:200], "decoded": msg}


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    out = {"scratch": SCRATCH, "cases": []}
    if not os.path.exists(DONOR):
        print("STOP: donor missing", flush=True)
        return 3
    try:
        if os.path.exists(SCRATCH):
            os.remove(SCRATCH)
        shutil.copy2(DONOR, SCRATCH)
        fresh()
        before = {o["uid"] for o in g.report_all(SCRATCH, CLS)}
        print(f"copied donor -> {os.path.basename(SCRATCH)}; {CLS} count={len(before)}, "
              f"ExecState={g.exec_state(SCRATCH)}\n", flush=True)

        vi = g.op(g.OP_DELETE)
        print("=== P1 controls that CANNOT succeed ===", flush=True)
        out["cases"].append(attempt(vi, "A out-of-range index", CLS, 999999))
        out["cases"].append(attempt(vi, "B unknown class", "NoSuchClassXYZ", 0))

        after = {o["uid"] for o in g.report_all(SCRATCH, CLS)}
        out["disappeared"] = sorted(before - after)
        print(f"\n  P2 objects that disappeared during the controls: {out['disappeared'] or 'NONE'}", flush=True)

        live = any(c["decoded"] for c in out["cases"])
        out["indicator_live"] = live
        out["verdict"] = (
            "P1 TRUE - `error out` IS wired and live. The clean read in diag_delete_error.log was real evidence: "
            "Generic.Delete returned no error and deleted nothing. Remaining candidates: object-level locking, "
            "wrong method for this class, or a LabVIEW defect."
            if live else
            "P1 FALSE - `error out` never moves for ANY input, so it is a DEAD indicator. diag_delete_error.log "
            "proves nothing about the method's error, and OpDelete_v0 must be rebuilt with the Invoke Node's "
            "error wired out before any claim about delete is made.")
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
