---
type: facts
status: current
date: 2026-10-10
card: 160-a2-1
---
# 160-a2-1: delete branch = "Wire with no source row"; BASE register inner face compiles like srR/srL (PD391(b)(c)); offline, no LabVIEW
## Step 0 (before any edit)
- `diag_c160_a2_1_baseline.py` -> `.log` RESULT 9/0, `diag_c160_a2_1_baseline.json` 25b320c456621ae4b047f28a11906b62 (stagesim a3261b56, stagexec c4a6e0b6).
  Op-list md5 p5s01a 5f95830f (14 ops), p5s01b b8b59791 (8 ops), p5s02b_in fc5411e0 (8 ops). Pre-edit copies kept: `selftest_c160_delwire_stagesim_a3261b56.txt`, `_stagexec_c4a6e0b6.txt`.
- Measured before: graph objs hold EVERY wire; the old delete path unwired t24139 but LEFT Wire 24264 in objs, so `termless_wire` became True after (baseline.log, delete w24264 line).
## Changes
- stagesim a3261b56 -> 95a162baec5324ff037a8d23bd7ef46d: new `sourceless_wire` `stagesim.py:632-637`; `op_delete_wire` `:1445` (flag before unwiring) and `:1461-1463`
  (sink rows only: rows wire 0 as before, Wire object removed, effect `sourceless_wire_object`). Termless branch `:1440-1442` and the source-carrying path unchanged.
- stagexec c4a6e0b6 -> ddf23a31b10767015da246be8ceaa2e2: `plan_base_owners` `stagexec.py:626-637` now loops `plan_base_docs` `:640-648` (extracted, same refs/md5 rule);
  `plan_base_state` `:651-659`; `base_register_end` `:662-679`; compile `base_st` `:856-859`, outside end `:906-912` (plain dict end -> base_register_end, oside 'inner');
  delete executor `:2896-2900` (a sourceless wire is never 'already gone'; terminal path = one live wire with exactly its sinks -> `be.delete_wire` uid call);
  stale docstring `:30-33` corrected (base cases, base registers, uid / sourceless delete).
- stagesim has NO copy of the compile decision (Grep srR|srL|register_end|compile_plan in stagesim.py: only docstring mentions at :300, :2557, :2764).
- base_register_end returns '' for a WIRED SOURCE face (needed for R4: t_gi / t_hi LSR inner sources on stubs w24285 / w24312 stay `tunnel` / cfw).
## Self-tests (new bytes)
- `selftest_c160_regface.log:36` RESULT 12/0. R1 temp plan `diag_c160_a2_1_plan_tmp.json` 73971108 (20 actions; dw_go w24264 / dw_ho w24300 read from the
  w_gr / w_hr sink rows): groups t_go / t_ho compile `connect_term_uid` `register_end_case_border` (log:7-8), route check PASS, final True, 0 UNROUTABLE;
  old routes 4/7 = k5 / k9 route connect_term_uid; t_gi / t_hi cfw; dw_* delete_wire (log:9-20). R2 p5s01a 5f95830f == baseline, p5s01b b8b59791 == baseline
  (log:22-25). R3 only t_go / t_ho changed in p5s02b_in; base_register_end '' for t_el (BuildArray) and t_in3 (LoopTunnel) (log:26-29). R4 t_gi / t_hi
  == baseline `tunnel`; LSR 24190 wired '' / unwired 'srL'; RSR 24139 'srR' (log:30-32).
- `selftest_c160_delwire_c160a2.log:39` RESULT 20/0 (old 12 green + TA1-TA5, TB x2, TC). TA2 measured: end pairs lose exactly (None, 24139, 23405) and
  (None, 24235, 23405) - `stagekit.wire_end_pairs` keys a sink-only wire as (None, sink, frame) (`stagekit.py:2102-2103`), so the brief's "no pair changes" was
  not literally true; nothing added, stubs equal (log:24-25). First run 19/1 on that expectation: `selftest_c160_delwire_c160a2_try1.log`.
  TB w24285 (source-only) and w32594 (source+sink) = old path, == a3261b56 / c4a6e0b6 (log:30-33). TA5 second delete of w24264 refused.
- Re-runs on the new bytes, counts == last pass: cen2_ends `selftest_c159_cen2_ends_c160a2.log:16` 8/0; runcheck `selftest_c158_runcheck_c160a2.log:23` 10/0;
  wire0face `selftest_c158_wire0face_c160a2.log:40` 24/0; stagemap `selftest_c160_stagemap_c160a2.log:9` 5/0. Internal: `stagesim.py selftest` 106/0,
  `stagexec.py selftest` 141/0 (`diag_c160_a2_1_simselftest.log:111`, `diag_c160_a2_1_xselftest.log:145`).
- Re-pins (stagesim a3261b56 -> 95a162ba only): `selftest_c158_runcheck.py:152` (+docstring :24), `selftest_c158_wire0face.py:260` (+docstring :29).
  cen2_ends / stagemap pin neither tool. delwire pins the pre-edit copies (+ a3261b56 / c4a6e0b6 txt, :51-52).
## md5 unchanged
- stagekit 1441bb4c, stage_prerun 7605116f, addrcheck 207beb0d, vigraph a7eb58c7, plan_ring_p5s01a ed62e8d6, plan_ring_p5s01b 75a77a00, plan_in 56bfddd3,
  graph 7ac24924. VIs 94ffff94 / s09 eb1d0f31 / P5-1a 2482fe7b / P5-1 7f2582ae unchanged (V0 == V1 in delwire and regface). tools/hooks: only the hook-written material_marker.log.
OPEN: other files pinning the moved md5s (not edited): `selftest_c156_b2_2_invcheck.py:100` (stagexec c4a6e0b6, stagesim a3261b56), `selftest_c156_passwire.py:163`
  (stagesim a3261b56); cycle-160 scripts `diag_c160_g1_1.py:27-28`, `diag_c160_h1_1_check.py:24`, `diag_c160_b2_1_md5.py:14-15`, `prep_c160_b1_1_mk.py:40`.
OPEN: base_register_end excludes a wired SOURCE face (R4) and a sink-only delete keeps the measured LoopTunnel auto-drop (shared path; RSR owners drop nothing) - accept both?
OPEN: the old delete path (a wire WITH a source row) still leaves its Wire object in objs, so `termless_wire` turns True afterwards (baseline.log w24285 / w32594).
