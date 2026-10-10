---
type: facts
status: current
date: 2026-10-10
card: 160-b3-1
---
# 160-b3-1: plan_ring_p5s02b.json FINAL on 94ffff94 with the two PD391(a) stub deletes (offline, no LabVIEW)
- Ran `tools/bench/prep_c160_b3_1_mk.py` c0a012ce -> `prep_c160_b3_1_mk.log` 646eda5f: RESULT 19/0, `BGRUN END rc=0 after 37s` (log:109-111).
- md5: in 56bfddd3c519d793b676865185bc14c6 (unchanged); in2 927b805c90d3aa2507aa682bc54db17c; plan final f4520b101baad70f065ba5d6c9d14925;
  b1 plan 09ebc7a6c08f466997ba472ec0c64109; c159 plan caef7e1c8a4a331c1a3f3337653052ba (unchanged); graph 7ac24924f979afde964e63fb27957b45;
  94ffff94 VI 94ffff94 (prefix, M0/U, log:3,109); session json `prep_c160_b3_1_session.json` e5279899.
- Gates (all PASS): M0 pins (log:3) · B1 b1 kept (:4) · E1 (:5) · CM (:6) · MAP (:10) · FRM (:18) · DW w10394 (:19) · ROWS 18 == input, MERGE why aside (:20)
  · MERGE A28/A35 why (:23) · STUB (:26) · IN2 (:32) · SB (:96) · MERGE-END (:99) · STUB-END (:102) · C (:105) · X10 (:106) · X8 (:107) · X17 (:108) · U (:109).
- STUB read from graph rows: t24139 -> [24264], t24235 -> [24300], both `stagesim.sourceless_wire` True; groups t_go / t_ho (log:24-25).
- 20 actions (log:27): dw_a13, t_in3, w_in3_t, w_in3_376, t_gi, w_gl, w_g376, dw_go, t_go, w_gout, w_gr, w_gpass, t_hi, w_hl, w_h376, dw_ho, t_ho, w_hout, w_hr, w_hpass.
  dw_go/dw_ho are inserted before the group TUNNEL (as `selftest_c160_regface.py:74-78`), i.e. before A30/A37 groups that contain A32/A39.
- why: A32/A39 = "PD374(d) | stub deleted first (PD391); fresh connect to the register inner face; uid NOT predicted; CEN2 judges by ends" (the
  origin tag PD374(d) kept, ASSUMPTION suffix replaced); dw_* = "PD391(a): sink-only stub on the base register inner face, deleted before the group's connect".
- REALSIM: final True, failed None, 20/20 steps, 0 PROVISIONAL, route check PASS, 0 UNROUTABLE (log:95-96). Route rows (log:85-94):
  k1 delete_wire dw_a13 · k2 tunnel t_in3 cfw · k3 tunnel t_gi cfw · k4 delete_wire dw_go · k5 connect_term_uid t_go/w_gout/w_gr · k6 case_frame_wire w_gpass
  · k7 tunnel t_hi cfw · k8 delete_wire dw_ho · k9 connect_term_uid t_ho/w_hout/w_hr · k10 case_frame_wire w_hpass.
- MERGE-END: t24190 -> [24285], t24288 -> [24312] (log:97-98). STUB-END: t24139 -> sim wire [-17] (source row t-13), t24235 -> [-29] (t-25);
  stub Wire objects 24264 / 24300 gone (log:100-101). New uids not predicted (PD391(d)).
- Compile (log:103): 10 ops [delete_wire 1] [tunnel 2-4] [tunnel 5-7] [delete_wire 8] [connect_term_uid register_end_case_border 9-11]
  [case_frame_wire new_wire 12] [tunnel 13-15] [delete_wire 16] [connect_term_uid register_end_case_border 17-19] [case_frame_wire new_wire 20];
  checkpoints [0,2,3,5,7,9,10].
- STALE b1 EXPECTATION CHANGED (not loosened): b1's "C 8 ops {delete_wire 1, tunnel 5, case_frame_wire 2}, checkpoints [0,2,3,4,6,7,8]"
  (`prep_c160_b1_1_mk.py:125-126`) -> 10 ops {delete_wire 3, tunnel 3, connect_term_uid 2, case_frame_wire 2}: +2 stub deletes, and groups
  t_go / t_ho now compile to connect_term_uid (stagexec ddf23a31 base-register face, PD391(c)). b1's MERGE gate on A32/A39 dropped (PD391(d)),
  replaced by the STUB / STUB-END gates; b1's "18/18" -> 20/20.
- X10: START_ASSUMED 603.4 (x10_start(94ffff94) 599.7), Executor peak 652.3, MAIN 657.4 <= 675 (log:104-106; b1 had 654.6 at 8 ops).
- md5 UNCHANGED (U gate log:109): s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae, 94ffff94, stagekit 1441bb4c, stage_prerun 7605116f,
  stagesim 95a162ba, stagexec ddf23a31, vigraph a7eb58c7, addrcheck 207beb0d, plan in 56bfddd3, c159 plan caef7e1c, graph 7ac24924. No tool or hook edit.
OPEN: the delete-row insertion (prep_c160_b3_1_mk.py, IN2 block) repeats the logic of `selftest_c160_regface.py:70-79`; no shared function exists
  and tools/ was outside this card's write globs - extract to stagekit (e.g. insert_stub_deletes) in a tooling card?
OPEN: dw_go/dw_ho sit before the group tunnel (A30/A37), not directly before A32/A39 as the card goal words it; the brief's selftest order was followed.
