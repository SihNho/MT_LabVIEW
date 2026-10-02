# Card 138-1 facts (offline, 2026-10-02; no LabVIEW, no stage_prerun / v7 edit). Inputs v7 01ab0893, graph p3b2b 50595c62
## 1. FS-exit row (stagesim `_fs_exit_wire`, `FS_EXIT`, `FS_EXIT_NAMES`; op_wire branch `lf and not ld`)
- Model = U6/U6' measured shape: ONE FlatSequenceOuterTunnel, sink face on the frame, source face on the FS's diagram, 2 rows,
  2 new wires, source net not re-created (diag_c137_5_routes.log:168; diag_c137_7_types.log:299-302; rows 6018->6024 = 3 FSOT x2, :101,208).
- broken_predicted False only for an Index Array source with 'array' wired (U6' :317,328); face_type recorded "= source type" (:290,305-306).
- 1b name: reproduces 'Index of closest\ncal image slice, bead 2' (:301-302) for the measured row (IndexArray fed by 'Num');
  any other feed -> faces carry 'UNPREDICTED-NAME' + st.unpredicted_names + effect.unmeasured (never ''). The graph holds the
  string only on DigitalNumericConstant #2640 t9229 - the name is not derivable from graph data in general.
- Refused: void source (IAN 'array' unwired, U6), wired source, wired sink, sink off the FS's own diagram (>1 border).
  Non-IndexArray source: allowed, broken_predicted 'UNMEASURED' flagged.
## 2. delete_wire row loss (#10465) - root cause
- `tools/stagesim.py:62` (HEAD) DROP_WHEN_UNWIRED = ("LoopTunnel", "Tunnel"), applied at HEAD :1274-1279: Case Tunnel #10465's
  inner faces t10467/t10468 were already unwired, so deleting w25415 dropped the node; evidence covers LoopTunnels only
  (opmodels/delete_wire.json:5; stage_d1_l7_r.json:221,228,588-589 #1929/#5020).
- Fix: drop ("LoopTunnel",) only; Tunnel/SelectorTunnel left unwired KEPT, effect `unmeasured_unwired_tunnels` (new key only then).
- Self-test `tools/bench/selftest_stagesim_fsexit_c138_1.py`: current 14/0 (`selftest_stagesim_fsexit_c138_1.log`);
  HEAD stagesim --only D: D1, D2 FAIL, D3 PASS (`selftest_stagesim_fsexit_c138_1_prefix.log`) = fails before, passes after.
## 3. stagexec FS-exit route
- fs_wire_ops: `elif ls and not ld` -> variant 'fs_exit' -> compile kind connect_term_uid (U6' ran g.connect_term_uid(W, snk, src),
  diag_c137_7_types.py:30,64; RLE :77 = the plan's own wire_remove_loose_ends row). FS_VARIANT_HOW += fs_exit (real op uses the
  sim census, broken-until-RLE tolerated as fs_border); _fs_connect_check fs_exit branch (source on FS frame, unwired, other diagram).
- NOT in ROUTE_CENSUS: selftest_case_frame_c124 U01 requires ROUTE_CENSUS == census_samples.json, which has no FS-exit sample.
- compile_plan(v7): OK, 160 ops, per meta step {1:33, 2:27, 3:37, 4:36, 5:27}; #171 p4_x_n2_out = connect_term_uid/fs_exit;
  kinds: connect 70, create 48, delete_wire 8, tunnel 6, RLE 6, branch 6, fs_border 3, fs_inner_branch 1, fs_exit 1 (`prep_c138_1_replay.log`).
## 4. c125_1_offline_measure rerun (PD252(a)) - `tools/bench/c125_1_offline_measure_c138_1.log`
- RESULT {"status":"PASS","gates":{"pass":6,"fail":0}}; stagexec selftest 136/0, case_frame_c124 29/0, fs_c126 13/0,
  c134_1_dry 11/0, census_hookin 12/0, COM trips 0, LabVIEW.exe 0 -> 0.
## 5. replay v7 (fixed sim) - `tools/bench/sim/c138_1_v7/ring_p4_v3/summary.json`
- END: 173 steps (base + 172), errors none, last step 172 p4_rle_x_n2_out; 158 keeps #10465 (unmeasured_unwired_tunnels [10465]),
  159 wires t9668 -> t10469 (new wire), 171 how fs_exit, name MEASURED. v7 md5 unchanged.
- final False: end cdiff 24 rows (step 1: 16, 157: 23, 158: 24, flat to the end) vs 11 declared open_rows; open_rows_match False,
  classed ok False (11 unclassed keys); failed None, undecided 0, candidates 18. Re-written plan sim/c138_1_v7/plan_ring_p4_v3.json 1224a446.
## 6. Regression (all existing stagesim/stagexec self-tests) - FIRST UNEXPECTED RESULT, step finished, not diagnosed
- `prep_c138_1_regress.log` (18 tests, 541/3 gates): PASS stagesim selftest 105, stagexec 136, k79 4, l2a1_80 13, unflip_81 8,
  pin 10, tunnel_naming 16, stagexec_gate 13, stagexec_c124_6 136, c134_1_fsmap 6, c134_2_gates 11, c134_4_owners 7,
  c135_2_device 6, fs_c126 13, fsexit_c138_1 14. FAIL case_frame_c124 U01 (my ROUTE_CENSUS entry) -> fixed, 29/0 in c125_1.
- STILL FAIL: selftest_c133_1_fsroutes R1 "base is not provisional - nothing to rebase" (stage_prerun rebase) then IndexError :62;
  selftest_c134_2_regress 16/1, nested selftest_c133_6_fr "KeyError: 'fs_frames'" (`prep_c138_1_regress2.log:3-8`).
- Cause NOT separated: stage_prerun.py has 224 uncommitted changed lines (card 138-2); the HEAD-module discriminator run failed on
  the HEAD copy's file-relative census path (`prep_c138_1_regress_head.log`). regress2 hit its 12-min bgrun limit after these.
OPEN: are c133_1 R1 / c133_6_fr failures from 138-2's stage_prerun edits or from this card's stagesim/stagexec edits?
