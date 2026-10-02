---
type: facts
status: current
date: 2026-10-02
---
# Card 141-2 facts: P4 v16 session-1 scratch (bed byte copy) - stopped at gate TD, no launch
- Scratch `diag_c141_p4s01_scratch.log` (BGRUN END rc=1, 364 s): 21 pass / 1 fail (:311). Bed md5 395118775a52 unchanged (:318), LabVIEW gone (:319).
- PASS: E1 real == sim at every checkpoint, 24 ops (:272); NG (:273); FR 3 created objects on frames [27641, 27722, 32464] (:274); D new 2 / lost 2 == sim (:275); PB cdiff == pred 16 rows + 11 open pairs (:281); HB handles 45653 -> 46066 (:283); PS saved; H2/H3/H5/H6.
- PRIM gate: 3 PASS / 0 FAIL - every created node read back 'Replace Array Subset' / GrowableFunction (#29407, #6942 :160, #6805 :246).
- FAIL TD (:280, recipe `stage_d1_ring_p4_s01.py:65-69`): lost_rows [27997, 28018, 28030, 28973, 28983, 28989] vs plan_deletes [27997, 28004, 28018, 28030, 28973, 28979, 28983, 28989]; difference {28004, 28979}.
- 28004 / 28979 are the real sink uids of ops 12 (`connect #28962->#28004`, sink D[58].N[3].t0 of new #6942, :167) and 24 (`connect #29252->#28979`, sink D[59].N[11].t2 of new #6805, :267).
- CEN2 UNPREDICTED (declared set empty in pred) (:276); CENSUS-ALL net {GrowableFunction +1, Terminal +4}, new {GrowableFunction 3, Terminal 9, Wire 2}, lost 9 (:277-279).
- Memory: peak 601.4 MB (X10 pred 669.3, d -67.9) (:315); MEM PASS, MEML (<= 675) PASS (:316-317).
- ExecState 0 after all rows (expected, bed broken by design) (:281 area).
- Jev ladder: `JEV-LADDER | 22:40:14 | diag_c141_p4s01_scratch.log | new-problem p=0.664 | BLOCK (review owed)` -> hypothesis review dispatched.
- Review `archive/peer/2026-10-02-c141-2-scratch-td.md` ANSWERED: LabVIEW re-used deleted uids in-session (#28004/#28979 now belong to the new nodes); TD, `unw` and gate D key on raw uid -> should key on (uid, owner, name); scratch likely acceptable. Disposition written (not acted on: tools edit forbidden by the card).
- Not done (card rule "return BEFORE the launch"): scratch Error List read, launch, in-between file, graph read.
- Cleanup `diag_c141_2_cleanup.log` 3/0: scratch `scratch_c141_p4s01_20261002_223304.vi` (md5 9cad0cad) deleted, bed md5 unchanged, no LabVIEW.
