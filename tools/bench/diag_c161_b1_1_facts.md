---
type: facts
status: current
date: 2026-10-10
card: 161-b1-1
---
# 161-b1-1: makers re-pinned to stagexec a4df7e15, pred re-made (checkpoint set only); recipe DRY runs all 10 ops (past 5 and 9) then FAILS gate PB; NOT launched
- Re-pin (stagexec ddf23a31 -> a4df7e15 only): `prep_c160_c3_1_md5.py:17`, `prep_c160_c3_1_pred.py:39`, `prep_c160_b3_1_mk.py:46` (b3_1_mk NOT re-run: it rewrites the plan).
- Pred maker E1 gate edited (`prep_c160_c3_1_pred.py:72-75`): expected `session [0,2,3,5,7,9,10]` -> `session | delete_wire ops [1,4,8]` (PD393(a)); else it fails on the stale b3-1 session set.
- md5 `prep_c161_b1_1_md5a.log`: `GATE PASS | U 14 pinned files unchanged | []` rc=0 (incl. the 4 VIs s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae, p5s02a 94ffff94 by prefix).
- pred `prep_c161_b1_1_pred.log` 14/0 rc=0: `GATE PASS | E1 checkpoints [0, 1, 2, 3, 4, 5, 7, 8, 9, 10] == stagexec.checkpoint_ops == session [0, 2, 3, 5, 7, 9, 10] | delete_wire ops [1, 4, 8]`.
- CHANGED plan_ring_p5s02b_pred.json 48b50b29 -> 187294099b3d8ced0e1c0b29b7c3a959; diff vs `prep_c161_b1_1_old_pred.json`: 3 new `e1.checkpoints` rows
  (op 1 dw_a13 step_01 13ed9171, op 4 dw_go step_08 3ead0987, op 8 dw_ho step_16 54b5d4a6), `memory_pred.checkpoints` + 1, 4, 8, `sg_census_file.md5` 287827be -> ee18cbf8.
- CHANGED prep_c160_c3_1_session.json 287827be -> ee18cbf8d47b7f16d093a2193b689ea2; diff: `checkpoints` + 1, 4, 8 only.
- UNCHANGED licence f61a2514 (`prep_c161_b1_1_licence.log` 5/0), EL 79ec3207 (`prep_c161_b1_1_el.log` 9/0, total 51), recipes 083fda6d / 3f6fb898 (no edit:
  the recipe takes `RingSession.CHECKPOINTS = SX.checkpoint_ops(ops)`, `tools/stagekit.py:2376`; only docstring `stage_d1_ring_p5s02b.py:15` still says [0,2,3,5,7,9,10]).
- Pred X10 still on the OLD set: `FACT X10 ... N 10 R 7 ... MAIN 653.7; at START_ASSUMED 603.4: peak 652.3 MAIN 657.4` with `'checkpoints': [0, 2, 3, 5, 7, 9, 10]`
  (`prep_c161_b1_1_pred.log`) - `prep_c156_a1_1_lib.main_of` :98 hand-codes BIND|{0,n}, bypassing `stagexec.checkpoint_ops` (outside this card's globs).
- DRY recipe `prep_c161_b1_1_dry.log` rc=1 after 66s: STEPX 01..10 every checkpoint diff 0 (op 05 :37, op 09 :45 PASS, 06 not a checkpoint); E1, NG, FR, D, TD PASS;
  `UNPREDICTED CEN2` (:52); `FAIL PB frame-keyed cdiff(S1, real end) by POSITION ... ([31, 31] rows) and == the pred's 26 rows (26 slots) + 0 RECORDED tag-only row(s),
  the plan's 24 open (node, term) pairs` (:55): `eq_diff []`, `pairs_extra_left [(376,'cal cluster path'),(376,'error in'),(376,'file size'),(376,'selected path'),(376,'total data array in')]`;
  blocked whys: frame tags not the plan's frame(s) [] (3 sinks), source terminal uids doubled vs S1 (error in, total data array in).
- `=== DRY FAIL: first_fail=GATE PB ... coverage 34/36 lines, first mutation Stage._op delete_wire, unverified 1` (:57). No JEV-LADDER row for this log yet.
- NOT RUN (return at first unexpected result): scratch dry, prerun (X10/X14/X17/X8), --check-launch, --scratch-required, prep_c160_c3_3_hash.py.
- md5 UNCHANGED: stagesim 95a162ba, stagexec a4df7e15, stagekit 0b5bb678, stage_prerun 7605116f, plan f4520b10. No --launch, no LabVIEW process, no tools/*.py or hook edit.
- OPEN: PB is the new first failure now that the dry gets past ops 5/9 - plan/pred open-pairs (24 / 26) vs real 31 rows on #376: plan defect or PB key defect? (judgement)
- OPEN: pred memory_pred.peak_mb / main_peak_mb are on the old checkpoint set (main_of hand-copy); X10 with the 3 extra reads is unmeasured until prerun runs.
