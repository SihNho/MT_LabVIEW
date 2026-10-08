---
type: facts
status: current
date: 2026-10-08
card: 149-a3-2
---
# Card 149-a3-2 facts: plan data fixed, s06 graph read 15/0, load_by_vi added; RETURNED FAIL at the Void census (COV 1112/4379 in 600 s)

## Step 1 - offline discriminating test `diag_c149_a3_2_disc.log` 4/0
- (a) set(new) 15 | kept_by_key {23807} = 16 == d_new 16. (b) real_end_rows: w23807 src (5171,5058), sinks (3173,23166),(10975,10969).
- (c) E5 expression on real_end_rows (6030 rows, 2008 wires): as written (deleted [23807], 15 new) -> deleted_wires_present [23807] FAIL;
  23807 moved to new (deleted [], 16 new) -> PASS.

## Step 2 - fix `diag_c149_a3_2_mkgraph.py:46-48` (kept_by_key uids -> new_wires, removed from deleted_wires); log 4/0
- W 16 == D line 16; DW plan delete_wire [23807], deleted_wires after fix []; plan `diag_c149_a3_2_graph_plan.json` md5 9561959c346544068c8ff03ca08e4c4f.

## Step 3 - graph read `diag_c149_a3_2_graph.log` 15/0, 172 s
- Launch gate: prerun without --graph failed X4/X6 (no graph JSON for 569ffbf5); passed 15/0 with `--graph graph_ring_p4s05_20261008_013759.json`,
  the same form as diag_c147_a1_1_graph_prerun.log:1 (predecessor graph). Logged nothing as gate-fp (accepted form exists).
- `graph_ring_p4s06_20261008_192149.json` md5 a3ecb92b27654c3d85b9ab5ff58aa069: 6062 rows, 10571 objs, 25 loops, 23 FS, 71 border tunnels.
- MEM after load 593.8 MB (log :24), after read 605.1, after FS 605.1; handles 45682 -> 45959. E5 PASS (2 made Local/IndexArray, 0 deleted,
  16 new present). G1 G2 G3 FS1 B X H2-H6 PASS.

## Step 4 - `diag_c149_a3_2_memload.log` 5/0
- memory_model.json 88eeb037 -> 8eec443c; flattened diff: added /load_by_vi/569ffbf5.../{cite,value,vi} only; removed [], changed [].
  value 593.8, cite diag_c149_a3_2_graph.log:24. Calibration fact only: scratch start 605.2 vs 612.6 assumed; peak 659.5 vs X10 674.2.

## Step 5 - Void census `diag_c149_a3_void_s06.log` 8/1 FAIL (first unexpected result -> return)
- s06 byte copy: load 16.6 s, read_terms 6062 rows 42.1 s, 4379 wired terminals on 2008 wires; read_term_type 0.54 s/read (flat 0.54-0.63);
  1112 read in 600.2 s (TCAP), wires w86637..w26932 (511). FAIL `COV every wired terminal read within TCAP`.
- Script Void test is BLIND (name contains 'void'; gscript.TD_NAMES:4585-4588 has no 0x00 -> '0x00'). Raw codes: 0 terminals with TD code 0x00,
  0 with no TD, 0 read errors (diag_c149_a3_void_census.md). Of the 16 new wires, w10166 and w23807 are NOT covered.
- s05 byte-copy census NOT run; s06-only list not computable. Census md5 b895f391; json a8bbd193.

| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c149_a3_void_s06.log | our-script-bug 0.584 (jev_gate.log:5328) | hypothesis review owed | dispatched c149-a3-2-void | ANSWERED: throughput holds; 'void' name test blind |

## Close - `diag_c149_a3_2_inv_after.log` 11/0
- s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877, s06 569ffbf5, stagekit, stagexec, gscript, elrule, errorlist_check unchanged;
  memory_model 8eec443c (one entry); no _c149a32_/scratch_c149_a3_2_ left; tasklist LabVIEW 0. Handles: census 48952 -> 42412.

OPEN: (1) complete census route: ~40 min/file per-terminal (~80 min s06+s05) vs checking whether allterms' op can return Data Type per row;
(2) Void check on code 0x00 needs a known-Void calibration read through OpTermDataType_v0 before it is trusted (peer sec. 4).
