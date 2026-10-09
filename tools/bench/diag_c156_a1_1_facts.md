---
type: facts
status: current
date: 2026-10-09
card: 156-a1-1
---
# 156-a1-1 facts - P5-2 plan RE-MADE per PD379 on graph 6716c499: census 13 groups OK, K3/K4 GAP (stagesim.py:1536), K3f/K4f BLOCKED; step 1 = actions 1..23 / 17 ops (groups A-F2), MAIN 672.1 <= 675; dry + prerun PASS; prior-art novel; NOT launched (LabVIEW 0)
## Maker `prep_c156_a1_1_mk.py` 3cbe8fc8, log `prep_c156_a1_1_mk2.log` RESULT 76/0 (:261), BGRUN END rc=0 after 289 s (:262)
- (earlier attempts of the same build step: `prep_c156_a1_1_mk.log` - my STOP gate counted #23042's own y as a peer; then aliases 'K3I'/'K4I' failed the stageplan alias pattern; run killed, fixed to KI3/KI4.)
- Shared blocks: `prep_c156_a1_1_lib.py` fc6ce5f6 (Gate, step_facts, tie_rows, main_of, sg_census), self-test 3/0 (`prep_c156_a1_1_lib.log`), CALLED by mk/pred/licence/inv.
- MAP (mk2.log, same uids as 155): QO1 #31258, L17 #23041 on 686, body #23405, #376, #3052, #3453, out-tunnels #5204 (in t8776 / out t9631 -> #6384 t6480, #2048 t3182) and #10404 (in t24342 / out t24363 -> #6384 t6511).
## (a) Stop mode READ (mk2.log:60-61)
- Graph: cond t23456 <- w23489 <- #23042 'x = y?' t23472; x and y both fed by #23501 t23505 (always True). The graph carries no stop-mode field (keys listed :60).
- Mode quoted from the measurement `diag_c138_5_facts.md:37-38`: all six While loops incl. 23041 read Stop If True? = True. So Equal? -> cond is the polarity-correct form; no '>= 0', no And, no Not.
## Route census (greedy compile + X17 + stagesim; mk2.log:88-104)
- OK: A, B, C, D, E, F1, F2, F3, G, H, I, J (J routes: delete_wire, delete_object x2, local_read, primitive Equal?, branch, connect, stop).
- GAP K3 / K4 (:86-87, :101,:103): compile ACCEPTS the in-tunnel group with the frameless pass as its one out-wire (stagexec.py:857-859 passes), but stagesim refuses action 69 `w_k3pass` / `w_k4pass`: "wire new:IK3.inner -> new:OK3.inner: source on diagram -30, sink on diagram -29 - a border needs a tunnel/register action first" (stagesim.py:1536). Cause: a frameless OK3.inner resolves to its group frame f0 (case_tunnel_frame, stagesim.py:832-836) while IK3's group face is f1; with a `frame` end the wire stops being a group wire (stagexec.py:853-859). No tool written.
- BLOCKED K3f / K4f (depend on K3/K4): feed form T = O.outer -> #5204 inner t8776 / #10404 inner t24342.
- t3/t4 sink sim result: not produced (K not compiled; mk2.log NT lines). Read from 155 sim step_10: after mv_376, #5204 / #10404 survive with outers still on #6384/#2048 and loose inner wires 10362 / 25232.
## Cut / replay
- All-groups plan `plan_ring_p5s02r_all.json` 15da9551: 60 actions, 40 ops; start 603.4 = x10_start(7f2582ae) 597.5 + 5.9 (:110). Group ends at actions [7,8,9,14,17,20,23,26,33,40,52,60].
- Step 1 = ops 1..17 / actions 1..23 = groups A B C D E F1 F2 (:111-113); MAIN 672.1 <= 675 (next group end, action 26, = 676.0). Executor 667.0; kinds add_sr 1, connect 4, create 4, wire_sr 2, move_in 3, tunnel 3 (:254).
- Later cut (:112): step 2 = actions 24..60 / ops 18..40 = F3 G H I J (37 actions); its X10 start = measured load of step 1's adopted file (unknown offline). Saved files: `D1_ring_p5s02a_<ts>.vi` (in-between), `D1_ring_p5_<ts>.vi` (last, counted 6 of 6) - K3/K4 rows absent while GAP.
- Pass A 24 steps, failed null, 0 PROVISIONAL (:139); TIE 29 end rows -> 27 open pairs (:169); REALSIM FINAL, route check PASS, states == pass A (:235-236); X8 clean, X17 PASS (:256-257); t31246 named by no action (:84, :259).
## Pred `prep_c156_a1_1_pred.py` 27fc52dc -> `plan_ring_p5s02a_pred.json` 31d8e9be, log RESULT 12/0 (:23)
- E1 checkpoints with step files + E1-MOVE (:13): mv_376 op 10 step_10 9b820f15, mv_3052 op 11 step_11 b290d35f, mv_3453 op 12 step_12 24d481f4 (scratch-run items, PD379(e)).
- EL base 45: no carry 47, carry 47; new input x2 (Dequeue/Release 'error in'); per class input 3, not-connected 22, loose-ends 21, two-types 1 (:18-19). Non-gating. CENSUS UNPREDICTED 22 rows.
## Licence `prep_c156_a1_1_licence.py` 43e40d75 -> `plan_ring_p5s02a_licence.json` e8fd6a98, 5/0; X11 `prep_c156_a1_1_x11.log` CLEAN
- renames 2: #376 t5754/5760/5772/5778, #23405 t3453; rename_by_uid 0. SG census 1 ctlsink row (w_prog), 0 sink gates.
## Recipes `stage_d1_ring_p5s02a.py` b52b9ff5, `_scratch.py` 71c3aed4 (pair shape of stage_d1_ring_p5s02*; names/plan/pred/licence/session only)
- Main dry PASS 1/0 (PASS-UNVERIFIED PB, coverage 35/36); prerun PASS 16/0: X10 peak 672.1 (fail above 680, recorded meter UNMEASURED) :96, X17 PASS :85, X14 WARN rows 23 budget 15 proven no :97.
- Scratch dry PASS (29/32), prerun PASS 16/0 (X10 667.0). `--scratch-required` rc 3 (CENSUS-UNPREDICTED rows 1..8, 10..23). `--check-launch` scratch: ALLOW rc 0. NOT launched.
## Prior-art `archive/peer/2026-10-09-priorart-priorart-c156-a1-1-p5s02a.md` ANSWERED 50 s: `PRIOR-ART: novel` (:319); task cited 155's A4; NOVEL RECORD for stage_d1_ring_p5s02a.py sha 3f1d3dda7e84.
## Invariants `prep_c156_a1_1_inv.py` 18b7b1ea: 209 files before == after, pins PASS (only tools/hooks/material_marker.log changed, hook-written). LabVIEW processes 0 before and after.
## OPEN
- K3/K4: no existing route expresses "in-tunnel's only use = pass wire to an out-tunnel's face in another frame" (stagesim.py:1536 vs stagexec.py:853-859); PD379(b)'s narrow stagexec/stagesim fix is authorised by the PD but forbidden by this card.
- SR init type for t3/t4: not in graph 6716c499 nor in `docs/wiki/subvi/save trace.json` (type ""); the plan used the I32 0 donor DonorSRInit_v0 #248.
- Copied blocks (not moved to stagekit, pinned): MAP/census/cut code `prep_c156_a1_1_mk.py:47-299` (= prep_c155_a4_1_mk.py:76-449); pred E1/EL `prep_c156_a1_1_pred.py:60-140` (= prep_c155_a4_1_pred.py:67-158); licence table `prep_c156_a1_1_licence.py:39-62`; inv file_set `prep_c156_a1_1_inv.py:48-58`. The lib's 5 blocks belong in stagekit.
