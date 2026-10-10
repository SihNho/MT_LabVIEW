---
name: labview-snaps-to-terminals-hover-and-verify
description: "LabVIEW snaps to terminals when the cursor is near them, so GUI wiring should be hover-verify-click rather than pixel-perfect coordinate arithmetic"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 72babae7-a0eb-4591-80eb-3f88511dbec4
  modified: 2026-08-25T17:11:55.751Z
type: decision
status: in-force
date: 2026-08-25
source: memory/labview_snaps_to_terminals_hover_and_verify.md
---

# LabVIEW snaps to terminals — hover and verify, don't compute and hope

The user pointed out (2026-08-26), while watching Claude burn round-trips trying to hit a ~4-pixel
node terminal by calculating its coordinates: *"when I drag the mouse near the terminal, LabVIEW
tends to react near the terminal. Otherwise, how could people wire them in such a micro-control
manner?"*

That is the correct model, and it makes the pixel arithmetic largely unnecessary. With Automatic
Tool Selection on, moving the cursor **near** a terminal makes LabVIEW switch the cursor to the
wiring spool, highlight the terminal it intends to connect, and show a **tip strip naming that
terminal**. Humans do not aim precisely — they get close and read the feedback before committing.

So the standard technique for GUI wiring and terminal-clicking should be **hover → capture → verify →
click**, not compute-then-click:

1. `move` to the approximate position from whatever arithmetic is available.
2. Capture, and read what LabVIEW is telling you — the tip strip, the highlighted terminal, and the
   Context Help window, which names the terminal under the cursor.
3. Only click once the feedback confirms the intended target; otherwise nudge and re-check.

Two corollaries worth remembering. **A negative signal is still information**: Context Help showing
"No description available" means the cursor is not on a terminal, which is a useful correction rather
than a broken tool. And **LabVIEW wiring is click-source-then-click-destination, not a drag** — so a
press-glide-release drag primitive is the wrong tool for making a wire, though it remains right for
rubber-band selection.

This matters beyond wiring: it is the general lesson that a GUI application's own feedback is a more
reliable oracle than coordinates computed from a screenshot, and should be consulted before acting
rather than after failing.
