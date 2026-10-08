# Brief chat-T6 - result gates D / TD / PB key terminals by POSITION, not by name (user 2026-10-08 "두 가지 모두 적용하자")

User, same day: "단자 네이밍은 몇 차례나 이야기했던 것 같은데, 왜 아직도 수정이 안되는거임?" S1 (card chat-S5, PD337) moved PLAN
ADDRESSING to (owner uid, terminal index, terminal class) but left the post-run RESULT GATES on names:
`tools/stagekit.py:1346-1356` term identity = (term uid, owner uid, term NAME); wires by (wire uid, source terminals'
...); PB ranks node|class|name|ordinal (`:1406` comment). LabVIEW renames terminals when it wires them and re-issues
deleted wire uids, so these gates call a correct build "lost": cycle 147 (`result_147-a1-8.json`: D 15 vs 16, TD/PB FAIL
on 5 renames on #9503 9505/9508 'Value'->'' etc. and re-used wire uid 23807). Cycle 147 patched it with a renames LICENCE
(`result_147-b1-2.json`, `result_147-c3-2.json`, stagekit `term_identity_356`, `licence_renames`) - a whitelist that the
next batch will need again. Remove the cause.

## Do
1. D / TD / PB compare terminals by POSITION KEY = (owner uid, terminal index in the owner's terminal list, terminal
   class); the name is a report column only. Reuse S1's position machinery (`tools/addrcheck.py` `check_plan(...,
   addr_pos)`, the rebase binding in stage_prerun/stagexec) - one shared helper, no per-recipe copy. Find where the
   terminal index comes from in the graph reads; if a read has no stable order, say so with file:line and STOP (return).
2. A wire is identified by its two ends' position keys, not by its uid (uid re-use is LabVIEW's, not ours). Report
   re-used uids as INFO.
3. Renames become INFO lines. The `renames` licence field stays readable (old licences parse) but is no longer
   required; an unlicensed rename does not fail.
4. Nothing true may slip through: a terminal that really disappears, a wired terminal that becomes unwired, a wire whose
   source changes, an index/class change at the same owner -> still FAIL.

## Prove it offline (labview none)
- Re-score the STORED real reads of P4 batches 3, 4, 5, 6 (the scratch logs / graph JSONs of cycles 144-149, e.g.
  `diag_c147_p4s06v18_scratch.log`, the 147-b1 rescore inputs) WITHOUT the renames licence: all PASS, and the batch-6 case
  that failed in 147 now passes.
- Mutation cases on the same data: drop a terminal, unwire one, change a wire's source, swap two indices -> each FAILS.
- Existing self-tests green or each difference explained: selftest_stagekit (51/0 today), selftest_td_key_c141_3 (9/0),
  selftest_c147_b1_2 (17/0), stagexec/stagesim regressions, and selftest_assign_flow.py (the chat just changed
  tools/hooks/guard_assign.py: `never_in_runner_globs` - report its result, do not edit the hook).

## Limits
- WORKTREE: you run in an isolated git worktree. Read data from the MAIN tree by absolute path
  (G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop\tools\bench\...), edit code ONLY in
  your worktree, commit there. The runner is using the main tree's stagekit right now - never write the main tree.
- labview none, hardware none, Edit tool only. Do not touch tools/hooks/**.
- Decision record: docs/d1/tooling.md is at its line cap - write the PD as a NEW short topic file
  `docs/d1/result-gates.md` (frontmatter like its siblings) + one line in docs/d1/INDEX.md.
- Return ONE result/1 JSON object (facts with file:line, the worktree path and branch, commit id, OPEN).
