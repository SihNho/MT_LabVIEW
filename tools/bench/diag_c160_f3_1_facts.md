---
type: facts
status: current
date: 2026-10-10
card: 160-f3-1
---
# 160-f3-1: stale pins + selftest_c134_1_dry (PD391(g)); offline, no LabVIEW, no tool / hooks / plan / pred edit
## selftest_c134_1_dry
- Before (`selftest_c134_1_dry_c160_f3_1_before.log:14`) RESULT 9/2. T2a: full md5 0d1f0c15 != pin bb5ba064 (log:5). T2: DRY FAIL first_fail GATE PB, unverified 1 (log:6).
- Measured (`diag_c160_f3_1_pb.log`, 3/0): recipe 0d1f0c15 = bb5ba064 + the trailing scope header (header-stripped md5 bb5ba064, log:3); name-keyed cdiff 12 rows vs stored 16, missing = `2626|Terminal|array|0..3`, extra none (log:6-8); `stagekit.pb_check` on the stored rows / open pairs ok, slots 12/12, pairs 10/10 (log:11-12).
- T2 unverified 1 = CEN2 (census not measured in a dry); old T2 demanded `unverified 0`, PD387(e) (`stage_prerun.py:1074-1075`) counts every UNVERIFIED-DRY / UNPREDICTED gate line.
- Edit (self-test only): T2a = full md5 0d1f0c15 AND header-free md5 bb5ba064 (`selftest_c134_1_dry.py` header_free_md5); T2 runs the dry on a TEMP copy whose PB condition (1 line, count checked == 1) is `K.pb_check(...)["ok"]` = the PD370(b) converter `stagekit.pos_convert` / `pos_convert_open_rows` (`stagekit.py:1774-1802`, called by `pb_check` :1821-1847); expected unverified N = `SP.merge_unverified([], SP.dry_unverified_labels(out))`. Scope header `labview: read` -> `none` (it never opens LabVIEW; `selftest_dry_c130_5.py:85` same pattern) - the card's labview:none launch gate refused `read`.
- After (`selftest_c134_1_dry_c160_f3_1.log:15`) RESULT 11/0; T2 `DRY PASS-UNVERIFIED CEN2 ...` unverified 1 == PD387(e) count 1, coverage 72/81 (log:7).
## selftest_c156_b2_2_invcheck
- Before (`selftest_c156_b2_2_invcheck_c160.log:183`) 19/1 (ring-p5.md drift pin aa238a09). Suite :83 now reads `docs/d1/ring-p5.md` md5 from disk (99c812e6); pins :100 stagexec c4a6e0b6->ddf23a31, stagesim a3261b56->95a162ba; docstring :13-15.
- After (`selftest_c156_b2_2_invcheck_c160_f3_1.log:183`) RESULT 20/0. Its DRIFT lists tools/hooks/guard_cycle.py changed vs the 156 snapshot (log:164) - not this card.
## passwire / basecase_frame
- basecase_frame: :206 pins no moved tool -> no edit. Before (`selftest_c155_basecase_frame_c160.log:25`) 21/0; after (`selftest_c155_basecase_frame_c160_f3_1.log`) RESULT 21/0.
- passwire: :163 stagesim a3261b56->95a162ba (+docstring :32-33). Before (`selftest_c156_passwire_c160.log:34`) 20/0; after (`selftest_c156_passwire_c160_f3_1.log:34`) RESULT 19/1 = FAIL of this card:
  `D plan_ring_p5s02r_all.json compiles EQUAL to the before-list (40 ops)` (log:27). P pins PASS (log:32). Not diagnosed (card chat-P2). Context only: 160-a2-1 changed stagexec compile for t_go / t_ho (`diag_c160_a2_1_facts.md` R3), and p5s02r_all holds G/H groups t_go / t_ho (passwire log:4).
## md5
- self-tests before -> after: c134_1_dry 10178208 -> c0434146; invcheck c6460301 -> 687eb213; passwire 6ad1e1bd -> 321ef700; basecase_frame 7286edd8 unchanged.
- UNCHANGED: stagesim 95a162ba, stagexec ddf23a31, stagekit 1441bb4c, stage_prerun 7605116f, ring-p5.md 99c812e6, plan_ring_p5s02b_in.json 56bfddd3, recipe p3b2a 0d1f0c15. tools/hooks: no edit by this card.
- plan_ring_* with mtime after this card's bind (06:49): p5s02b.json, p5s02b_b1.json, p5s02b_in2.json - written by the parallel card 160-b3-1, not by this card (no plan write here).
OPEN: passwire D: re-baseline `sim/ring_p5s02pw/compile_before.json` for p5s02r_all after 160-a2-1's adopted compile change, or treat as a regression? (count differs from last pass -> not re-pinned)
OPEN: other files pinning the moved md5s, not edited: `diag_c160_g1_1.py:27-28`, `diag_c160_h1_1_check.py:24`, `diag_c160_b2_1_md5.py:14-15`, `prep_c160_b1_1_mk.py:40`.
