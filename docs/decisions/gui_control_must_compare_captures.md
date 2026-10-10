---
name: gui-control-must-compare-captures
description: "The user's 2026-09-18 rule — every GUI action in the LabVIEW harness must be verified by comparing screen captures before and after (target located in the live capture, change confirmed after), because a derived coordinate silently missed the \"Done Picking Beads?\" button"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: b5d0cc76-fda8-4724-8899-5a019fc98595
  modified: 2026-09-18T08:52:09.032Z
type: decision
status: in-force
date: 2026-09-18
source: memory/gui_control_must_compare_captures.md
---

# GUI control must compare captured images — before and after every action

On 2026-09-18 the unattended D0 driver clicked the three beads correctly but missed the `Done Picking Beads?`
Yes button: it clicked (1114, 915) while the button sat at about (1178, 864). The coordinates had been derived
from another copy's panel geometry, and the front panel was not maximised, so the origin differed. The driver
then waited 300 s for a loop that never ended. The user watched it happen and ruled:

> *"GUI 컨트롤 중에는 반드시 캡처 이미지 비교하는게 필요할듯"*

## What this fixes

- **Never click a derived or remembered coordinate blind.** Before each GUI action, take a capture and locate the
  target in *that* capture (template/colour match on the button, OCR of its label, or the control's screen rect
  read from LabVIEW). After the action, take another capture and confirm the expected change (button state, a
  counter such as `Count`, a window appearing) before the next step.
- **No change after a click = a failed step, recorded and stopped**, never a wait-and-hope. A GUI step's
  prediction contract includes what the after-capture must show.
- Panel geometry is read live (maximise the window or read its real rect), never reused from a different VI copy
  or an earlier session.
- This sits on top of the standing rule that GUI is used only where scripting is verified unreachable; the
  bead-pick clicks are the user's approved exception, and this rule is how that exception is made reliable.
