---
type: facts
status: current
date: 2026-10-10
card: 160-b1-1
---
# 160-b1-1: step-1 mapping into stagekit (PASS) + plan_ring_p5s02b on 94ffff94 (FAIL at gate SB, route check); offline, no LabVIEW
## Part 1 - stagekit
- `tools/stagekit.py` ac3a8f57 -> 1441bb4ca75eb5a59afaa3555690db37: one appended section `stagekit.py:2733-2869` (before the trailing scope header;
  no existing line moved or edited). `FRAME_SYM` :2738, `made_symbols` :2741, `_head` :2747, `used_symbols` :2751, `map_symbols` :2769, `map_frames` :2796,
  `apply_map` :2832, `bound_from_cmap` :2858. Bodies == prep_c159_c1_1_lib.py:31-157; module-level `import copy`, `import re` added for them (:2736-2737).
  Docstrings name selftest_c160_stagemap; bound_from_cmap's docstring now states its real return `(head, {sim: real})`.
- `selftest_c160_stagemap.log:9` RESULT PASS 5/0: P0, T1 symbols map, T2 frame map ['#30914'], T3 == plan_ring_p5s01b 75a77a00 (12 rows),
  T4 all six stagekit.<f> == prep_c159_c1_1_lib.<f> (log:7; bound_from_cmap on p5s01a map 52 entries and the 94ffff94 run's map 42).
- prep_c159_c1_1_lib.py unedited (218af76c).
## Pins
- Only `selftest_c160_delwire.py:43` pinned stagekit (ac3a8f57); re-pinned -> 1441bb4c (docstring :17 says so). runcheck / wire0face / cen2_ends pin no stagekit.
- Re-run on the new bytes, counts == last pass: runcheck `selftest_c158_runcheck_c160b.log:23` 10/0; wire0face `selftest_c158_wire0face_c160b.log:40` 24/0;
  cen2_ends `selftest_c159_cen2_ends_c160b.log:16` 8/0; delwire `selftest_c160_delwire_c160b.log:25` 12/0.
- Other files with ac3a8f57 (not edited): cards task_159-f1-1.json, task_159-f1-2.json, task_160-a1-1.json (input pins of past cards); stage_prerun pins no stagekit md5.
## Part 2 - plan (prep_c160_b1_1_mk.py, 140 lines, mapping by stagekit calls) -> `prep_c160_b1_1_mk.log` RESULT FAIL 9/1 (log:76)
- PASS: M0 pins (VIs 94ffff94/eb1d0f31/2482fe7b/7f2582ae, tools, input 56bfddd3), K old plan kept `plan_ring_p5s02b_c159.json` caef7e1c, E1, CM
  (map plan_ring_p5s02a_4284c22a_20261010_023453.jsonl), MAP CQ7 -> #31308, f0 -> #31506, f1 -> #31517 (log:8-11), FRM 7 ends (log:19),
  DW w10394 from P5-1 #3052 'File # Saved', Wire obj, 0 rows (log:20), ROWS delete + stagekit.apply_map(A24..A40) == input, 18 actions (log:21).
- REALSIM now replays action 1 and all 18 steps: failed null, 0 PROVISIONAL (log:28-45, 74).
- **SB FAIL (log:75): route check FAIL, so final False.** stagesim FINALIZE REFUSED (log:54): UNROUTABLE 2 rows -
  route 4 acts [8,9,10] ['t_go','w_gout','w_gr']: "ADDRESS: node #24083 not in Diagram[124] (#23405).Nodes[]" (log:49);
  route 7 acts [15,16,17] ['t_ho','w_hout','w_hr']: "ADDRESS: node #24150 not in Diagram[124] (#23405).Nodes[]" (log:52). Message from stagexec.py:1920.
  Routes 1 delete_wire, 2/3/6 cfw, 5/8 case_frame_wire route fine (log:46-53). #24083 / #24150 are the RSR nodes of the A32 / A39 MERGE rows.
- Stopped there (PD390e, gate fatal): compile, MERGE-END, X10 MAIN, X8, X17 and gate U did NOT run; prep_c160_b1_1_session.json not written.
- Output `plan_ring_p5s02b.json` 09ebc7a6c08f466997ba472ec0c64109, final False (written by stagesim.simulate).
## MERGE rows (plan_ring_p5s02b_in.json:192,235,271,314; log:22-25, gate PASS log:26)
- A28 w_gl t24190 stub w24285 | A32 w_gr t24139 stub w24264 | A35 w_hl t24288 stub w24312 | A39 w_hr t24235 stub w24300; each why =
  "ASSUMPTION (PD388(c), not measured ...): MERGE ... sim-end uid w<uid> ...; CEN2 judges by wire ENDS, not uid (PD389(b))".
## md5 unchanged
- stage_prerun 7605116f, stagesim a3261b56, stagexec c4a6e0b6, addrcheck 207beb0d, vigraph a7eb58c7, prep_c159_c1_1_lib 218af76c, input 56bfddd3.
  VIs checked at M0 only (no LabVIEW process ran). tools/hooks: only hook-written material_marker.log modified.
OPEN: route check UNROUTABLE for route rows 4 and 7 (tunnel route, nodes #24083 / #24150 not in Diagram[124] #23405) - plan change or tool?
OPEN: past cards task_159-f1-1/-2, task_160-a1-1 still pin stagekit ac3a8f57 (closed cards; no re-pin done).
