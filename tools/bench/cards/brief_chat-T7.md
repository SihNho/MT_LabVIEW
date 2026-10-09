# Brief chat-T7 - repeated recipe blocks become shared functions (user 2026-10-09)

User: "보통 같은 함수가 계속 반복되면 복사 붙여넣기 대신 공통 함수로 만들고 호출하지 않아?" → "지금것도 당연히 공용함수로
빼야하고 추가로 다른 작업을 할 때도 스크립트 제대로 작성하도록". Read `docs/script-writing.md` first; it binds this card.

Basis: the ring recipes `tools/recipes/stage_d1_ring_*.py` were made by copying the previous one. The open-rows check
(PB) is inline in 21 of them (e.g. `stage_d1_ring_p4_s06v18.py:140-149`: build4 + computation_diff_frame + a
`node|class|NAME|ordinal` sink key, `split("|")[2]`), so card chat-T6's position keys (PD366, `tools/stagekit.py`
term_identity_pos) never reached it; cycle 153 failed on the stored s06 read (14 vs 18 rows, fp-70,
`tools/bench/cards/handback_153_3.json`, `diag_c153_a2_4_realpb.log`). Recipes grew from ~100 to ~200 lines (p4 s02-s05
vs s06-s09, p5s01a).

## Do (main tree; the runner is stopped while this card runs)
1. CENSUS: diff the newest recipe pairs (p4_s06..s09, p5s01a main + `_scratch`) against each other and list every block
   repeated in >= 2 of them that is logic, not inputs (PB block, sink-gate setup, licence/rename loading, X10/memory
   lines, census snapshots, adopt/EL tail, ...). One table: block, files:lines, what it computes.
2. EXTRACT each logic block into `tools/stagekit.py` (or the module that owns it: vigraph, stagexec, ...) as a named
   function; PB must compare by POSITION keys like PD366 (owner, index, class; sink names only reported). Keep
   behaviour otherwise identical.
3. NEW recipes call the functions: re-write the recipe pair(s) that have NOT run yet (check stage_runs.jsonl / adopt
   records; p5s01a and later if not launched) as inputs + calls. Recipes that already ran stay as they are (record).
   Write one short TEMPLATE recipe pair `tools/recipes/stage_template_ring.py` + `_scratch.py` showing the inputs +
   calls shape, for the next batches.
4. PROVE offline (labview none): every extracted function has a self-test replaying recorded data; the PB function on
   the stored end reads of P4 batches 3-9 and the fp-70 s06 case gives the PRED's rows (18 for s06) with no licence;
   mutation cases still FAIL; the re-written unrun recipes pass `--dry` + `stage_prerun --prerun` with the same verdict
   lines as before the rewrite; existing self-tests green or each difference explained (selftest_t6_poskey,
   selftest_t6_regress minus the frozen-pin cases, stagexec, stagesim, assign_flow).
5. Drain fp-70 with `tools/gate_fp.py drain --fixed <path:line> --selftest <name>`. Record the decision as the next PD
   in `docs/d1/result-gates.md` (+ INDEX line). Commit by explicit path.

6. FUNCTION LIST (user 2026-10-09 "전부 적용", after: the generated block in `docs/toolkit-capabilities.md` covers only
   LabVIEW-touching gscript functions + stage verbs + fn_records.RECIPE_FUNCS; the checking/comparison functions and
   the other shared modules are missing; 9 of stagekit's 36 top-level defs have no docstring; the hand-written stagekit
   section at :753 is stale):
   (a) extend `tools/gen_capabilities.py` so the generated block lists EVERY public function (no leading `_`) of every
       SHARED file, chosen by the IMPORT GRAPH, not by a fixed list (user: "8개만 보기에는 너무 적지 않은가"): a `.py`
       under tools/ (tools/, tools/bench/, tools/recipes/, tools/hooks/) that at least one OTHER file imports. Measured by
       the chat today: 46 of the 73 tools/*.py (protocol 815, gscript 660, stagekit 260, stagexec 251, stage_prerun 174,
       stagesim 168, vigraph 162, jev_candidates 105, ...) and ~35 files under tools/bench/ (diag_s2_scaffold 75,
       bench_prep 41, drive_original_copy 21, jev_gate 17, drive_m8 14, imaqdx_limits 13, ...). Per function: module,
       name(args), first docstring line, self-test name if the docstring names one. One section per module, a module
       table of contents at the top; tools/bench files marked "shared file in the bench folder (move to tools/ later)";
       hooks marked "reference". Keep the existing fncontract rows. The import scan must be fast (ast/regex, one pass).
   (b) write a docstring (what it does, what it returns, its self-test) for every public function of the tools/*.py
       shared modules that has none - text only, no behaviour change (bench-folder shared files: list the undocumented
       count, do not write them all);
   (c) REGENERATE ON CHANGE (user: "함수가 바뀌면 목록 갱신 되어야하는거 아님?"): `tools/hooks/guard_write.py`
       (PostToolUse Write|Edit) starts `py tools/gen_capabilities.py` DETACHED (never blocks the turn, ~10 s) when the
       written file is in the shared set (read the set from a small cache file the generator writes); one run at a time
       (lock file; a write during a run sets a re-run flag). This hook edit is authorised for THIS chat card (user
       2026-10-09 "갱신은 훅으로"), not for runner cards. PLUS the cycle end: `tools/cycle_runner.py`'s cycle-end hooks
       run it before the git commit and log one `CAPABILITIES | ... | regenerated N rows | drift ...` line (a failure
       logs and never stops the runner). Self-test both (hook: write to a shared file -> regenerated; to a non-shared
       file -> not started; two writes -> one run + one re-run);
   (d) mark the hand-written stagekit section (`docs/toolkit-capabilities.md:753`) as history with a pointer to the
       generated block, and keep doc_lint's drift check.

## Limits
labview none, hardware none, Edit/Write tools only, no `tools/hooks/**` edits. Return one result/1 JSON: the census
table summary, functions made (file:line), recipes re-written, self-test counts, commit id, OPEN.
