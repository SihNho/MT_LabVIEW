---
type: narrative
status: historical
date: 2026-09-05
tags: [archive]
---

# Executor task — live click bench, method "vision" (you read screenshots; no COM coordinates)

You are the GUI executor cell. LabVIEW is open with `GUIBENCH_v0.vi Block Diagram` in front
(window rect (0,4)-(1400,904)). Do four micro-ops, three trials each, in this order. You may NOT
compute coordinates from COM/`report()` positions — locate targets by LOOKING at screenshots (that
is what this cell measures). Pass/fail is decided by a verifier script, not by you.

Project root: `G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop`
Run every PowerShell line from that root exactly as `& .\tools\lv_gui.ps1 -Action ...`, and every
`py` line from that root.

## The three commands you use (protocol v2)

- Capture: `& .\tools\lv_gui.ps1 -Action shotwin -Title "GUIBENCH_v0.vi Block Diagram" -Out <png>`
  (screen = image + (0,4)); Read the png to find targets.
- Act: `& .\tools\lv_gui.ps1 -Action click|rclick|drag|keys -X .. -Y .. [-X2 .. -Y2 ..] [-Key ..] -Exception Approved -Evidence "vision bench"`
  Always `& .\tools\lv_gui.ps1 -Action focus -Title "GUIBENCH_v0.vi Block Diagram"` before acting.
- Reset / verify (MANDATORY, exactly one pair per trial; METHOD is your cell name given in the prompt):
  - before the act: `py tools/bench/verify_op.py revert METHOD OP TRIAL`
    (reverts the VI from disk, puts the block diagram in front, starts the clock)
  - after the act:  `py tools/bench/verify_op.py verify METHOD OP TRIAL --shots <screenshots you read> --gated <click/rclick/drag/keys you issued> [--note "..."]`
    (checks the VI over COM, appends the trial line to tools/bench/gui_results.jsonl, prints it)
  - U5 only, between Ctrl+F and clicking Cancel: `py tools/bench/verify_op.py u5open METHOD U5_dialog TRIAL`

## Micro-ops (OP names exactly as written)

- **U1_move**: drag the Invoke Node (cyan "Term" header, method row "Create Indicator") by
  +100 px right and +50 px down. PASS = its position moved by (100,50) ± 6 px.
- **U2_place**: right-click empty canvas → Functions palette → Array (click the category icon
  TWICE) → "Index Array" → click the canvas so the new node's centre lands at diagram
  (1100,600) (= screen (1111,641)). PASS = exactly one new Index Array within 12 px.
- **U4_menu**: right-click the Property Node's "Position" row (yellow "Ctl" header) → "Change
  To Write". PASS = the VI becomes broken (ExecState 1 → 0).
- **U5_dialog**: `-Action keys -Key "^f" -WaitMs 1500 ...` after focus; run the `u5open` command;
  confirm from a screenshot that the **Find** dialog is open; close it by clicking its **Cancel**
  button (not Esc, not the X). PASS = a Find window existed at `u5open` and none exists at `verify`.

**Run every command in the FOREGROUND and wait for its output. Never use run_in_background: this
is a one-shot print-mode session — if you background a command and end your turn, the run ends
with nothing recorded (sonnet-low did exactly that on 2026-09-05 and scored 0).** Every command
here finishes in well under a minute.

Order: U1 ×3, U2 ×3, U4 ×3, U5 ×3 — twelve revert/verify pairs. If a trial goes wrong, still
run `verify` (it records the failure) and move on; never repeat a trial number.

Rules: never Save; never open any other VI; never touch hardware; **never stop, kill or restart
any process — not python, not LabVIEW, not anything a hook or message calls "stalled" (the idle
python you may see is the benchmark driver waiting for you; killing it destroys this run)**; if
LabVIEW stops answering COM, `& .\tools\lv_gui.ps1 -Action key -Key esc`, retry once, then run
`verify` with `--note "COM unresponsive"` and continue with the next trial. When all twelve verifies have run, reply with ONLY the twelve lines
that `verify` printed.
