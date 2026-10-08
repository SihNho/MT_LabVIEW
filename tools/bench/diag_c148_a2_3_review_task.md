Hypothesis review, card 148-a2-3. Attack the claim below. Read-only; project dir is the working directory.

CLAIM UNDER ATTACK
"The 3 failing children of tools/bench/selftest_t3_regress.py - selftest_c133_1_fsroutes.py (R1/R2), selftest_rebase_uidreuse_c143_4.py
(U1/U2), selftest_stage_prerun_c106e.py (E1, the X17 row) - are PRE-EXISTING failures caused by stale premises inside those self-tests,
and are NOT caused by the cycle-148 edits (tools/stage_prerun.py, tools/hooks/guard_cycle.py, tools/hooks/guard_write.py,
tools/hooks/guard_assign.py, plus their self-tests)."

EVIDENCE OFFERED FOR IT
- tools/bench/diag_c148_a1_2_before_t3_regress.log lines 7, 11, 15, 19: t3_regress RESULT 7/3. R1/R2 and U1/U2 fail with
  "base is not provisional - nothing to rebase"; c106e E1 fails on prerun exit 1 with an X17 row ("every created primitive's donor
  label == its declared prim (PD323(b))").
- tools/bench/diag_c148_a1_1_facts.md:24 - the same 3 children, each run by tools/bench/diag_c148_a1_1_before.py (the 4 edited
  modules loaded from their git HEAD blobs, in-process, runpy) gave the SAME failures: logs tools/bench/diag_c148_a1_1_before_c133.log,
  diag_c148_a1_1_before_c143_4.log, diag_c148_a1_1_before_c106e.log.
- tools/bench/diag_c148_a1_2_facts.md:22 notes the t3_regress wrapper run is NOT pre-fix in effect: the children are subprocesses
  (selftest_t3_regress.py:44-46) and load current disk files.
- Edits of cycle 148 per gate-fp entry: tools/bench/diag_c148_a1_1_facts.md:9-17 (stage_prerun.py :592,:848,:3150,:3415,:3433,:4474;
  guard_cycle.py :383,:546,:662; guard_write.py :49,:90; guard_assign.py :326).

WHAT I WANT FROM YOU
1. The strongest reason the claim is wrong. In particular: does diag_c148_a1_1_before.py really make those children pre-fix? (Do the
   children or the code they call start their OWN subprocesses - e.g. `py tools/stage_prerun.py ...` - which would load the current,
   edited stage_prerun.py from disk, so that the "pre-fix" individual runs were in fact post-fix too?) Read the three self-tests and
   the code path that prints "base is not provisional - nothing to rebase" and the X17 check in stage_prerun.py.
2. An alternative explanation (e.g. a fixture on disk - a plan/graph JSON the tests read - changed after the tests were written; or
   one of the edited lines - :3150 sha256 pin, :3415 offline_run_of, :3433 check_cap - reaching these paths).
3. What observation would falsify the claim.
4. The CHEAPEST discriminating test that needs no LabVIEW and edits no tool/self-test (only new files under tools/bench/diag_c148_a2_3*
   may be written), e.g. a git-log/blame check of when "base is not provisional" and X17 were introduced vs when these self-tests were
   last passing, or a run of a child with every subprocess also pointed at HEAD blobs.
End with one line: VERDICT-LINE: claim REFUTED | claim STANDS | claim UNDETERMINED - <one sentence>.
