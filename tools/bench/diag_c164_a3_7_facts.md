---
type: facts
status: current
date: 2026-10-10
card: 164-3-7
---
# 164-3-7 facts: by identity (class, owner, owner uid, pos) both plan-deleted nodes are GONE; structural condition HOLDS; memory_model + pred census WRITTEN; offline, no LabVIEW.
## Inputs: 14 card inputs md5 == card (md5sum at start); originals/pins below.
## Identity table (tools/bench/prep_c164_a3_7_ident.log, RESULT PASS 12/0 :33; graphs base 3d5196ab, adopted 2a5fa0c4)
| node | base (class, owner, owner uid, pos) | adopted row at that uid | adopted object with base identity | IDENTITY GONE |
|---|---|---|---|---|
| #23042 | Comparison, Diagram, 23405, (15713, 30518) | none | none (also none of that class at that pos) | yes (:5) |
| #23501 | LoopTunnel, WhileLoop, 23041 (stagexec.tunnel_owner), (15675, 11867) | ParameterTerminal 'y' of new #12170, wire 31744, pos (5478, 11923) | none | yes (:6) |
- Re-used terminal uid 23481: base 'x' of #23042 (wire 23460, pos (15713, 30518)) -> adopted 'x = y?' of #12170 (wire 31749, pos (5488, 11913)); base owner identity gone True (:7).
- LoopTunnel uid set base 147 / adopted 146: base-adopted [23501], adopted-base [] (:9); identity set base-adopted = #23501's only, adopted-base [] (:10). I1 PASS (:11), I2 PASS (:12).
## Structural condition, line by line (ident log; each line found by search in its source log)
- G1 graph.log:308 PASS (:14); G2 :309 PASS (:16); G3 :310 PASS (:18); FS1 :311 PASS (:20); B :313 PASS (:22); X :314 PASS (:24); no FAIL other than E5 (:25).
- EL: diag_c164_a3_5_el.log:88 items 53 / window 53, extra 0 missing 0; :89 RESULT PASS 11/0; elexp.log:5-6 predicted 2c1edf78, extra [] missing [] -> S3 PASS (:28).
- w23460 absent: 0 rows, no object (:29). w23519 source [8494], real sinks [7606, 23241, 23450] == prediction (:30-31). STRUCTURAL CONDITION HOLDS (:32).
## Writes (tools/bench/prep_c164_a3_7_write.log, RESULT PASS 11/0 :30)
- memory_model.json 8fb432e4 -> ff0fabca: ONE new load_by_vi key 6dcd5c3d506f69947a5ce259ccbe2221 = 603.9 (cite diag_c164_a3_5_graph.log:24, W3 :13); compare: only load_by_vi differs, by that key, old keys equal, fail_above_mb 680.0 (W7 :18).
- plan_ring_p5s02d_pred.json 87a65b89 -> 5a7bfc81: census = stagekit.scratch_census of diag_c164_p5s02d_scratch.log:223 (== _sum.json, W4 :14) {Comparison 1, DigitalNumericConstant 1, InnerTerminal 6, LeftShiftRegister 1, Local 1, OuterTerminal 4, ParameterTerminal 1, RightShiftRegister 1, SelectorTunnel 2, Terminal 2, Wire 7}; census_overall MEASURED-SCRATCH; census_source cites :223, net :222 and the graph reads; only census/census_overall/census_source differ, plan md5 unchanged (W8 :19).
- Byte copies before: diag_c164_a3_7_memory_model_before.json 8fb432e4, diag_c164_a3_7_pred_before.json 87a65b89. Text diff (CRLF kept, W8b :20): memory_model +5 lines only.
- Run 1 of the write script wrote LF line endings (content identical; prep_c164_a3_7_write_run1_lf.log); both files were restored from the byte copies (md5 back to 8fb432e4 / 87a65b89) and run 2 rewrote them with CRLF.
## Tool defects logged (tools/bench/gate_fp_queue.jsonl)
- fp-87 checker:diag_graph:E5 - deleted nodes tested by uid only (diag_c164_a3_5_graph.py:65); by identity both are gone.
- fp-88 checker:stagekit:term_identity_gates:reuse - reuse_noted covers deleted WIRE uids only (stagekit.py:1512-1514), recycled covers base position keys (stagekit.py:1499); neither saw 23501/23481 re-used (scratch log :220, :225).
- fp-89 guard_bash - refused a gate_fp log whose --cmd text named a labview:read script (guard_card.log:1015); nothing was run.
## Invariants
- VI pins before and after equal (write log W0 :10, W9 :29): eb1d0f31, 7f2582ae, 94ffff94, f9ae7751, 564d8cbe, adopted 6dcd5c3d, original 2a78e17c. tasklist LabVIEW count 0. No hook/stage-tool/detector edit, no scratch, no motor/camera.
OPEN: E5 and the D/TD reuse detectors still judge by uid / position key; the next graph read of an adopted file will fail E5 again whenever LabVIEW re-uses a deleted uid (fp-87, fp-88 queued, not fixed).
