---
type: facts
status: current
date: 2026-10-09
card: 152-b3-1
---
# Card 152-b3-1 facts: s09 scratch PASS 20/0 + MEM 4/4, ADOPTED eb1d0f31; EL 45 (s08 46, pred 46, carry-alt 45); graph 15/0; load_by_vi 596.7 added
## Before
- `diag_c152_b3_1_inv_before.log` 38/0 (all card inputs md5 == task pins; step-8 pins incl. addrcheck 207beb0d, stagesim 128bacfb, derived e26b4d90, ring-p4d cf2ffa4a).
- Scratch `--dry` 1/0 (`diag_c152_b3_1_scr_dry.log:88`); `--prerun` 16/0, X10 633.3 (:107), X11 PASS (:90), X14 rows 6 / 15 proven: no (:108);
  `--scratch-required` MAIN rc 3, CENSUS-UNPREDICTED rows [1..6] (`diag_c152_b3_1_scrreq.log:3-4`); `--check-launch` ALLOW rc 0. All == 152-b2-1.
## Prior art
- Not demanded: the launch gate did not refuse; no prior-art review run.
## Scratch (ONE run) `diag_c152_p4s09v18_scratch.log` RESULT 20/0 (:178), BGRUN END rc=0 after 277 s
- NEW byte copy of f99e8414 = `claudeDev\D1_ring_p4s09_20261009_060515.vi` (K3 :64); saved md5 eb1d0f3107bbba49c9ae67a47c0ee50f, 320361 B (S2 :156, PS :158).
- SG 0 rows (:67). L1 6 actions -> 6 ops, checkpoints (0, 1, 3, 5, 6) (:68). E1 every checkpoint real == sim, 6 ops (:137): STEPX 01/03/05/06 diff 0 (:84,:104,:124,:136).
- Op 187 `p4_x_slot_fs`: NAMEGATE sim == real 'min slot' on both faces (:103), bound #30724. Op 189 `p4_x_n2_out`: NAMEGATE ok (:123), bound #30743. Op 185 #30710 (:82). NG PASS (:138).
- FR 0 created, nc 0 (:139). D new 6 == sim 6, lost 2 == 2, reuse none (:140). TD renames 0, unlicensed [] (:145). PB == pred 21 rows / 19 open pairs (:147).
- CENSUS-ALL net {FlatSequenceOuterTunnel 3, Terminal 6, Wire 4}, lost 2 (:142-144). PRIM: no primitive created (0 creates).
- Licence: renames 0 / unlicensed [] (TD :145); licence file has 0 renames (all dsts name-form). X11 CLEAN (prerun :90).
- Memory: METER start 561.9 MB (:69) vs pred start 595.0 (d -33.1); peak 590.5 MB vs X10 633.3 (d -42.8) (:180); MEM/MEML/IN/GONE PASS (:181-184).
- Handles: PH 45685 -> 45843, HB PASS (:148-149); H5 7 == 7 (:162).
## Adopt `diag_c152_b3_1_adopt.log` 3/0 (stagexec.adopt_scratch by import)
- `claudeDev\D1_ring_p4s09_20261009_060515.vi` md5 eb1d0f3107bbba49c9ae67a47c0ee50f, input f99e8414; adopted_scratch.jsonl -> fa629f3b; L PASS (:38).
## Final Error List (elrun) `diag_c152_b3_1_el.log`: 45 items == window N 45, rc 1 MISMATCH vs s08 expected (extra 0, missing 1); 578.5 s
- Read `errorlist_D1_ring_p4s09_20261009_060515_20261009_061027.json` 080255ad; bed md5 unchanged; handles 37248 -> 31287.
- Review: discharged by RULE-SAME-ROW (`jev_gate.log`, review 2026-10-09-c151-a3-1-el46.md, same script diag_c149_a1_2_elrun); none bought.
- Expected `errorlist_expected_D1_ring_p4s09_20261009_060515.json` 5146f980, total 45, 8 entries (`diag_c152_b3_1_elexp.log` 5/0).
- Dropped s08 entry: Index Array 'Contains unwired or bad terminal' x1 (:6); added [] (:7).
- elcls vs pred 46: input -1, total -1. vs s08 46: input -1, total -1 (:21-22). Equals the pred's carry alternative_total 45 (closes input #29879) (:19).
- OCR classes: 'not connected to anything' 21 + 'anvthing' 1 = 22, s08 20 + 2 = 22 (same total, OCR split moved) (:14-15).
## Graph `diag_c152_b3_1_graph.log` 15/0, 172 s (dry 1/0, prerun 15/0 with --graph graph_ring_p4s08_20261009_033522.json)
- `tools/bench/graph_ring_p4s09_20261009_062044.json` md5 22f967b513726a01c9d8f63269f689e6: 6097 rows, 10631 objs, 25 loops, 23 FS, 74 border tunnels (:301).
- MEM after load 596.7 MB (:24), after read 608.3; handles 45619 -> 45890 (:300). E5 PASS 0 made / 6 new wires present (:299). Plan `diag_c152_b3_1_graph_plan.json` a93a3c70.
## FS #29721 (`diag_c152_b3_1_fs.log` 2/0): frames [29869], owner ('FlatSequenceFrame', 0); 10 rows on #29869, 3 border tunnels [30710, 30724, 30743]
- #29879 IndexArray 0 'array' t29882 w30685 | 1 'element' t29885 w30772 src | 2 'index' t29888 w30687; #30002 0 'array' t30013 w30691 | 1 'element' t30025 w0 src | 2 'index' t30028 w0;
  #30016 Local 'Num' t30023 w30685 src.
- Tunnel #30710 'Bead is good? array out' inner t30720 w30691 src / outer t30728 w30755 (entry, outer frame 23166).
- Tunnel #30724 'min slot' (op 187) inner t30736 w30687 src / outer t30760 w30763 (entry). Tunnel #30743 'Index of closest\ncal image slice, bead 2' inner t30761 w30772 / outer t30768 w30682 src (exit).
## memory_model `diag_c152_b3_1_memload.log` 5/0: a28b6dd7 -> 6f2b5687; added /load_by_vi/eb1d0f31.../{cite,value 596.7,vi} only; removed [], changed [].
## After `diag_c152_b3_1_inv_after.log` 37/0: every step-8 pin + card input unchanged; no _elc_/scratch_c152 left; claudeDev p4s08 + p4s09 files; tasklist LabVIEW 0.
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c152_b3_1_el.log | RULE-SAME-ROW (no JEV-LADDER row) | discharged by c151-a3-1-el46 | nothing | graph/memload launches allowed |
OPEN: EL 45 = pred's carry alternative, not the no-carry 46 - set carry as the pred default for P4 s10+? Metered start -33.1 vs pred 595.0 (s08 was +21.4).
