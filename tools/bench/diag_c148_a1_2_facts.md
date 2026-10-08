---
card: 148-a1-2
date: 2026-10-08
status: BLOCKED - stagekit plain 51/0, 7 x10 self-tests all rc0; the pre-fix t3_regress run left a FAIL RESULT line, guard_peer then refused every further run (hypothesis review owed, card peers [])
---
## Runs (all `py tools/bgrun.py --material --max-min N --log <log> -- py -u <script>`)
| script | log | rc | counts |
|---|---|---|---|
| selftest_stagekit.py (plain, header labview read, no COM) | diag_c148_a1_2_stagekit.log | END rc=0 1 s (NO RESULT LINE) | `=== GATES: 51 pass / 0 fail` |
| selftest_x10_c130_1.py | diag_c148_a1_2_x10_c130_1.log | rc 0, 10 s | RESULT 9/0 |
| selftest_x10_c132_1.py | diag_c148_a1_2_x10_c132_1.log | rc 0, 7 s | 4/0 |
| selftest_x10_c132_4.py | diag_c148_a1_2_x10_c132_4.log | rc 0, 7 s | 6/0 |
| selftest_x10_c136_2.py | diag_c148_a1_2_x10_c136_2.log | rc 0, 8 s | 6/0 |
| selftest_x10_c138_2.py | diag_c148_a1_2_x10_c138_2.log | rc 0, 7 s | 12/0 |
| selftest_x10_c141_1.py | diag_c148_a1_2_x10_c141_1.log | rc 0, 3 s | 4/0 |
| selftest_x10_chat_m2.py | diag_c148_a1_2_x10_chat_m2.log | rc 0, 3 s | 9/0 |
| diag_c148_a1_1_before.py selftest_t3_regress.py | diag_c148_a1_2_before_t3_regress.log | END rc=1 164 s (process said 0) | t3_regress RESULT 7/3; then `BEFORE ...: rc 1 (non-zero as predicted)` + RESULT 1/0 |
No x10 test was non-zero, so no x10 pre-fix run was needed.

## t3_regress
- Failing children (pre-fix wrapper run): selftest_c133_1_fsroutes R1/R2, selftest_rebase_uidreuse_c143_4 U1/U2 ("base is not provisional - nothing to rebase"), selftest_stage_prerun_c106e 14/1 (E1, X17). The other 7 passed incl. @stagexec 141/0, t3 22/0, s5 22/0; chat_p1 and stagexec_s4 SKIPPED (labview read).
- The wrapper does NOT make t3_regress pre-fix: the children run as subprocesses (selftest_t3_regress.py:44-46) and load the CURRENT files from disk; only the parent process holds the HEAD blobs. So this run equals a post-fix run in effect.
- The same 3 children were already run individually on the pre-fix blobs by 148-a1-1 with the SAME failures (diag_c148_a1_1_facts.md:24). The post-fix t3_regress of 148-a1-1 has no saved final lines (diag_c148_a1_1_runall_after.log:76: rc1 149.5 s, no count line); a fresh plain run was refused (below).
- bgrun sets rc=1 when ANY RESULT line in the log fails (tools/bgrun.py:296), so the child's FAIL line made the diag log a failing log.

## Blocked
- guard_peer: latest failing log diag_c148_a1_2_before_t3_regress.log; JEV-LADDER 15:55:41 new-problem p=0.782, BLOCK, NEXT-ACTION: hypothesis review owed. Card flags.peers = [] so no review dispatched; plain t3_regress and the four 240 s suites (c134_1_a4, c134_2_regress, c_e3_suite, f2_suite) NOT run.

## md5 (after)
invariants unchanged: stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, memory_model 88eeb037, s06 plan cfbd9823 / pred c4a6a35a / in db72d8af / licence 7f70bbf9, recipe d947df5d, scratch 31009bfc, selftest_stagekit 29df9b64.
148-a1-1 edited tools, same as its list: stage_prerun dcd45aba, guard_cycle 2df2f11c, guard_write f61bec73, guard_bash 76d09957 (unedited), selftest_guard_cycle_rerun 5dde9eea, _offline 9f170fee, selftest_c148_prerun_fp 23283816, selftest_c148_guard_fp 6ada8882.
DIFFERENT from 148-a1-1's list, changed before this card bound (not by it): guard_assign.py bbaa2325 (was eb8ba4d6, mtime 15:45:00), selftest_c147_b1_2.py 1dd09f3d (was 2166d93f, 15:45:30), gate_fp_queue.jsonl 512d8660 (was c4272b8b, 15:47:20).
This card edited nothing outside tools/bench/diag_c148_a1_2*. LabVIEW processes: 0 before and after.

OPEN: does a hypothesis review (or a release) discharge diag_c148_a1_2_before_t3_regress.log, whose 3 failures equal the pre-fix ones, before the plain t3_regress and the four 240 s suites run?
