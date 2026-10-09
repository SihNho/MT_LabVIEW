---
card: 154-a3-2
status: current
date: 2026-10-09
---
# 154-a3-2 facts - P5-1 form S replays clean on s09 22f967b5, but X10 MAIN 701.0 > 680: RETURN (brief step 1), no pred/licence/recipes (offline, LabVIEW 0)

## Plan maker (`prep_c154_a3_2_mk.py` 56976dd5, log `prep_c154_a3_2_mk.log`, RESULT 14/1, BGRUN END rc=1)
- Rows come from census `diag_c154_a3_1_census.py` (3904fb9d). Its 17 assignments were executed from its own AST, and the actions are FORMS["S"] =
  OBT(686) 3 + A0 20 + S_REF 9 = **32 actions** (<= 40) (log:5-7).
- Changed vs census: (c1) 5 aliases failed the schema `as` pattern (docs/protocol/stageplan.json:317-320) and were renamed, with their references:
  SQR->QS1, TCI->TC1, TCO->TC2, TQI->TQ1, TQO->TQ2 (log:8-9); (c2) `data_stream: true` + why on c_obt, c_enq (X8, stage_prerun.py:1180-1188);
  (c3) a `why` with its census row on every action; (c4) the term_class values were checked, not edited: 21 terminals == measured (queue Function
  terms ParameterTerminal x23 in graph_qrt_pool_20260928.json d265b283; ArrayConstant/DNC/Local Terminal; #1978 x+1 OverridableP) (log:12-14).
- Pass A (`sim/ring_p5s01/_passA/ring_p5s01a/`, step_00..step_32) failed null, 33 steps, 0 collect-all PROVISIONAL (log:16-49).
- REALSIM = the finalize run on the same real graph (`sim/ring_p5s01/step_00_base.json`..`step_32_wire.json`, summary 9758aeb4) was FINAL,
  route check PASS (22 rows), fs_border_gate PASS, 0 PROVISIONAL (log:140). Its state equals pass A's at all 33 steps (log:141). model_source per
  step is in the `FACT STEP` lines (log:16-48, :107-139).
- TIE: 21 end rows, all at step 0 = s09 declared open rows (19 pairs); no end row is made by a P5-1 action (log:50-51).
- Compile: 22 ops = create 9, connect 4, tunnel 1, add_sr 2, connect_term_uid 4, case_frame_wire 2. 16 of them are BIND ops (1,2,4-10,12-14,16,18,20,21).

## X10 - the return condition (log:164-165)
- start 602.6 = s09 load 596.7 + op-0 5.9 (stage_prerun.x10_start(eb1d0f31)); N 22, R 18; Executor peak **695.9**; MAIN (+2 reads x 2.53)
  **701.0** > fail 680.0 (and > MEMSTOP 695). Model: read 2.53, edit 0.58 + other 0.80 per op, final read 17.4 (memory_model.json 6f2b5687:10-27).
- Prefix numbers (same formula, no cut made): ops 1..12 MAIN 669.5, 1..13 673.4, **1..14 677.3** (ends with the count-SR R2 group t_co),
  1..15 681.2 (adds the False pass-through), 1..22 701.0.
- Not reached (the script stops at the first FAIL): X8 lint, X17, SG census, session json. Steps 3-7 were not done: no pred, licence,
  recipes, dry/prerun or prior-art review.

## Files
- plan_ring_p5s01_in.json fabc4b9c; plan_ring_p5s01.json ed6ceb9e (final:true by simulation, X10-refused, no recipe names it);
  sim/ring_p5s01/_passA/plan_ring_p5s01a_in.json 66314ec8; prep_c154_a3_2_inv.py 1a2df968.

## Invariants (`prep_c154_a3_2_inv_before.log` / `_after.log`, RESULT 1/0 and 2/0)
- 154 files: the brief's pins, every P4 recipe/plan/pred/licence and tools/hooks/**. Before == after, except the hook-written
  tools/hooks/material_marker.log. No LabVIEW process before or after (tasklist).
- No JEV-LADDER row exists for prep_c154_a3_2_mk.log in tools/bench/jev_gate.log.

OPEN: P5-1 = 32 actions = 22 ops at X10 MAIN 701.0 > 680. Where to cut P5-1 (e.g. after op 14, 677.3), or how else to reduce it, is the judgement's call.
