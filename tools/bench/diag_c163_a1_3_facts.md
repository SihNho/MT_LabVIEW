---
type: facts
status: current
date: 2026-10-10
card: 163-a1-3
---
# 163-a1-3: p5s02c (group I A41..A52) recipe pair + pred + licence + predicted step-3-end EL (offline). DRY FAIL at PB (gate-fp fp-86); NOT launched
- Outputs (`prep_c163_a1_3_md5.log`): pred `plan_ring_p5s02c_pred.json` fc908036; licence `plan_ring_p5s02c_licence.json` c8fdf33a; EL
  `errorlist_predicted_D1_ring_p5s02c_end.json` 373e0bf4; SG census `prep_c163_a1_3_session.json` b7d13a25 (0 rows); recipes
  `stage_d1_ring_p5s02c.py` 6d1d5786, `stage_d1_ring_p5s02c_scratch.py` a517557d (inputs only on stagekit.RingSession, shape of the p5s02b pair).
- Makers: `prep_c163_a1_3_licence.py` 5/0 (X11 CLEAN `prep_c163_a1_3_x11.log`; 1 rename #376 [5763 'frame index'] by w_c7_fi);
  `prep_c163_a1_3_el.py` 9/0; `prep_c163_a1_3_pred.py` 15/0 (`prep_c163_a1_3_pred.log:70`); `prep_c163_a1_3_md5.py` 1/0.
- Pred per action (`prep_c163_a1_3_pred.log:57-68`): NEW A41 sr_c7 (CS7L/CS7R), A42 c_k07 (K07), A44 c_inc7 (IN7), A45 t_ci7 (TC7), A49 t_co7 (TD7);
  CASE-FRAME A48 w_c7_fi (branch, #31506), A52 w_c7_pass (new_wire, #31517); PLAN A43, A46, A47, A50, A51; every wire sink wired at sim end (WS 7/7).
- E1 checkpoints [0,1,2,4,5,7,8] == checkpoint_ops == session; step files step_00/01/02/04/07/11/12 (md5 == recorded); 0 delete_wire.
- X10: x10_start(f9ae7751) == x10_plan_start == session 607.1 -> Executor 653.2, MAIN 658.3 <= 675 (== 163-a1-2 session); X17 PASS.
- Census UNPREDICTED (12/12 rows no sample); sim info Wire 6, InnerTerminal 6, OuterTerminal 4, SelectorTunnel 2, L/R SR 1/1, const 1, Function 1.
- Error List (`prep_c163_a1_3_el.log`): CLEARED 0 (no group-I action names a row's object); RAISED 0 (elrule new [] closed []); UNPREDICTED 2 =
  A45 t_ci7 group [t_ci7,w_ci7_in,w_ci7_inc], A49 t_co7 group [t_co7,w_inc7_co,w_co7_r] (register_end_case_border; step 2's same verb left +2
  loose ends, unattributed); STANDING 53; TOTAL 53 (upper 55). compare(read 53, file) 0/0; compare(read, predicted) extra 0 missing 0.
- STALE (not changed, reported): items 4, 6, 7 (clears_by step 3 'A70 w_k3f') and 8, 49, 50 ('A80 w_k4f') - not actions of this plan
  (group I alone, PD396(c)); they stay STANDING.
- DRY main (`prep_c163_a1_3_dry.log`): L0, SG, L1, E1, NG, FR, D, TD PASS; CEN2 UNPREDICTED (:48); `FAIL PB ...` (:54) -> `=== DRY FAIL:
  first_fail=GATE PB frame-keyed cdiff(S1, real end) by POSITION ...` rc=1. DRY scratch (`prep_c163_a1_3_scr_dry.log`): same PB FAIL, rc=1.
- PB detail (:54): eq_diff [] (real == sim re-keyed); blocked #376 'error in' (S1 uids [3934,4965] vs end [3934,3934,4965,4965], frames
  [31506,31506,31517,31517], inherited [31506]) and #376 'total data array in' ([1842,3954] x2, same frames); pairs_extra_left those 2; recorded 3
  (cal cluster path, file size, selected path). Both rows were wired by STEP 2 (w_g376 / w_h376, PB class 2 x[2] in diag_c162_a1_2_scr_dry.log).
- Logged fp-86 (checker:stagekit:PB): no PB class for a row an EARLIER step wired into an inherited case on 2 frames. No release -> BLOCKED.
- NOT RUN (return at the first unexpected result): prerun (X10/X14/X17/X8), --check-launch, --scratch-required, prior-art.
- Commands for later: scratch `py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c163_p5s02c_scratch.log -- py -u
  tools/recipes/stage_d1_ring_p5s02c_scratch.py --unverified-card <launch card>`; real `py tools/bgrun.py --material --max-min 50 --log
  tools/bench/launch_c163_p5s02c.log -- py -u tools/recipes/stage_d1_ring_p5s02c.py`. diag_c163_p5s02c_scratch.log does not exist yet.
- md5 UNCHANGED (`prep_c163_a1_3_md5.log` U 13/13): stagesim 95a162ba, stagexec a4df7e15, stagekit 9b8f82c1, stage_prerun 7605116f, stage_shared
  b688edd4, memory_model def9e640, plan 930699ec, graph 431cfd83, EL 60e02787, VIs f9ae7751 / 94ffff94 / 7f2582ae / eb1d0f31. No tool/hook edit.
  LabVIEW never launched (all runs offline, COM stubbed).
- OPEN: fp-86 - PB (stagekit.pb_386) needs a licence class for rows a PREVIOUS step wired into an inherited case on several frames (or the
  step-2 class-2 rows carried into step 3's inherited set); tooling card, outside this card's globs.
- OPEN: copied logic without a shared function: EL-row raised-owner attribution (prep_c160_c3_1_el.py:106-114 vs prep_c163_a1_3_el.py
  raised loop); pred/EL maker flow (prep_c160_c3_1_pred.py / _el.py are top-level scripts, not importable).
- OPEN: check-launch needs a card naming `DRY-UNVERIFIED-OK: CEN2 new-object census` (stage_prerun.py:3432-3456); this card names none.
