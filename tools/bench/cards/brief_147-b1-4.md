---
card: 147-b1-4
status: current
date: 2026-10-08
---
# Brief 147-b1-4 - T6 of 147-b1-2, third attempt: compare selftest_stagekit before/after with COM blocked

Retry of 147-b1-3 (`tools/bench/diag_c147_b1_3_facts.md`). It found: `selftest_td_key_c141_3.py` on the NEW stagekit (06b8d844) rc 0, 9/0. `selftest_stagekit.py` on the NEW stagekit: 47 pass / 2 fail, J1 (`selftest_stagekit.py:336`) + case_j IndexError :339, because `tools/stagekit.py:794` calls the real `g.create_local_read` (since cycle 102, :790-792) while the test stubs only `diag_s3b_l0_localname_v2` (`selftest_stagekit.py:330`); the stray call reached COM (`gscript.open_panel`, com_error 5507). Lines 779-800 are outside the 147-b1-2 diff (hunks @@1371/@@1379/@@1395). It was NOT measured on the pre-edit stagekit. A ready pre-edit runner is `tools/bench/diag_c147_b1_3_runold.py` (git show HEAD stagekit, md5 9a3fceaf checked, in memory).

## To measure (no edit of `selftest_stagekit.py`, `tools/stagekit.py` or any tool; your driver is a new file `tools/bench/diag_c147_b1_4_run.py`)
1. Driver rule: before either run, replace every gscript function that can reach COM (at least `g.create_local_read`, `g.open_panel`, `g.lv`) on the module the test imports with a stub that RAISES and counts its calls, so any leak is recorded in the log and never reaches LabVIEW. For case J only, `g.create_local_read` must behave as the test's own stub intends (read `selftest_stagekit.py:325-345` to see what J1 asserts and stub accordingly, or report that J cannot be made to run offline without editing the test). `tasklist | grep -i labview` before and after must show 0.
2. Run `selftest_stagekit.py` on the PRE-EDIT stagekit (HEAD, md5 9a3fceaf) and on the NEW (06b8d844) with the same driver: quote command, rc, pass/fail counts and the list of failing check ids for each; COM-leak counts for each.
3. Run `selftest_td_key_c141_3.py` on the PRE-EDIT stagekit: command, rc, counts (the NEW result 9/0 is already known).
4. Re-run `py tools/bench/selftest_c147_b1_2.py`: rc, count (expect 17/0).
5. Compare: identical per-check results before/after, or list the checks that differ with `file:line`.
6. md5 of stagekit.py (06b8d844), stagexec.py (1bab9cf9), gscript.py (1a80236e), elrule.py (a5ee7d5c), s06 plan/pred/in/licence/recipes and memory_model.json (88eeb037) after.

## Report (`tools/bench/diag_c147_b1_4_facts.md`, <= 25 lines)
Per-check comparison, commands + rc, COM-leak counts, md5 list, `OPEN:` line (include whether the stale case-J stub is a pre-existing tool defect, by the HEAD run). No tool, plan, licence, recipe or memory_model.json edit.
