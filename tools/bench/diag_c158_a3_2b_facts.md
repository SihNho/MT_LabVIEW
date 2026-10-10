---
type: facts
status: current
date: 2026-10-10
card: 158-a3-2b
---
# Card 158-a3-2b facts: prior-art novel; the ONE retry scratch PASSED 23/0 and was ADOPTED (94ffff94); final Error List 56 (pred 47, P5-1 45) -> hypothesis review -> RETURN before graph read / load_by_vi / delete / step-2 plan. LabVIEW gone.
## Prior-art (first act) `archive/peer/2026-10-10-priorart-c158-a3-2-p5s02a-retry.md` ANSWERED 45 s, `PRIOR-ART: novel` (:320); NOVEL RECORD scratch sha 3d820dd7 (diag_c158_a3_2b_priorart.log)
- Note (not a finding): SCRATCH label still `scratch_c156_p5s02a` (recipe :31). Disposition filled (:328-333).
## Invariants before `diag_c158_a3_2b_inv_before.log` 63/0; after `_inv_after.log` 61/0 (helper diag_c158_a3_2_inv.py now takes the card id as argv[2], no copy)
- s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae, every card pin unchanged after; memory_model c87d170a unchanged; adopted_scratch dd0aa787 -> 83e74ded (the adoption).
## Pre-checks on unchanged bytes (re-run)
- dry MAIN PASS 35/36 unverified 0 (_dry.log); dry scratch PASS 34/37 unverified 0 (_scr_dry.log).
- prerun MAIN 16/0, X10 planned peak 674.7 <= 675 (_prerun.log); scratch 16/0, X10 669.6 (_scr_prerun.log); --scratch-required rc 3 CENSUS-UNPREDICTED (_scrreq.log).
- check_launch ALLOW, RETRY_CARD ('158-a3-2b', None) (_checklaunch.log; helper diag_c158_a3_2_checklaunch.py takes the card id as argv[1]).
## Scratch `diag_c158_p5s02a_scratch.log` (6a18fd61) RESULT PASS 23/0 (:315), BGRUN END rc=0 after 442 s (:322); work copy D1_ring_p5s02a_20261010_023239.vi
- E1 diff 0 at checkpoints 0,1,3,6,8,9,12,15,16,17 (:55,67,94,127,146,161,225,251,259,267); E1 PASS (:268); L1 17 ops, checkpoints as planned (:52).
- FATE (read at op 12, :219-224): src_wire=0 for 10394 (t3060), 24091 (t25235), 24153 (t24367), 24330 (t24360); kept 24285, 24312; every sink_wire 0.
- Op 16: connect_term_uid #5760 <- #24360 err '' (:254), node census 704->704; op 17: #5778 <- #24367 err '' (:262).
- OPCENSUS op 16 NOT measured ("whole read after op 15: False", :294); op 17 {SelectorTunnel 1, InnerTerminal 2, OuterTerminal 1, wires 2} (:295) == R1 delta.
- NG PASS (:269); FR PASS 4 objects on [686, 23405] (:270); D PASS pairs 21 == sim 21, lost 12 == 12 (:271), RECORD stub 24091 sim-only (:272).
- CEN2 PASS measured == declared, all 13 classes (:273); TD PASS (:277), RECORD (25223,1,InnerTerminal) (:278).
- PB PASS frame-keyed, RECORDED tag-only rows #376 'cal cluster path' @31546/f0 and 'file size' @31557/f0 (:280-282).
- No CD or INV gate line exists in this recipe's log (grep). HB PASS 45681 -> 46325 (:284); PS saved 323486 B (:293); H5 refs 12 == 12; H2/H3/H6 PASS (:299-309).
- METER start 573.6 MB (:53) vs 597.5 (-23.9); peak 621.1 (:266) vs MAIN 674.7 / X10 667.0 (-45.9); MEM/MEML/IN/GONE PASS (:318-321); handles 33996 -> 40234 (:45,:310).
## Adopt `diag_c158_a3_2b_adopt.log` 3/0 (copy of diag_c158_a2_2_adopt.py, log/sum names + note only)
- ADOPTED claudeDev\D1_ring_p5s02a_20261010_023239.vi md5 94ffff9413599d5153a5e6fb409294ab (adopt/1 iso 2026-10-10 02:40:59; required E1,FR,D,TD,PB,PS).
## Final Error List `diag_c158_a3_2b_el.log` (elrun --role final vs P5-1 expected ffc4cf66): 56 items == window 56, extra 11, missing 0, MISMATCH, rc 1, 753.7 s
- Read `errorlist_D1_ring_p5s02a_20261010_023239_20261010_024108.json` 25d6084b; bed md5 unchanged; handles 37248 -> 31281.
- Reasons P5-1 45 -> 56: no-source 0->5, not-connected 22->23, loose ends 21->23, LoopTunnel undirected 0->2, While-input-to-SubVI-input 0->1, input 1->1, two-types 1->1.
- vs pred 47 (input 3, not-connected 22, loose-ends 21, two-types 1): total +9; input -2.
## Jev ladder / review
| log | ladder class p | NEXT-ACTION | what I did | result |
| diag_c158_a3_2b_el.log | new-problem p=0.658 (guard_peer 02:54:02) | hypothesis review owed | dispatched claude -Role hypothesis (flags.peers) | ANSWERED 268 s |
- `archive/peer/2026-10-10-c158-a3-2b-el56.md`: my claim (11 extras = step-2-owed rows) PARTLY REFUTED: A48 frame index was already open in P5-1 (plan :78-82),
  the named case tunnels do not exist yet; 'Loop Tunnel undirected' fits out-tunnels #5204/#10404 (re-fed by K3/K4, not actions 24-40); 11 is a NET count; a
  remnant no later action re-feeds would be a rule-1a change. Proposed offline test: errorlist_shots bd_*_after{1,2,4,6,7,8,49,50}.png vs node positions.
  It warns NOT to write the expected file from these 56 items until attributed. Disposition filled; nothing acted on.
## Not done (returned at this result): expected EL file (diag_c158_a3_2b_elexp.py written, not run), graph read (diag_c158_a3_2b_graph.py + plan
  diag_c158_a3_2b_graph_plan.json 91fcfbec, dry 1/0 prerun 15/0, not launched), load_by_vi (memload written, not run), nodes, failed-copy delete
  (diag_c158_a3_2b_delete.py written, not run; 152721 cac5236b + resume_plan_ring_p5s02a_20261009_153334.json still on disk), step-2 plan.
- Step-2 facts for later: plan_ring_p5s02r_in.json A24..A80 = 57 actions > 40 (PD379(c)), so step 2 = F3..J (A24..A60, 37) and K3/K4 (A61..A80) a step 3;
  the card's write globs hold no tools/recipes/** file, so a step-2 recipe dry/prerun cannot be written under this card.
OPEN: run the review's screenshot attribution test (8 new-class items) before accepting 94ffff94 as the step-2 base and writing its expected file?
OPEN: the step-2 plan needs a recipe pair under tools/recipes (not in this card's write globs) - which card writes it?
