FAILED PREDICTION in tools/bench/sim_l7_split.log (card chat-S2, the stage simulator tools/stagesim.py).

Prediction: replaying the loop-1.7 split (45 actions) from tools/bench/graph_s3_loop15_20260924.json, the simulated END
graph's uid-edges equal the recorded reference (S3 edges - L7-1a removed + L7-1b added - / + L7-R lists from
tools/bench/l7_r_prediction.json, whose PC1/PC2 gates passed in tools/bench/stage_d1_l7_r_r2.log:454-455) up to new-uid
naming. Observed: diff count 22, ALL of them only in the reference (only_sim empty), e.g. ('wire', 13404, 13410, 13425,
13430). At the L7-1a and L7-1 checkpoints the diff was 0, and the end computation_diff matched the recorded 1 row.

My explanation: the only action between L7-1 and the end that can remove edges unrelated to #376 is the last one,
`remove_bad_wires` (tools/stagesim.py op_remove_bad_wires), whose provisional rule clears every wire with n_src != 1 or
no sink COUNTED BY ROWS. Measured on the base graph: 13 wires qualify BEFORE any action, and the ones checked (13486,
19372, 16880, 25478, 25186, 23614, 25404) each have their source as TWO rows of the SAME Diagram-owned terminal (e.g.
#13404 terminal 13410 listed twice) - a reader duplicate, not a broken wire; LabVIEW's real RBW removed no live edge
(stage_d1_l7_r_r2.log 'RBW removed no live uid edge'). Proposed fix: count distinct source term_uids.

Already ruled out: (1) L7-R's delete_object/auto-dropped tunnels - the 22 edges touch none of 15/51/24/1108/1929/5020;
(2) naming - canon() maps only negative/new uids, the 22 are all base uids on both ends.

Attack this: is there another action or rule in stagesim.py that could remove these edges; is 'distinct term_uid'
the right rule, or does LabVIEW's Remove Bad Wires actually delete some wires that the reader shows as duplicated
sources; what is the cheapest discriminating test without LabVIEW?
