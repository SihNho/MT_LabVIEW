---
type: facts
status: current
date: 2026-10-10
card: 161-b2-1
---
# 161-b2-1: offline pre-check of the p5s02b step-2 launch on the final tools - every gate as PD393(c)/PD395 expect; NOT launched
No LabVIEW process opened; every run under bgrun --material; no --launch; nothing edited except this file and the logs below.
## 1. Dry (form of prep_c161_b1_1_dry.log)
- prep_c161_b2_1_dry.log:65 `=== DRY PASS-UNVERIFIED CEN2 new-object census (classes of the pred) == plan_ring_p5s02b_pred.json census: first_fail=None
  coverage 35/36 lines, first mutation Stage._op delete_wire, unverified 1, graph tools/bench/graph_ring_p5s02a_20261010_032547.json`; :67 `BGRUN END rc=0 after 77s`.
- prep_c161_b2_1_dry_scratch.log:86 same line with `coverage 34/37 lines ... unverified 1`; :88 `BGRUN END rc=0 after 76s`.
- The only unverified label (both): `UNPREDICTED  CEN2 new-object census ... (declared set empty {}; measured {})` (dry.log:52, dry_scratch.log:66). No FAIL line in either.
- PB (dry.log:60, dry_scratch.log:77): `PASS  PB ... == the pred's 26 rows (26 slots) + 5 RECORDED tag-only row(s), the plan's 24 open (node, term) pairs`
  `'blocked': [], 'pairs_extra_left': [], 'pairs_missing': [], 'recorded': ['376|Terminal|cal cluster path|0', '376|Terminal|error in|0',
  '376|Terminal|file size|0', '376|Terminal|selected path|0', '376|Terminal|total data array in|0'], 'unlicensed': []`.
  (b1-1, prep_c161_b1_1_dry.log: PB FAIL, 0 RECORDED, 5 pairs_extra_left.)
- Past ops 5 and 9: dry.log:37 `STEPX 05 connect_term_uid ... bound {-12: 10000014} diff 0`, :45 `STEPX 09 ... bound {-24: 10000026} diff 0`, :47 `STEPX 10 case_frame_wire ... diff 0`.
## 2. Prerun (prep_c161_b2_1_prerun.log, recipe stage_d1_ring_p5s02b.py)
- :88 `=== PRERUN PASS: 16 pass / 0 fail; first None`; :90 `BGRUN END rc=0 after 78s`.
- X10 :82 `N 10 ops, BIND 5, R 12 reads, predicted peak 661.3 MB (fail above 680.0)`; :84 `PASS X10 ... (peak 661.3 MB)` recorded `UNMEASURED: no recorded meter ... (0 record(s))`.
  The prerun log never prints 675 or 665. The 675 test is the pred's: plan_ring_p5s02b_pred.json:656 `main_peak_at_start_assumed_mb 665.0`, :657 `card_limit_mb 675.0` (665.0 <= 675).
- X14 :85 `WARN X14 rows 20, budget 15 (proven: no)`; X17 :73 `PASS ... 0 primitive create action(s)`; X8 :67 `PASS X8 control_path_lint ... 1 stageplan(s)`.
- Other WARN: :71 `X13 WARN wire_sr.json: 2 sample(s), no replayer for op 'wire_sr'`.
## 3. --check-launch (no --launch)
- prep_c161_b2_1_checklaunch.log (_scratch.py): `ALLOW`, `BGRUN END rc=0 after 1s`.
- prep_c161_b2_1_checklaunch_main.log (stage_d1_ring_p5s02b.py): `ALLOW`, `BGRUN END rc=0 after 1s`.
## 4. --scratch-required (prep_c161_b2_1_scrreq.log)
- `SCRATCH-REQUIRED | stage_d1_ring_p5s02b.py | CENSUS-UNPREDICTED tools/bench/plan_ring_p5s02b.json rows [1..20] - the scratch run measures the census before the ONE launch`; `BGRUN END rc=3` (expected 3).
## 5. VI hashes (prep_c161_b2_1_hash.log, prep_c160_c3_3_hash.py, 4/0) - all EQUAL
- s09 D1_ring_p4s09_20261009_060515.vi eb1d0f31; P5-1a D1_ring_p5s01a_20261009_101219.vi 2482fe7b; P5-1 D1_ring_p5s01_20261009_124542.vi 7f2582ae;
  p5s02a D1_ring_p5s02a_20261010_023239.vi 94ffff94. claudeDev holds exactly one *p5s02* file: `D1_ring_p5s02a_20261010_023239.vi`.
## 6. md5 UNCHANGED after the card
pred a1fd43fb, plan f4520b10, licence f61a2514, EL 79ec3207, recipe 083fda6d, _scratch 3f6fb898, stagekit 9b8f82c1, stagesim 95a162ba, stagexec a4df7e15, stage_prerun 7605116f.
OPEN: --check-launch ALLOWs the main recipe (rc 0) while --scratch-required returns 3 for it; the launch gate's ordering relies on the scratch run being made first.
OPEN: prerun X10 judges 661.3 vs 680.0 (memory_model) and does not check the card's 675 at START_ASSUMED; that check lives only in the pred maker.
