---
type: facts
status: current
date: 2026-10-10
card: 159-a1-1
---
# Card 159-a1-1 facts: read-only graph read of the adopted P5-2a file 94ffff94 PASS 15/0; load_by_vi entry added (593.8 MB) 5/0; LabVIEW gone. No scratch, no rebuild.
## md5 pins (diag_c159_a1_1_pins_before.log 7/0, _after.log 6/0; helper diag_c159_a1_1_pins.py, hashlib only)
| file | before | after |
| claudeDev\D1_ring_p5s02a_20261010_023239.vi (adopted) | 94ffff9413599d5153a5e6fb409294ab | 94ffff9413599d5153a5e6fb409294ab |
| D1_ring_p4s09_20261009_060515.vi (s09) | eb1d0f31 | eb1d0f31 |
| D1_ring_p5s01a_20261009_101219.vi (P5-1a) | 2482fe7b | 2482fe7b |
| D1_ring_p5s01_20261009_124542.vi (P5-1) | 7f2582ae | 7f2582ae |
| tools/bench/adopted_scratch.jsonl | 83e74ded | 83e74ded |
| tools/bench/memory_model.json | c87d170a | 5b87de43 (memload, the one added entry) |
- No LabVIEW process before (pins_before.log) and after (pins_after.log, tasklist empty).
## Prerun on current bytes `diag_c158_a3_2b_graph_prerun.log:59` 15/0 (card 159-a1-1, labview read), BGRUN END rc=0 :60
## Graph read `diag_c158_a3_2b_graph.log` (0f99c8e1) RESULT PASS 15/0 (:336), BGRUN END rc=0 after 175 s (:338)
- K1 input md5 (:8), K2 original 2a78e17c (:14), K3 work copy byte-identical (:21): PASS.
- E5 PASS (:305): made {31262 Function, 31266 Function, 31448 DigitalNumericConstant, 31308 CaseStructure}; deleted nodes present []; deleted wires present []; new wires missing [].
- G1 PASS (:308); G2 PASS (:309) ('WhileLoop', 637), ('FlatSequenceFrame', 0); G3 PASS (:310) frames 27219, 27232 owned by Case 22694.
- FS1 PASS (:311) 23 FlatSequences; B PASS (:313) 7 UNMEASURED border tunnels [14430, 31050, 34409, 34489, 43605, 44160, 44164] of 74 (:312), none used.
- X PASS input md5 unchanged (:314); H5 refs 4 == 4 (:319); H4 scratch deleted (:321); H2 (:322); H3 pins (:328); H6 files left [] (:330).
- FACT close_panel(scratch) raised com_error 0x47D "Cannot close ... a closed" in hygiene (:317) - gates unaffected.
- MEM after load 593.8 MB private, handles 45657 (:24); after full read 605.4 MB (:280); after FS reads 605.4 MB, handles 45657 -> 45935 (:306); handles at exit 33989.
## Graph json `tools/bench/graph_ring_p5s02a_20261010_032547.json` md5 7ac24924f979afde964e63fb27957b45 (:307)
- 6175 terminal rows, 10769 objs, 25 loops, 23 FS, 74 border tunnels, 20 border entries (:307); 2048 distinct non-zero wire_uid (grep count).
## load_by_vi `diag_c158_a3_2b_memload.log` (5d95634b) RESULT PASS 5/0, BGRUN END rc=0
- Gates M, K, D, F, T PASS. Flattened diff: added /load_by_vi/94ffff94.../{cite,value,vi}; removed []; changed [].
- Text diff: '+  },' and the new entry: value 593.8, vi "claudeDev\\D1_ring_p5s02a_20261010_023239.vi (...card 158-a3-2b; PD354(a), PD379(c), PD386(e))",
  cite "tools/bench/diag_c158_a3_2b_graph.log:24 (MEM after load: 593.8 MB private)". memory_model.json c87d170a -> 5b87de43.
- Calibration print (no coefficient changed): scratch metered start 573.6 MB vs pred 603.4 (d -29.8); last-segment peak 621.1 vs X10 667.0 (d -45.9).
## Notes
- Load 593.8 MB for 94ffff94 vs the scratch METER start 573.6 MB (diag_c158_a3_2b_facts.md) - different meters/moments, quoted, not reconciled.
- Error List items NOT attributed (next card).
OPEN: memload's START_ASSUMED 603.4 vs measured scratch start 573.6 (-29.8) - does step 2's memory plan use load_by_vi 593.8 or a recalibrated start?
