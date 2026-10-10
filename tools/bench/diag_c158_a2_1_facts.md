---
type: facts
status: current
date: 2026-10-10
card: 158-a2-1
---
# Card 158-a2-1 facts: PD385(a)(b)(c) wire-0 LoopTunnel inner face act = connect_term_uid, built offline; op lists and suite unchanged
## Changed: tools/stagexec.py df82d75e -> 7a712ccb4c1f754d8bee4557f632177f (stagekit 0d8f6d25, stagesim eb99c6ba, addrcheck 207beb0d, stage_prerun 9decb20f, gscript 1a80236e unchanged)
- NEW `struct_parent_diags(rows, struct, owners)` stagexec.py:1650 (diagram a structure sits on: its tunnels' outer faces).
- NEW `LOOP_FACE_WIRE0 = "loop_inner_face_wire0"` + `LOOP_FACE_WIRE0_STATUS` ("UNMEASURED - predicted ...") stagexec.py:1665-1667.
- NEW `loop_face_wire0_act(rows, rs, rd, owners)` stagexec.py:1670: src = face term uid, sink = dst term uid (both from the read; a
  missing row -> ExecStop); census: dst on face's diagram -> {Wire 1}; dst on a frame of a CaseStructure on the face's diagram ->
  ROUTE_CENSUS register_end_case_border (R1); else None 'UNPREDICTED'.
- NEW `state_addr(st, zero_terms)` stagexec.py:1693, extracted from route_on_state (:1708 now calls it; same steps, same result).
- LVBackend.connect: 'cfw' with info src_wire0 -> NEW `LVBackend.loop_face_wire0` (:3220 -> :3578) = ONE existing
  `connect_term_uid(src, dst, real, op+variant+sim_census)` (its checks reused: no wire / Is Broken? True / junk Invoke); wired 'cfw'
  path unchanged. connect_term_uid takes op['sim_census'] for LOOP_FACE_WIRE0 too (:3573).
- SimBackend.connect: same case adds check['act'] = loop_face_wire0_act(...) (:3972); route label stays 'cfw' (c157 F3 unchanged).
- Census variant kept OUT of ROUTE_CENSUS['connect_term_uid'] like fs_exit (comment :330): U01 needs that table == census_samples.json.
## Measured
- Before (stagexec df82d75e): prep_c158_a2_1_before.log A1 3 op lists + A2 200 stored plans EQUAL to before.json (:7-10), before_a2.json
  written (:11), A4 p5s02a checkpoints (0,1,3,6,8,9,12,15,16,17) (:12), suite :13-26, BGRUN END rc=0 939 s (:28).
- After (7a712ccb): prep_c158_a2_1_after.log A1/A2 3 op lists + 200 plans EQUAL to before_a2.json, 0 differ (:7-10); A3 all four
  recipes' CHECKPOINTS equal (:11-14); A4 (:15); RESULT 9/0, BGRUN END rc=0 888 s (:31-32).
- Suite after == before: stagexec 141/0, stagesim 106/0, c155 21/0, c120 1/0, case_frame_c124 28/1 (V02, U01 PASS both), stagexec_gate
  13/0, tunnel_naming 21/0, fs_c126 13/0, t6_regress 9/2 (c147_b1_2, t4), addrcheck_s5 22/0, t7_ring 35/0, c156 20/0, c157 13/0,
  c158_runcheck 10/0 (before.log:13-26, after.log:16-29); new c158_wire0face 24/0 (after.log:30). No md5 re-pin was needed.
- selftest_c158_wire0face.py -> selftest_c158_wire0face.log:42-82 RESULT 24/0: A ops 16/17 on steps 15 and prev (17/20) via
  LVBackend.connect on a recording backend: wired -> one connect_from_wire to (1,1,6)/(1,1,9); wire 0 -> one connect_term_uid(work,
  5760, 24360) / (work, 5778, 24367), census R1, UNMEASURED; A3 three reused stops; S1/S2 dry act path (check['act'] connect_term_uid,
  same triple [183,1,6]/[183,1,9] as wired); C1 SelectorTunnel #1479, C2 FS #151, C3 relabelled body -> existing stops, 0 calls;
  V0 dst_pos "frame #-29 of CaseStructure #-28 on the face's diagram #23405"; V1-V4; K1; pins.
- First self-test run 20/4 (log :1-41): my S1/S2 expected the dry triple [1,1,6]; the dry backend's Diagram index is 183. Gate
  rewritten to "same triple as unpatched, node/term (1,6)/(1,9)"; tool code not changed between the two runs.
## Side facts
- I edited stagexec once during the before run's suite window and reverted it at once (md5 back to df82d75e verified); suite
  subprocesses had started at 00:09:2x, before the edit. Before-suite counts equal card 158-a1-2's after2 counts on the same bytes.
- prep_c158_a2_1_probe.log: step_15 rows found (:3-14); its all-owners scan hit its 5-min bgrun deadline (TIMEOUT 303 s), step_16 not printed.
- selftest_c156_b2_2_invcheck.py:99 pins stagexec 25a1494c (stale since card 157-a1-1; not in the suite or this card's globs).
- No LabVIEW process; no hook, plan, pred, licence, recipe, stagesim, addrcheck, stage_prerun or gscript edit; no gate refusal.
OPEN: census prediction rule only covers dst on the face's diagram or one Case frame on it; deeper nesting returns UNPREDICTED - enough for P5?
OPEN: the dry backend reports the wire-0 act in check['act'] while its route stays 'cfw' (kept so c157 F3 holds) - accept the label?
