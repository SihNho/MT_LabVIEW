---
type: facts
status: current
date: 2026-10-10
card: 165-3-4
---
# 165-3-4 facts: the ONE step-5 scratch PASSED 20/0 (peak 594.8 <= 675) and was ADOPTED as D1_ring_p5_20261010_172913.vi (75773b0d, P5 final); Error List 47 vs predicted 49 (missing 2) -> RETURN; graph / memory_model / pred census NOT done; LabVIEW gone.
## Pre-checks (offline)
- Hashes before (diag_c165_a3_4_hash_before.log) 12/0: 10 card inputs equal; VIs eb1d0f31 / 7f2582ae / 94ffff94 / f9ae7751 / 564d8cbe / 6dcd5c3d; stagekit dd57c1ca, stagesim 95a162ba, stagexec 1d5309f4, stage_prerun 7605116f, memory_model ff0fabca.
- check_launch on the brief's command: ALLOW, units == 1 (diag_c165_a3_4_checklaunch.log); --scratch-required rc 3 CENSUS-UNPREDICTED rows [1..13] (diag_c165_a3_4_scrreq.log). Scratch log absent before launch, no LabVIEW process.
## Scratch diag_c165_p5s02e_scratch.log: RESULT PASS 20/0, BGRUN END rc=0 after 448 s
- `SCRATCH-P5S02E peak 594.8 MB (X10 659.9, d -65.1); final ...D1_ring_p5s02e_20261010_172913.vi md5 75773b0d...; bed md5 6dcd5c3d...`; `GATE MEM ... PASS`, MEML PASS, IN PASS, GONE PASS (tail). METER start 564.2 MB (:60; pred X1 609.8).
- L1 13 actions -> 9 ops == pred kinds, checkpoints (0,1,3,4,6,7,8,9) (:59). STEPX diff 0 at 00,01,03,04,06,07,08,09 (:62,76,92,101,116,124,133,141); E1 PASS (:142) = plan's last checkpoint reached.
- PRIME-SKIP #8776 (:64) and #24342 (:65) exactly as 165-3-1; PRIME 0 proved, unprovable [] (:66).
- Bound: sr_k4 {-1: 31812 RSR, -2: 31817 LSR} (:92), c_k4i -7: 31824 (:101), t_k4o -10: 31847 (:116), t_k4i -16: 31855 (:124) (SelectorTunnels).
- NG 0 ops (:143); FR 1 created on [686] (:144); D pairs 10 == sim 10, lost 7 == 7, reuse noted [] (:145); TD PASS, lost = #5204/#10404 outer direction (:150); PB PASS by position [31,31] = 26 + 5 RECORDED (:157), RECORD rows cal cluster path 1, error in 3, file size 1, selected path 1 (:152-155); HB 45621 -> 45950 (:159); PS 324562 B (:166-168); H5/H2/H3/H6 PASS (:176-186). ExecState 0 (by design, :151).
- CEN2 UNPREDICTED (:146). MEASURED new uids (:148): DigitalNumericConstant 1, InnerTerminal 6, LeftShiftRegister 1, OuterTerminal 4, RightShiftRegister 1, SelectorTunnel 2, Terminal 1, Wire 5; net (:147) Wire 3; lost uids 2 (:149).
- OPCENSUS op 2 {lost_wires 1, wires 0, owners {}, terms {}} (:169); op 9 same (:172); ops 6/7 not measured (:170-171).
## PD401(b) per pair (scratch log + diag_c165_p5s02e_scratch.json ops)
- dw_10362: OP err '' (:71), Node census 706 -> 706 (:73), checkpoint 1 diff 0 vs sim step_01 (face t8776 wire 0 in sim) (:76). w_k3f: `connect_term_uid #8776 <- #31815` err '' (:79), result wire_uid 31792 (== sim w31792), broken False (json :52-53), node census 0 new (:81), OPCENSUS {} new + lost_wires 1 (:169).
- dw_25232: err '' (:128), 706 -> 706 (:130), checkpoint 8 diff 0 (:133). w_k4f: `connect_term_uid #24342 <- #31858` err '' (:136), wire_uid 31837 (= the wire op 6 made from #5739 -> #31820, json :115), broken False (json :170-171), 0 new (:138), OPCENSUS {} + lost_wires 1 (:172).
- Face net source in the adopted graph (OK3 t31815 / OK4 outer): NOT read - the graph read was not run (card returned at the EL step).
## Adopt diag_c165_a3_4_adopt.log 4/0
- Byte copy claudeDev\D1_ring_p5_20261010_172913.vi md5 75773b0ded2a08586bb1a542ddda5af6 == claudeDev\D1_ring_p5s02e_20261010_172913.vi 75773b0d (both kept); adopt/1 record artefact = the D1_ring_p5_ copy, input 6dcd5c3d, required E1,FR,D,TD,PB,PS; adopted_scratch.jsonl 8d7a8651 -> c5d73bcc.
## Error List diag_c165_a3_4_el.log (elrun --role final vs 2a8e2984): 47 items == window 47, extra 0, MISSING 2, BY-DESIGN STOP, MISMATCH, rc 1 (:82-86), 603 s, handles 37245 -> 31284
- Read errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json 0c0664d8. Per class (diag_c165_a3_4_elcmp.log): loose ends 23, not connected 22 (21 + 1 OCR 'anvthing'), Build Array 1, two types 1; no source 0, undirected 0, While-input-to-SubVI 0.
- Short predicted entries: entry 0 'has no source [item 4]' w4337 used 0/1; entry 41 'While Loop to SubVI [item 49]' w9636 used 0/1. CLEARED as predicted: items 6/7/8/50 (nosource w10362/w25232, undirected #5204/#10404): vs p5s02d read 7450dd98 no source -3, undirected -2, whilesubvi -1.
- The predicted file itself names clears_by A70 w_k3f for item 4 (errorlist_predicted_D1_ring_p5s02e_end.json:180-186) and A80 w_k4f for item 49 (:1007-1013), yet kept them STANDING (diag_c165_a3_3_facts.md:14-15). Scratch term_identity re-ended old wires 4337, 9636, 31792 (diag_c165_a3_4_mkgraph.log).
- Hypothesis review archive/peer/2026-10-10-c165-a3-4-el-missing2.md (ANSWERED, $1.37): predictor bug (uid-only STANDING rule, stale A70/A80 numbering); real_end_rows keep w4337 / w9636 with the same sinks, #5204/#10404 outer flip to source; rule-1a open: tunnel indexing/type, #31815 value vs P5-1's #376.
## Prepared, NOT run (return at first unexpected result): diag_c165_a3_4_graph_plan.json 0aaef82b (mkgraph 4/0: 5 made, deleted wires [10362, 25232], 8 new wires), diag_c165_a3_4_graph.py (dry PASS, prerun 15/0), diag_c165_a3_4_reads.py, diag_c165_a3_4_elexp.py.
## Not done: memory_model.json unchanged ff0fabca (no load_by_vi); pred unchanged 825cbf65; no errorlist_expected file; no graph json.
## End: hashes after (diag_c165_a3_4_hash_after.log 11/0) all VIs and pins unchanged; tasklist LabVIEW none; _elc_ scratch removed. No original opened, no hook/recipe/plan/licence/EL/stage-tool edit, no motor/camera.
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c165_a3_4_el.log | new-problem 0.672 | hypothesis review owed | dispatched (card peers), recorded, returned | ANSWERED: predictor bug, file structurally consistent |
OPEN: accept 47 (items 4/49 cleared by w_k3f / w_k4f per the predicted file's own clears_by) and run the prepared graph read + load_by_vi + pred census, or fix the EL predictor first?
OPEN: rule-1a: LoopTunnel #5204 / #10404 indexing + outer type, and #31815 / OK4 source value vs P5-1's #376 'file progress' feed - measured where?
