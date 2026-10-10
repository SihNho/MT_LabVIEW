---
type: facts
status: current
date: 2026-10-10
card: 163-a2-2
---
# 163-a2-2 facts: prior-art `novel`; the ONE step-3 scratch PASSED 21/0 (peak 602.0 <= 675) and was ADOPTED (564d8cbe); EL 53 == pred 53, item diff none; graph + load_by_vi + pred census written; LabVIEW gone.
## Pre-checks (offline)
- Hashes before (diag_c163_a2_2_hash_before.log) 10/0: 21 card inputs equal; s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae, p5s02a 94ffff94, p5s02b f9ae7751; tool pins equal.
- Prior art: prep_c163_a2_2_priorart.log (plan prep_c163_a2_2_priorart_plan.md, --recipe scratch + main), rc 0, 69 s: `PRIOR-ART: novel`; archive/peer/2026-10-10-priorart-priorart-c163-a2-2-p5s02c.md:333;
  NOVEL RECORDs for both recipes (sha f65c91ba / e596ea23). Only new part per reviewer: Increment created INTO inherited frame 31506. Disposition written (:341-).
- check_launch on the exact launch string (recipe form, card 163-a2-2): ALLOW (diag_c163_a2_2_checklaunch.log); --scratch-required rc 3 CENSUS-UNPREDICTED rows [1..12] (diag_c163_a2_2_scrreq.log).
- diag_c163_p5s02c_scratch.log absent before launch (glob); no LabVIEW process.
## Scratch diag_c163_p5s02c_scratch.log: RESULT PASS 21/0 (:186), BGRUN END rc=0 after 376 s (:193)
- `SCRATCH-P5S02C peak 602.0 MB (X10 653.2, d -51.2); final ...D1_ring_p5s02c_20261010_125755.vi md5 564d8cbe...; bed md5 f9ae7751` (:188)
- `GATE MEM peak <= 680.0 and peak <= X10 + 10: PASS` (:189); MEML/IN/GONE PASS (:190-192). METER start 561.9 MB (:56) vs pred start 607.1 (-45.2).
- L1 12 actions -> 8 ops (:55). E1 diff 0 at checkpoints 0,1,2,4,5,7,8 (STEPX :58,70,79,101,109,125,135; ops 3/6 not checkpoints :86,:117); E1 PASS (:136).
- PRIM-GATE PASS c_inc7: Increment/Function #31697 on diagram 31506 (:89-98, the reviewer's named check); c_k07 #31674 on 686, node census diff 0 (:73-76, as P5-1 c_k0).
- Bound: sr_c7 {-1: 31659 RSR, -2: 31666 LSR} (:70), c_k07 -7: 31674, c_inc7 -10: 31697, t_ci7 -13: 31718, t_co7 -19: 31735 (SelectorTunnels, :101-125).
- NG PASS (:137); FR PASS 2 created on [686, 31506] (:138); D pairs 7 == sim 7, lost 0 == 0, wires_new 6 (:139); TD PASS (:144); HB 45687 -> 46029 (:153); PS saved 324194 B (:159-162); H5/H2/H3/H6 PASS (:170-180).
- PB PASS by position (:151): 26 slots + 5 RECORDED rows; class per row: cal cluster path 1, error in 3, file size 1, selected path 1, total data array in 3 (:146-150) - first live class 3, both PASS.
- CEN2 UNPREDICTED (:140). MEASURED census new uids (:142): DigitalNumericConstant 1, Function 1, InnerTerminal 6, LeftShiftRegister 1, OuterTerminal 4,
  OverridableParameterTerminal 1, ParameterTerminal 1, RightShiftRegister 1, SelectorTunnel 2, Terminal 1, Wire 6; net == new (:141); lost 0 (:143).
- OPCENSUS op 6 {SelectorTunnel 1, InnerTerminal 2, OuterTerminal 1, wires 2} (:164); ops 5/7/8 not measured (:163,:165-166).
## Adopt diag_c163_a2_2_adopt.log 3/0 (copy of diag_c162_a1_2_adopt.py, names/input/note only)
- ADOPTED C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p5s02c_20261010_125755.vi md5 564d8cbec316ea95f29f49d25ba5713e (adopt/1 13:04:40); adopted_scratch.jsonl 1a6e9f47 -> 332e9ca6.
## Error List diag_c163_a2_2_el.log (elrun --role final vs 373e0bf4): 53 items == window 53, extra 0 missing 0, verdict OK, rc 0, 706 s
- Read errorlist_D1_ring_p5s02c_20261010_125755_20261010_130451.json 8789ed58; bed md5 unchanged; handles 37243 -> 31286.
- Per class (diag_c163_a2_2_elexp.log): loose ends 23, not connected 22 (21 + 1 OCR variant), no source 3, Loop Tunnel undirected 2, input (Build Array) 1, two types 1, While-input-to-SubVI 1.
- vs 373e0bf4 (53): extra [], missing [], no entry dropped, none added; per-class diff vs pred {} and vs p5s02b read {} (total +0).
  UNPREDICTED A45 t_ci7 / A49 t_co7 raised NO item (53, not the upper bound 55).
- Expected file tools/bench/errorlist_expected_D1_ring_p5s02c_20261010_125755.json md5 26d45c71 total 53, 52 entries (elexp 5/0).
## Graph diag_c163_a2_2_graph.log 15/0, BGRUN END rc=0 174 s (plan diag_c163_a2_2_graph_plan.json 9a53af60 from _mkgraph.log 4/0; dry PASS, prerun 15/0)
- tools/bench/graph_ring_p5s02c_20261010_131658.json md5 3d5196ab098c5fb1401037e5c3c49e2d: 6203 rows, 10821 objs, 25 loops, 23 FS (:307)
- `MEM after load: 575.9 MB private` (:24); E5 PASS: 6 made objects with scratch classes, 6 new wires present (:305).
## memory_model.json (diag_c163_a2_2_memload.log 6/0): def9e640 -> 8fb432e4; ONLY added load_by_vi/564d8cbe {value 575.9, cite diag_c163_a2_2_graph.log:24};
  flattened diff added 3 leaves, removed [], changed []; fail_above_mb 680.0 old == new; memstop/formula/start_mb equal.
## Pred census (prep_c163_a2_2_census.log 4/0, stagekit.scratch_census on scratch log :142): plan_ring_p5s02c_pred.json fc908036 -> 721b9546;
  changed keys exactly [census, census_overall (-> MEASURED-SCRATCH), census_source]; plan md5 key unchanged; before-copy sim/ring_p5s02c_c163/pred_before_a2_2.json.
## End: hashes after (diag_c163_a2_2_hash_after.log 10/0): s09, P5-1a, P5-1, 94ffff94, f9ae7751 and tool pins unchanged; tasklist LabVIEW none. No original opened, no hook/recipe/plan/licence/EL edit.
OPEN: load MB 575.9 for 564d8cbe vs 601.2 for f9ae7751 (-25.3) and scratch start 561.9 vs model 607.1 (-45.2): the X10 model ran 51 MB above the measured peak this step.
OPEN: LabVIEW counts 'not connected' as 21 + 1 OCR variant ('anvthing'), unchanged from p5s02b; no new class.
