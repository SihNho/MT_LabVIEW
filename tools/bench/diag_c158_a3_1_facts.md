---
type: facts
status: current
date: 2026-10-10
card: 158-a3-1
---
# Card 158-a3-1 facts: PD386(a)-(e) gate change offline (no LabVIEW, no hook / plan / licence / stagexec / vigraph / stagesim edit)
## Changed files (md5 after)
- tools/stagekit.py 0d8f6d25 -> 07f9e35f: new shared functions stagekit.py:1836-2161 (run_bind, real_rows_from_record, frame_tag_map, frame_src_resolve,
  case_move_frames, pb_bound_rows, pb_check_bound, pb_386, wire_pairs_pos, term_identity_pairs, scratch_census, op_class_census[_install/_print],
  retry_card_arg); RingSession D :2350, TD RECORD facts, PB :2384 now call them. gate_cen2 :2362 unchanged.
- plan_ring_p5s02a_pred.json 31d8e9be -> ed84b5fd (only census / census_overall / census_source; prep_c158_a3_1_census.log C3).
- stage_d1_ring_p5s02a_scratch.py 71c3aed4 -> 64b4f18b: LOG / OUT_JSON / SUM_JSON = diag_c158_p5s02a_scratch.* (:30, :33), CARD label, OPCENSUS print (:42, :52),
  retry card print (:48), docstring launch line. SCRATCH name, acts and R unchanged.
- re-pinned md5 string only: selftest_c155_basecase_frame.py:206 -> fd4fe9c7, selftest_c156_passwire.py:161 -> 2b628fab.
- new: selftest_c158_gates386.py 46c76aee; prep_c158_a3_1_{regress,census,rescore,checklaunch,probe,proto}.py; mutation_table_p5_rescore.json 307f4aaf / .md 5085fc7f.
- unchanged (md5 checked): stagexec 7a712ccb, stagesim eb99c6ba, vigraph a7eb58c7, stage_prerun 9decb20f, addrcheck 207beb0d, gscript 1a80236e, plan 4284c22a,
  licence e8fd6a98, main recipe b52b9ff5, graph 6716c499, mutation_table_p5.json 2d9fd051 / .md 72e54d23, tools/hooks/** (no edit).
## 1-2 regression (prep_c158_a3_1_before.log / _after.log)
- Before == 158-a2-1 after: 3 op lists, 200 stored plans, 4 checkpoint sets EQUAL (before.log A1-A3). After == before_a3.json: same, 0 differ (after.log A2).
- Suite counts identical before/after: stagexec 141/0, stagesim 106/0, c155 21/0, c120 1/0, case_frame_c124 28/1 (known), stagexec_gate 13/0, tunnel_naming 21/0,
  fs_c126 13/0, t6_regress 9/2 (known), addrcheck_s5 22/0, t7_ring 35/0, c156 20/0, c157 13/0, c158_runcheck 10/0, c158_wire0face 24/0.
## 3 selftest_c158_gates386.log :22-42 = 16/0 (lines :1-21 = its first build run, C1 test expectation wrong, fixed)
- PB(386) recorded data: ok; real == sim-bound row for row (31 rows each); RECORDED = 376 'cal cluster path' / 'file size' (S1 source uids 3454 / 1807,
  tags @31546/f0, @31557/f0 = frame 31506 = bound CQ7.f0 = plan move frame of #376); blocked none. Sim '@-49/f1' resolves to -29 -> 31506 (P1).
- D/TD(386): new pairs 21 == 21, lost 12 == 12; stub recorded sim-only = wire 24091 (25223,1,InnerTerminal); TD unwired recorded = that end; old gates still fail (A3).
- BLOCK: re-sourced #376 (B1), non-plan frame real-only and both-sides (B2), source uid 1807 != S1 3454 under @31546 both sides (B3), new pair real-only (B4),
  wire 11666 dropped whole / sinks only (B5), census Wire +1 (B6).
- Created-object ends: index dropped only when (node, class, direction) is unique on that node (stagekit.py:2020-2039); needed for SR 31347's swapped faces
  (prep_c158_a3_1_proto.log: raw pairs differ by 2 per side, reduced pairs equal). Old D compared created-node wires by count only.
## 4 mutation re-score (prep_c158_a3_1_rescore.log :74-110, 4/0)
- No invariant row stopped blocking; no row's net moved. PB alone changed on M1.1 PASS -> BLOCK (stronger). M3t / M5n / M5a still BLOCK (no mover); M6 gap unchanged.
## 5 dry / prerun / launch (diag_c158_a3_1_*.log)
- dry MAIN and scratch: DRY PASS, unverified 0 (was PASS-UNVERIFIED on PB, diag_c158_a2_2_dry.log:78): the new PB passes on the dry's own bound end, 2 rows RECORDED.
- prerun MAIN 16/0, X10 planned MAIN 674.7 MB (<= 675); prerun scratch 16/0, X10 669.6 (recorded 664.6 from the c156 log); scrreq rc 3 CENSUS-UNPREDICTED rows (as a2-2).
- check_launch (prep_c158_a3_1_checklaunch.log): ALLOW for no card, `--retry-card` on the bgrun line, and `--unverified-card`; counted runs cycle 158 = 1 < RETRY_CAP 2,
  so the gate does not read a retry card for run 2; a card must carry `"retry_of": "stage_d1_ring_p5s02a_scratch.py"` (stage_prerun.py:3413) to count past the cap.
## CEN2 reading (stagekit.py:307-334, :2362)
- EMPTY declared set -> UNPREDICTED, no gate (:311-322); non-empty -> equality gate per class (:327-333). `census_overall` is a label: stagekit never reads it.
- RS.SRC = the pred census keys, so the snapshot now keeps all 13 classes and CEN2 compares all 13 (log :555 values, Wire 12, ParameterTerminal 13, ...).
## FINDING
- Simulator model gap: the sim end keeps wire 24091 as a source-only stub (25223,1) after its sink moved; LabVIEW deletes it (diag_c158_a2_3_facts.md:173-180). No stagesim edit.
- G1 in PB now uses the sim end's loops re-keyed by the bindings (stagekit.py:2002-2017), as diag_c158_a2_3_measure did; before it used unbound loops.
OPEN: the created-node index rule (unique-group ends without index) goes beyond the brief's literal (owner, index, class) key; judgement may prefer strict index (then D BLOCKs on SR 31347).
OPEN: the dry PB is now a real PASS (not UNVERIFIED), so the retry launch needs no DRY-UNVERIFIED-OK card; confirm that is acceptable.
