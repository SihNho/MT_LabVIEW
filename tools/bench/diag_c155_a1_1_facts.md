---
type: facts
status: current
date: 2026-10-09
card: 155-a1-1
---
# 155-a1-1 facts: a base-graph Case takes `frame: "#<diagram uid>"` and R1/R2 in stagexec + stagesim. Offline, 0 LabVIEW processes
## Frame order: measured on two cases, and they agree (selftest_c155_basecase_frame.log gates M1, M2)
- #30726: frame list in graph bd67a511 `owners` = [30914, 30922]. LabVIEW Frames[k] binding = [30914, 30922] (diag_c154_p5s01a_scratch.log:144, -18 = f0 and -19 = f1, from sim step_20 c9c3a0b8). EQ1 was planned on f1 ('True') and its rows are on #30922. Expected = observed.
- #22694: frame list in graph_ring_p3a_20261001_190155.json (2fa6ce0c) = [27219, 27232]. Binding = [27219, 27232] (stage_d1_ring_p3a.log:146). case_frame_wire frame 0 (:231) put Q&R.x on #27219 (:256). Expected = observed.
- Frame index = position in the owners-ordered frame list. This is the order `_case_tunnel` already used (it now calls `base_case_frames`).
## What changed
- stagesim.py:681 `base_case_frames`, :691 `case_frame_names` (a base case's frames are named '#<diag uid>'; a plan-made case keeps its case_frames names), :702 `case_frame_of` (falls back to the base case).
- stagesim.py:823 `resolve_addr`: a base tunnel with a wrong or name-style `frame` is refused, and the message names the case and its '#' frames. `_case_tunnel` now calls `base_case_frames` (same list).
- stagexec.py:593-652: new `_uid_int`, `base_case_named`, `base_case_of_frame` (uses FS_FACE_RE), `plan_base_owners` (base or finalized.base, md5-checked) and `_base_case_wire`.
- stagexec.py:654 `case_frame_op(..., owners)` and :707 `_cfw_variant(..., frame_diag)`: base-case branch. The plan-made path is unchanged.
- stagexec.py:803 `compile_plan(plan, owners=None)`. The base owners are loaded lazily. The tunnel R1/R2 condition at :865 adds a base case. The wire branch at :883 sends a base-case '#' frame to case_frame_wire before fsw.
- stagexec.py:3811: dry `case_frame_wire` uses `case_frame_names`. At :3929-3931, dry `connect_term_uid` gets a base case's parent from the owners row. Before this fix the route check said "case #30726 sits on #None" (prep_c155_a1_1_probe.log, run 2).
## New self-test `tools/bench/selftest_c155_basecase_frame.py`: 21 pass / 0 fail (selftest_c155_basecase_frame.log, last run)
- (a) A1: the 12 mapped P5-1b actions compile to case_frame_wire, create, connect, add_sr, connect, connect_term_uid x2 (register_end_case_border, case 30726) and case_frame_wire (case 30726, '#30914', index 0, new_wire). These are the same kinds as whole-P5-1 ops 15..22.
- A2: passing owners explicitly gives the same ops. A3: with no base, compile keeps the old plain `tunnel`. A4: pass A simulates all 12 actions. A5: the route check has 8 rows and no UNROUTABLE row.
- (b) B1/B2: compile ('#23166', '#27219') and resolve_addr ('#23166') refuse, and each message names 30726 ['#30914', '#30922'].
- (c) C1/C2: `frame: 'False'` on the base case is still refused.
- (d) D1/D2/D3: the plan-made case is unchanged.
## Regression
- Compile of every stored plan (185 plans: 111 compile, 15 refused, 59 have no actions): before == after, 0 differ (prep_c155_a1_1_after2.log). The before-list is prep_c155_a1_1_compile_before.json 785976e0, written first.
- P5-1a plan ed62e8d6: 14 ops before = 14 after, equal.
- Self-test suite, before edit (prep_c155_a1_1_suite_before.log + _before_c120.log) and after (prep_c155_a1_1_suite_after2.log) give identical counts:
  - stagexec 141/0; stagesim 106/0; c120_caseshape 1/0 (needs the graph argument); stagexec_gate 13/0; stagesim_tunnel_naming 21/0; fs_c126 13/0.
  - Already failing before the edit, with the same counts after: case_frame_c124 28/1 (V02, plan_ring_p3a_in_v3) and t6_regress 9/2 (selftest_c147_b1_2 P0 pin drift; selftest_t4 P4). Not re-pinned.
## md5
- stagexec.py 1bab9cf9 -> 53e17623961d2fd2be711d2754891bd4; stagesim.py 78b8d5a1 -> eb99c6bab81633f9bdd7c10dce6bfc0a.
- Pins unchanged: stagekit aec03c6c, stage_prerun 9decb20f, addrcheck 207beb0d, gscript 1a80236e, vigraph a7eb58c7 (gate P1). No hook was edited.
- guard_write warns that open cards 149-a2-1 / 149-a3-3 / 149-a3-4 still pin stagexec 1bab9cf9.
OPEN: compile sees a base case only through `plan['base']`/`finalized.base` or an explicit `owners=`. A prep that compiles `dict(TOP, actions=...)` without a base (prep_c154_a4_1_mk.py:158) still gets the old fs_face/tunnel shape. Should the P5-1b prep pass `base` (or owners), or should compile refuse an unclassifiable '#' frame?
