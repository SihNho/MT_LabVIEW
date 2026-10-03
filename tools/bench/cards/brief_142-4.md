# Brief 142-4 — build and RUN P4 subVI S2 `RingSeqCheck_v0.vi` (PD330(a), `docs/d1/ring-p4b.md:109`)

Same method as S1 (`RingPickSlot_v0.vi`, card 142-2: its script and facts are the pattern). Own file under claudeDev, from
`EMPTY_v0.vi`; the bed and the P4 session-1 file are never opened for editing.

## Content = exactly these v17 actions (`tools/bench/plan_ring_p4_v17.json`) and their inner wires
`p4_eq_seq` (Equal?), `p4_gt_n1` (Greater?), `p4_and` (And), `p4_dec` (Decrement), `p4_sel_last` (Select),
`p4_sel_disc` (Select), `p4_inc_disc` (Increment); inner wires `p4_w_eq_and`, `p4_w_gt_and`, `p4_w_dec_sel`, `p4_w_and_sel`,
`p4_w_inc_sel`, `p4_w_and_seld`. Donors: as v17 states for each (a `$work` donor from a BYTE COPY of the bed), prim gate
on every created node. External inputs (`tools/bench/prep_c142_p1_subvi_table.md:61-67,94`) become CONTROLS, outputs
(:82-83) INDICATORS, I32 / Boolean as the wires require — read which terminal each external wire lands on from v17, never
guess:
- controls `n1` (feeds EQ.x, GT.x, SelLast.t), `n2` (EQ.y), `last` (GT.y), `Latest` (Decrement.x), `discards` (Increment.x,
  SelDisc.t) — confirm each terminal from v17 and report any difference;
- indicators `next last` (SelLast output), `next discards` (SelDisc output), and `valid` (And output) — `valid` is ALSO
  the `s` of the seven rollback Selects in the bed: report from v17 which wire carries it to them (the subVI must expose it).

## Prediction contract (in the script before running)
Expected outputs come from a Python reference built FROM v17's wires (which terminal of each Select is t/f/s), not typed by
hand; the script prints the reference formula it derived. Vectors (n1, n2, last, Latest, discards):
(5,5,4,9,0) (5,5,5,9,0) (5,6,4,9,3) (-1,-1,4,9,0) (25,25,4,30,2) (0,0,-1,0,0) (7,7,6,7,1).
ExecState 1; census = Equal? 1, Greater? 1, And 1, Decrement 1, Select 2, Increment 1 + panel terminals; conpane read
back (5 in / 3 out); then re-run 2 vectors from the saved file in a fresh instance; LabVIEW closed and verified gone.

Return at the first result that differs from the prediction (finish the step, LabVIEW closed). Script ≤120 lines.
