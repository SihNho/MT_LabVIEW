---
type: facts
status: current
date: 2026-10-10
card: 160-c3-1
---
# 160-c3-1: p5s02b recipe pair + pred + licence + predicted step-2-end Error List (offline). DRY FAIL at L0 (gate-fp fp-82); NOT launched
- Outputs (md5, `prep_c160_c3_1_md5.log`): pred `plan_ring_p5s02b_pred.json` 48b50b29; licence `plan_ring_p5s02b_licence.json` f61a2514;
  EL `errorlist_predicted_D1_ring_p5s02b_end.json` 79ec3207; SG census `prep_c160_c3_1_session.json` 287827be (b3-1's session has no
  `sink_gate_census`, RingSession needs it: 0 rows); recipes `stage_d1_ring_p5s02b.py` 083fda6d, `_scratch.py` 3f6fb898.
- Makers: `prep_c160_c3_1_licence.py` 5/0 (X11 CLEAN `prep_c160_c3_1_x11.log`; renames #376 [5683,5782,5787], #24083 [24139], #24150 [24235]);
  `prep_c160_c3_1_el.py` 9/0; `prep_c160_c3_1_pred.py` 14/0; `prep_c160_c3_1_md5.py` 1/0.
- Pred per action (`prep_c160_c3_1_pred.log`): DELETE dw_a13 w10394 / dw_go w24264 / dw_ho w24300 (present at n-1, gone at n); MERGE
  A28 w_gl t24190 -> uid 24285, A35 w_hl t24288 -> 24312 (read from session `merge`, equal on the sim end); DELETE+FRESH A32 w_gr (dw_go first),
  A39 w_hr (dw_ho first), new uid NOT predicted; CEN2 by ENDS, 12 new sim pairs; the other 12 actions PLAN.
- E1 checkpoints [0,2,3,5,7,9,10] == checkpoint_ops == session; step files step_00/04/07/11/15/19/20 (md5 == recorded). 0 move_in ops.
- X10: x10_start(94ffff94) == x10_plan_start 599.7 -> Executor 648.6, MAIN 653.7; START_ASSUMED 603.4 -> 652.3 / 657.4 == b3-1; limit 675.
- Census: census_predict UNPREDICTED, 20/20 rows without a sample (census {}); sim info OuterTerminal 5, InnerTerminal 10, SelectorTunnel 5, Wire 7.
- Error List (`prep_c160_c3_1_el.log`): CLEARED 5 = item 0 (dw_a13), 1 (dw_go), 2 (dw_ho), 3 (A28 w_gl MERGE), 5 (A35 w_hl MERGE); RAISED 0
  (elrule new [] closed []); UNPREDICTED 2 = A32 w_gr, A39 w_hr (base RSR inner face through connect_term_uid, PD391(e)); STANDING 51;
  TOTAL 51 (53 if each UNPREDICTED raises one). compare(read 56, 56 rows) 0/0; compare(read minus 5 cleared, 51 rows) extra 0 missing 0.
- STALE expectations changed, not loosened: 56-row clears_by 'A32 w_gr' / 'A39 w_hr' (items 1, 2) -> dw_go / dw_ho (PD391(a)(d)); 156's X1
  "plan start == maker start" -> the maker's start is START_ASSUMED 603.4, both starts gated; 156's E1M (3 move_in) -> none in step 2.
- DRY (`prep_c160_c3_1_dry.log`): `=== DRY FAIL: first_fail=GATE L0 plan FINAL, open_rows_match, plan_in = plan_ring_p5s02b_in; ...` rc=1.
  Cause: `stagekit.py:2410` requires finalized.plan_in to end `<stem>_in`; plan f4520b10 has `plan_ring_p5s02b_in2.json`
  (`plan_ring_p5s02b.json:350-353`, card 160-b3-1). Every other L0 clause holds (pred plan md5, graph, bed, 26 cdiff rows). Logged fp-82
  (checker:stagekit:L0). No equivalent form or release exists -> BLOCKED.
- NOT RUN (return at the first unexpected result): scratch dry, prerun (X10/X14/X17/X8), --check-launch, --scratch-required.
- md5 UNCHANGED (`prep_c160_c3_1_md5.log` U 14/14): stagesim 95a162ba, stagexec ddf23a31, stagekit 1441bb4c, stage_prerun 7605116f, plan
  f4520b10, in 56bfddd3, in2 927b805c, graph 7ac24924, 56-row 1fd016bf, b3-1 session e5279899, VIs s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae,
  94ffff94. No tool or hook edit. LabVIEW: never launched; tasklist refused by the permission layer (not checked).
- OPEN: fp-82 - change gate_l0 to accept `<stem>_in<N>`, or re-make the plan with plan_in = `_in`? (tooling or plan card; not this card's globs).
- OPEN: copied blocks - licence rename table == `prep_c156_a1_1_licence.py:49-60`; pred E1 checkpoint table == `prep_c156_a1_1_pred.py:79-82`;
  no shared function holds them (tools/ outside the globs).
- OPEN: census UNPREDICTED -> RingSession.gate_cen2 returns before the Wire-by-ends judgement (`stagekit.py:2494-2496`), so the dry can reach
  at best PASS-UNVERIFIED 1, not unverified 0, until a census sample or a measured census exists.
