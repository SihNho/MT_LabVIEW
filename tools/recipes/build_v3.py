"""build_v3.py - the FULL, replayable build of PARALLEL_kernel_v3.vi from a clean four-fold copy.

Serialization of the 2026-08-31 assembly (user's five-step cycle, step 2: one long script).
Run:  py tools\\recipes\\build_v3.py [--fresh]
  --fresh  delete the existing v3 and rebuild from READONLY_fourfold_COPY.vi

Every name comes from docs/NAMES.md (labels contain REAL newlines/trailing spaces - never retype
them by eye). Steps marked [GUI] are the two operations with no scripting path (primitive
placement, terminal-count growth) plus IndexMode flips until OpSetIndexMode_v0 lands; the script
pauses there with exact instructions and verifies the result before continuing, so a human (or the
GUI recipes in the skill) can perform them and re-run with --resume.

Verification model: consolidated checkpoints (counts + ExecState after each PHASE, not each edit),
a proactive LabVIEW restart between phases to preempt error 2 (memory full), and a final report
table. Structural only - functional acceptance is a separate fixture run.
"""
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

V3 = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3.vi")
BASE = os.path.join(g.CLAUDEDEV, "READONLY_fourfold_COPY.vi")
KERNEL = (r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\background VIs"
          r"\Track 1 of N bds xyz-kernel-reentrant.vi")

# --- names (docs/NAMES.md is the source of truth) -------------------------------------------
IN_CTRL = ["Image In", "Array of cal clusters", "cross size", "Bead is good? array in"]
IN_TERM = ["Image", "Calibration cluster 1", "cross size", "Bead 1 is good? in"]
COS_CTRL = ["Cosine bandpass\nfor Hilbert ", "Real-space cosine window"]   # newline + trailing sp!
COS_TERM = ["cosine window\nfor hilbert", "real-space\ncosine window"]
OUT_XYZ = ["X pos 1", "Y pos 1", "Z pos 1"]
OUT_GOOD = "Bead 1 is good? out"
OUT_POS = "Index of closest\ncal image slice, bead 1"                       # real newline!
IND_GOOD = "Bead is good? array out"
IND_POS = "pos in cal image out"
LOOP_AT = (-1300, 1150)


def restart_labview():
    """Preempt error 2: kill LabVIEW between phases; panel-first reload on next use."""
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"],
                   capture_output=True)
    time.sleep(5)
    g._lv = None
    g._cache.clear()


def check(label, **want):
    got = {k: g.count(V3, k) for k in want if k != "ExecState"}
    if "ExecState" in want:
        got["ExecState"] = g.exec_state(V3)
    ok = all(got[k] == v for k, v in want.items())
    print(("  OK " if ok else "  ** MISMATCH ") + label, got, "" if ok else f"wanted {want}")
    if not ok:
        raise SystemExit(f"checkpoint failed at: {label}")


def pause_gui(instructions):
    print("\n[GUI] " + instructions)
    print("      Perform it (skill: references/gui-recipes.md), then press Enter.")
    input()


def main():
    fresh = "--fresh" in sys.argv
    if fresh:
        if os.path.exists(V3):
            os.remove(V3)
        shutil.copyfile(BASE, V3)
        print("phase 0: fresh copy from four-fold", os.path.getsize(V3), "B")

    g.open_panel(V3)                                   # NEVER cold-load a broken v3 headless
    check("baseline", ForLoop=1, SubVI=6, Wire=250, ExecState=1)

    # --- phase 1: parallel loop + kernel + 4 named inputs (ONE fused call) ------------------
    g.loop_kernel(V3, LOOP_AT, IN_CTRL, KERNEL, IN_TERM, parallel=4)
    g.save(V3)
    check("phase 1 loop+kernel", ForLoop=2, SubVI=7, Wire=254, ExecState=1)
    restart_labview()

    # --- phase 2: Decimate (x,y,z split) ----------------------------------------------------
    g.open_panel(V3)
    if g.count(V3, "Unbundler") == 0:
        pause_gui("Quick-Drop 'Decimate 1D Array' on empty canvas OUTSIDE the loop; "
                  "select it; drag the bottom-centre blue handle DOWN 8 px (3rd output).")
    terms = [o for o in g.report(V3, "GObject") if o["owner"] == "Unbundler"]
    assert len(terms) == 4, f"Decimate must have 1 in + 3 out, found {len(terms)}"
    g.save(V3, allow_broken=True)                       # broken: required input unwired
    g.wire_control(V3, ["x,y,z array"], "Unbundler", 0, ["array"], branch=True)
    assert g.exec_state(V3) == 1, "branch to Decimate should legalise the VI"
    g.save(V3)
    restart_labview()

    # --- phase 3: output tunnels + indicators ----------------------------------------------
    g.open_panel(V3)
    di = 1                                              # the P-loop's inner diagram index
    g.exit_loop(V3, 0, OUT_XYZ + [OUT_GOOD], di)
    g.exit_loop(V3, 0, [OUT_POS], di)
    pause_gui("Delete the DEAD wires into the 3 output indicators "
              "(click each wire, Delete). They come from the old structure.")
    g.wire_indicators(V3, 0, [OUT_GOOD], [IND_GOOD])
    g.wire_indicators(V3, 0, [OUT_POS], [IND_POS])
    g.save(V3)
    check("phase 3 outputs", LoopTunnel=16, ExecState=1)
    restart_labview()

    # --- phase 4: Interleave (x,y,z array out) ---------------------------------------------
    g.open_panel(V3)
    pause_gui("Ctrl+U (Clean Up Diagram) to spread the loop; Quick-Drop 'Interleave 1D "
              "Arrays' near the loop's right border; grow to 3 inputs (+8 px); wire the three "
              "X/Y/Z tunnel outers to its inputs 0/1/2 (identify each by Context Help hover: "
              "'X pos 1' top); wire its output to the 'x,y,z array out' terminal.")
    check("phase 4 interleave", ExecState=1)
    g.save(V3)

    # --- phase 5: cosine windows (whole-array, NON-indexed) --------------------------------
    for ctl, term in zip(COS_CTRL, COS_TERM):
        g.wire_control(V3, [ctl], "SubVI", 0, [term], branch=True)
    # TODO(OpSetIndexMode_v0): flip the two new top-border tunnels by script.
    pause_gui("Right-click EACH of the two new top-border tunnels -> 'Disable Indexing' "
              "(deselect first by clicking empty canvas; menus block COM until Esc).")
    check("phase 5 cosine", ExecState=1)
    g.save(V3)

    # --- final ------------------------------------------------------------------------------
    check("FINAL (connector pane is inherited from the four-fold copy - nothing to assign)",
          ForLoop=2, SubVI=7, Unbundler=1, ExecState=1)
    print("\nbuild_v3 complete:", os.path.getsize(V3), "B - structural level only; "
          "functional acceptance is the fixture run.")


if __name__ == "__main__":
    main()
