# Brief chat-PI2 — whole block-diagram images of six Op VIs for the PI meeting (user 2026-10-19)

User 2026-10-19: "Op 관련 항목도 정리했으면 좋겠음. 블럭 다이어그램 사진, 무슨 기능을 하는지, 왜 필요한지".
Lean runner STOPPED - keep it so. No hardware; never Run a VI. One LabVIEW client; run only after chat-PI1f returned.

## The six Op VIs (claudeDev, our own files; open BYTE COPIES in claudeDev\shots_20261016\ops\, md5 before/after)
OpReport_v3.vi, OpWireSource_v5.vi, OpMoveIn_v0.vi, OpConnectNested_v1.vi, OpCreateLocalRead_v0.vi,
OpForLoopParSet_v0.vi  (+ OpGetImage_v0.vi as the seventh, built 2026-10-16).

## How
Whole diagram at native size: VI class method **Block Diagram: Get Image Scaled** (data name "BD.Get Image Scaled",
method ID 42C, owning class VI; inputs Image Depth I32, Maximum Width / Maximum Height I32 - leave UNWIRED for the
actual size; output Image Data). Source: https://labviewwiki.org/wiki/VI_class/Block_Diagram.Get_Image_Scaled_method
(fetched 2026-10-19). Verify the method by its terminal names from LabVIEW first (RETURN if they differ beyond short
names). Build ONE op `claudeDev\OpGetBDImage_v0.vi` (VI path + PNG path in; Image Depth 24; Write PNG File.vi), in
tools/recipes/ through the prior-art gate and with an op_hygiene record, like OpGetImage_v0 (chat-PI1d). If the method
needs the VI paused / UI idle and refuses, RETURN with the error - no GUI workaround.

## Output
`tools/bench/pi_shots_20261016/op_<name>.png` for the seven Op VIs + `ops.json` (file, source md5, pixel size, the
node classes / subVI names visible on the diagram, one line on what the diagram shows). Close unsaved; LabVIEW gone;
labview-lock set/cleared; one STATUS history line; commit nothing. Result card `tools/bench/cards/result_chat-PI2.json`.
