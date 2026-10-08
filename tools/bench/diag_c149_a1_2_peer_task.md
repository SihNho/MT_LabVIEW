ATTACK this claim (card 149-a1-2, failing log tools/bench/diag_c149_a1_2_el.log, script tools/bench/diag_c149_a1_2_elrun.py).

CONTEXT. tools/errorlist_check.py (unchanged) read the LabVIEW Error List of a byte copy of claudeDev\D1_ring_p4s06_20261008_174730.vi
(md5 569ffbf5, the P4 session-6 scratch work copy, broken by design). It ran through diag_c149_a1_2_elrun.py, which only puts the Claude
app's MSIX LocalCache site-packages at sys.path[0] (comtypes 1.4.17, rapidocr_onnxruntime 1.4.4, numpy 2.2.6;
tools/bench/diag_c149_a1_2_probe.log:6-11). Result (diag_c149_a1_2_el.log): OCR engine rapidocr-onnxruntime; "window's own count: 51
(from '51 errors and warnings')"; 51 items read, "reached the window's own count of 51 items"; verdict MISMATCH vs the s05 expected file
(extra 5, missing 9); rc 1. Read json: tools/bench/errorlist_D1_ring_p4s06_20261008_174730_20261008_181243.json.
Prediction (tools/bench/plan_ring_p4_s06v18_pred.json:96-230, errorlist.per_class.predicted): total 55 = s05 read (55,
tools/bench/diag_c147_a1_1_el.log:22) + 1 shift-register item - 1 local item.

PER-CLASS (read - predicted), counted from the read json's "raw" fields with the recipe's classifier
(tools/recipes/stage_d1_ring_p4_s06v18_scratch.py:95-103):
  input -2 (4 vs 6) | types-mismatch +1 (2 vs 1) | wire-loose-ends +1 (21 vs 20) | wire-not-connected +2 (22 vs 20)
  loop-tunnel-undirected -3 (0 vs 3) | wire-sinks-no-source -1 (0 vs 1) | output-tunnel->Replace Array Subset -1 | output-tunnel->subVI -1
  local 0, sr 0. Total diff -4 -> EL-ADVISORY |diff| > 3 -> RETURN (rule stage_d1_ring_p4_s06v18_scratch.py:106-123).

CLAIM: the reader is right (the window itself says 51) and the 4-item drop is real content of the s06 file: session 6's 21 edits
(diag_c147_p4s06v18_scratch.log 691-1047: 16 new wires, 8 lost, wire w23807 deleted, Index Array + local created) resolved the 3 undirected
loop tunnels, the source-less sink wire and both output-tunnel-to-input items, and the fixed-rule prediction (tools/elrule.py, which models
only local/cond/sr classes) does not model wire/tunnel class changes - so the prediction, not the file, is what is off.

Give: the strongest reason the claim is wrong; an alternative explanation (e.g. OCR/stepping misread, a numpy 2.2.6 vs 1.26.4 effect,
an edit the scratch made that the plan did not intend); what would falsify the claim; and the cheapest discriminating test that uses
no new LabVIEW scratch build (read-only files or the existing read json / scratch log only).
