---
type: facts
status: current
date: 2026-10-08
card: 147-b1-1
---
# Card 147-b1-1: offline re-score of D / TD / PB on the s06 retry end read (PD356(b) rules) -> ALL PASS under the 5-rename licence
Script `tools/bench/diag_c147_b1_1_rescore.py` (offline; pure stagekit/stagexec/vigraph functions), run of record `diag_c147_b1_1_rescore2.log` RESULT 9/0.
(`diag_c147_b1_1_rescore.log` = the first run; my TD scorer also scored created-tunnel names, e.g. t30289 '' -> '# FD points'; restricted to base terminals as TD is, stagekit.py:1377-1379.)

## Reconstruction (does the stored data reproduce the run?)
- R0 :6 term_identity_gates on the stored rows == the run's :652/:657 (new 15/16, lost 7/8, TD lost 5). R1 :8 all 6030 sim-end rows bind 1:1 to real rows.
- R2 :11 PB on the sim end == the pred's 18 rows. R3 :12 PB on the real end, no licence == run :659 (missing 2626|Terminal|array|0..3, extra none).
- Sim end vs real end :9: names differ ONLY on 2832/4160/4165 ('array'->'element'), 9505/9508 ('Value'->''), and the created tunnels' terminals
  30289/30292 ('' -> '# FD points'), 30293/30301 ('' -> '# DT points'); owners differ: none.

## Verdicts (PD356(b): TD/PB key (uid, owner), a name change passes only for a licensed uid; D reuse note)
| scorer | L5 = 5 measured renames | L3 = today's licence (2832/4160/4165) |
|---|---|---|
| D  | PASS new 16 == 16, lost 8 == 8 (:22) | PASS 16/16, 8/8 (:26) |
| TD | PASS lost [] == gone [], unwired [], unlicensed renames [] (:24) | FAIL unlicensed renames (9505,9503) 'Value'->'', (9508,9503) 'Value'->'' (:28) |
| PB | PASS cdiff == pred 18 rows + plan open pairs (:25) | PASS (:29): the #9503 rename does not change any cdiff row |
- VERDICT :30 `ALL PASS (L5)`. TD's run-time "unwired (9505,9503)" is not real: keyed by (uid, owner), 9505 is still the source of w28684.
- PB here restores base names for licensed uids (shape of stage_d1_l2b1.py:76); stage_d1_l2b1.py:75 additionally requires the licensed uids to
  be UNWIRED in the real end, which would VOID the licence in s06 (this session wires 2832/4160/4165) - PD356(b) drops that condition.

## PB's fourth missing row (4 rows for 3 renamed): the same key defect, not a graph difference
- Key = node|class|name|ordinal, ordinal = rank by term uid inside (node, class, name) (vigraph.py:244-245, :371-372); a row = a sink whose
  effective sources differ between S1 and the graph, or that exists on one side only (vigraph.py:862-871).
- S1 #2626 :13: array|0 = t4168 (src 5058 'x,y,z array out'), element|0..2 = 2832/4160/4165. Sim end :14: all four 'array', so array|0..3 =
  2832, 4160, 4165, 4168 by uid rank. Sim rows :16: array|0 (2832's source -19 vs S1's 4168 source 5058), array|1..3 (no S1 key), element|0..2 (no sim key).
- Real end :15: array|0 = 4168 alone, same source 5058 as S1 -> NO row; element|0..2 rows present :17 (same keys as the pred). So the 4th missing
  row is array|0 = the UNCHANGED 4168 (w25283 from #5058), seen as a row in the sim only because the rename-free sim ranks 2832 into slot 0.

## Wire 23807
- BASE :18: source (5171, #5058, 'pos in cal image out'); sinks (3173, #23166, 'Pos within cal image'), (9519, #23166, 'Pos: Diffraction Pattern'),
  (10871, #10757, 'array'), (10975, #10969, 'array'), (23798, #23508, '').
- REAL END :19: source (5171, #5058, 'pos in cal image out'); sinks (3173, #23166, 'Pos within cal image'), (10975, #10969, 'array').
- SIM END :20-21: w23807 absent; wire -25 = source (5171, #5058) with sinks (3173, #23166), (10975, #10969) == the real 23807 exactly.
- Sinks the sim removed: 9519, 10871, 23798 - all gone from the real 23807 -> REUSE-NOTED (:23).

## After
- md5 stagekit 9a3fceaf, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c == pins (log :3, :31); tasklist LabVIEW count 0.
OPEN: whether the #9503 'Value'->'' renames (9505/9508) are licensed like #2626, and whether a created tunnel's name change (# FD/# DT points) needs a scorer (NG passed).
