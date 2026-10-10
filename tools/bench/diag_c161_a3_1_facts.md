---
type: facts
status: current
date: 2026-10-10
card: 161-a3-1
---
# 161-a3-1: PB class 1 / class 2 BUILT and green (10/0); pred NOT re-made - its X10 gate compares to the old-rule session MAIN
Offline only, no LabVIEW process. Runs under bgrun --material; logs named below.
## 1. Shared functions (tools/stagekit.py 9b8f82c1)
- `pb_inherited_row(sink, y, res, G1, S1f, bound_end, ctx)` `stagekit.py:2093` - THE one function that records class 1 (PD394(a)) and class 2
  (PD395(b) (i)-(iv)); returns (1|2|None, why, action id). `PD374D_PASSTHROUGH` `:2030` = (376 error in), (376 total data array in).
- `pb_inherit_ctx(plan, flat, base_vi_md5=None, labels, fs_pairs, S1f, V, adopt_path)` `:2033` - adopt chain from the base VI md5
  (adopted_scratch.jsonl), frames via each step's scratch-json `stagexec` bindings; = the chain walk of prep_c161_a2_1_measure.py:43-59, extracted.
- PB extended, not duplicated: `pb_check_bound(..., inherit=None)` `:1979` calls pb_inherited_row at `:2011` only for a row the PD386(a)
  rule blocks; `pb_386(..., inherit=None)` `:2135` builds the ctx at `:2148` (None = on, False = off) and returns inherit_frames / inherit_missing.
- Call sites: RingSession.gate_pb `stagekit.py:2656` (unchanged) -> pb_386 -> on by default; recipes p5s01b / p5s02 / p5s02a / p5s02b /
  template call RS.gate_pb (stage_d1_ring_p5s02b.py:53; the _scratch imports that body, :24). No other pb_check_bound caller in a recipe.
## 2. selftest_c161_pbinherit.py (130 lines) -> selftest_c161_pbinherit.log: 10/0
- C0 ctx: inherited {376,3052,3453: [31506]}; cases {31308: [31506,31517], 30726: [30914,30922]}; missing []; chain = 11 records (p5s02a..p4_s02).
- A1 p5s02b sim end: RECORDED 5 = class 1 cal cluster path, file size; class 2 selected path (w_in3_376), error in (w_g376), total data array
  in (w_h376); ok True, pairs_extra_left []; eq_diff / pairs_missing / n_rows / pb_check dict == inherit off (off: 0 recorded, 5 blocked, 5 left).
- B1 changed source uid, B2 frame of a non-adopted case, B3 f1 tag on selected path (mult 2 = frame count), B4 no connect action (also
  pb_check_bound not ok), B5 multiplicity 3 / 2 -> each BLOCKS.
- R stored runs, inherit off == on: p5s01a ok, 21/21 rows, 0 rec (stored PB PASS diag_c154_p5s01a_scratch.log:240, cdiff 21); p5s01b ok, 21/21,
  0 rec (diag_c155_p5s01b_scratch.log:158); p5s02a ok, 31/31, 2 rec (cal cluster path, file size) (diag_c158_p5s02a_scratch.log:282).
## 3. Pin sweep (listed before the edit: grep -l 0b5bb678 = 10 files) - prep_c161_a3_1_suite_before.log / _after.log
- Re-pinned stagekit only, before -> after: c155_basecase_frame 21/0 -> 21/0, c156_b2_2_invcheck 20/0 -> 20/0 (want line + pin),
  c156_passwire 20/0 -> 20/0, c160_delwire 20/0 -> 20/0, c160_regface 12/0 -> 12/0, prep_c160_c3_1_md5 -> 1/0, prep_c160_c3_1_pred (section 4).
- selftest_c161_delckpt 9/2 -> 9/2: both fails PRE-EXISTING (before any edit): D2 expects the stored pred set (0,2,3,5,7,9,10) but pred
  18729409 holds (0,1,2,3,4,5,7,8,9,10); P pins pred 48b50b29. Not loosened; its pred pin not touched (the pred did not change here).
- prep_c160_b3_1_mk / prep_c160_b1_1_mk NOT re-pinned, NOT run: plan makers (b3_1 writes plan_ring_p5s02b_in2 / plan); b1_1 outside write globs.
- Suites: s4 24/0, c157 13/0, t7_ring 35/0, c158_gates386 16/0 (unchanged before/after).
## 4. PD394(b) - pred MAIN on SX.checkpoint_ops: FAIL at the maker's X10 gate, pred NOT written
- prep_c156_a1_1_lib.py:99 now `cps = list(SX.checkpoint_ops([{"kind": k} for k in KINDS[:n]]))` (was BIND|{0,n}).
- prep_c161_a3_1_pred.log:10 `FACT X10 at start 599.7: Executor peak 656.2 MAIN 661.3; at START_ASSUMED 603.4: peak 659.9 MAIN 665.0`, limit 675:
  both <= 675. Checkpoints [0,1,2,3,4,5,7,8,9,10], R 10.
- prep_c161_a3_1_pred.log:11 GATE FAIL (fatal, before any write): X10 also requires peak == session 652.3 and MAIN == session 657.4
  (prep_c160_b3_1_session.json x10, made on the old BIND|{0,n} rule); new 659.9 / 665.0 (+7.6 MB). So pred stays 18729409, licence / EL makers not run.
- prep_c161_a3_1_lib.log:5 lib --selftest 2/1: T3 main_of(155 step 1, 19 ops) 682.5 != stored 680.0 (same cause: shared rule adds checkpoints).
## 5. md5
- Changed: stagekit 0b5bb678 -> 9b8f82c1 (PB classes); prep_c156_a1_1_lib -> 5ade19fe (shared checkpoint rule); prep_c160_c3_1_pred -> fd94f035
  (stagekit pin); 7 self-test / md5 files (pins); new selftest_c161_pbinherit 9be05189, prep_c161_a3_1_{probe,probe2,suite}.py.
- UNCHANGED: stagesim 95a162ba, stagexec a4df7e15, stage_prerun 7605116f, plan f4520b10, pred 18729409, licence f61a2514, EL 79ec3207.
- guard_write warned: open card 160-c3-2 pins stagekit 0b5bb678 (stale now; not in my write globs).
OPEN: the maker's X10 gate equates MAIN to the b3-1 session value made on the old checkpoint rule; replace that equality (and lib T3 680.0) by
the shared-rule numbers 665.0 / 659.9 (and 682.5), or keep them? (judgement - not changed here)
OPEN: delckpt D2 / P were written against pred 48b50b29 and fail since 161-b1-1 re-made the pred; re-pin / restate them? (judgement)
