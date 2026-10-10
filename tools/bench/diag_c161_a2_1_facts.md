---
type: facts
status: current
date: 2026-10-10
card: 161-a2-1
---
# 161-a2-1: HAND-BACK before any edit - only 2 of the 5 #376 rows meet PD394(a); stagekit NOT edited, pred NOT re-made
Offline: `tools/bench/prep_c161_a2_1_measure.py` -> `prep_c161_a2_1_measure.log` (BGRUN END rc=1 after 3 s, RESULT FAIL 2/3), data
`diag_c161_a2_1_measure.json` e7f4a15d. Calls only existing stagekit functions (run_bind, case_move_frames, pb_bound_rows, frame_tag_map,
frame_src_resolve, s1_frame_graph, pred_end_graph) + stagexec.bind_state; G1 := sim end re-keyed by the dry bindings (as 161-b1-2).
## 1. Binding records (all on disk; plan md5 now == adopt record)
- p5s02a: `adopted_scratch.jsonl:11` -> `diag_c158_p5s02a_scratch.json` `stagexec` (18 ops, 12 uids); `diag_c158_p5s02a_scratch.log:161`
  `STEPX 09 create c_case7 bound {-28: 31308, -29: 31506, -30: 31517, -31: 31485}`. case_move_frames -> {376, 3052, 3453: [31506]}.
- p5s01b: `adopted_scratch.jsonl:10` -> `diag_c155_p5s01b_scratch.json` (9 ops, 5 uids), log `:137`; no move_in -> {}.
- p5s01a: `adopted_scratch.jsonl:9` -> `diag_c154_p5s01a_scratch.json` (15 ops, 16 uids), log `:229`; creates CQ1 but no move_in -> {}.
- Walking further (p4_s09..s02, lines 8..1): only p4_s06 has move_in (p4_mv_10068, p4_mv_29240) and it yields {} (dest not a created case).
- Inherited frames = {376: [31506], 3052: [31506], 3453: [31506]}; none unbound (log `FACT inherited frames`).
## 2. PD394(a) on the 5 rows (p5s02b sim end; frame_tag_map: f0 = 31506, f1 = 31517 of CQ7)
| sink (#376) | (i) base==end | (ii) S1 uids | (iii) frames | end sources (tags) |
|---|---|---|---|---|
| cal cluster path | yes | [3454]==[3454] | 31506 ok | 3391 @(31546,31506) - p5s02a tunnel |
| file size | yes | [1807]==[1807] | 31506 ok | 1766 @(31557,31506) - p5s02a tunnel |
| selected path | NO: base after [] (unwired at step 0) | [29557]==[29557] | 31506 ok | 29551 @(10000003=t_in3,31506) |
| error in | NO: base after [] | [3934,3934,4965,4965] vs [3934,4965] (set equal) | NO: 31517 | 376/4910 error out via tunnels 10000008/10000014, f0 AND f1 |
| total data array in | NO: base after [] | [1842,1842,3954,3954] vs [1842,3954] (set equal) | NO: 31517 | 376/781 via 10000020/10000026, f0 AND f1 |
- RECORDABLE as written: cal cluster path, file size. NOT: selected path, error in, total data array in (log `FACT RECORDABLE ...`).
- Correction to `diag_c161_b1_2_facts.md` ("unchanged by every action"): 3 of the 5 are present at step 0 as UNWIRED sinks (base
  `after` []) and are wired by THIS plan (#4 w_in3_376, #7 w_g376, #15 w_h376) through its own new tunnels; only 2 rows are truly inherited.
- error in / total data array in: each S1 source reaches the sink twice, once via frame 31506 (f0, where 376 sits) and once with tags
  on 31517 (f1, the other CQ7 frame) - 31517 is the frame of no node moved by any adopted plan.
## 3. Not done (brief: a row not matched = STOP)
Steps 2-6 not started: no stagekit edit, no self-test, no pin sweep, no pred MAIN recompute (PD394(b) is independent of PB but the card stops here).
md5 UNCHANGED: stagekit 0b5bb678, stagesim 95a162ba, stagexec a4df7e15, stage_prerun 7605116f, plan f4520b10, pred 18729409, licence f61a2514,
EL 79ec3207. Written only `tools/bench/prep_c161_a2_1_{probe,measure}.py/.log`, `diag_c161_a2_1_*`. No LabVIEW process.
OPEN: the 3 rows wired by p5s02b itself through new CQ7 tunnels (tags on 31506 and, for 2 of them, also 31517) are neither inherited nor this
plan's case moves: is the licence this plan's TUNNEL frames (dest case of t_in3/t_gi/t_hi...), the pred/open_rows, or a plan defect? (judgement)
OPEN: is a source reached through both CQ7 frames (doubled S1 uids, set-equal) a computation-preserving route under rule 1a? (judgement)
