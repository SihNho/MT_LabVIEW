---
card: 148-a1-2
status: current
date: 2026-10-08
---
# Brief 148-a1-2 - finish the open runs of card 148-a1-1 (retry, ALONE, labview read)

Retry of `148-a1-1` (`result_148-a1-1.json`, facts `tools/bench/diag_c148_a1_1_facts.md`). All nine fp entries are already handled there; do NOT redo or re-edit them. This card is `labview: read` only because `selftest_stagekit.py` declares `labview: read` in its header (card 148-a1-1 was `none`, so guard_bash correctly refused the plain run). No LabVIEW process may start; tasklist 0 before and after. No hook, checker, tool, plan, licence, recipe or `selftest_c147_b1_2.py` edit (T0b at `selftest_c147_b1_2.py:123` is left as it is; it goes to the judgement session).

## To produce (runs only; measurements)
1. ONE plain run of `tools/bench/selftest_stagekit.py` under `bgrun` (its header, no driver, no COM routing): rc, pass/fail count line, and the number of COM calls if it prints one.
2. The seven self-tests the previous run did not reach (`selftest_x10_c130_1` .. `selftest_x10_chat_m2`; list them with a glob on `tools/bench/selftest_x10_*.py`) under bgrun, one log each, timeout generous enough (<= 15 min each, <= 40 min total, rc written on timeout). Quote rc + counts. For any non-zero result run the same test on the pre-fix blobs the way `tools/bench/diag_c148_a1_1_before.py` did, and say whether the result is identical.
3. `selftest_t5_termclass`-style extras are NOT wanted. `t3_regress` (rc1, 149.5 s previously, no count line): run it once more on the pre-fix blobs via `diag_c148_a1_1_before.py` and compare the final lines. The four 240 s timeouts (`c134_1_a4`, `c134_2_regress`, `c_e3_suite`, `f2_suite`) are only run if the 40-minute total allows; otherwise list them as not run.
4. md5 after of the invariant files (stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, memory_model 88eeb037, s06 plan/pred/in/licence/recipes) and of every edited tool (they should be unchanged from 148-a1-1's list).

## Report (`tools/bench/diag_c148_a1_2_facts.md`, <= 30 lines)
Commands + rc + counts per run, pre-fix comparisons, md5 list, `OPEN:` line. Facts only.
