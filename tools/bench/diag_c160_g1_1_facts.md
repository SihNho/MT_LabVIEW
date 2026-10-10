---
type: facts
status: current
date: 2026-10-10
card: 160-g1-1
---
# 160-g1-1: whole-group split of A41..A80 (PD390(d)); offline, no LabVIEW, no plan written
Run `py tools/bgrun.py --material --max-min 10 --log tools/bench/diag_c160_g1_1.log -- py -u tools/bench/diag_c160_g1_1.py` -> RESULT PASS 6/0 (log:21).
Calls: prep_c159_c1_1_lib map_symbols/map_frames/apply_map/bound_from_cmap, stagexec.compile_plan + plan_base_owners, stage_prerun.load_creation_map,
prep_c156_a1_1_lib.main_of (= stage_prerun.x10_model_peak + 2 reads), the same calls as prep_c159_c1_1_mk.py:84-146.
- A24..A80 compiles to 35 ops (no delete action); no op spans a group boundary (log:5).
- REPRO: today's bytes give the 159 cumulative MAINs exactly: DEL 632.3, F3 633.7, G 645.4, H 654.6, I 678.3, J 694.4 (log:6 vs prep_c159_c1_1_mk.log:48-71).
- START_ASSUMED 603.4 (log:7; prep_c156_a1_1_session.json start_mb). Fresh MAIN = main_of over the group's ops only, from 603.4.
## Groups (status from prep_c156_a1_1_session.json census; ops from log:8-13)
| group | actions | status (session.json line) | ops | op kinds | fresh MAIN |
|---|---|---|---|---|---|
| I | A41-52 (12) | OK (:293-295) | 8 | add_sr, create, connect, create, connect_term_uid, case_frame_wire, connect_term_uid, case_frame_wire | 654.6 |
| J | A53-60 (8) | OK (:341-343) | 8 | delete_wire, delete_object x2, create x2, branch, connect, stop | 647.1 |
| K3 | A61-69 (9) | GAP (:382-396) | 5 | add_sr, create, connect, connect_term_uid x2 | none |
| K3f | A70 (1) | BLOCKED (:401-407) | 1 | branch | none |
| K4 | A71-79 (9) | GAP (:412-426) | 5 | add_sr, create, connect, connect_term_uid x2 | none |
| K4f | A80 (1) | BLOCKED (:431-437) | 1 | branch | none |
## Rule applied
Greedy prefix of whole OK groups with fresh MAIN <= 675 per step, new instance per step from 603.4; a step ends before a group that would exceed 675
or at a GAP/BLOCKED group. I+J fresh = 670.7 <= 675 (log:19), so I and J form one step; K3 (GAP) ends it.
## Steps
| step | actions | groups | ops | MAIN | start file | saved in-between file pattern |
|---|---|---|---|---|---|---|
| p5s02c | A41-A60 (20) | I J | 16 | 670.7 (log:14) | step 2's saved file `D1_ring_p5s02b_<YYYYMMDD_HHMMSS>.vi` (not on disk yet) | `claudeDev\D1_ring_p5s02c_<YYYYMMDD_HHMMSS>.vi`, graph `tools/bench/graph_ring_p5s02c_<YYYYMMDD_HHMMSS>.json` |
| - | A61-A69 (9) | K3 | 5 | none: GAP, no MAIN | - | - |
| - | A70 (1) | K3f | 1 | none: BLOCKED | - | - |
| - | A71-A79 (9) | K4 | 5 | none: GAP, no MAIN | - | - |
| - | A80 (1) | K4f | 1 | none: BLOCKED | - | - |
Name pattern follows `D1_ring_p5s02a_20261010_023239.vi` / `graph_ring_p5s02a_20261010_032547.json`; no timestamp invented. Only p5s02a is on disk in claudeDev.
## What GAP/BLOCKED are missing (session.json census `error`)
- K3 :396 "action 69 (wire w_k3pass): wire new:IK3.inner -> new:OK3.inner: source on diagram -30, sink on diagram -29 - a border needs a tunnel/register action first" (stage sim, tool null).
- K4 :426 same text for w_k4pass (new:IK4.inner -> new:OK4.inner; the error names "action 69" too).
- K3f :407 "depends on ['K3']"; K4f :437 "depends on ['K4']" (stage dep).
## Pins
stagekit 1441bb4c, stagesim a3261b56, stagexec c4a6e0b6, stage_prerun 7605116f, plan input 56bfddd3, graph 7ac24924, memory_model 5b87de43: gate M0 before and U after (log:3,20). tools/hooks untouched.
OPEN: K3/K4 compile to ops (5 each) although the census marks them GAP at the sim stage, so "no compile" is not literally true; a MAIN could be computed. Should it be?
OPEN: K4's census error says "action 69" for w_k4pass, which is A79 in plan_ring_p5s02r_in.json. Is that a stale label in the census text or a different numbering?
