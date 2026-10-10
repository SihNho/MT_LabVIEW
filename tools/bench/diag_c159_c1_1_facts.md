---
type: facts
status: current
date: 2026-10-10
card: 159-c1-1
---
# 159-c1-1: split check on the real 94ffff94 graph + plan_ring_p5s02b (offline; no LabVIEW, not launched)
Run `py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_c159_c1_1_mk.log -- py -u tools/bench/prep_c159_c1_1_mk.py` -> RESULT FAIL 20/1
(only gate SB fails, which the script predicted). Mapping is done by `prep_c159_c1_1_lib.py`, whose self-test passes 3/0 (`prep_c159_c1_1_lib.log`).
## Split (PD388(h)), from `prep_c159_c1_1_mk.log`
- Groups in A24..A80 (log:6-14): F3 A24-26 | G A27-33 | H A34-40 | I A41-52 | J A53-60 | K3 A61-69 (GAP) | K3f A70 | K4 A71-79 (GAP) | K4f A80.
- J ends at A60 and K3 starts at A61, so no group crosses. Delete + A24..A80 compiles on the real owners to 36 ops; no op spans A60/A61 (log:32).
- Planned MAIN uses START_ASSUMED 603.4 (unchanged). x10_start(94ffff94) = 599.7 = 593.8 + 5.9 (log:46). MAIN at each group end (log:48-71):
  DEL 632.3, F3 633.7, G 645.4, **H 654.6**, I 678.3, J 694.4.
- **Verdict:** delete + A24..A60 = 694.4 > 675, so the rule cuts at the last whole group that fits: **A40 (end of H), 8 ops, MAIN 654.6** (log:72).
  Step 2 = 18 actions. Remainder = A41..A80, 40 actions, groups I J K3 K3f K4 K4f (log:74).
## Plan
- Input `plan_ring_p5s02b_in.json` 56bfddd3: 18 actions, 24 open rows, validates against stageplan/1 (log:100). Output `plan_ring_p5s02b.json` caef7e1c, **final False**.
- Action 1 = `delete_wire` w10394. The uid is read from P5-1's #3052 'File # Saved' row, not typed. In 94ffff94 it is a Wire obj with 0 terminal rows,
  and #3052 now feeds w11774 (log:30-31).
- Step-1 symbols mapped through the creation map `plan_ring_p5s02a_4284c22a_20261010_023453.jsonl`: CQ7 -> #31308, f0 -> #31506, f1 -> #31517.
  Seven frame ends: 'False' -> '#31506', 'True' -> '#31517' (log:18-29).
- Compile (stagexec.compile_plan, real owners) passes: 8 ops = delete_wire 1, tunnel 5, case_frame_wire 2; checkpoints [0,2,3,4,6,7,8];
  Executor peak 649.5; MAIN 654.6. X8 and X17 clean (log:108-111).
- **REALSIM refuses action 1:** "delete_wire: wire 10394 is not in the current graph" (log:105). Predicted: stagesim.py:1424-1426 needs terminal rows
  of the wire. stagexec also resolves delete_wire by terminals (stagexec.py:2843-2851). The route check did not run.
- Probe = the same 17 rows without action 1: replays on 94ffff94 with failed null, 0 PROVISIONAL, 26 end rows, all tied (log:93,99).
## MERGE rows (assumption text in each action's `why`, plan_ring_p5s02b_in.json:192,235,271,314)
| action | stub terminal (stub wire in 94ffff94) | probe sim end | expected uid |
|---|---|---|---|
| A28 w_gl | t24190 LSR #24133 (w24285) | branch, one wire | w24285 |
| A32 w_gr | t24139 RSR #24083 (w24264) | join_stub, kept_stub_uid | w24264 |
| A35 w_hl | t24288 LSR #24187 (w24312) | branch, one wire | w24312 |
| A39 w_hr | t24235 RSR #24150 (w24300) | join_stub, kept_stub_uid | w24300 |
Each `why`: ASSUMPTION (PD388(c), not measured), MERGE, the expected sim-end uid, CEN2 judges by wire ends (PD389(b)) (log:94-98).
## Pins (gate M0 before, gate U after; both PASS)
- VIs 94ffff94 (023239.vi), s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae. Tools stage_prerun 7605116f, stagekit 9cd8822e, stagexec 7a712ccb,
  stagesim eb99c6ba. memory_model 5b87de43. No tools/hooks or stage-tool edit; no original opened.
- The card's vigraph pin has 33 characters (typo). The file is a7eb58c7e35a..., so the gate checks the 8-character prefix (`prep_c159_c1_1_mk_pinfail.log`).
OPEN: delete_wire refuses a termless wire (stagesim.py:1424-1426, stagexec.py:2843-2851). For action 1: `remove_bad_wires` (a schema op), a tool change, or carry w10394 as owed?
OPEN: `--rebase` not used: _remap_plan (stage_prerun.py:4199-4248) maps uid fields only, and base-case frames resolve only as '#<uid>' (stagesim.py:691-699). Used the P5-1b map route (PD378(b)).
OPEN: the cut moves I and J (A41..A60) into step 3 with the K3/K4 GAP groups (A61..A80): 40 actions.
