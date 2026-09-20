---
type: narrative
status: historical
date: 2026-09-04
tags: [archive]
---

# Executor task — live click bench, method "vision" (you read screenshots; no COM coordinates)

You are the GUI executor cell. LabVIEW is open with `GUIBENCH_v0.vi Block Diagram` (window
rect (0,4)-(1400,904)). Do three micro-ops, three trials each, in this order, and record each
trial. You may NOT compute coordinates from `report()` positions — locate targets by LOOKING at
screenshots (that is what this cell measures). Verification is by COM only.

Project root: `G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop`
Run every PowerShell line from that root exactly as `& .\tools\lv_gui.ps1 -Action ...`.

## Tools you use
- Capture: `& .\tools\lv_gui.ps1 -Action shotwin -Title "GUIBENCH_v0.vi Block Diagram" -Out <png>`
  (screen = image + (0,4)); Read the png to find targets.
- Act: `-Action click|rclick|drag|key -X .. -Y .. [-X2 .. -Y2 ..] -Exception Approved -Evidence "vision bench"`
  Always `-Action focus -Title "GUIBENCH_v0.vi Block Diagram"` before acting (it taps Esc).
- Reset + verify (Python, from `tools\`):
  `py -c "import gscript as g; g._lv=None; g.revert(r'C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\GUIBENCH_v0.vi')"`
  `py -c "import gscript as g; g._lv=None; T=r'...GUIBENCH_v0.vi'; print([o for o in g.report(T,'Invoke')])"`
  `py -c "import gscript as g; g._lv=None; T=r'...GUIBENCH_v0.vi'; print(g.report(T,'IndexArray'))"`
  `py -c "import gscript as g; g._lv=None; T=r'...GUIBENCH_v0.vi'; print(g.exec_state(T))"`

## Micro-ops (revert BEFORE each trial)
- **U1_move**: drag the Invoke Node (cyan "Term" header, method row "Create Indicator") by
  +100 px right and +50 px down. PASS if report() shows its position moved by (100,50) ± 6 px
  from (1044,350).
- **U2_place**: right-click empty canvas → Functions palette → Array (click the category icon
  TWICE) → "Index Array" → click the canvas so the new node's centre lands at diagram
  (1100,600) (= screen (1111,641)). PASS if exactly one new IndexArray appears within 12 px.
- **U4_menu**: right-click the Property Node's "Position" row (yellow "Ctl" header) → "Change
  To Write". PASS if ExecState goes 1 → 0.

## Record per trial (append one JSON line to tools\bench\gui_results.jsonl)
{"method":"vision-sonnet","op":"U1_move","trial":1,"ok":true,"seconds":<wall>,
 "gated_actions":<count of click/rclick/drag/keys you issued>,"screenshots_taken":<n>,
 "screenshots_read":<n>,"px_error":<if applicable>,"at":"<time>"}

Rules: never Save; never open any other VI; never touch hardware; if LabVIEW stops answering
COM, press Esc via `-Action key -Key esc`, retry once, then record ok=false with reason.
When done, reply with ONLY the nine JSON lines.
