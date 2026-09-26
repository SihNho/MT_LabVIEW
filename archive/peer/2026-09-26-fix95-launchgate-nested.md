# fix95-launchgate-nested

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.8309  in 36 / out 20339 / cache-create 130422 / cache-read 1902972  (231s, 25 turn(s))
- **date:** 2026-09-26 13:04:36
- **outcome:** ANSWERED (235s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim (card 95-1, offline only, no LabVIEW).

CHANGE: tools/stage_prerun.py find_graph() now returns only graph JSONs of the terminal-list shape ({terminals, objs});
OfflineGraph raises GraphShapeError on any other shape; _graph() catches it and sets D.graph_error (new DryState field).
Nothing else in stage_prerun.py changed (launch gate check_launch, records, control_path_lint untouched).

OBSERVED (tools/bench/prerun_fix95_selftests_before.log vs tools/bench/prerun_fix95_selftests_after.log, harness
tools/bench/prerun_fix95_selftests.py, which sets PRERUN_RECORDS to a %TEMP% file per tag and runs each test as a child):
- BEFORE the change: selftest_stage_prerun_stageplan.py 12/0, its child EX selftest_launch_gate.py rc 0 PASS.
- AFTER the change: selftest_stage_prerun_stageplan.py 11/1, failing "EX selftest_launch_gate.py rc 0" (the child
  selftest_launch_gate.py returned rc != 0 inside stageplan's subprocess). The harness did not keep the child's detail.
- In the SAME after-run: selftest_launch_gate.py run directly = 28/0 PASS; selftest_stage_prerun_headcmp_79-6.py runs
  selftest_launch_gate.py again in a HEAD-vs-worktree sandbox = 28/0; selftest_prerun_diag 9/0; --selftest-control-lint
  10/0; the new selftest_stage_prerun_graphload.py 18/0.

CLAIM: the stageplan-nested launch_gate failure is NOT caused by the graph-loader change; it is an environment/timing
interaction of selftest_launch_gate.py when nested (inherited PRERUN_RECORDS / PRERUN_LOG_DIR env, or a same-second
record-time comparison), because the same test passes 28/0 twice in the same run and the loader is not on the
launch-gate path.

Read tools/bench/selftest_launch_gate.py, tools/bench/selftest_stage_prerun_stageplan.py (lines 61-64) and
tools/stage_prerun.py (find_graph, OfflineGraph, _graph, check_launch). Give the strongest reason the claim is wrong,
an alternative cause, and the cheapest discriminating test.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The claim does not hold as written.** The loader probably isn't the cause, but the two mechanisms the claim offers in its place are both ruled out by the code. What's left is an explanation nobody measured, even though the detail that would settle it was printed and then cut off by the harness.

## 1. Strongest reason the claim is wrong

- **Inherited environment is impossible.** `selftest_launch_gate.py` sets its own values for PRERUN_RECORDS, PRERUN_LOG_DIR, STAGE_RUNS and STAGE_RUNS_CYCLE before it imports `stage_prerun` (`tools/bench/selftest_launch_gate.py:24-29`). `stage_prerun` reads them at import (`tools/stage_prerun.py:75-76`, `:1377`, `:1397`). Whatever the parent passes down is replaced. The only variable `selftest_stage_prerun_stageplan.py` adds is PRERUN_RECORDS (`selftest_stage_prerun_stageplan.py:12`), and it is replaced too. Neither `stage_prerun.py` nor the hook/protocol modules write to `os.environ` (grep: no hits except the read at `:1398`).
- **A same-second race has no code to happen in.** Every record the gates compare is backdated with `t=time.time()-100` (`selftest_launch_gate.py:69,103,196,204`). `last_failed_run_after` compares file mtime against that time, which is 100 s old (`stage_prerun.py:1357`). There is no comparison at one-second precision.
- **The failure detail existed and was thrown away.** `selftest_stage_prerun_stageplan.py:64` prints the child's `=== GATES` line and, when rc≠0, the last 200 characters of its stderr. The harness then printed only `lines[-4:]` (`prerun_fix95_selftests.py:24-25`). The EX launch_gate line is the fifth line from the end, just outside what was printed. So the claim was inferred with the deciding measurement one line out of view.
- **No history supports "fails only when nested".** The earlier nested failures (`selftest_stage_prerun_stageplan.log:67`, `lint_verify_20260925.log:226`) happened while the direct run also failed 20/8 (`lint_verify_20260925.log:215`). That was the known pre-chat-L2 set, not a nesting effect.

## 2. Alternative explanations for the same evidence

- **A) Ordinary flakiness in a %TEMP% sandbox.** For example, `os.remove` in `records()` / `clear_logs()` (`:46`, `:59`) hitting a file that the virus scanner still holds open, right after writing it. Python documents that on Windows, removing a file in use raises an exception (https://docs.python.org/3/library/os.html#os.remove). The child would then end with rc 1 from a traceback, not from a failed gate. With one before-run and one after-run, "fails after the change" and "fails sometimes" look exactly the same.
- **B) Repo state that is not sandboxed and depends on run order.** `guard_bash._main` calls `jev_advisories()` (`tools/hooks/guard_bash.py:459`). That function is rate-limited per session id through the real `tools/bench/jev_drift_state.json`, one call per 60 s (`tools/jev_drift.py:45-46,179`). The session id is the constant `"selftest"` (`selftest_launch_gate.py:180`).
  - The before-run started at 12:57:51 and the after-run at 12:59:45, more than 60 s apart. So the nested child was the first launch_gate process of the after-run and the only one of the three that took the live-Jev path (`jev_preflight.classify`, timeout 25 s, `tools/jev_preflight.py:228-237`). The headcmp and direct runs came within 60 s and were rate-limited.
  - Its exceptions are swallowed (`guard_bash.py:366-385`), so this is the weaker alternative. But it is the one real difference I can find between the nested run and the two direct runs, and it has nothing to do with nesting itself.
- **C) The change itself** can't be excluded by n=1 either. Reading the code supports "the loader is not on `check_launch`'s path" (`stage_prerun.py:1490-1537` never touches `find_graph`/`OfflineGraph`), and the headcmp worktree run is 28/0 (`prerun_fix95_selftests_after.log:9`). That makes C unlikely, not ruled out.

## 3. What would falsify the claim

The child's detail line naming a gate whose result depends on `stage_prerun`'s current code. Also: the nested failure repeating on the worktree while the HEAD `stage_prerun.py` passes nested, several runs each.

The claim's specific mechanism is already falsified by the code above. The failing detail showing a traceback (A), or a failure that disappears once 60 s have passed since the last run (B), would confirm an alternative instead.

## 4. Cheapest discriminating test

Rerun `py -u tools/bench/selftest_stage_prerun_stageplan.py` alone under bgrun, with its full log. This takes about 5 s, is offline, and doesn't touch LabVIEW. Line 64 prints the child's `=== GATES x/y` and its stderr tail.
- A traceback (`PermissionError`/`WinError 32`) points to A.
- A named L/C/M/R gate FAIL points to the change, or to an order effect.
- If it passes, run it 3× on the worktree and 3× with the HEAD `stage_prerun.py` (the headcmp sandbox pattern), with one of each pair started more than 60 s after the previous launch_gate run. That separates B, and gives a flake rate instead of a one-sample story.

Until that detail line has been read, "not caused by the loader" should be recorded as an unmeasured assumption, not a finding.

## Sources

(extract from answer)

## What was done with it

Accepted: the claim's two named mechanisms (inherited env, same-second race) are withdrawn as refuted by the code
(`selftest_launch_gate.py:24-29`, backdated `t`). Ran the review's cheapest test: `selftest_stage_prerun_stageplan.py`
alone under bgrun on the worktree WITH the card-95-1 loader change, full log kept -> 12/0, nested EX
selftest_launch_gate.py 28/0 (`tools/bench/selftest_stage_prerun_stageplan_95.log:75,78`). The one nested failure in
`prerun_fix95_selftests_after.log` did not reproduce; its detail line was lost to the harness's `lines[-4:]` cut, so its
cause stays UNMEASURED (the review's A: transient os.remove / B: Jev rate-limit path are both open). Recorded as such in
result_95-1.json, not as "not caused by the loader". The 3x worktree-vs-HEAD flake-rate run was not done (card budget).
