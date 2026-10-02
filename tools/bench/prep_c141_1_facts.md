---
type: facts
status: current
date: 2026-10-02
---
# Card 141-1 facts: prim gate (2 halves) + X10 provisional refusal + P4 plan v16 + session 1 FINAL (offline, no LabVIEW)
## Gates built
- Run-time: `tools/stagexec.py:435-461` (PRIM_GATE_EXEMPT, purge_entry, prim_check), `:2524` (_done keeps last_purge), `:2779-2786` (primitive route: gate "PRIM ..." + ExecStop on mismatch).
- Offline X17: `tools/stage_prerun.py:2528-2606` (PRIM_DONORS registry: DonorRAS1D #175, DonorErrSel #529, OpWaitDonor #163; $work labels from main_vi_node_labels.json; $work donor deleted earlier = refused), gate line `:2674`.
- X10: `tools/stage_prerun.py:2005-2012` + `:2325-2332` - a provisional base is REFUSED (UNMEASURED), no fallback to model start_mb.
- Self-tests: `selftest_prim_gate_c141_1.log` 13/0 (R1 140-3 case 'Insert Into Array' FAIL, R5 LVBackend.create ExecStop, O1 #29157 refused, O2 DonorRAS1D #175 PASS); `selftest_x10_c141_1.log` 4/0; `c125_1_offline_measure_c141_1.log` 6/0 (stagexec selftest 136/0 == baseline).
## v16 (`prep_c141_1_mkv16.log` 17/0)
- `plan_ring_p4_v16.json` 36981c83 (in 0dc06c03, meta 1a169e10): 235 actions = 50 repair (10 per node, #27928 #28916 #29048 #29265 #29316) + v15's 185; only v15 change p4_ras_bufdiff donor -> DonorRAS1D_v0 uid 175.
- EDIT ORDER is CREATE-FIRST (create RAS; cfw-branch array/index/new from the still-wired sources; delete_wire old output; delete_object old; RLE the 3 old input wires; wire output to the old sink). PD323(a)'s literal delete-first order on #29316 fails route check: UNROUTABLE "node #29411 not in Diagram[173] (#32464).Nodes[]" (unwired FS tunnel face, mkv16.log gate L).
- Replay END 236 steps; end cdiff == v15's 24; every repair step's cdiff == step 0's 16; route_check PASS; compile 217 ops == 167 + 50; route diff only on repair ids; fs_routes regenerated (5 keys).
- X17 over whole v16 refuses ONLY p4_eq_seq: $work donor #10171 is deleted by p4_do_10171 (pre-existing in v15, session 5).
## Session table (`prep_c141_1_sessions.json` d9eb0d6c; start 606.1 every session, <=675, no split `of` pair / repair block)
| s | ops | first .. last | N | R | peak |
|---|---|---|---|---|---|
| 1 | 1-24 | p4_rp27928_c .. p4_rp29048_new | 24 | 5 | 669.3 |
| 2 | 25-54 | p4_rp29048_dwo .. p4_c_stopall_f | 30 | 4 | 675.0 |
| 3 | 55-68 | p4_i_stopall_k .. p4_rle_i_rab1 | 14 | 11 | 670.7 |
| 4 | 69-82 | p4_x_bufdiff .. p4_k_max | 14 | 12 | 673.2 |
| 5 | 83-94 | p4_k_max_found .. p4_eq_seq | 12 | 13 | 672.9 |
| 6-11 | 95-217 | p4_gt_n1 .. p4_rle_x_n2_out | 13/25/20/26/26/13 | 12/6/8/6/6/7 | 671.8/673.2/671.3/674.6/674.6/659.1 |
## Session 1 (`prep_c141_1_s01.log` 13/0)
- `plan_ring_p4_s01.json` f4831031 FINAL (24 actions, 11 open pairs, all 16 end rows bed-declared, route PASS); pred fc87180a: X10 669.3 (R 5); EL predicted 51 (0 created nodes with an unwired input; 0 base nodes newly unwired).
- Recipes `stage_d1_ring_p4_s01.py` b90f4003 / `_scratch.py` 2022eca8: dry PASS both; prerun 16/0 both (X17 PASS); X10 launch 674.4 (2 census reads), scratch 669.3; scratch x10() reads the md5-pinned pred (669.3).
- `--scratch-required` rc 3 CENSUS-UNPREDICTED rows 1-24 (`prep_c141_1_scrreq.log`; fp-34: not a failure). Prior-art `archive/peer/2026-10-02-priorart-c141-1-p4s01.md` NOVEL, disposed.
