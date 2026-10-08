---
card: 148-a3-1
date: 2026-10-08
status: FAIL - step 3 (unmask) ran first and its c106e case came out DIFFERENT; the review (ANSWERED) says my script ran the wrong configuration; returned (card chat-P2). Steps 1-2 not run
---
## Step 0
- LabVIEW processes: 0 before (tasklist 16:1x, "no tasks"), 0 after (tasklist after the review). git worktree list before: main 07202624, Temp/e3head_r96iqm4t + Temp/f2head_1n3cihvt (detached 07202624), V6_bench/A, A13, A13K, A_run1_20261006_2113, B.
- Invariants unchanged: stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c; stage_prerun dcd45aba (HEAD blob 61d6f590).

## Step 1 - stale worktrees: NOT done
- `git worktree remove --force` from Bash needed approval (refused in this non-interactive session). The removal is coded in diag_c148_a3_1_suites.py (STEP 1, rc checked), which was never launched. Worktrees unchanged.

## Step 2 - suites: NOT run
- Wrapper written: tools/bench/diag_c148_a3_1_suites.py (014319cd). It checks every git/tasklist rc and prints stderr; pre-fix tree = `git worktree add --detach %TEMP%\c148a31_* HEAD`; md5s of 12 edited files (tree vs HEAD blob vs CRLF blob vs disk); NOW and PRE lanes run at the same time, 4 suites each, 1500 s cap; e3head_/f2head_/c148a31_ worktrees removed only at the end. Not launched: steps 2/3 order was swapped so the short unmask ran first.

## Step 3 - unmask (diag_c148_a2_3_unmask.py, run 1, log diag_c148_a2_3_unmask.log ff34a47e, BGRUN END rc=1 292 s, RESULT 4/1)
| case | HEAD | DISK | verdict |
|---|---|---|---|
| p3b2_A (current plan + provisional base from plan_ring_p3b2_in.json, simulate) | ok, 116 uids bound, re-sim final=True | same | EQUAL, 89/89 lines |
| p3b2_B (plan_ring_p3b2_in.json 4df60e63) | ok, final=True | same | EQUAL 89/89 |
| s03_A (current s03v18 + base from _in 2c2c0edb, simulate=False) | ok, 20 uids, REUSE-NOTED 23276 | same | EQUAL 4/4 |
| s03_B (plan_ring_p4_s03v18_in.json) | ok | same | EQUAL 4/4 |
| c106e_noX17 (--prerun, X17 stubbed) | rc 1, X5 FAIL ops 19 | rc 1 | DIFFERENT, first diff line 55 = dry scratch VI clock stamp 161939 vs 162206 |
- Inputs: plan_ring_p3b2 04204133, s03v18 da66a030, graph p3b1 6cfa6ecb, graph p4s02 eda9db40.
- 16:23 re-launch (`_r2`, clock stamp normalised) REFUSED by guard_peer: JEV-LADDER 16:23:21 diag_c148_a2_3_unmask.log new-problem p=0.770, NEXT-ACTION hypothesis review owed (jev_gate.log:5185). Never ran.

## Review (flags.peers hypothesis)
- archive/peer/2026-10-08-c148-a3-1-unmask-clockstamp.md (b6678f43), claude/hypothesis, ANSWERED, log diag_c148_a3_1_peer.log (BGRUN END rc=0 203 s).
- VERDICT: claim REFUTED. The c106e case was not E1's setup: sys.argv not set, so the recipe ran in full mode (ops 19, par1359_95 graph, coverage 56/70). Also PRERUN_LOG_DIR was set after import (LOG_DIR is read at stage_prerun.py:124). Pre-148 E1 passes X5 (ops 7, s4_c106e_e1_full.log:88); only X17 fails.
- Disposition written (FIXED: at diag_c148_a2_3_unmask.py:65): c106e now runs in its own child per variant, with a fresh PRERUN_LOG_DIR in the env, sys.argv = recipe argv, clock stamps normalised, both tallies shown and up to 20 differing lines printed. The revised script (efb5f66b) is NOT run.

| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c148_a2_3_unmask.log | new-problem 0.770 | hypothesis review owed | dispatched the review (card peers: hypothesis), accepted it, patched only my diag, returned | ANSWERED, claim REFUTED |

Written: diag_c148_a2_3_unmask.py, _unmask.log, _unmask_review_task.txt (c80b56b0), diag_c148_a3_1_suites.py, _peer.log, this file, review file. No tool/hook/plan/recipe/self-test edited.

OPEN: re-issue as a card that (1) runs the revised unmask (prediction: c106e X5 PASS ops 7 on both, 0 differing lines; rebase cases already EQUAL), then (2) launches diag_c148_a3_1_suites.py (worktree cleanup + 4 suites)?
