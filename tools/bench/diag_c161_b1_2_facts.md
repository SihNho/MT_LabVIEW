---
type: facts
status: current
date: 2026-10-10
card: 161-b1-2
---
# 161-b1-2: PB's 31 rows vs the pred's 26 = FRAME-keyed vs NON-frame cdiff of the same sim end; the 5 extra #376 rows are already in the base (step 0)
Offline only: `tools/bench/prep_c161_b1_2_measure.py` -> `prep_c161_b1_2_measure2.log` (BGRUN END rc=0, 43 s, RESULT PASS 4/0), data
`diag_c161_b1_2_measure.json` 729a272f. (`prep_c161_b1_2_measure.log` rc=1 = my own argument-order bug in the scratch script, fixed, not a measurement.)
## 1. PB definitions (tools/stagekit.py)
- sim-end / real-end rows `[31, 31]` = `n_rows = [len(R_), len(S_)]` (:2014); R_ = pb_bound_rows(cdiff(S1f, G1)), S_ = pb_bound_rows(computation_diff_frame(S1f, Gsimb)) (:1988-1989);
  S1f = `s1_frame_graph` FRAME-keyed (:1805-1811), Gsimb = `pred_end_graph(bind_state(L))` frame_keyed=True (:1814-1818, :2024, :2028); L = `x.step(len(A))` (:2461).
- "pred's 26 rows (26 slots)" = `len(pred_rows)` / `len(want)` (:1842-1843); pred_rows = `PRED["cdiff_rows"]` (:2535) = `sorted(fz["end_cdiff_rows"])` (`prep_c160_c3_1_pred.py:162`)
  = stagesim's NON-frame `V.computation_diff(S1, graph(st))` with S1 = `load_s1` = `JC.load(s1_key)` (`tools/stagesim.py:2688-2689, 2700, 2460-2467`).
- "plan's 24 open pairs" = `len(self.P["open_rows"])` (:2540); compared as pw = `pos_convert_open_rows` pairs (:1838-1839) vs pg = (node, S1 name) of the frame cdiff rows (:1840).
## 2. Symmetric difference (same key: sink string, sim uids; log :9-13)
- frame cdiff(S1f, sim end) 31 rows; non-frame (stagesim route) 26 rows == pred 26 (`nonframe == pred rows true`, :11).
- only in the 31: `376 cal cluster path|0`, `376 error in|0`, `376 file size|0`, `376 selected path|0`, `376 total data array in|0` (:12). only in the 26: [] (:13).
- Recomputed PB (G1 := Gsimb): n_rows [31,31], pred/slots_want/slots_got 26/26/31, extra = the 5, missing [], pairs_want 24 / got 29 (2626 element|0..2 = 1 pair),
  pairs_extra_left = the 5, blocked whys identical to `prep_c161_b1_1_dry.log:55`, move_frames {} (:19-27).
## 3. The 5 pairs on #376
- Per step 0..20 the frame cdiff is 31 rows at EVERY step, the 5 present from step 0 (base p5s02a graph 7ac24924, before any action) (:8; json per_step).
  Non-frame cdiff: 29 at base -> 28 after #4 w_in3_376 -> 26 after #11 w_gr -> 27 #12 w_gpass -> 25 #19 w_hr -> 26 #20 w_hpass (json per_step).
- Plan actions with dst #376 on these terms: #4 `w_in3_376` (selected path), #7 `w_g376` (error in), #15 `w_h376` (total data array in); `cal cluster path`
  and `file size`: no action of this plan (:29). All 5 sink keys exist in S1f (:30).
- after-sources at sim end: cal cluster path `3391 string@31546/f0`, file size `1766 int@31557/f0` (base tunnels), selected path `29551 path@-1/f0` (TF3);
  before (S1) = the same terminals untagged (json `row ...`).
- Doubled uids 3934/4965 (and 1842/3954): sim end has ONE terminal row per sink, `error in` t5683 wire -11, `total data array in` t5782 wire -23 (:31-32);
  the 3 delete_wire uids 10394/24264/24300 are on no terminal (:33). The doubling is effective_sources returning each S1 source twice with DIFFERENT frame-tag sets
  (`376 error out@-12/f0+-12/f1+-7/f0+-7/f1` and `@-12/f0+-7/f0`; `4910 error out@-7/f0` and `@-12/f1+-7/f0+-7/f1`) (:35) - not a leftover wire (measured on the sim end; real==sim by eq_diff []).
## 4. Answers
- Pred differs from the sim end by exactly those 5 pairs: YES (31 = 26 + the 5; only-in-26 empty).
- Old checkpoint set (0,2,3,5,7,9,10): dry NOT re-run (not measured). PB's inputs (L, pred, open_rows, S1f) carry no checkpoint set; this recompute uses none and gets the same [31,31]/26.
## md5
UNCHANGED: stagesim 95a162ba, stagexec a4df7e15, stagekit 0b5bb678, stage_prerun 7605116f, plan f4520b10, pred 18729409. Written only `tools/bench/prep_c161_b1_2_*`, `diag_c161_b1_2_*`. No LabVIEW process.
OPEN: pred rows come from stagesim's non-frame cdiff while PB counts a frame-keyed cdiff; the 5 frame-tag rows exist from the base on and no plan frame (move_frames {}) can RECORD them - which side is the defect (pred maker, PB keying, or plan open_rows)? (judgement)
