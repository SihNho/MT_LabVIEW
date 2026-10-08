---
type: facts
status: current
date: 2026-10-08
card: 147-a1-1
---
# Card 147-a1-1 facts: s05 work copy 3f9ac26b ADOPTED without a rerun; final EL 55 == 06a59001; load 606.7 MB; graph + #2626 table

## Before (`diag_c147_a1_1_check_before.log` 13/0)
- 8 card inputs md5 == card; work copy `D1_ring_p4s05_20261008_002621.vi` 3f9ac26b (319045 B); s04 95e408ff, s03 282301ca, bed 39511877; no LabVIEW.

## Adopt (`diag_c147_a1_1_adopt.log` 3/0, by import, no LabVIEW)
- `stagexec.adopt_scratch` record appended (stage `stage_d1_ring_p4_s05v18.py`, plan md5 1fc9b486, iso 2026-10-08 01:22:36); artefact = the work copy
  itself, same bytes (stagexec.py:4027 copies nothing). `adopted_scratch.jsonl` md5 83c0a7d2. Adopted file:
  `claudeDev\D1_ring_p4s05_20261008_002621.vi` md5 3f9ac26b69179eb53c202d90407ce7ee.

## Error List, full --role final read of the adopted file (`diag_c147_a1_1_el.log`, rc=0, 784 s)
- Prediction = `diag_c147_a1_1_elpred.json` (96d9fcde), built from read 06a59001 (`diag_c147_a1_1_elexp_pred.log` 4/0).
- 55 items == window N 55, 55 double-clicked and fronted, extra 0, missing 0, ERRORLIST-VERDICT OK, bed md5 unchanged; read file
  `errorlist_D1_ring_p4s05_20261008_002621_20261008_012323.json` b654430d. Handles 37205 -> 31253 (record).
- Expected file `errorlist_expected_D1_ring_p4s05_20261008_002621.json` 6f2ca28a, total 55, 12 entries = s04's entries with counts from the
  read; dropped (0 items): SubVI 'Image In' x1, Shift Register SL1/SD1 x2 (`diag_c147_a1_1_elexp_final.log` 4/0).
- RECORD vs 06a59001: total 55 == 55; all 13 per-class counts equal (`diag_c147_a1_1_elexp_final.log` RECORD lines).

## Fresh load + graph (`diag_c147_a1_1_graph.log` 15/0, 175 s)
- Launch gate DRY first refused ("no graph JSON carries md5 3f9ac26b", the file the script writes); logged fp-51; passed with
  `--graph graph_ring_p4s04_20261007_223245.json` as cycle 145 did (`diag_c147_a1_1_graph_dry.log`, `_prerun.log` 15/0).
- Fresh LabVIEW 33970 handles; MEM after load 606.7 MB private (:24, the meter of every load_by_vi entry); after full read 618.3 MB.
- `graph_ring_p4s05_20261008_013759.json` md5 cbeeadf5: 6054 rows, 10549 objs, 25 loops, 23 FS, 71 border tunnels (7 UNMEASURED, unused).
  E5: 6 made (Local 30116/30215/30239, IndexArray 30119/30216/30240), 11 new wires present. In-run handles 45655 -> 45927; exit 33970.

## Build Array #2626 (`diag_c147_a1_1_t2626.log` 3/0) - identical to s04
| term_uid | dir | name | class | wire | other end |
|---|---|---|---|---|---|
| 2813 | output | appended array | Terminal | 0 | - |
| 2832 | input | array | Terminal | 0 | - |
| 4160 | input | array | Terminal | 0 | - |
| 4165 | input | array | Terminal | 0 | - |
| 4168 | input | array | Terminal | 25283 | #2765 SelectorTunnel, #5058 SubVI 'x,y,z array out', #10850 RightShiftRegister |
Data type is not a field of the graph read: UNREAD.

## memory_model.json (`diag_c147_a1_1_memload.log` 5/0)
- One key added: `load_by_vi/3f9ac26b69179eb53c202d90407ce7ee` {value 606.7, cite diag_c147_a1_1_graph.log:24}; flattened diff added = its 3 leaves,
  removed [], changed []. md5 559be4cf -> 88eeb037. X10 / MEM_STOP / MEMSTOP untouched.

## After (`diag_c147_a1_1_check_after.log` 12/0): 3f9ac26b, s04, s03, bed unchanged; no LabVIEW process.
