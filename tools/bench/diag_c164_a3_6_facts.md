---
card: 164-3-6
date: 2026-10-10
status: current
---
# 164-3-6 facts (offline; no LabVIEW) - plan re-made with plan_in plan_ring_p5s02d_in2.json; both dries PASS-UNVERIFIED (CEN2 only); NOT launched
- Plan: `prep_c164_a3_6_mk.py` = ONE call of `prep_plan_flow_lib.make_step_plan` with 164-3-1's arguments (prep_c164_a3_1_mk.py:53-55), only
  plan_in = `tools/bench/plan_ring_p5s02d_in2.json` (dc309d2c, byte-equal to prep_c164_a3_1_plan_in.json), session `prep_c164_a3_6_session.json`
  (f0965880), keep_prev `plan_ring_p5s02d_prev725cd68e.json` (725cd68e, `prep_c164_a3_6_mk.log` ASIDE PASS). NEW plan `plan_ring_p5s02d.json` 97837e2a,
  final True, written by stagesim.simulate (SB REALSIM FINAL PASS, route PASS, 0 UNROUTABLE, 0 PROVISIONAL).
- Compare vs 725cd68e (`prep_c164_a3_6_mk.log`): actions (19, A53..A71), open_rows, base, context, schema, stage, goal, final, finalized/end_cdiff_rows,
  open_rows_match (True), finalized/base, route_check all EQUAL; 15 ops, checkpoints [0,1,2,6,7,11,12,14,15], MAIN 647.8. END w23460 0 rows; w23519
  src t8494 sinks {23450, 23241, 7606}. Differing leaf keys (3): `/finalized/at` (14:48:07 -> 15:10:52), `/finalized/plan_in/path`
  (prep_c164_a3_1_plan_in.json -> plan_ring_p5s02d_in2.json), `/finalized/summary/md5` (83887b66 -> d76b10c2; summary.json:5 holds the plan_in path).
  The mk log ends RESULT FAIL 42/1: its own CMP whitelist omitted the `finalized/at` timestamp (driver prediction error, not a row/op diff).
- X11 `prep_c164_a3_6_x11.log:3` CLEAN. Licence `prep_c164_a3_6_licence.log` 5/0: d9d0810d, 0 renames.
- Error List `prep_c164_a3_6_el.log` 10/0: `errorlist_predicted_D1_ring_p5s02d_end.json` 2c1edf78; `EL COUNTS cleared 0 raised 0 unpredicted 3 standing 53
  stale 6 total 53 (upper 56)` (:22); unpredicted A66 t_k3o, A69 t_k3i (reb), A56 do_23501 (w23519); stale items 4/6/7 (A70 w_k3f), 8/49/50 (A80 w_k4f);
  compare B / F / W extra 0 missing 0.
- Pred `prep_c164_a3_6_pred.log` 17/0 -> `prep_c164_a3_4_session.json` 9ff1b285 (SG census, 0 rows); PD399(a) `prep_c164_a3_6_pd399.log` 5/0
  (driver `prep_c164_a3_4_pd399.py 97837e2a`, plan pin now argv[1], default 725cd68e) -> pred `plan_ring_p5s02d_pred.json` 87a65b89.
  Ops delete_wire 2, delete_object 2, wire_remove_loose_ends 1, create 3, connect 3, stop 1, add_sr 1, connect_term_uid 2; census UNPREDICTED 19 rows.
- Recipes: docstring md5 725cd68e -> 97837e2a only (line counts unchanged): main f3581d02, scratch 3d77e914.
- DRY main `prep_c164_a3_6_dry.log:78` `=== DRY PASS-UNVERIFIED CEN2 new-object census ... first_fail=None coverage 35/36`, rc 0 (:80).
  DRY scratch `prep_c164_a3_6_scr_dry.log:105` same, coverage 34/37, rc 0 (:107).
- PB (dry :73 / scr :94) PASS by POSITION, 31/31 rows == pred 26 + 5 RECORDED, 24 open pairs, blocked []. RECORD rows (dry :68-72): 376 'cal cluster path',
  'file size', 'selected path' class 1 (PD394(a)); 376 'error in', 'total data array in' class 3 (fp-86). No PB BLOCK.
- PRERUN main `prep_c164_a3_6_prerun.log:105` `=== PRERUN PASS: 16 pass / 0 fail`: X8 PASS (:80), X17 PASS (:90), X10 PASS peak 647.8 <= 680 (:101),
  X14 WARN rows 19 budget 15 proven no (:102). Scratch `prep_c164_a3_6_scr_prerun.log:132` PASS 16/0, X10 642.7 (:128), X14 WARN (:129).
- `--scratch-required` `prep_c164_a3_6_scrreq.log:3` rc 3: `SCRATCH-REQUIRED | stage_d1_ring_p5s02d.py | CENSUS-UNPREDICTED ... rows [1..19] - the scratch
  run measures the census before the ONE launch`.
- check_launch full scratch cmd + `--unverified-card tools/bench/cards/task_164-3-5.json` (`prep_c164_a3_6_release.log`): REFUSE, newest dry PASS-UNVERIFIED
  (15:19:00), CEN2 unnamed, `task_164-3-5.json does not load: [Errno 2]`. Stand-in (`prep_c164_a3_6_checklaunch.log`): own card task_164-a2-3.json REFUSE
  (names no DRY-UNVERIFIED-OK); task_163-a2-2.json (rules carry DRY-UNVERIFIED-OK: CEN2) ALLOW. Scratch log diag_c164_p5s02d_scratch.log absent.
- Prior art c164-a2-3 on final bytes (`prep_c164_a3_6_release.log`): RELEASED ['contradicted', 'settled-already'] REJECTED []; FIXEDCLAIM both recipes
  claimed True released True; STOPREC scratch (sha ca0c1bde684c) and main (c9377ad5eeb1): kind blocking state released decision(build) allow. 5/0.
- Commands: scratch `py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c164_p5s02d_scratch.log -- py -u
  tools/recipes/stage_d1_ring_p5s02d_scratch.py --unverified-card tools/bench/cards/task_164-3-5.json`; real `py tools/bgrun.py --material --max-min 50
  --log tools/bench/launch_c164_p5s02d.log -- py -u tools/recipes/stage_d1_ring_p5s02d.py`.
- md5 UNCHANGED (`prep_c164_a3_6_md5.log` 1/0): stagesim 95a162ba, stagexec a4df7e15, stagekit dd57c1ca, stage_prerun 7605116f, stage_shared b688edd4,
  memory_model 8fb432e4, r_in 9dadb0c1, prev plan 725cd68e, graph 3d5196ab, EL 26d45c71, VIs 564d8cbe / f9ae7751 / 94ffff94 / 7f2582ae / eb1d0f31.
  No tool / hook / doc edit; review file af784c98 unchanged.
- OPEN: card pass 1 says only plan_in/md5 keys differ; `finalized/at` (sim timestamp) also differs - accept as a non-row key?
- OPEN: launch card task_164-3-5.json must exist with `DRY-UNVERIFIED-OK: CEN2 new-object census` before the scratch launch (gate needs the file).
