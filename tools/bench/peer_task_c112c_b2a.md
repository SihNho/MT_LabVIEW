ATTACK this claim about the FAILED L2-B2a stage run tools/recipes/stage_d1_l2b2a.py (log tools/bench/stage_d1_l2b2a.log, card 112-3 W3,
plan tools/bench/plan_l2b2a.json md5 4b782c1f, bed claudeDev\D1_l2_b1_20260927_193100.vi md5 b705728a, UNCHANGED; nothing saved).

Observed (log :96-123): all 7 ops dispatched without an op error (Executor RECORD MODE, checkpoints 0/4/7). Gate E1 FAILED: two step
diffs, only_real_terms (terminals the real read has and the simulation does not):
 - after op 4 (covers b2_09..b2_12): t25829, t25862 on IndexArray #8741 'disabled index (col)';
 - after op 7 (covers b2_13..b2_15): the same two plus t25854, t25961 on IndexArray #30331 'disabled index (col)'.
The card's allow-either rule covers ONLY the split-page s3 cascade owners #8634/#29625 (tools/bench/plan_l2b2a_allow.json), so E1
failed by design of the rule and the run stopped before save (input md5 unchanged, work copy deleted, LabVIEW gone).
Scratch check the same evening (tools/bench/diag_c112c_t1t2.log, PASS 15/0): ONLY b2_10, b2_11, b2_15 on a bed copy, a checkpoint after
EVERY op - NO step diff at all.

CLAIM (mine): LabVIEW's type propagation, not a wiring fault. b2_09 (#8953 'initialized array' -> SRB1 L.outer, cfw) and b2_12
(#28124 -> SRB2 L.outer) give the Void registers SRB1/SRB2 their array type; the type flows through the register's inner faces and the
LoopTunnels #9087/#29911 into the loop bodies, and the downstream polymorphic IndexArray nodes #8741 / #30331 grow a 'disabled index
(col)' terminal pair (a 2-D input). stagesim has no model of polymorphic terminal growth, so the simulated step lacks those
terminals. The split page s3 (tools/bench/cards/split_plan_111_l2b2.md:44-55) already lists #8741/#30331 among the saved-B1 cascade
pairs ('IndexArray #8741/#30331 (index, index (row), disabled index (col))'), yet only #8634/#29625 were declared allow-either.
Evidence for 'the init rows cause it': the scratch run without b2_09/b2_12 had no diff.

Already ruled out: an op error (none), addressing (all 7 routed as dry-predicted), input modification (md5 unchanged).
Attack: (a) could the extra terminals come from b2_10/b2_13 (the feeds) or from b2_15 rather than the init rows, and what reading
would separate them; (b) are these terminals computation-relevant (rule 1a) or display-only 'disabled' index terminals; (c) is
widening allow-either to #8741/#30331 safe, or does it hide a real type change the original (S1) does not have - compare with
S1's #8741/#30331 terminal lists (D1_s1_copy wiki); (d) the cheapest discriminating test.
