r"""diag_save_persists.py - does ONE scripted edit survive save + a fresh LabVIEW? The A1 build says no.

WHY. `tools/bench/build_opownerchain_v0.log` made six deletes and three connects, reported success on all of them,
saved, and `tools/bench/diag_ownerchain_state.log` then read the saved file back as **the donor's topology,
unchanged** - every "deleted" node present, every wire at its original uid. Same byte size as the donor (18 163),
different md5, so a file WAS written.

Two worlds need opposite fixes and must not be guessed between:
  W1 SAVE is the defect - scripted edits do not reach disk at all. (`gscript.delete_object`'s own docstring already
     records a related history: "unusable since the editor's Save became a no-op for scripted edits".)
  W2 SAVE is fine and THAT BUILD's edits never really happened - which the peer review makes likely for the
     connects: `gscript.py:2084` and the skill's `vi-scripting.md:603,:623` both say **Connect Wire on an
     ALREADY-WIRED SINK re-routes and breaks the VI; only unwired sinks may be wired**, and the recipe wired three
     already-wired sinks. That would not, by itself, explain the six deletes reporting success and doing nothing.

This test separates them with the smallest possible edit and no rewiring at all: ONE delete, verified twice - once
in the same process, once from a FRESH LabVIEW that can only see the file.

PREDICTION CONTRACT:
  P1 `delete_object(..., verify=True)` returns a non-empty "gone" uid set containing the target. If it returns an
     EMPTY set, the delete path is broken independently of saving, and W2's second half is confirmed on the spot.
  P2 In the same process, the class count drops by exactly 1 and the uid is no longer enumerated.
  P3 After `save()` and a FRESH LabVIEW, the uid is STILL gone and the count is still one lower.
     P3 holding => save works, W2. P3 failing while P1/P2 hold => save is the defect, W1.
  P4 The saved file's size differs from the donor's. Equal size with a changed topology would itself be a finding.

Scratch discipline (CLAUDE.md rule 4): the scratch VI is created and DELETED in the same run. No original is
opened; nothing outside claudeDev is written.

  py tools/bgrun.py --max-min 12 --log tools/bench/diag_save_persists.log -- py -u tools/bench/diag_save_persists.py
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
SCRATCH = os.path.join(g.CLAUDEDEV, "ScratchSavePersist_v0.vi")
TARGET_UID, TARGET_CLS = 1319, "Property"      # one of the six the A1 build "deleted"
OUT = os.path.join(HERE, "diag_save_persists.json")


def snapshot(tag):
    n = g.count(SCRATCH, TARGET_CLS)
    present = TARGET_UID in {o["uid"] for o in g.report_all(SCRATCH, TARGET_CLS)}
    st = g.exec_state(SCRATCH)
    print(f"  [{tag}] {TARGET_CLS} count={n}  uid {TARGET_UID} present={present}  ExecState={st}", flush=True)
    return {"count": n, "present": present, "exec_state": st}


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    out = {"donor": DONOR, "scratch": SCRATCH, "target_uid": TARGET_UID}
    if not os.path.exists(DONOR):
        print("STOP: donor missing", flush=True)
        return 3
    try:
        if os.path.exists(SCRATCH):
            os.remove(SCRATCH)
        shutil.copy2(DONOR, SCRATCH)
        out["donor_size"] = os.path.getsize(DONOR)
        fresh()
        print(f"copied donor -> {os.path.basename(SCRATCH)} ({out['donor_size']} bytes)", flush=True)

        out["before"] = snapshot("before")

        print(f"\n=== P1 delete uid {TARGET_UID} ({TARGET_CLS}) with verify=True ===", flush=True)
        idx = [o["uid"] for o in g.report_all(SCRATCH, TARGET_CLS)].index(TARGET_UID)
        gone = g.delete_object(SCRATCH, TARGET_CLS, idx, verify=True)
        out["gone"] = sorted(gone) if gone else []
        p1 = bool(gone) and TARGET_UID in gone
        print(f"  delete_object returned gone={out['gone']}  -> P1 {'PASS' if p1 else '**FAIL**'}", flush=True)

        out["after_delete"] = snapshot("after delete, same process")
        p2 = (not out["after_delete"]["present"]) and out["after_delete"]["count"] == out["before"]["count"] - 1
        print(f"  P2 {'PASS' if p2 else '**FAIL**'}", flush=True)

        print("\n=== P3/P4 save, then a FRESH LabVIEW reads the file ===", flush=True)
        try:
            g.remove_bad_wires_scripted(SCRATCH)
        except Exception as e:
            print(f"  remove_bad_wires_scripted raised: {str(e)[:80]}", flush=True)
        st = g.exec_state(SCRATCH)
        print(f"  ExecState before save = {st}", flush=True)
        try:
            size = g.save(SCRATCH, allow_broken=True)
            print(f"  save() returned size {size}", flush=True)
            out["saved_size"] = size
        except Exception as e:
            out["save_error"] = str(e)[:200]
            print(f"  **save raised**: {out['save_error']}", flush=True)

        g._lv = None
        fresh()
        out["after_reload"] = snapshot("after save + FRESH LabVIEW")
        out["disk_size"] = os.path.getsize(SCRATCH)
        p4 = out["disk_size"] != out["donor_size"]
        p3 = (not out["after_reload"]["present"]) and out["after_reload"]["count"] == out["before"]["count"] - 1
        print(f"  disk size {out['disk_size']} vs donor {out['donor_size']}  -> P4 {'PASS' if p4 else '**FAIL**'}",
              flush=True)
        print(f"  P3 {'PASS' if p3 else '**FAIL**'}", flush=True)

        out["verdict"] = ("W2 - save works; that build's edits never happened" if (p1 and p2 and p3) else
                          "W1 - the edit was real in-process but did NOT survive save/reload" if (p1 and p2)
                          else "the DELETE PATH itself is broken (P1/P2 failed) - saving is not the question")
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
