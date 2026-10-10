---
type: facts
status: current
date: 2026-10-10
card: 161-a3-2
---
# 161-a3-2: PD394(b) finished offline - X10 restated on the shared checkpoint rule in a NEW record, pred re-made 18729409 -> a1fd43fb
No LabVIEW process; every run under bgrun --material; MAIN 665.0 <= 675 (no hand-back).
## 1. New record tools/bench/prep_c161_a3_2_x10.json (md5 4d339c0f), made by prep_c161_a3_2_x10.py (1a4b6fa5, 51 lines, calls L.main_of only)
- prep_c161_a3_2_x10.log:3 `FACT X10 p5s02b at START_ASSUMED 603.4: checkpoints [0,1,2,3,4,5,7,8,9,10] exec_peak 659.9 MAIN 665.0
  (old BIND rule: exec_peak 652.3 MAIN 657.4); T3 155 step 1: 19 ops MAIN 682.5 (old 680.0)`; gates 2/0.
- Keys: rule_fn `prep_c156_a1_1_lib.main_of -> stagexec.checkpoint_ops + stage_prerun.x10_model_peak`, cause `PD394(b) checkpoint rule`,
  old {exec_peak 652.3, main 657.4} read from prep_c160_b3_1_session.json x10, lib_t3 {main 682.5, old_main 680.0}, limit 675,
  pins (full md5) of plan, b3-1 session, plan_ring_p5s02, prep_c155_a4_1_session, memory_model, stagexec, stage_prerun, stagekit, lib (25a01f0b).
- prep_c160_b3_1_session.json untouched: e5279899 (x10 gate W).
## 2. Pred maker X10 gate (prep_c160_c3_1_pred.py b5d596dc, lines 88-90; line count unchanged)
- :88 loads the record (missing -> {}), XOK = every record pin == current md5; :90 `mp["ok"] and MAIN <= LIMIT and XOK and
  XR["start_assumed_mb"] == SA and mpa["peak_mb"] == XR["exec_peak"] and MAINA == XR["main"] and MAINA <= LIMIT` (== kept, LIMIT 675.0 at :41).
- prep_c161_a3_2_pred.log:11 `GATE PASS | X10 MAIN 661.3 (start 599.7) <= 675.0; at START_ASSUMED 603.4: Executor peak 659.9 == x10 record 659.9,
  MAIN 665.0 == x10 record 665.0 <= 675.0; record present + pins match True`; whole maker 14/0 (:23).
## 3. Pred re-made: 187294099b -> a1fd43fb121a7a9ea234d562794ac509 (prep_c161_a3_2_diff.log, 3/0)
- Moved keys (all): memory_pred.R 7->10, peak_mb 648.6->656.2, main_peak_mb 653.7->661.3, peak_at_start_assumed_mb 652.3->659.9,
  main_peak_at_start_assumed_mb 657.4->665.0, sg_census_file.md5 ee18cbf8->cea6e1e9. Checkpoint lists did NOT move (18729409 already held the new set).
- prep_c160_c3_1_session.json ee18cbf8 -> cea6e1e9: main_peak_mb 653.7->661.3, main_peak_at_start_assumed_mb 657.4->665.0 only.
- Before copies: prep_c161_a3_2_pred_before.json (18729409), prep_c161_a3_2_sgsession_before.json (ee18cbf8).
- Licence / EL makers NOT run: their inputs (plan f4520b10, b3-1 session e5279899, graph 7ac24924, expected 1fd016bf) did not move.
## 4. Consumers restated (same cause)
- lib --selftest T3 reads the record's lib_t3 (prep_c156_a1_1_lib.py:139-141): prep_c161_a3_2_lib.log 3/0 (T3 682.5 == 682.5; old 680.0 == session).
- selftest_c161_delckpt D2 reads the record's checkpoints and the pred's stored sets (:97-99); P re-pins pred only 48b50b29 -> a1fd43fb (:138):
  selftest_c161_delckpt_c161_a3_2.log 11/0 (was 9/2).
## 5. Re-run counts (logs *_c161_a3_2.log)
- selftest_c161_pbinherit 10/0, selftest_stagexec_s4 24/0, selftest_c156_b2_2_invcheck 20/0, selftest_c157_innerface 13/0, prep_c160_c3_1_md5 1/0.
- Pred-md5 pins listed BEFORE editing (grep 18729409 over tools/**/*.py): no selftest_*.py; only a docstring in prep_c161_b1_2_measure.py:12
  (not a pin, outside write globs, not edited). Pins of 48b50b29: only selftest_c161_delckpt.py (re-pinned). No .py pins lib 5ade19fe / maker fd94f035.
## 6. md5
- Changed: lib 5ade19fe -> 25a01f0b (T3 + 2 docstring lines), pred maker fd94f035 -> b5d596dc, delckpt -> 9bd4889a, pred -> a1fd43fb,
  SG census file -> cea6e1e9; new prep_c161_a3_2_x10.py / .json, prep_c161_a3_2_diff.py (7efe31c7).
- UNCHANGED: plan f4520b10, stagesim 95a162ba, stagexec a4df7e15, stage_prerun 7605116f, stagekit 9b8f82c1, licence f61a2514, EL 79ec3207, b3-1 session e5279899.
## 7. Card 160-c3-2: never ran (guard_assign refused its dispatch, fp-83, assign_result_160_2.json:26); re-issued as 160-c3-3
  (brief_160-c3-3.md:6). No result_160-c3-2.json exists; its task file still pins stagekit 0b5bb678 (not edited).
OPEN: open cards pinning pred 18729409 (task_161-a2-1 / -a3-1 / -a3-2 / -b1-2 inputs) are now stale by md5; the next card should pin a1fd43fb.
