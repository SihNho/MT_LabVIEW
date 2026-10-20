# Plan under prior-art review - card chat-PI2, 2026-10-19

Brief: `tools/bench/cards/brief_chat-PI2.md` (user 2026-10-19: the Op VIs in the PI deck - diagram photo, what it does,
why it is needed). Previous related card: chat-PI1d (OpGetImage_v0, Node.Get Image 6358C01, one NODE per image,
`archive/peer/2026-10-16-priorart-op-getimage-v3.md` verdict novel).

## What is built
1. `tools/recipes/build_op_getbdimage_v0.py` -> `claudeDev\OpGetBDImage_v0.vi`: donor `OpReport_v3.vi` (pure reader,
   no Close Reference); a `VI Server:VI` Invoke, method ID `42C` = **Block Diagram: Get Image Scaled** (labviewwiki
   VI_class/Block_Diagram.Get_Image_Scaled_method; inputs Image Depth I32, Maximum Width / Maximum Height I32 left
   UNWIRED = actual size; output Image Data), its `reference` branched from the donor's `Open VI Reference.vi reference`
   by `g.wire(branch=True)` (the OpBuildIA_v0 route; `connect2` made a bad wire on this kind of branch,
   `tools/bench/diag_bdloaded_reader.log:13`), then `Write PNG File.vi` (same tail and names as OpGetImage_v0). Gate M1
   first verifies the method's terminal names from LabVIEW on a scratch EMPTY_v0 copy (fatal on a mismatch). Then the
   op-hygiene record via `gscript.hygiene_run` (2,000 calls), exactly as build_op_getimage_v0.py.
2. `tools/bench/pi_shots_lib.py`: + `get_bd_image()` (wrapper of the new op, labels JSON) and `png_stats()` (blank check);
   self-test extended.
3. `tools/bench/pi_shots_ops.py`: byte copies `shot_<name>.vi` of seven Op VIs (OpReport_v3, OpWireSource_v5, OpMoveIn_v0,
   OpConnectNested_v1, OpCreateLocalRead_v0, OpForLoopParSet_v0, OpGetImage_v0) -> whole-diagram PNG each + ops.json
   (node classes by report_all('Node'), subVI names by gscript.subvis per diagram). Retry once in a fresh LabVIEW on an
   error or a blank PNG (lesson of chat-PI1f), then report.

## Questions for this review
- Does the project already own a whole-diagram image op or a record of VI method 42C / Get Image Scaled (or a refusal of it)?
- Is there an existing op whose VI-class branch from Open VI Reference is a better donor than OpReport_v3?
- Is any helper hand-rolled here that gscript or pi_shots_lib already provides?

## Retry chat-PI2b (2026-10-19) - what changed since the first review (archive/peer/2026-10-19-priorart-op-getbdimage.md, novel)
- Gate M1 of build_op_getbdimage_v0.py measured the 42C terminals as LabVIEW short names (GetDiagramImageScaled /
  img depth / img data / max width / max height, tools/bench/build_op_getbdimage_v0.log:8); judgement accepted them.
- Hypothesis review archive/peer/2026-10-19-hypothesis-op-getbdimage.md: M1 is now an EXACT lower-cased set (short or
  long names), b.ctl/b.w take the measured names, B4c also checks the OUT-side img data wire. Log -> build_op_getbdimage_v0b.log.
- Nothing else changed in the plan; pi_shots_lib.py / pi_shots_ops.py unchanged since the first review.
