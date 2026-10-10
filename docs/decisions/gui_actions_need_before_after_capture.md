---
name: gui-actions-need-before-after-capture
description: "The user's 2026-09-18 rule — every GUI action must locate its target in a capture taken just before, act, then capture again and confirm the expected change; remembered or derived coordinates are never clicked blind"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 65a1e34f-8e02-4570-b9c4-69fc023ffb64
  modified: 2026-09-18T09:33:07.473Z
type: decision
status: in-force
date: 2026-09-18
source: memory/gui_actions_need_before_after_capture.md
---

# Every GUI action is capture → locate → act → capture → confirm

While watching a live unattended run of the D0 harness on 2026-09-18, the user saw the three bead clicks land
correctly but the `Done Picking Beads?` Yes button never get hit, and wrote the rule:

> **"GUI 컨트롤 중에는 반드시 캡처 이미지 비교하는게 필요할듯"** — EVERY GUI action: capture BEFORE and locate the
> target *in that capture* (colour/template match, OCR of the label, or the control's live screen rect), act,
> capture AFTER and CONFIRM the expected change (button state, a counter, a new window) before the next step.
> No change ⇒ FAIL and stop. **Derived or remembered coordinates are never clicked blind.**

## Why it matters — what it would have caught

The driver clicked (1114, 915) because that point had worked on a *different* copy of the same VI. On the copy
actually being driven, the button was at (1177, 862) — 63 px left and 53 px below. The click was *delivered*
(the proof path confirmed the target window received it); it simply landed on empty panel. The run then sat in
the bead-picking loop for 303 s and every later stage silently never happened.

Two lessons sit underneath the rule:

- **Proving delivery is not proving effect.** A click-with-proof helper can confirm the window got the message
  and still tell you nothing about whether the right control was under the cursor. Only the confirmation
  capture closes that gap.
- **A window rect is not a control position.** A gate comparing window rectangles passed with delta (0,0) while
  the control inside the panel sat 65 px away, because control positions are not readable over this project's
  COM path. When the machine cannot be asked, **the screenshot is the measurement** — so locate on it, every
  time, rather than inheriting a coordinate from another VI or an earlier session.

Applying this turned a 13-pass/3-fail run into 39-pass/1-fail with every stage of the workflow reached on both
legs, so it is cheap and it is what works.
