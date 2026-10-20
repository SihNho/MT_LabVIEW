# Plan under prior-art review - card chat-PI1d (retry of chat-PI1c), 2026-10-16

Same goal and same recipe as chat-PI1c (brief `tools/bench/cards/brief_chat-PI1.md`; previous review
`archive/peer/2026-10-16-priorart-op-getimage-v2.md`, verdict novel + helper-exists, released by two FIXED: lines).

## What changed since the v2 review (the only edits)
- chat-PI1c FAILED at M1 only on a name: Node.Get Image 6358C01 exists and its terminals read `Image Depth`, `BG Color`,
  `Image Data` (tools/bench/build_op_getimage_v0c.log:8). The judgement session accepted `BG Color` as LabVIEW's short
  name of the Background Color input (same method, labviewwiki Node_class/Get_Image_method).
- `tools/recipes/build_op_getimage_v0.py`: WANT and the control-creation loop use `BG Color`; log/record names v0d,
  hygiene card id chat-PI1d; the hygiene PNG goes to `tools/bench/pi_shots_20261016/hygiene_tmp/` and that folder is
  deleted after the op-hygiene record (gate H2).
- `tools/bench/pi_shots_lib.py`: get_image() sets the labels-JSON key `BG Color` instead of `Background Color`.
- Nothing else: still imports B / retarget / uid_echo from tools/bench/diag_c100_verbs_build.py (v2 B3 fix kept).

## Question for this review
Does the one-word rename, or the hygiene-PNG folder, re-introduce anything the project already owns or has refuted?
Is a `BG Color` terminal (or Node.Get Image) recorded anywhere in docs/vi-server-ids.json or docs/toolkit-capabilities.md
that this plan should reuse?
