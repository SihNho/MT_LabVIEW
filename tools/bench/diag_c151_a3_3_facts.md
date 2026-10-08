---
card: 151-a3-3
date: 2026-10-09
status: current
---
# 151-a3-3 facts - s07 stored end read re-scored offline, position-keyed D / TD / PB (stagekit 604529e8)

Run: `tools/bench/diag_c151_a3_3_rescore.py` -> `tools/bench/diag_c151_a3_3_rescore.log` (BGRUN END rc=0 after 2s; 8 pass / 0 fail; labview none, no licence: renames=None).
Inputs: base = plan finalized.base 765c687c, sim end = step_30_create.json c2b902b7 (both == plan pins, log P1); real = graph_ring_p4s07_20261008_224835.json
terminals (md5 field b3f86b32 = the s07 save), dedupe projection == scratch json `real_end_rows` 6050 rows (log P2); obj bind = 5 stored `bound`
entries (-1:30398, -9:4594, -15:4590, -22:4586, -29:4538), no created front-panel terminal needs a term bind (log P3). PB objs = the graph file's `objs`.

| gate | s07 RE-SCORE (position keys, 604529e8) | s07 ORIGINAL (150 log) | s08 (150 log) |
|---|---|---|---|
| D | PASS: new 13 == sim 13, lost 9 == sim 9, new-on-kept-nodes 0/0, reuse noted 0 (rescore.log D line) | PASS: new 8 == 8, lost 4 == 4, wire uid + source identity (diag_c150_p4s07v18_scratch.log:363) | PASS: new 11 == 11, lost 5 == 5 (diag_c150_p4s08v18_scratch.log:267) |
| TD | PASS: unwired 0, moved 0, lost 0 == deletes 0, recycled 0, renames 0, extra 0 | PASS: key uid+owner, renames 0, unlicensed [] (:368) | PASS: key position, renames 0 (:272) |
| PB | PASS: cdiff 19 == pred 19, open pairs == plan 17, restored 0, unlicensed [], rows == run's stored cdiff_rows | PASS: 19 rows / 17 pairs (:370) | PASS: 21 rows / 19 pairs (:274) |

- D count difference 13/9 vs 8/4: under position keys 5 wires (23807, 23850, 25309, 25358, 25394) count as lost + new (their ends changed), and the sim predicts the same 5 (rescore.log D detail). Verdict unchanged.
- The 150 s07 log is 27 pass / 0 fail with D, TD, PB all PASS (diag_c150_p4s07v18_scratch.log:363,368,370,399); no D/TD/PB failure is recorded there, unlike the brief's "failed on a false positive".
- Invariants before == after in-run: stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, vigraph 13be0847, stagesim 748bbf30, s07 VI b3f86b32, memory_model a28b6dd7 (rescore.log INV).
- gate_fp_queue.jsonl: 72bd4902 at card start (03:5x), a89ac37d at script start and end; this card wrote no line to it (another writer in between).
- tools/hooks: no edit (git status shows only the pre-existing material_marker.log). tasklist LabVIEW count 0.

OPEN: brief says s07 "failed on a false positive" but the 150 log shows s07 D/TD/PB PASS - which s07 failure was meant (if any)?
