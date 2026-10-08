# c148-a2-3-t3regress-prefix

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.1554  in 20 / out 9488 / cache-create 99687 / cache-read 840415  (98s, 23 turn(s))
- **date:** 2026-10-08 16:02:17
- **outcome:** ANSWERED (102s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** guard_peer owed a hypothesis review for tools/bench/diag_c148_a1_2_before_t3_regress.log (RESULT 7/3; JEV-LADDER new-problem p=0.782), card 148-a2-3 step 1
- **verdict:** unverified

## Question

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


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The claim stands — the three children are not broken by the cycle-148 edits — but two of the four pieces of evidence offered for it are invalid, and the claim reaches further than the evidence does.**

**1. Strongest reason it is wrong: the "pre-fix" E1 run was actually a post-fix run.**
- `diag_c148_a1_1_before.py:54-58` loads the four HEAD blobs only into its own process. But E1 of `selftest_stage_prerun_c106e.py` starts its own subprocess: `py tools/stage_prerun.py --prerun RECIPE --no-record` at `selftest_stage_prerun_c106e.py:90` (E2 does the same at :107).
- That subprocess loads the edited `stage_prerun.py` (dcd45aba) from disk. So the X17 failure in `diag_c148_a1_1_before_c106e.log:20` came from the edited code. It is not a pre-fix measurement, and `diag_c148_a1_1_facts.md:24` ("SAME on the pre-fix code") is false for E1.
- The 2026-10-08 `t3_regress` wrapper run is post-fix too, as `diag_c148_a1_2_facts.md:22` already admits.
- The pre-fix runs of c133 and c143_4 did not give the "same failures" either. They crashed: c133 with `IndexError` (`diag_c148_a1_1_before_c133.log:12`) and c143_4 with `KeyError: 'sim_of'` at `docs(p3)` (`diag_c148_a1_1_before_c143_4.log:14`). The post-fix runs show only "no count line" (`diag_c148_a1_1_runall_after.log:12,48`), so whether they crashed the same way was never checked line by line.

**2. Alternative explanations, and what the record shows**
- **(a) Stale plan files (the claim's own explanation).** The `rebase()` refusal is the first check in the function: `stage_prerun.py:4243-4244` refuses whenever `plan.base.provisional` is not set. That depends only on the plan file's content, and none of the edited lines (592, 848, 3150, 3415, 3433, 4474) is in that path.
  - Both plan files the tests read have since been rebased onto a real base and carry no `provisional` flag: `plan_ring_p3b2.json:65-68` and `plan_ring_p4_s03v18.json:8-11`.
  - c133's docstring expects input md5 98992a59 (`selftest_c133_1_fsroutes.py:9`); the file is now 04204133 (`diag_c148_a1_1_before_c133.log:7`). The plan file changed after the test was written.
  - X17 was added in card 141-1 (`stage_prerun.py:2795,2946-2948`), long after the c106e test (card 106). It rejects the disp plan's `r7_wait` because that action has no donor uid.
- **(b) The edits break these paths too, hidden behind the stale plans.** The refusal at :4244 ends U1/U2 and R1/R2 before any later rebase or simulate code runs, and X17 fails E1's prerun first. These tests currently check nothing past those points, so a regression there would show identical output. The evidence cannot rule this out.

**3. What would falsify the claim**
A `t3_regress` run from before cycle 148 that did *not* show these three failures. The opposite is on disk:
- `selftest_t5_regress.log:1-15`, 2026-10-07 16:26 (card chat-T5, before cycle 148): RESULT 7/3, the same three children, the same strings. That covers "base is not provisional" for R1/R2 and U1/U2, and E1 at 14/1 with X17 on `r7_wait`.
- `selftest_t3_regress_final.log:1-15`, 2026-10-07 14:56: identical.
- The E1/X17 failure also appears in `s2_regress_after.log:10`, `s3_regress.log:10` and `s4_regress.log:10`. `selftest_f2_suite.log:9` and `selftest_c_e3_suite.log:11` each list it as PRE-EXISTING with a matching HEAD result.

Cycle 148's edits are dated 2026-10-08: the logs start 14:51 and the runner log is `cycle_runner_main_20261008_1231.log`. So the failures came first. The older logs refute the claim's offered evidence, not the claim.

**4. Cheapest discriminating test (no LabVIEW, no tool edits)**
- **For causation:** compare the failure strings in `selftest_t5_regress.log` lines 3, 7 and 11 with `diag_c148_a1_2_before_t3_regress.log` lines 7, 11 and 15. They are already identical apart from temp-folder names. This costs nothing and settles causation.
- **For the masking risk in 2(b):** make a new `tools/bench/diag_c148_a2_3_unmask.py`. It would copy `plan_ring_p3b2.json` and `plan_ring_p4_s03v18.json` into %TEMP% and put the provisional base back. The plan's `finalized.plan_in` points at the provisional input, e.g. `plan_ring_p4_s03v18_in.json` (`plan_ring_p4_s03v18.json:335-337`). Then run `SP.rebase` on those copies twice: once with the HEAD blob of `stage_prerun` and once with the disk copy. Do the same for the c106e recipe with X17 skipped, comparing the HEAD and current `stage_prerun.py` from a HEAD worktree (`selftest_t3_regress.py --root`, as `selftest_t3_regress_head.log:1` already did). Matching gate output in both runs closes 2(b); any difference refutes the claim.

VERDICT-LINE: claim STANDS - the same 7/3 with identical failure strings was recorded on 2026-10-07 16:26 (`selftest_t5_regress.log`), before any cycle-148 edit, but the cycle's own "pre-fix" evidence is invalid for E1 (the stage_prerun.py subprocess ran the edited code), and the stale plans hide whether the edits break the code past the first refusal.

## Sources

(extract from answer)

## What was done with it

Card 148-a2-3 (material). Claim STANDS per the verdict; accepted with both corrections. Verified on disk: `tools/bench/selftest_t5_regress.log:1,3,7,11,15` (2026-10-07 16:26, before cycle 148) = RESULT 7/3 with the same three failure strings; `tools/bench/selftest_stage_prerun_c106e.py:90` starts its own `tools/stage_prerun.py` subprocess, so the 148-a1-1 "pre-fix" E1 run was post-fix (diag_c148_a1_1_facts.md:24 is wrong for E1). The pre-fix comparison is therefore re-done from a clean HEAD `git worktree` (every subprocess pre-fix), as the review proposes, by `tools/bench/diag_c148_a2_3_suites.py` (t3_regress --root, c134_1_a4, c134_2_regress; c_e3/f2 already compare against HEAD). The masking risk 2(b) (stale plans stop R1/R2/U1/U2/E1 before the edited code runs) is NOT tested here - the unmask script is outside this card's pass list; it is returned as an OPEN item to the judgement session.
