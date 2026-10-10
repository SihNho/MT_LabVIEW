---
type: facts
status: current
date: 2026-10-10
card: 164-3-5
---
# 164-3-5 facts: the ONE step-4 scratch PASSED 21/0 (peak 652.6 <= 675) and was ADOPTED (6dcd5c3d); EL 53 == pred 53, diff none; graph read FAILED E5 on uid re-use (#23501) -> RETURN; memory_model / pred census NOT written; LabVIEW gone.
## Pre-checks (offline)
- Hashes before (diag_c164_a3_5_hash_before.log) 11/0: 19 card inputs equal; VIs eb1d0f31 / 2482fe7b / 7f2582ae / 94ffff94 / f9ae7751 / 564d8cbe; stagekit dd57c1ca, stagesim 95a162ba, stagexec a4df7e15, stage_prerun 7605116f.
- check_launch: recipe form ALLOW (diag_c164_a3_5_checklaunch.log:5), brief form ALLOW (_checklaunch2.log:5); --scratch-required rc 3 CENSUS-UNPREDICTED rows [1..19] (_scrreq.log:3-4).
- diag_c164_p5s02d_scratch.log absent before launch; no LabVIEW process. Launched: `py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c164_p5s02d_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02d_scratch.py --unverified-card tools/bench/cards/task_164-3-5.json`.
## Scratch diag_c164_p5s02d_scratch.log: RESULT PASS 21/0 (:269), BGRUN END rc=0 after 480 s (:276)
- `SCRATCH-P5S02D peak 652.6 MB (X10 642.7, d 9.9); final ...D1_ring_p5s02d_20261010_152518.vi md5 6dcd5c3d...; bed md5 564d8cbe` (:271); `GATE MEM ... PASS` (:272), MEML PASS (:273). METER start 617.2 MB (:61).
- L1 19 actions -> 15 ops == pred kinds (:60). E1 diff 0 at checkpoints 0,1,2,6,7,11,12,14,15 (STEPX :63,75,84,137,153,184,193,208,216); E1 PASS (:217). PRIM c_eq7 Equal?/Comparison #12170 PASS (:150).
- Bound: c_lr7 -1: 12169 Local, c_eq7 -3: 12170, sr_k3 {-9: 31756 RSR, -10: 31764 LSR}, c_k3i -15: 31773, t_k3o -18: 31803, t_k3i -23: 31807 (SelectorTunnels).
- NG PASS 0 ops (:218); FR PASS 3 created on [686, 23405] (:219); D pairs 8 == sim 8, lost 4 == 4 (:220); TD PASS (:225); HB 45949 -> 46544 (:234); PS 324370 B (:241-243); H5/H2/H3/H6 PASS (:253-263).
- PB PASS by position (:232): 31/31 = 26 slots + 5 RECORDED; class per row: cal cluster path 1, error in 3, file size 1, selected path 1, total data array in 3 (:227-231).
- CEN2 UNPREDICTED (:221). MEASURED new uids (:223): Comparison 1, DigitalNumericConstant 1, InnerTerminal 6, LeftShiftRegister 1, Local 1, OuterTerminal 4, ParameterTerminal 1, RightShiftRegister 1, SelectorTunnel 2, Terminal 2, Wire 7; net (:222) adds LoopTunnel -1; lost 8 (:224).
- OPCENSUS op 3 {lost_wires 1} (:244), op 8 {owners Comparison 1, terms ParameterTerminal 3} (:247); ops 4/5/14/15 not measured (:245,246,248,249).
## Adopt diag_c164_a3_5_adopt.log 3/0 (copy of diag_c163_a2_2_adopt.py, names/input/note only)
- ADOPTED C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p5s02d_20261010_152518.vi md5 6dcd5c3d506f69947a5ce259ccbe2221 (adopt/1 15:34:04, :38); adopted_scratch.jsonl 332e9ca6 -> 8d7a8651.
## Error List diag_c164_a3_5_el.log (elrun --role final vs 2c1edf78): 53 items == window 53, extra 0 missing 0, RESULT PASS 11/0 (:88-89), 708 s, handles 37245 -> 31292
- Read errorlist_D1_ring_p5s02d_20261010_152518_20261010_153416.json 7450dd98. elexp (diag_c164_a3_5_elexp.log) 5/0: vs 2c1edf78 extra [] missing [], none dropped, none added.
- Per class: loose ends 23, not connected 22 (21 + 1 OCR 'anvthing'), no source 3, Loop Tunnel undirected 2, Build Array input 1, two types 1, While-input-to-SubVI 1; diff vs pred {} and vs p5s02c read {} (+0).
- UNPREDICTED A66 t_k3o / A69 t_k3i / A56 do_23501 raised NO item (53, not upper 56). Expected file errorlist_expected_D1_ring_p5s02d_20261010_152518.json c74200f2, total 53, 52 entries.
## Graph: plan diag_c164_a3_5_graph_plan.json 725c8b00 (mkgraph 4/0 on run 2); dry PASS, prerun 15/0; diag_c164_a3_5_graph.log RESULT FAIL 14/1 (:336), BGRUN END rc=1 178 s
- mkgraph run 1 (diag_c164_a3_5_mkgraph_run1.log:5) FAILED its own gate W (predicted term_identity.new == 7, got 9): helper prediction error; review archive/peer/2026-10-10-c164-a3-5-mkgraph-termidentity.md (ANSWERED): new = 7 new uids + 2 re-ended (23519, 31712); W tightened to that split.
- `MEM after load: 603.9 MB private` (graph.log:24); after full read 615.2 (:280). WROTE tools/bench/graph_ring_p5s02d_20261010_154830.json md5 2a5fa0c40866f88111d3ab14e5f9c32d: 6213 rows, 10840 objs, 25 loops, 23 FS (:307).
- G1/G2/G3/FS1/B/X PASS (:308-314). **E5 FAIL (:305): deleted_nodes_present [23501]**; made 7 classes right, deleted wires absent, 9 new wires present (:304).
- In base 3d5196ab, #23501 = LoopTunnel (owner WhileLoop); in the adopted graph #23501 = ParameterTerminal 'y' of the NEW Comparison #12170 on wire 31744 (diag_c164_a3_5_reads.log). #23042 absent.
- Review archive/peer/2026-10-10-c164-a3-5-graph-e5-uid23501.md (ANSWERED, refute failed): LoopTunnel set base - adopted = {23501}, none new; uid 23481 also re-used (#23042 'x' -> #12170 'x = y?'); w_eq7_y == plan_ring_p5s02d.json:224-226; the scratch's reuse detectors reported [] (:220, :225).
## PD399(a) reads (adopted graph, diag_c164_a3_5_reads.log)
- w23460: ABSENT (0 rows, no object); base had 3 rows (23042 'y', 23042 'x', tunnel 23501 inner 23505).
- w23519: present, source t8494 'x+1' (#8486), REAL sinks {t23450 (#23417), t23241 (#23172), t7606 'x' (#7201)} == stagesim prediction; base had 4 sinks (+ t23514 on tunnel #23501).
## Not done (card returns at the E5 FAIL)
- memory_model.json NOT changed (8fb432e4); pred NOT changed (87a65b89); no load_by_vi entry (candidate value 603.9, graph.log:24). No graph/E5 re-run.
## End: hashes after (diag_c164_a3_5_hash_after.log 11/0): all VIs incl. 564d8cbe and tool pins unchanged; tasklist LabVIEW none. No original opened, no hook/recipe/plan/licence/EL/stage-tool edit, no motor or camera.
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c164_a3_5_mkgraph.log | new-problem 0.808 | hypothesis review owed | dispatched (card peers), applied the split | ANSWERED; mkgraph 4/0 |
| diag_c164_a3_5_graph.log | new-problem 0.860 | hypothesis review owed | dispatched, recorded, returned | ANSWERED; claim held |
OPEN: E5's deleted-node check by uid alone fails on LabVIEW uid re-use; accept the file and re-run the graph check by (class, owner, position) before adding load_by_vi 603.9 and the pred census?
OPEN: the scratch's reuse detectors (reuse_noted, recycled_uids) reported [] although 23501 and 23481 were re-used in the run.
