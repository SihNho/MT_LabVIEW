---
name: broken-intermediate-gui-save-allowed
description: "The user's 2026-09-22 permission — a staged-build INTERMEDIATE VI that is broken by design (ExecState 0) may be saved through the GUI (Ctrl+S on its block diagram) because COM SaveInstrument hangs on broken VIs; applies to claudeDev intermediates only, never to an original or a final deliverable"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: b5d0cc76-fda8-4724-8899-5a019fc98595
  modified: 2026-09-21T17:54:05.668Z
type: decision
status: in-force
date: 2026-09-21
source: memory/broken_intermediate_gui_save_allowed.md
---

# Broken intermediate VIs may be saved by GUI Ctrl+S

During the staged D1 build (2026-09-22), stage M3a-1 moved the focus-loop nodes and created shift registers whose
initial values belong to the NEXT stage, so the VI was broken by design at the save point (`ExecState` 0). LabVIEW's
COM `SaveInstrument` hangs forever on a broken VI, so the scripted save refuses; the only route that writes a file is
the GUI one (`gui_save`: bring the block-diagram window to the foreground, verified by a click probe, then Ctrl+S,
verified by the file's mtime moving). The firefighter used it, I put the question to the user, and the user ruled:

> **"저장 허용함."** (2026-09-22, after the report that two cycles in a row had saved broken intermediates by GUI)

## How I apply it

- **Allowed**: saving a `claudeDev` stage artefact that is broken by design, through `tools/lv_gui.ps1`'s
  `gui_save` path with `-Exception Approved -Evidence "user 2026-09-22 broken-intermediate save"`, logged in
  `tools/gui_actions.log` like every GUI act. The file is a hand-off for the next stage and for the user to open;
  it is **never run** (rule 34(f) of the plan), and it is never cold-loaded headless (recompile spin).
- **Not covered**: any original VI (rule 1), and the final deliverable, which must reach `ExecState` 1 and be saved
  by the scripted route. A broken FINAL is a failed stage, not something to save around.
- The exception exists because the scripted route is verified unreachable for this class (COM hang), which is the
  project's standing condition for GUI use; it does not loosen the "GUI only where scripting is unreachable" rule
  elsewhere.
