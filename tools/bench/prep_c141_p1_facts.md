---
type: facts
status: current
date: 2026-10-02
---
# Card 141-P1 facts: P4 plan v17 (p4_eq_seq donor) + session 2 on a PROVISIONAL base (offline, no LabVIEW)
Maker `tools/bench/prep_c141_p1_mk.py` d150ae5a -> `prep_c141_p1_mk.log` rc 0, 29/0. Queries `prep_c141_p1_q1.log`, `prep_c141_p1_q2.log`.
## Donor (pass 1)
- Surviving bed Equal? nodes (label file x graph objs - v16 deletes): #3812 #10019 #22284 #22731 #29111 (`mk.log:4`). No terminal TYPE of any is in a measured file: "I32 preferred" is UNMEASURED for all five.
- PICK **#10019** (diagram 639; x = `# of Auto-Reset`.Value, y = `Limit of Program`, `q2.log`): the only Equal? with a measured `$work` duplicate (class Comparison, terms `x = y?`/`y`/`x`, `docs/NAMES.md:1387`). X17 over all of v17 PASS, 33 primitive creates (`mk.log:16`).
## v17 (pass 2) - `plan_ring_p4_v17.json` **e19d7e14** (in 57b87e42, meta dfc15cb7)
- Only change vs v16: p4_eq_seq donor `$work` #10171 -> #10019 (+why). Replay END 236 steps; end cdiff == v16's 24; per-step cdiff == v16's summary for every id; route PASS; compile 217 ops == v16; route diff: NONE (empty); fs_routes == v16's; ops 1..24 == plan_ring_p4_s01.json == v16.
- Session table on v17 == prep_c141_1_sessions.json exactly (11 sessions) -> `prep_c141_p1_sessions.json` 83a9de8d.
## Session 2 (pass 3) - `plan_ring_p4_s02.json` **5e483ea6** (in 98feab54), pred `plan_ring_p4_s02_pred.json` b108c5cd
- v17 ops 25..54 = `p4_rp29048_dwo`..`p4_c_stopall_f`, 30 actions, N 30, R 4, X10 peak **675.0 at start 606.1 = the limit exactly** (`mk.log:21`); kinds delete_wire 5, delete_object 4, RLE 9, connect 9, create 3.
- Base PROVISIONAL `sim/ring_p4_s02_s01end/base_provisional.json` 2d0c2c99 = stagesim END of s01 (re-simulated; end rows == s01 finalized 16), sim_of {plan_ring_p4_s01.json, f4831031}; s01 sym RX1 -1, RX2 -7, RX3 -13, neg -17.
- 1 cross ref: `p4_rp29048_out`.src `new:RX3.output array` -> {uid -13} (rebase re-binds). FINAL, open_rows_match, 11 open pairs (16 end rows, all step-0 bed-declared); route_check off (provisional, as 140-P1). X17s2 PASS (2 RAS creates).
- EL pred 51 (= s01 pred 51 + 0 created nodes with an unwired input), alt 52: base node #23166 term '' newly unwired at the end (`mk.log:49`). Census {} (30/30 unpredicted -> scratch measures).
## Recipes (pass 4) - `stage_d1_ring_p4_s02.py` ab065d05, `_scratch.py` b117205e (copies of the s01 pair, names only)
| run | result | refusals (all provisional-base) |
|---|---|---|
| dry launch / scratch | FAIL rc 1 | E1 BASE `unbound [-17,-16,-15,-14,-11,-10]` = s01-created objects (created-object binding) (`prep_c141_p1_dry.log:26`, `_scr_dry.log:39`) |
| prerun launch / scratch | 13/3 | X1 (= that dry stop), X5 (0 ops executed, cascade of X1), X10 UNMEASURED base PROVISIONAL (`prep_c141_p1_prerun.log:27,43,47`, `_scr_prerun.log:40,56,60`) |
- Every other prerun gate PASS (X2 X3 X4 X6 X7 X8 X9 X11 X12 X13 X15 X16 X17); WARN X14 rows 30 > budget 15 (proven: no). Same dry stop as 140-P1 (`prep_c140_p1_facts.md:22-25`). Prior art (pass 5): guard_cycle never asked in this card; none dispatched.
