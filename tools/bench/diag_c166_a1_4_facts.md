---
type: facts
status: current
date: 2026-10-12
card: 166-a1-4
---
# 166-a1-4 facts (offline, no LabVIEW): PB class 2/3 tightened per PD397(e), stricter only; fp-86 drained
## Change (tools/stagekit.py dd57c1ca -> 93299121; pre copy `diag_c166_a1_4_stagekit_pre.txt` dd57c1ca)
- (1) provenance: NEW `pb_record_lines` (:2104, parses `RECORD PB <sink>: ... S1 source uids [..]` lines) + `pb_provenance` (:2121): a class-3 row needs a RECORD PB line for the sink in the scratch log of the adopted step that WIRED it (ctx `chain_logs`, filled at :2079), every such line with the same S1 uid set. Called at :2202, gate `(v) provenance` :2210.
- (2) coverage: NEW `pb_frame_coverage` (:2134), called for classes 2 and 3 at :2201. Allowed set = the case's frames on a PD374(d) pass-through sink, else the sink node's own frame (must be one). Each `after` entry passes ONE frame (its tag frames outside the node's own frame, else its own frame); ok iff every (allowed frame, S1 source uid) is carried exactly once and no tag sits off the allowed set.
- The old multiplicity count is KEPT as a guard (:2209). Reason: coverage alone accepts a row when the node's own frames hold every case frame and the old count blocks it. With the guard the rule can only get stricter.
- (3) `chain_tunnel_case` is newest-wins via setdefault (:2083), like `chain_connects`.
- Docstrings: pb_inherit_ctx, pb_inherited_row, and the three new functions name `selftest_c166_pbtight.py`. `docs/fn_descriptions.json` is unchanged: no docstring-less old function was touched.
- The RECORD PB text is unchanged. A provenance suffix tried in run 1 was dropped so the dry output stays equal (`diag_c166_a1_4_dry.py:12-13`).
## Self-test `selftest_c166_pbtight.py` -> `selftest_c166_pbtight.log:103` RESULT PASS 26/0 (run 3; run 1 :28 FAIL = own N2 design, rebuilt as N2/N2b)
- Stored PB inputs per adopted line n (`adopted_scratch.jsonl`): the plan from plan_md5s, its finalized base graph + last step file, scratch json `real_end_rows` + `stagexec`, `<plan>_pred.json`, `<plan>_licence.json`. Lines 13/14/15 = diag_c163_p5s02c / diag_c164_p5s02d / diag_c165_p5s02e_scratch.{json,log}.
- P (:87,:89,:91): p5s02c/d/e NEW ok, blocked [], rows + classes == the stored RECORD PB lines (3x class 1, #376 error in / total data array in class 3). Provenance = diag_c161_p5s02b_scratch.log:[158] / [161].
- S stricter-only (:78-:90), lines 5-15: old ok == new ok == True; recorded 0/0/0/0/0/0/2/5/5/5/5 unchanged; blocked 0 everywhere. RETURN rows: none (:92).
- S lines 1-4 (P4 s02-s05): the stored PB inputs cannot be loaded (plan files absent, :74-77), so they are listed, not scored.
- N1 no chain_logs -> None, OLD -> 3 (:94); N1b provenance line with uid 4966/3955 -> None (:95); N1c log without the line -> None (:96).
- N2 missing frame on the p5s02b class-2 rows (line 12): 31517 entries dropped -> None, OLD -> 2 (:97). N2b on the class-3 rows: coverage not ok, BUT the whole row is then RECORDED as class 1 by OLD and NEW alike (:98) - see open.
- N3 doubled 31517 entry -> None (:99); N3b a 31506 entry replaced by a 31517 entry (count unchanged) -> None, OLD -> 3 (:100).
- N4 temp chain (p5s02b record newest + byte copy older): NEW -> real p5s02b, row class 3; OLD -> older copy, same row None (:101). F stored files unchanged (:102).
## Regressions (stagekit 93299121)
- selftest_c163_pbchain 10/0 (`diag_c166_a1_4_reg_c163.log`); selftest_c161_pbinherit 10/0 (`_reg_c161.log`); selftest_c158_gates386 16/0 (`_reg_c158.log`); selftest_t7_ring 35/0 (`_reg_t7.log`).
## Stored plans: compile + dry
- Recipe dry = prep_c165_a3_3_dry.log's command `stage_prerun.py --dry tools/recipes/stage_d1_ring_<s>.py`, run with --no-record under the pre and the new stagekit (`diag_c166_a1_4_dry.py`). Result: `diag_c166_a1_4_dry.log:23` RESULT PASS 8/0; per step :16-22 for p5s01a, p5s01b, p5s02a-e.
- Old == new line for line once the run timestamp in the output VI name is cut. Class-3 RECORD PB lines are byte-equal (p5s02c :51,:54; d :68,:71; e :57,:60 of the saved `_dry_<s>_new.txt`).
- Run 1 (:3-12) failed 5/8, all on the provenance suffix plus that timestamp. p5s02d dry rc 1 under BOTH versions: CEN2 vs plan_ring_p5s02d_pred.json census (:21), there before the change.
- stagexec.compile_plan / dry_run do not read stagekit (stagexec.py imports :53-56); stagexec 1d5309f4, stagesim 95a162ba unchanged.
## Pins that drift because stagekit changed (not re-pinned, PD396(a)(4))
- Self-test pin gates: `selftest_c165_innerface.py:250`, `selftest_c165_prime.py:117-118`. History (no action): diag_c163_a2_1/_a2_2, c164_a3_5, c165_a3_4 _hash.py; prep_c164_a1_1/_a2_1/_a3_1_post/_a2_3_md5/_a3_4_md5/_a3_6_md5/_pred, prep_c165_a1_1_pre/_hash, prep_c165_a3_3_hash/_pred.
## fp-86
- False positive: step-3 PB blocked #376 error in / total data array in, wired by ADOPTED step 2 (w_g376 / w_h376, class 2 at diag_c161_p5s02b_scratch.log:158,161); no class covered a carried row. Class 3 (163-a1-4) removed it; with the three tightenings the rows still RECORD (P :87-91).
- Drained: `gate_fp.py drain --id fp-86 --fixed tools/stagekit.py:2162 --selftest selftest_c166_pbtight.py` -> DRAINED.
## Checks
- `diag_c166_a1_4_hash_before.log` / `_after.log` PASS 8/0. Card inputs equal (after: stagekit excluded); the 7 VIs 75773b0d 7f2582ae eb1d0f31 94ffff94 f9ae7751 564d8cbe 6dcd5c3d are unchanged; tasklist shows no LabVIEW.
- `tools/lint.py --files shared` total 0 (`diag_c166_a1_4_lint.log`). No hooks / STATUS / INDEX / plan edit.
