---
card: 148-a2-3
date: 2026-10-08
status: FAIL - review ANSWERED (claim STANDS); the one measurement launch crashed in my own wrapper before any suite ran (git worktree add failed, unchecked)
---
## Step 1 - hypothesis review
- archive/peer/2026-10-08-c148-a2-3-t3regress-prefix.md (md5 3674436d after disposition), claude/hypothesis opus-5.5 high, ANSWERED 102 s, $1.16. Log tools/bench/diag_c148_a2_3_peer.log (BGRUN END rc=0 103 s).
- Verdict line: "claim STANDS - the same 7/3 with identical failure strings was recorded on 2026-10-07 16:26 (selftest_t5_regress.log), before any cycle-148 edit, but the cycle's own pre-fix evidence is invalid for E1 (the stage_prerun.py subprocess ran the edited code), and the stale plans hide whether the edits break the code past the first refusal."
- Verified: selftest_t5_regress.log:1,3,7,11,15 (2026-10-07 16:26) RESULT 7/3, same 3 children, same strings; selftest_stage_prerun_c106e.py:90 spawns `tools/stage_prerun.py --prerun` as a subprocess, so diag_c148_a1_1_facts.md:24 "SAME on the pre-fix code" is wrong for E1.
- Review also says (not verified here): pre-fix c133 / c143_4 runs CRASHED (IndexError, KeyError 'sim_of') rather than showing the same FAIL rows (diag_c148_a1_1_before_c133.log:12, _c143_4.log:14); rebase refusal is stage_prerun.py:4243-4244 (plan.base.provisional), off every edited line; X17 added in card 141-1.
- Disposition written under `## What was done with it`: accepted; pre-fix comparison moved to a clean HEAD worktree; masking risk 2(b) (stale plans stop R1/R2/U1/U2/E1 before edited code runs) not tested - OPEN.

## Step 2 - measurements
| script | log | rc | counts | seconds |
|---|---|---|---|---|
| diag_c148_a2_3_suites.py (one launch: t3_regress + c134_1_a4 + c134_2_regress + c_e3_suite + f2_suite NOW, and t3/c134_1/c134_2 in a HEAD worktree) | diag_c148_a2_3_suites.log | BGRUN END rc=1 41 s (NO RESULT LINE) | none - no suite started | 41 |
- Failure: diag_c148_a2_3_suites.py:81 FileNotFoundError `...\Temp\c148a23head_cqqsredu\tools/stage_prerun.py` - `git worktree add --detach <tmp> HEAD` (:79) did not create the tree; my script discarded its stderr and did not check rc (script bug, same call as selftest_c_e3_suite.py:46). Not diagnosed, not retried (card chat-P2 rule).
- JEV-LADDER row for diag_c148_a2_3_suites.log: none yet in jev_gate.log (only a JEV-PREFLIGHT line 16:02:50, missing-guard p=0.59).
- Therefore NOT measured: plain t3_regress, the 4 suites, every pre-fix comparison.
- `git worktree list` shows two stale worktrees from earlier killed suite runs: Temp/e3head_r96iqm4t and Temp/f2head_1n3cihvt (detached 07202624); not mine, not touched. My empty dir Temp/c148a23head_cqqsredu remains (rmdir outside the project needed approval).

## Invariants / LabVIEW
stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c - unchanged. LabVIEW processes 0 before, 0 after. Written: only tools/bench/diag_c148_a2_3_* (review_task ae101211, suites.py 98955561, suites.log 7616141c, peer.log, this file) and the review's two Claude fields.

OPEN: (1) retry the measurement with the wrapper fixed (check `git worktree add` rc/stderr; stale e3head/f2head worktrees may need `git worktree prune`)? (2) does the review's masking risk 2(b) need an unmask test (provisional base restored in %TEMP% copies, rebase/prerun at HEAD vs disk) before the cycle-148 stage_prerun edits are accepted?
