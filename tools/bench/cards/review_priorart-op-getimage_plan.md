# Plan under prior-art review - card chat-PI1b (retry of chat-PI1), 2026-10-16

User (chat, 2026-10-16): the PI wants to see the real block-diagram code - readable PNG crops of the KEY part of three
VIs, not the whole diagram (brief `tools/bench/cards/brief_chat-PI1.md`). Read-only on the sources; no hardware; no VI
under study is ever Run.

## What is built
`claudeDev\OpGetImage_v0.vi` by the recipe `tools/recipes/build_op_getimage_v0.py` (helpers `tools/bench/pi_shots_lib.py`):
inputs VI path + object UID + PNG path; inside: Open VI Reference -> `UID to GObject Reference.vi` (copied from the donor
op `OpOwnerChain_v1.vi`, the same donor `tools/bench/diag_swap_build.py` built OpReplaceGObj_v0 on) -> Invoke
`VI Server:GObject` method "Get Image" -> vi.lib `picture\png.llb\Write PNG File.vi`; plus a Property node GObject
Position (632A800) + Bounds (632A803) on the same reference so crops can be computed.
The Get Image method ID is not recorded in `docs/vi-server-ids.json` (only Move 632A400 / Replace 632A402), so the recipe
FINDS it from LabVIEW: Invoke nodes with candidate IDs 632A401, 632A403..632A40F on a scratch copy of EMPTY_v0.vi, read
back their terminal names, take the one with an Image output. Bounds 632A803 is verified the same way.
All edits use existing gscript verbs (build_invoke, build_property, drop_subvi, connect_terminals, create_control,
create_indicator, save, exec_state, node_terms_uid, fp_labels). stagekit is not imported (fp-106).

## What it is then used for (a later script `tools/bench/pi_shots_20261016.py`)
Byte copies of the three sources in `claudeDev\shots_20261016\` (original main VI 2f048e3a, P6-1 D1_ring_p6_20261012_212645
c2d9c13c, current D1_ring_p6latest_20261014_010104 15c664e3); for each: Get Image of the structure (While "B" of the
original; While #10170 / Flat Sequence #27509 of the copies) -> raw PNG; node Position+Bounds -> PIL crop at native
scale (no downscaling) to the listed nodes + 40 px. Copies closed without saving; source md5 before/after.

## Existing work checked
grep "Get Image|GetImage|Write PNG" over tools/gscript.py, docs/toolkit-capabilities.md, docs/NAMES.md: only IMAQdx Get
Image rows (camera, unrelated). No op captures a diagram image. GUI screenshots are not allowed under this card.
