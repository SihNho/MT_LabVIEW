# Brief chat-P2 - speed items 1-4, approved by the user 2026-09-28 17:xx ("그렇게 1~4번 적용하여 수정하면 되겠음. 아직 러너 돌리지는 말고")

Measured basis (cycles 114-119, 642 min): cards 93 % of wall time, judgement gaps 4 %, retro 3 %, pre-hooks <1 %.
28 cards: 12 PASS, 10 FAIL, 6 BLOCKED. Long sinks were FAIL cards that kept retrying inside the card (116-2 95 min,
115-3 65 min) and an escalation chain on one function (118: 84 min). Error List reads ~11 min each; the pool stage
read the same graph twice (scratch 664 s + final 665 s). The largest loss of all was a design direction that
contradicted user rules (cycles 84-120 area, pool/queue vs the user's frame rules).

THE RUNNER STAYS STOPPED. Do not remove the STOP line from STATUS.md. Do not touch LabVIEW. Do not edit CLAUDE.md
(the chat does). Safety guards unchanged (motor, originals, LabVIEW timeouts, rule 1a, failed-prediction review for a
NEW failure class).

## 1. Every new design is checked against the USER'S RULES before it is built
- Create docs/user-rules.md: one row per standing user design rule, each with the verbatim quote, date and source
  (memory file or doc line). Seed it from: CLAUDE.md 1a, 1b, 1c, 1c'', the 2026-09-15 frame rules (memory
  prefer_the_freshest_frame_over_a_complete_backlog.md, camera_free_runs_never_gate_it.md, docs/decisions.md:20-25),
  locals_not_queues_focus_loop_own_clock.md, display_in_separate_loop_fed_by_locals.md, and the new
  docs/ring-buffer-design.md (2026-09-28). Memory files are under
  C:\Users\KimLab\.claude\projects\G--Codes-LabVIEW-Codes-MinLab-zz-LabView-VI-AAA-UNIST-2--Tracking-V6-ParallelLoop\memory\
  (read-only for you; copy quotes, do not edit them).
- tools/prior_art_review.py: attach docs/user-rules.md to every dispatch and add one fixed question: "Does this plan
  contradict any rule in user-rules.md? Name the rule and the plan line." A contradiction answer counts as a
  non-`novel` verdict (the existing release rules REFUTED:/FIXED: apply). Keep the proven-pattern skip for pure
  repeats, but a plan that introduces a NEW structure class (op kinds not in any passing stage) always gets the review.
- tools/cycle_prompt.md: before writing any new Pre-decided DESIGN item, the judgement session reads
  docs/user-rules.md and writes a `USER-RULES:` line in that item citing the rules it relies on or "none apply".
  doc_lint: warn when a Pre-decided item added after 2026-09-28 lacks a `USER-RULES:` line.

## 2. Stop at the first unexpected result; soft 60-min alert (NO hard kill)
- .claude/agents/material*.md (all four) and cycle_prompt.md: when a step's result differs from its prediction, the
  material session FINISHES that step (LabVIEW closed, files saved/cleaned), records the facts, and RETURNS to the
  judgement session instead of diagnosing and retrying inside the card. The failure budget (2) is unchanged; the first
  failure is now a return, the judgement session decides the retry.
- Soft alert: tools/hooks/guard_card.py (or wherever the bound card's start time is known) refuses STARTING a new
  bgrun launch of a recipe/diag once the bound card is older than 60 min, with a message "finish the running step and
  return a result". Reads, docs, peers, and anything already running are never blocked or killed.

## 3. Error List: no duplicate full reads
- Where a stage reads the Error List of a SCRATCH copy and then of the saved FINAL file (e.g. stage_d1_qrt_pool_el_scratch
  + _el_final; find the call sites in tools/stagekit.py / tools/errorlist_check.py / recipes), the scratch read becomes
  a COUNT-ONLY read (per class counts vs the expected file); the FINAL saved file keeps the FULL read + reverdict every
  time. If the scratch counts differ from expectation, do the full scratch read as today.
- Never skip the final full read. Report the measured minutes saved on the next run in the result card later.

## 4. Same scripting function fails twice -> scratch-VI verification, not a model escalation
- cycle_prompt.md (intra-cycle escalation section) and tools/cycle_runner.py if it issues escalations: when a card's
  first_fail names the SAME gscript/stagekit function (or op VI) as the previous failing attempt of that stage, the next
  card is the scratch-VI verification of that function at the SAME model rung (the existing scratch_verify rule), not
  an escalation to Opus max / Fable low. Escalation stays for failures that are NOT a repeated tool function.

## Self-tests
Run the existing affected self-tests (guard_card, guard_session, protocol, cycle_runner, cycle_runner_ladder,
prior_art related, doc_lint, stage_prerun_*, chat_p1) and add cases: prior-art task text contains user-rules.md and
the question; 60-min alert blocks a new launch but not a read; scratch Error List count-only path; repeated-function
failure maps to scratch-verify not escalation. All green, one commit.
