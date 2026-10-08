---
card: 147-b1-3
status: current
date: 2026-10-08
---
# Brief 147-b1-3 - finish T6 of 147-b1-2: two stagekit self-tests, before/after, under a `labview: read` card

Retry of 147-b1-2 (retry_of_card). That card edited `tools/stagekit.py` (now 06b8d844) and passed T1-T5 (`tools/bench/selftest_c147_b1_2.log` RESULT 17/0) but was BLOCKED on T6: `guard_bash` refuses `tools/bench/selftest_stagekit.py` and `tools/bench/selftest_td_key_c141_3.py` under a `labview: none` card because their scope headers say `labview: read` (gate false positive fp-55; both are pure, `selftest_stagekit.py:1-2`, `selftest_td_key_c141_3.py:1`). This card carries `flags.labview: read` so the headers match. NO LabVIEW process is started; verify with `tasklist` before and after.

## To measure
1. Run both self-tests against the NEW `tools/stagekit.py` (06b8d844): quote command, rc, PASS/FAIL counts.
2. Run both against the PRE-EDIT stagekit (md5 9a3fceaf = `git show HEAD:tools/stagekit.py`; confirm the md5 of what you extract). Do it without touching the working-tree `tools/stagekit.py` (copy the needed modules into a scratch dir under `tools/bench/diag_c147_b1_3_old/`, import from there, delete the scratch dir afterwards): quote command, rc, counts.
3. State whether counts are identical before/after. If a self-test fails after but not before, report the first failing line with `file:line` and do not edit stagekit (RETURN).
4. Re-run `py tools/bench/selftest_c147_b1_2.py` once: rc and count (expect 17/0).
5. md5 of stagekit.py, stagexec.py (1bab9cf9), gscript.py (1a80236e), elrule.py (a5ee7d5c), the s06 plan/pred/in/licence/recipes and memory_model.json (88eeb037) after.

## Report (`tools/bench/diag_c147_b1_3_facts.md`, <= 25 lines)
Counts before/after per self-test with commands and rc; the md5 list; `OPEN:` line. Do not edit any tool, plan, licence, recipe or memory_model.json.
