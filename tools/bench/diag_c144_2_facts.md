---
type: facts
status: current
date: 2026-10-07
---
# Card 144-a2-1 facts: P4 session 3 scratch 20/0, Error List 55 == pred, ADOPTED `D1_ring_p4s03_20261007_202957.vi` (282301ca), graph read 15/0

## Before
- `diag_c144_2_check.log` 10/0: 7 card inputs md5 == card; s02 84cac487 and bed 39511877 unchanged; no LabVIEW.
- guard_cycle / guard_peer did not refuse the scratch launch; no prior-art review was asked for (none dispatched).

## Scratch (ONE run) `tools/bench/diag_c143_p4s03v18_scratch.log` (BGRUN END rc=0, 574 s; log name fixed by the recipe's LOG constant)
- RESULT 20/0 (:343-345) + MEM / MEML / IN / GONE PASS (:348-351). L0, K1-K3, L1 (20 ops, checkpoints 0,2,3,4,5,6,9,11,13,14,16,17,19,20),
  PRIM p4_ras_bufdiff (:130), E1 every checkpoint == sim, STEPX diff 0 at all 13 (:304), NG, FR 9 objects on [686, 4866, 29699, 32464] (:306),
  D new 9 == sim / lost 1 (w16483) (:307), TD (:312), PB 16 rows / 11 open (:314), HB 45926 -> 46532 (:316), PS, H5 9/9, H2, H3, H6.
- Peak **673.7 MB** (X10 676.4, d -2.7) (:347); MEMSTOP 680 not hit.
- `new:LRB1.value` / `new:LWB1.value`: no refusal; op 8 readback #29683 'BufDiff' (:170), ops 7-8 err '' (:163, :172), E1 diff 0 at op 9 (:184).
- Bound: K6 -2->29432, I6 -4->29636, LRB1 -6->29493, RAB1 -8->29396, LWB1 -13->29683, -17->29584, -21->29566, SL1 -27/-28->29403/29548,
  KL1 -33->29576, SD1 -36/-37->29648/29655, KD1 -42->29662, W1 -45->16483 (re-uses the cut wire's uid 16483), -46->29699, LRN4 -49->29720.
- Census MEASURED (:310) {ArrayConstant 1, ControlTerminal 1, Diagram 1, DigitalNumericConstant 3, FlatSequenceOuterTunnel 1,
  GrowableFunction 1, InnerTerminal 6, LeftShiftRegister 2, Local 3, OuterTerminal 5, RightShiftRegister 2, SelectorTunnel 1, Terminal 14,
  Wire 9}, lost uids 0; written into the pred by `diag_c144_2_census.py` 5/0 (`diag_c144_2_census.log`, cites line 310).

## Error List `tools/bench/diag_c144_2_el.log` (--role final, 763 s)
- Window N **55** == items 55 == pred predicted_total 55. Compared against the s02 expected file: extra 2 = 'Shift Register: unwired from
  inside the loop' x2 (pred new sr -27, -36), missing 0 (the new cond/local items took the 2 closed items' licences).
  JSON `errorlist_D1_ring_p4s03_20261007_202957_20261007_203956.json` 488c6866. Verdict line MISMATCH, rc 1 (vs s02 file); BY-DESIGN check STOP
  "no plan step files" (fail-closed). RESULT line 11/0.
- `diag_c144_2_elexp.py` 6/0: `errorlist_expected_D1_ring_p4s03_20261007_202957.json` 2b8f9f25 (55 = s02's 51 + 2 re-labelled boundary
  entries (LRN4 #29720 'Num', W1 #16483) + SR x2); compare(read, new expected) extra [] missing []; pred errorlist.measured_total 55, checked.

## Adopt + graph
- `diag_c144_2_adopt.py` 3/0 (stagexec.adopt_scratch by import): `adopted_scratch.jsonl` record, artefact 282301ca, input 84cac487,
  required E1,FR,D,TD,PB,PS; adopted_launch returns it.
- `diag_c144_2_graph.py` (copy of diag_c143_1_graph.py, names only; dry PASS, prerun 15/0) 15/0, 174 s: load **598.5 MB**, 610.0 after
  reads; handles 45617 -> 45895; E5 9 made objects with the plan classes, 9 new wires present; graph
  `tools/bench/graph_ring_p4s03_20261007_205535.json` **5638469b** (5992 rows, 10445 objs, 25 loops, 22 FS, 7 unmeasured borders unused).

## After
- `diag_c144_2_check_after.log` 9/0: s02 84cac487, bed 39511877 unchanged; inputs unchanged except the pred (now b212bb33, by design); no LabVIEW.
- Pred md5 e1ff772c -> 7c0cdc78 (census) -> b212bb33 (EL measured).

## Own-script failure (not a LabVIEW observation)
- `diag_c144_2_cls.py` (offline helper for E5 classes) v1 FAIL (walked wrong json fields), v2 traceback; guard_peer owed a hypothesis review
  (Jev ladder new-problem p=0.75; card peers = priorart only) -> gate-fp **fp-44** logged, RULE-GATE-FP discharged; v3 PASS 2/0
  (uid->class from plan creates x STEPX lines == graph plan edits.made).
