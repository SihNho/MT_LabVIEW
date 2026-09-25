# c79-6-k_launchgate

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $0.9646  in 14 / out 7505 / cache-create 86810 / cache-read 600066  (91s, 14 turn(s))
- **date:** 2026-09-25 09:38:42
- **outcome:** ANSWERED (95s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about a failed self-test (card tools/bench/cards/task_79-6.json).

Failing log: tools/bench/selftest_stage_prerun_stageplan.log (script tools/bench/selftest_stage_prerun_stageplan.py).
Its own 9 cases S1-S9 PASS; the one failing gate is "EX selftest_launch_gate.py rc 0": the pre-existing self-test
tools/bench/selftest_launch_gate.py, re-run as a subprocess, reported 20 pass / 8 fail (its last archived run,
tools/bench/selftest_launch_gate.log dated 2026-09-24 19:33, was 16/0 with fewer gates).

The change under test (card 79-6) is in tools/stage_prerun.py only: plan_files() now also admits a named
stageplan/1 json, a new stageplan_check(), and new branches in prerun() X2/X3/X5. check_launch/check_cap/
record_stage_run were NOT edited.

CLAIM: the 8 failures are PRE-EXISTING and unrelated to the 79-6 edit. They are the [C] RETRY CAP and [M] cases of
selftest_launch_gate.py (lines 99-196), which record runs via SP.check_launch(..., record=True) -> record_stage_run(by=
"check_launch"), while check_cap (tools/stage_prerun.py, "RECORDER REPAIR (card 78-2)") now COUNTS only lines with
"by": "bgrun". So run 3 is no longer refused (C2), and C3-C6/M6 cascade. selftest_launch_gate.py's STG recipe names no
.json, so plan_files()/stageplan code cannot be reached by it. selftest_retry_cap.py (the 78-2 test) passes 8/0.

Give the strongest reason this claim is wrong, an alternative explanation, what would falsify it, and the cheapest
discriminating test (e.g. running selftest_launch_gate.py against the HEAD version of stage_prerun.py).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict:** the code supports the claim, but nothing has measured it yet. It is a guess that fits a total of 20 pass / 8 fail, and it misnames three of the eight failures. I had no shell in this session, so everything below comes from reading the code and logs, not from running anything.

## 1. Strongest reason the claim is wrong: nobody has seen which 8 cases failed
- The parent test keeps only the `=== GATES` and `RESULT` lines from the child's output (`tools/bench/selftest_stage_prerun_stageplan.py:63`). The case-by-case lines of the failing run were never recorded, so "the 8 are C and M" is an inference, not a reading.
- "Pre-existing" has never been observed either. The only archived run, `tools/bench/selftest_launch_gate.log:38`, is 16/0 on an older version of the test that had no C cases and no M4–M6. No archived run exists of the current 28-gate version, passing or failing, before or after 78-2. So nothing shows it failed before 79-6.
- The claim's own list is incomplete. From the code, exactly C2, C3, C4, C5, C6, M4, M5 and M6 should fail. Only C2–C6 and M6 come from the check_cap change (`tools/stage_prerun.py:1108` counts only `by == "bgrun"`, while `check_launch` records with the default `by="check_launch"`, `:1119` and `:1182`).
  - **M4 and M5 fail for a different 78-2 reason.** guard_bash no longer records at all (`tools/hooks/guard_bash.py:387-390`), so `nruns()` stays at 0. M4 expects 1, M5 expects 1, and M6's third launch is never capped.
- Code reading does give L1–L9, L4b, C0, C1, C7, C8, M1–M3 and R1–R3 passing: 20, which matches the count exactly. That matters, but a matching total is not matching case names.
- "plan_files() cannot be reached" is also wrong as stated. `check_launch` calls `plan_md5s(s)` → `plan_files()` on every launch (`:904-908`, `:1159`). For the test recipe (`stage_lgtest.py`) it returns `([], [])` because the recipe names no `.json`. So the new branches cannot change the result, but the edited function does run.

## 2. Alternative explanations of the same 20/8
- **(a) The 78-2 change may be uncommitted.** `tools/stage_prerun.py` shows as modified against HEAD (commit 6f44092). If the RECORDER REPAIR hunk is in the working tree rather than in HEAD, then "pre-existing" means "introduced by uncommitted work in this same file". The 79-6 diff would then include it.
- **(b) A different set of 8 that happens to match the count.** For example, an exception inside the edited `plan_files` is swallowed by `plan_md5s`'s bare `except` and returns `{}`. That makes a different set of cases pass or fail. It is unlikely from the code, but it is exactly what a count cannot rule out.

## 3. What would falsify the claim
- A per-case run whose failing set is anything other than exactly {C2, C3, C4, C5, C6, M4, M5, M6}.
- Or: `selftest_launch_gate.py` scores 28/0 against a `stage_prerun.py` that has the 78-2 COUNTED_BY hunk but not the 79-6 hunks.

## 4. Cheapest test that separates them
1. Run `py -u tools/bench/selftest_launch_gate.py` directly under bgrun and read the case lines. The claim predicts exactly the 8 names above. This is one run of about a minute, and the sandbox is `%TEMP%`, so nothing in the project changes.
2. `git show HEAD:tools/stage_prerun.py | grep -n COUNTED_BY`.
   - If the hunk is in HEAD, run the self-test in a `git worktree` at HEAD. The claim predicts the same 20/8 with the same names.
   - If it is not in HEAD, the HEAD run cannot separate 78-2 from 79-6. Use `git diff HEAD -- tools/stage_prerun.py` instead, to show which hunks belong to which card.

## Even if the claim holds
- The 79-6 prediction "`selftest_launch_gate` rc 0" was wrong on arrival. `selftest_launch_gate.py` has been out of date since 78-2, and 78-2's acceptance never re-ran it.
- The fix is to update its C and M sections to count through `record_started(..., by="bgrun")`, not to excuse the failure.
- No `guard_bash.py.new` is staged (Glob found none), so the self-test's `os.replace` install branch cannot fire during these runs.

## Sources

(extract from answer)

## What was done with it

Ran the review's s4 test 1+2 as one script, tools/bench/selftest_stage_prerun_headcmp_79-6.py ->
tools/bench/selftest_stage_prerun_headcmp_79-6.log (BGRUN END rc=0): HEAD:tools/stage_prerun.py (has COUNTED_BY, has no
stageplan_check) and the working tree (79-6 edit) both give selftest_launch_gate.py 20/8 with the IDENTICAL failing set
{C2,C3,C4,C5,C6,M4,M5,M6} - the review's corrected list (M4/M5 via guard_bash no longer recording), not the claim's.
Accepted: the failures are pre-existing since 78-2 and not caused by 79-6; the claim's "plan_files cannot be reached"
wording was wrong (it runs, returns ([], [])). NOT done: updating selftest_launch_gate.py's C/M sections to count via
record_started(by="bgrun") - outside card 79-6's write list; returned to the judgement session as OPEN.
