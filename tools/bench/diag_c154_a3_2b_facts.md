---
card: 154-a3-2b
status: current
date: 2026-10-09
---
# 154-a3-2b facts - P5-1a = ops 1..14 / actions 1..20 of P5-1 (X10 MAIN 677.3 <= 680); plan, pred, licence, recipes written; dry + prerun PASS; prior-art novel; NOT launched (offline, LabVIEW 0)
## Cut (`prep_c154_a3_2b_mk.py` ba9b5546, log `prep_c154_a3_2b_mk.log`, RESULT 15/0)
- Rows read unchanged from plan_ring_p5s01_in.json fabc4b9c (== plan_ring_p5s01.json's 32 actions, field for field, log:5). Start 602.6 (x10_start(eb1d0f31)).
- Per-prefix MAIN (log:6): 1..12 669.5, 13 673.4, **14 677.3**, 15 681.2, ... 22 701.0. n* = 14, contiguous fit (log:7).
- Ops 1..14 cover exactly actions 1..20 (action boundary), k = 20 <= 40 (log:8). Op 14 = connect_term_uid [t_co, w_inc_co, w_co_r] (count-SR R2 group).
- P5-1a: 14 ops = create 8, connect 2, tunnel 1, add_sr 1, connect_term_uid 2; 12 BIND ops; checkpoints [0,1,2,4,5,6,7,8,9,10,12,13,14] (log:150).
## Remainder (NOT planned; for P5-1b on the real P5-1a graph; log:31)
- actions 21..32 = ops 15..22: 21 w_false_pass (row 16, op 15); 22 c_lw (17, op 16); 23 w_final (18, op 17); 24 sr_q (S4, op 18);
  25 w_obt_srq (S5, op 19); 26-28 t_qi / w_srq_qi / w_qi_enq (S6, op 20); 29-31 t_qo / w_enq_qo / w_qo_srq (S7, op 21); 32 w_q_false (S8, op 22).
- End-row (TIE) list of the prefix: 21 end rows, ALL step-0 declared s09 open rows (19 pairs), none made by a P5-1a action (log:55-77):
  #10068 x, #10150 x, #10382 x, #10757 array, #11261 array/element, #11529 x, #2626 array/element x3, #28083 'Magnet position', #29240 x,
  #29625 array, #376 'current frame data array in'/'frame index', #5058 'Bead is good? array in'/'Image In'/'pos in cal image in'/'x,y,z array', #8634 array.
- Not cdiff rows but open at the sim end, made by P5-1a (prep_c154_a3_2b_pred.log:15, 19 terminals): TC2 (count out case tunnel, False frame) sink;
  TC1 source; SN1R (count SR right) source; TE1 source; EQ1 Enqueue 'queue' / 'queue out' / 'timed out?' / 'timeout in ms (-1)' / error in/out;
  SQ1 tunnel x2; QO1 Obtain 'queue out' / 'max queue size' / 'name' / 'create if not found?' / 'created new?' / error in/out.
## Replay (log:32-135)
- Pass A `sim/ring_p5s01a/_passA/ring_p5s01ap/` 21 steps, failed null, 0 PROVISIONAL (log:54). REALSIM `sim/ring_p5s01a/step_00_base.json`..`step_20_wire.json`
  (step_20 c9c3a0b8): FINAL, route check PASS, fs_border_gate PASS, open_rows_match, 0 PROVISIONAL (log:134); states == pass A at all 21 steps (log:135).
- X8 lint clean, X17 PASS (3 primitive creates, donor label == prim), SG census 0 rows (log:152-154).
## Pred (`prep_c154_a3_2b_pred.py` ff8ff19d, log RESULT 11/0)
- RB/RB2 base IS the s09 graph 22f967b5, vi eb1d0f31; C 20 actions -> 14 ops once; X1 start 602.6 == prerun's; X10 Executor 672.2, MAIN 677.3, margin 2.7, MEMSTOP margin 17.7 (log:5-10).
- E1: 13 checkpoints, each with a sim step file + md5 (log:12); VG vigraph a7eb58c7, D/TD/PB position key (log:13). Census UNPREDICTED (20 rows), census {} (log:14).
- EL base = s09 expected file 5146f980 total **45** (read 080255ad, 45 items). No carry -> **48**; carry {4538,29843,29879,30002,2626} -> **48**; new 3 `input`
  (#-56 TC2, #-24 Enqueue, #-3 Obtain), closed 0. Per class: input 1->4, not-connected 22, loose-ends 21, two-types 1 (log:16-21). Neither gating.
## Licence / X11 (log `prep_c154_a3_2b_licence.log` 5/0, `_x11.log`)
- X11 `--buildarray-check` CLEAN (no Build Array: n/a). Licence renames 0, rename_by_uid 0; every P5-1a wire dst is symbolic (8 rows), no base sink wired.
## Recipes, dry / prerun (copies of the s09 pair; names / plan / pred / licence / census file / stage name / result key / docstring only)
- Main: dry PASS 1/0, prerun PASS 16/0 (`prep_c154_a3_2b_prerun.log:95-98`: X10 N 14, BIND 12, R 15, peak 677.3 MAIN, Executor 672.2; X17 PASS :86;
  X14 WARN rows 20, budget 15, proven: no :98; CENSUS-UNPREDICTED advisory :88). Scratch: dry PASS 1/0, prerun PASS 16/0.
- `--scratch-required` rc **3** (census unpredicted rows 1..20, `_scrreq.log:3`). `--check-launch` scratch: **ALLOW** (`_checklaunch.log:3`). NOT launched.
## Prior-art (`archive/peer/2026-10-09-priorart-priorart-c154-a3-2b-p5s01a.md`, ANSWERED 70 s)
- `PRIOR-ART: novel`; no release line needed. Notes (non-blocking): ring-p5.md :27/:60 still put Obtain on #4866; recipe :173/:191 strings copied from s09.
## Files (md5)
- plan_ring_p5s01a.json ed62e8d6; _in 80c3710e; _pred 2e84eb2c; _licence 323ac8e0; stage_d1_ring_p5s01a.py f3cbe6a0; _scratch.py 3b02d9a7; session a50bf0a5.
- Invariants: 160 files before == after (`prep_c154_a3_2b_inv_after.log:5`; only tools/hooks/material_marker.log, hook-written). LabVIEW processes 0.
OPEN: recipe strings "session 8's in-between file" (:173) / "v18 session 8" (:191) left as copied (names-only rule) - fix before launch or accept?
