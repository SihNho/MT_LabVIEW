---
card: 148-a1-1
date: 2026-10-08
status: FAIL - 9/9 gate-fp entries handled (8 fixes drained with self-tests, fp-55 closed as not a false positive); selftest_c147_b1_2 16/1 (T0b); runall TIMEOUT; selftest_stagekit plain run refused by the card's own labview flag
---
## gate-fp (tools/bench/gate_fp_queue.jsonl, through tools/gate_fp.py)
| fp | fix | self-test (after / pre-fix with the 4 files' HEAD blobs = card inputs) |
|---|---|---|
| 51 | stage_prerun.py:592,848 the dry's input-graph gate passes when the script's only MODIFY verb is discard_work (`dry_read_only`) | selftest_c148_prerun_fp P7/P8: 8/0 rc0 (diag_c148_a1_1_prerun_fp3.log) |
| 52 | stage_prerun.py:4474 record_started skips a run its own header's offline-args make labview none (`offline_run_of` :3415) | same P5; pre-fix raised AttributeError (diag_c148_a1_1_before_prerun.log) |
| 53 | guard_assign.py:326 memory-token window stops at the token's own clause | selftest_c148_guard_fp A1-A3: 6/0 rc0; pre-fix 4/2 (A1, W1 fail) (diag_c148_a1_1_before_guard.log) |
| 54 | guard_cycle.py:662 offline_only accepts `py -m py_compile <recipe>` (launchunit.module_arg_segment) | selftest_guard_cycle_offline O8: 9/0 rc0; pre-fix 8/1 (O8) |
| 55 | none - CLOSED as NOT a false positive (PD357(d), docs/d1/ring-p4c.md:54) | re-measured: guard_bash refused selftest_stagekit.py under this labview-none card |
| 56 | stage_prerun.py:3150 pin re-set to **5708c2d6...** (stage_prerun.sha256 hashes WITHOUT the scope header; raw-file sha256 0007d034 never matches; selftest_fn_f2's pin c744f767 is the same canonical form) | P1/P2 8/0; pre-fix P1 FAIL |
| 57 | guard_write.py:49,90 a card taken over by a later card with a result (`RESUME of [killed] card <id>` goal, or retry_of_card/resume_of/supersedes) is not open | W1-W3 6/0; pre-fix W1 FAIL |
| 58 | stage_prerun.py:3433 check_cap allows an offline-args run | P3/P4 8/0 |
| 59 | guard_cycle.py:383,546 re-run exemption also counts the recipe's own `LOG = "...log"` when that log's last BGRUN START ran this recipe | selftest_guard_cycle_rerun C5-C7 (exact fp-59 command; older log and other-recipe log still REFUSED): 7/0; pre-fix 6/1 (C5) |

## Runs
- selftest_stagekit.py plain run: REFUSED by guard_bash card flags ("flags.labview is 'none' - selftest_stagekit.py declares labview: read"); not routed around. Classifier part verified offline: launched_vi_modifying(...) == [] (P1).
- selftest_c147_b1_2.py P0 re-pinned (lines 23-24 only: licence 7f70bbf9, recipe d947df5d): **16 pass / 1 fail, rc 1** (diag_c148_a1_1_c147b12.log). P0 PASS; FAIL = T0b (selftest_c147_b1_2.py:123) "today's licence file (rename_by_uid only) -> licence_renames None" - licence 7f70bbf9 now has `renames` (plan_ring_p4_s06v18_licence.json:16), so T0b's premise is stale; fixing it is another line, not authorised.
- diag_c148_a1_1_runall.py after (every selftest_*.py naming an edited module, 82): **BGRUN TIMEOUT 40 min** after 75 (53 rc0, 10 nonzero, 12 SKIP-HEADER labview read); 7 x10 self-tests not run (selftest_x10_c130_1 .. x10_chat_m2).
  - rc0 incl.: c103d_hooks 17/0, launch_gate 29/0, retry_cap 8/0, guard_cycle_fixed 2/0, assign_flow, c_e3, headcmp_79-6.
  - nonzero, SAME on the pre-fix code (diag_c148_a1_1_before_*.log): c125_1 16/4, c133_1_fsroutes R1/R2, fn_f2 35/1 (P7b doc drift), rebase_uidreuse_c143_4 U1/U2, stage_prerun_c106e 14/1 (E1).
  - nonzero, pre-fix not measured: 4 TIMEOUT at 240 s (c134_1_a4, c134_2_regress - earlier runs 560/610 s rc 1 - c_e3_suite, f2_suite) and t3_regress rc1 (149.5 s, no count line).

## md5 after (edited)
stage_prerun.py dcd45aba (was 61d6f590); hooks/guard_cycle.py 2df2f11c (c080fb7a); hooks/guard_write.py f61bec73 (391a8324); hooks/guard_assign.py eb8ba4d6 (b9dc09bb); guard_bash.py, bgrun.py unedited; selftest_c147_b1_2.py 2166d93f (24c56042); selftest_guard_cycle_rerun.py 5dde9eea; selftest_guard_cycle_offline.py 9f170fee; new: selftest_c148_prerun_fp.py 23283816, selftest_c148_guard_fp.py 6ada8882, diag_c148_a1_1_runall.py, diag_c148_a1_1_before.py; gate_fp_queue.jsonl c4272b8b.
## invariants (unchanged)
stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, memory_model 88eeb037, s06 plan cfbd9823 / pred c4a6a35a / in db72d8af / licence 7f70bbf9, recipe d947df5d, scratch 31009bfc, selftest_stagekit 29df9b64. LabVIEW processes: 0 before and after.

OPEN: T0b in selftest_c147_b1_2 needs a second line edit (or the 16/1 accepted); selftest_stagekit's plain run needs a labview-read card; t3_regress + 4 timeouts + 7 unrun x10 tests have no pre-fix comparison.
