---
type: facts
status: current
date: 2026-10-09
card: 156-a1-2
---
# 156-a1-2 facts - PD379(b) pass wire: `frame` on the pass wire's DST end, accepted as the case in-tunnel group's out-wire (stagexec only); stagesim unchanged; LabVIEW 0
## Measured (prep_c156_a1_2_measure.log, RESULT 11/0, BGRUN END rc=0 after 394 s)
- K rows are NOT in plan_ring_p5s02r_all.json (60 actions, groups A..J only, its goal line :7); they are in plan_ring_p5s02r_in.json d84634bd, whose first 60 actions == the all-plan's (R0). K3 = in-file 61..69 + K3f 70; used from there.
- Refusal reproduced (:5, gate R3 :10): action 69 w_k3pass, "source on diagram -30, sink on diagram -29" (stagesim.py:1536). K4 same (:16-21).
- src = IK3 inner t-131, SelectorTunnel #-128, InnerTerminal, frame -30 ('True'); dst = OK3 inner t-125, SelectorTunnel #-123, InnerTerminal, frame -29 ('False') (:9). CQ7 #-28 frames [['False',-29],['True',-30]] (:8).
- Each tunnel has ONE inner face per frame: IK3 faces on -29/-30, OK3 faces on -29 (wired, #376 t3) and -30 (unwired) (:6-7); case_tunnel_frame IK3 = -30, OK3 = -29. Code: stagesim._case_tunnel stagesim.py:1363 (one InnerTerminal per frame), :1364 (case_tunnel_frame = `body`).
- Recorded graph 6716c499: all 6 tunnels/selectors of base case #30726 have an inner face on both frames [30914, 30922] (:27-28).
- The end to change = the DST: frameless, OK3.inner resolves to OK3's group frame f0 (stagesim.py:832-836); with `frame: 'True'` it resolves to t-126 on -30, the source's diagram (F3b :12).
- Current tools with `frame: 'True'` on the dst: compile REFUSED "action 67: tunnel new:IK3 must be followed by exactly one wire ..." (:13-14, stagexec.py:857); stagesim ALREADY replays it: failed None, 70 steps, 0 PROVISIONAL (V3s :15, V4s :26). So stagesim needs no change.
## Change (stagexec.py only, 53e17623 -> 25a1494c)
- stagexec.py:856-857: a tunnel group's out-wire is `grp(b) or case_pass_wire(...)`.
- stagexec.py:5997 NEW `case_pass_wire(A, i, k, created, base_owners)` (docstring, self-test named): True when wire k's src = the in-tunnel's frameless inner face and its dst = inner face of an EARLIER tunnel of the same case with `frame` = the in-tunnel's own body frame name (plan case: create `frames`; base case: '#<uid>'). Specific ExecStops: dir not 'in'; loop not a case; wrong frame; dst not an earlier same-case tunnel.
- New plan field: none new; the existing wire-end `frame` (card 124-2) is now allowed on the pass wire's dst inside the group. Why: it alone picks OK<k>'s face in the in-tunnel's frame.
- stagesim.py unchanged (eb99c6ba). Op kinds unchanged: K3 = add_sr, create, connect, connect_term_uid x2 (register_end_case_border, new:CQ7), branch (selftest log :37).
## Self-test tools/bench/selftest_c156_passwire.py 8335875b -> selftest_c156_passwire.log run 2 (:33-67) RESULT 20/0 (:66), BGRUN END rc=0 after 538 s
- (a) A31-A34 / (b) A41-A44: compile OK; 70 actions simulate, failed None, 0 PROVISIONAL; w_k<k>pass effect case_frame (CQ7, index 1, 'True', diagram -30, new_wire).
- Sink rows: K3 SK3 R.inner net = {OK3.outer t-124, SK3R.inner t-116, #5204 inner t8776} (:42); #5204 outer t9631 net = {#2048 t3182, #6384 t6480} (:43). K4: {OK4.outer, SK4R.inner, #10404 inner t24342} (:50); #10404 outer t24363 -> #6384 t6511 (:51).
- AB: K3+K3f+K4+K4f (80 actions) 52 ops, simulate failed None, 0 PROVISIONAL.
- (c) C1-C4: as written, still refused at action 69 with the stagesim.py:1536 message; compile refuses frame 'False' and a non-tunnel dst, each with its own message. (d) D: 5 plans compile EQUAL to before.
- Route check (dry backend; not a card criterion): no UNROUTABLE row in the K R1 groups. UNROUTABLE rows: G row 20 "#24083 not in Diagram[124] (#23405).Nodes[]" and H row 23 "#24150", ALSO on the 60-action all-plan without K (baseline :36); plus w_k3f / w_k4f "#8776 / #24342 is an INNER face of LoopTunnel ...: only the outer face's owner route is measured (l2a1_faces_81.log)" (:40, :48).
- First run (:1-32) FAIL 17/3: my own route-check gate wanted 0 UNROUTABLE rows with no baseline measured; regated to K rows + baseline in the same build step.
## Regression
- Before-list tools/bench/sim/ring_p5s02pw/compile_before.json 7ca1c4c4 (written before the edit). prep_c156_a1_2_regress_after.log: 200 plans (120 compiled, 15 refused, 65 skipped), 0 differ, refusal texts included; EQUAL: p5s01a 14, p5s01b 8, p5s01_in 22, p5s02a 17, p5s02a_in 17, p5s02 19, p5s02_all 42, p5s02_in 19, p5s02r_all 40, p5s02r_in 52 ops.
- Suite before (prep_c156_a1_2_suite_before.log) == after (prep_c156_a1_2_suite_after.log): stagexec 141/0, stagesim 106/0, c155_basecase_frame 21/0, c120_caseshape 1/0, stagexec_gate 13/0, stagesim_tunnel_naming 21/0, fs_c126 13/0; failing before and after with the same counts: case_frame_c124 28/1 (V02 plan_ring_p3a_in_v3), t6_regress 9/2 (selftest_c147_b1_2, selftest_t4). Not re-pinned.
## Pins / invariants
- Unchanged: stagekit aec03c6c, stage_prerun 9decb20f, vigraph a7eb58c7, addrcheck 207beb0d, gscript 1a80236e, stagesim eb99c6ba. New stagexec 25a1494c420685f9049264ceefc8604a.
- No stored plan/recipe/pred/P5 file edited; no tools/hooks edit; LabVIEW processes 0 (tasklist). guard_write: cards 149-a2-1/149-a3-3/149-a3-4 still pin stagexec 1bab9cf9 (already stale before this card).
- Shared helpers prep_c156_a1_2_lib.py 17ec7a73 (k_actions, sim_plan, compile_all, run_suite) CALLED by measure/regress/selftest; compile_all/run_suite re-cut from card-specific prep_c155_a1_1_regress.py:30-43 / prep_c155_a1_1_suite.py:28-40.
OPEN: K3f/K4f feed form T (O.outer -> #5204 / #10404 INNER face) is UNROUTABLE in the dry route check (only the outer-face route is measured); G/H out-groups rows 20/23 are UNROUTABLE on the 60-action all-plan as well, while the 156-a1-1 step-1 REALSIM route check passed - which form / which step plan the next card uses is judgement.
