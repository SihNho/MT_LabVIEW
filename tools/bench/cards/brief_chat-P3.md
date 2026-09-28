# Brief chat-P3 - finish chat-P2's verification, then speed item A (user 2026-09-28: "A는 실행")

RUNNER STAYS STOPPED (keep STATUS.md's STOP line; do not launch cycle_runner / supervisor). No LabVIEW. Do not edit
CLAUDE.md or STATUS.md.

## Part 1 - close chat-P2 (result_chat-P2.json: BLOCKED 19/1, commit 99e99f8)
1. `tools/bench/p2run_selftest_guard_cycle_offline.log:5-6` O3/O4 FAIL: the fixture encodes the real 09-27 state whose
   prior-art review was later released by FIXED lines (archive/peer/2026-09-27-priorart-c111e-l2b2a.md:543-547). The
   owed failed-prediction review: dispatch ONE hypothesis peer (`tools/peer.ps1 -Agent claude -Role hypothesis`, under
   bgrun) naming that log, asking it to ATTACK "stale fixture, pre-existing drift, not caused by chat-P2". Annotate it.
2. Fix the fixture: make selftest_guard_cycle_offline build its own fabricated state (a temp review file with an
   unreleased non-novel verdict) instead of reading the live archive. Re-run it green.
3. Run every self-test chat-P2 could not: stage_prerun_* (all), guard_cycle_rerun, stoprecord c116a/c107/table,
   prerun_diag, c110, c111c, c103d, cycle_runner (the fp-8 name clash: resolve it, e.g. guard_card's RUNNER_CMD_RE must
   not match `selftest_cycle_runner`). All green. Drain gate-fp entries fp-7/8/9 with `tools/gate_fp.py drain`.
4. Decisions on P2's open items (from the chat): offline self-test iterations inside a tool-build card may continue
   (keep as written); guard_session importing stage_prerun lazily is accepted (stricter is fine).

## Part 2 - speed item A: skip the SCRATCH build on a proven pattern
- Today every build step runs the recipe on a scratch byte copy (~15 min) and then the ONE real launch. When the step's
  recipe is a PROVEN pattern (`stage_prerun.proven_pattern`, >= 2 OTHER clean stages, PD232) AND its offline dry run +
  prerun PASS on the current plan md5, the scratch launch is NOT required: the launch gate stops requiring a scratch
  PASS record for that stage and logs `SCRATCH-SKIP-PROVEN | <stage> | proven: <stages>`.
- A NEW structure class (op kinds not in any passing stage) always keeps the scratch build.
- If the real launch then fails, the next attempt of that stage requires the scratch build again (no second skip).
- Find where the scratch requirement lives (stage_prerun check_launch / records, stagekit, prompt text) and change it
  there; add the rule to cycle_prompt.md and a Pre-decided line in docs/d1-loop12-17-split-plan.md (next free number,
  with a USER-RULES: line).
- Self-test cases: proven + prerun PASS -> scratch not required; new class -> required; after a failed real launch ->
  required again.

One commit at the end. Return result/1.
