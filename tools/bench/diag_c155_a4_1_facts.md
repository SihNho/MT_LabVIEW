---
type: facts
status: current
date: 2026-10-09
card: 155-a4-1
---
# 155-a4-1 facts - P5-2 plan on the REAL P5-1 graph 6716c499: census 10 groups OK + 3 GAP rows; step 1 = actions 1..29 / 19 ops (MAIN 680.0); dry + prerun PASS; prior-art novel; NOT launched (offline, LabVIEW 0)
## Maker `prep_c155_a4_1_mk.py` 166f6003, log `prep_c155_a4_1_mk.log` RESULT 80/0 (:281), BGRUN END rc=0 after 156 s
- Pins M0 (:3): graph 6716c499, P5-1 _in fabc4b9c, P5-1b plan 75a77a00 + session 79447fab, donor_queue 15269b6c, memory_model c87d170a, ring-p5.md a4b596f0, stagesim eb99c6ba, stagexec 53e17623, stage_prerun 9decb20f, vigraph a7eb58c7, stagekit aec03c6c.
- MAP (:5-60, each checked in the graph): QO1 Obtain -> #31258 (session symbol_map; 'queue out' t31335); loop 1.7 #23041 on 686; body #23405; #376; #3052 ('File # Saved' t3060 -> 'saved file refnum' t5772); #3453 (sink of t5704); out-tunnels #5204 (t3) / #10404 (t4); RSR #24083 / #24150; LSR read from wires #24133 (t24190) / #24187 (t24288); in-tunnels #24357 t24360 / #24361 t24367 / #25223 t25235; scaffold #23042 -> cond t23456 by w23489; #23501 (outer fed by #8486, kept).
- Donors: Dequeue #45 / Release #46 (DonorQueue_v0); Equal? $work #10019, And $work #9647 (labels == prim, :57-58); Increment $work #1978 and I32 0 DonorSRInit_v0 #248 as P5-1.
## Route census (greedy compile + X17 + stagesim, `_census` sims; log :87-105, session `census`)
- A refnum SR #23041 + 2nd branch of #31258 -> Dequeue (wire_sr LeftIn/RightIn) + Release on 686: OK. B I32 100 on Dequeue timeout (const_on_term): OK. C case_wired on DQ1 'timed out?': OK.
- D move_in #376/#3052/#3453 -> new:CQ7.f0 + w_ref (connect) + w_prog (ctlsink): OK (move_in model opmodels/move_in.json, measured on loop-body moves).
- E element -> case tunnel -> t5754: OK. F1-F3 base in-tunnel inner faces -> case tunnels -> #376: OK (executor route cfw, :271-273). G / H LSR inner -> case tunnel -> #376, #376 -> case tunnel -> RSR inner, True-frame pass (case_frame_wire new_wire): OK.
- I counter SR + 0 const + Increment in f0 (R1/R2 register_end_case_border) + t7 branch (case_frame_wire branch) + True pass: OK. J delete_wire w23489, delete_object #23042/#23501, local_read, Equal?, And, branch from TD7.outer, And -> {#23041 cond} (stop): OK.
- GAP J-ge0 (create primitive '>= 0' of PD374(c) + 2 wires, LR7 value -> AN7 'y'): donor search 'Greater Or Equal*' over main_vi_node_labels.json 626 labels + PRIM_DONORS 7 = [] (:63); refused by stage_prerun.py:2861 / :2866 (prim_donor_check). No row written; AN7 'y' left open.
- GAP K3 / K4 (NEW SRs for t3 'file progress' / t4 'file number to append out'): in-tunnel IK3/IK4 whose only inner use is the True-frame pass has no group out-wire -> compile ExecStop "tunnel ... must be followed by exactly one wire into it and one out of it" (stagexec.py:857-859; log :87,89). No row written.
## Cut / replay
- All-groups input `plan_ring_p5s02_all.json`: 62 actions (A..J) -> 42 ops. Start 603.4 = x10_start(7f2582ae) = 597.5 (diag_c155_a3_2_graph.log:24) + op-0 read 5.9.
- Per-prefix MAIN (:109): op 19 / action 29 = 680.0; op 20 / action 32 = 683.9 > 680. Step 1 = actions 1..29 = groups A B C D E F1 F2 F3 + G's first tunnel group (t_gi, w_gl, w_g376) (:112).
- Later cut (:111): step 2 = actions 30..62 / ops 20..42 (33 actions; G rest, H, I, J); its X10 start = the measured load of step 1's adopted file (not known offline).
- Pass A 30 steps, failed null, 0 PROVISIONAL (:144). TIE 28 end rows: 7 by mv_376 (#2048 array/length, #376 error in / total data array in, #6384 actual # data points / error in / file # to append), 21 step-0 declared (:145,:174); open pairs 26.
- REALSIM `sim/ring_p5s02/step_00..29`: FINAL, route check PASS, states == pass A (:254-255). X10 ops 19 (add_sr 1, connect 4, create 4, wire_sr 2, move_in 3, tunnel 5), Executor 674.9, MAIN 680.0, fail_above 680.0 (margin 0.0), MEMSTOP 695 (:275-276). X8 clean, X17 PASS 2 prims (:277-278).
## Pred `prep_c155_a4_1_pred.py` 9c587c75, log RESULT 11/0
- E1 11 checkpoints with step files; VG a7eb58c7; census derived {CaseStructure 1, Diagram 2, Tunnel 1, OuterTerminal 1, InnerTerminal 2, Wire 1}, UNPREDICTED 28 rows (:14).
- EL vs P5-1 base 45 (ffc4cf66, read 2e49ed9f): elrule no carry 47, carry 47; new = input x2 (Dequeue / Release 'error in', optional sinks, PD378(d)), closed 0 (:16). Per class predicted: input 3, not-connected 22, loose-ends 21, two-types 1 (:21). P5-1 offsets read-pred: input -1, tunnel -1. Non-gating.
- OPEN-NEW 14 unwired terminals of created objects (TG1, TF1-3, TE7 inner sources, selector SL7, RQ1 / DQ1 error terms) (:15).
## Licence / X11 (`prep_c155_a4_1_licence.py` 8a35a601, log 5/0; `prep_c155_a4_1_x11.log` CLEAN)
- rename_by_uid 0; renames 2: #376 t5683/5754/5760/5772/5778/5787, #23405 t3453. SG census 1 ControlTerminal sink (w_prog ctlsink), 0 sink gates.
## Recipes (RingSession pair shape of stage_d1_ring_p5s01b*; only plan / pred / licence / session / names / output differ)
- Main dry PASS 1/0 (PASS-UNVERIFIED CEN2, coverage 35/36, first mutation add_sr; `prep_c155_a4_1_dry.log:81-82`); prerun PASS 16/0 (`prep_c155_a4_1_prerun.log:108`): X10 :102-104 N 19, BIND 10, R 13, peak 680.0 (recorded meter UNMEASURED), Executor 674.9; X17 PASS :93; X14 WARN rows 29, budget 15, proven: no :105; CENSUS-UNPREDICTED advisory :95.
- Scratch dry PASS 1/0 (coverage 29/32), prerun PASS 16/0. `--scratch-required` rc 3 (CENSUS-UNPREDICTED rows 1..8, 10..29). `--check-launch` scratch: ALLOW rc 0. NOT launched; output name `claudeDev\D1_ring_p5s02_<ts>.vi`.
## Prior-art (`archive/peer/2026-10-09-priorart-priorart-c155-a4-1-p5s02.md`, ANSWERED 150 s): `PRIOR-ART: novel`; NOVEL RECORD for stage_d1_ring_p5s02.py (sha cdfe40a5778d); no PROVEN-PATTERN waiver.
- A3: census row 10 (p5_route_census.md:22,42-44) vs F1-F3/G base-tunnel sources - wording clash, row 10 was about plan-made tunnels. A4: cycle-97/98 move_into_frame into case frames left termless + loose-end wires (d1-loop12-17-split-plan.md:1504-1509,1531-1534); test = read them after ops 10-12 vs sim step_10..12.
- guard_peer refused the dispatch until the 155-a2-1 review was disposed: its 'What was done with it' written from diag_c155_a3_2_facts.md:26-29 (facts only).
## Files (md5)
- plan_ring_p5s02.json 285cb59a; _in bed3a5e7; _all fc5b38a0; _pred e6700921; _licence 01eccf67; stage_d1_ring_p5s02.py 8e8b3d74; _scratch.py 5779649b; session prep_c155_a4_1_session.json f99c8324; inv fbcd6cb1; probe 5862fa3a / probe2 3b127aff; priorart plan 35046fd4.
- Invariants `prep_c155_a4_1_inv_before.log` / `_after.log`: 198 files, before == after, pins PASS (only tools/hooks/material_marker.log changed, hook-written). LabVIEW processes 0 before and after.
## Duplicate blocks (copied, not extracted - outside write globs)
- OPEN: gate() prep_c155_a4_1_mk.py:62, _pred.py:51, _licence.py:32, _inv.py:60 (= prep_c155_a2_1_*); step_facts mk.py:460, TIE loop mk.py:480, SG census mk.py:541, main_of mk.py:423 (= prep_c155_a2_1_mk.py:255/274/336/229); whole pred / licence / inv bodies = prep_c155_a2_1_pred.py / _licence.py / _inv.py.
OPEN: (1) PD374(c) '>= 0': no donor - substitute, new donor, or drop (counter >= 0 makes '==' imply it)? (2) K3/K4: no route for the t3/t4 SR in-tunnel; also undecided: their init and whether #5204/#10404 stay or SR R.outer feeds #6384/#2048. (3) step 1 MAIN 680.0 = limit (margin 0) and the cut splits group G; sr_q R.outer t31246 stays unwired; prior-art A3/A4 to cite.
