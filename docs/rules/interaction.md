---
type: rules
status: current
date: 2026-10-10
tags: [rules, user, interrupts, reporting]
---

# Rules - working with the user: interrupts, start/stop, usage limits, reports

Restated briefly from `docs/rules/CLAUDE-full-2026-10-10.md` (cited ranges = full wording and quotes).

- **Rule 2 - LabVIEW is shared with real experiments; be interruptible at any point.** The user may stop a session at
  any moment to reclaim LabVIEW; keep `STATUS.md`'s state current DURING work, after each real milestone.
  `docs/rules/CLAUDE-full-2026-10-10.md:146-151`
- **Rule 2b - the user's messages during work are interrupts: answer first, then continue.** The very next reply,
  first line, before any tool call; a progress line is not an answer; a yes/no question gets its yes/no first. Stop or
  redirect the work if the message implies it; background anything slow. *Mechanism:* `tools/hooks/answer_first.py`
  (UserPromptSubmit) re-injects it on every user message. `docs/rules/CLAUDE-full-2026-10-10.md:152-161`
- **Rule 2c - once a cycle is turning, run it to the end.** Finish the cycle, then report once. When uncertain:
  do every part that does not depend on the answer; for the part that does, write the assumption down, proceed under
  it and flag it in the closing report; stop only when proceeding under any assumption would be unsafe, destructive
  or useless. Mid-cycle questions make the user the scheduler; 2b still holds for their messages.
  `docs/rules/CLAUDE-full-2026-10-10.md:162-177`
- **Start/stop is explicit, never inferred** ("지금 진행해" / "멈춰"); silence is not authorization. Keep the
  `labview-lock` block in `STATUS.md` (status acquired|released, owner, since, purpose) true so any session can see
  whether LabVIEW is safe to touch. `docs/rules/CLAUDE-full-2026-10-10.md:178-191`
- **Usage-limit protocol (2026-09-04).** Detect (check usage before long units; a limit error is the trigger; never
  assume the quota is fine). Schedule, don't wait: at ~95 % or on a limit error write the resume point to STATUS and
  schedule a wake-up at renewal + 2 min. Rerun, don't resume: an interrupted bench/build is rerun from the beginning,
  the partial attempt logged as a non-result. Never wait on a user turn for something a script can do. Platform
  limits only - self-imposed usage gates are retired (see `docs/rules/reviews.md`, run mode).
  *Mechanism:* `cycle_runner.py` usage-limit rerun. `docs/rules/CLAUDE-full-2026-10-10.md:233-251`
- **Reports reach the user through the Claude session - the user is remote (2026-09-25).** A toast, a local file or a
  session-only timer is not a report. Path: (1) `cycle_runner.py` writes `HEARTBEAT` at every cycle end and runner
  stop (`tools/bench/heartbeat_latest.md`); (2) the app scheduled task `runner-cycle-report` (every 30 min) turns new
  events into a Korean report under `tools/bench/reports/`, acks `report_gate`, and the main chat relays it verbatim
  and pushes a notification; (3) `tools/hooks/report_gate.py` blocks the chat's turn on unreported events. Open user
  decisions (`tools/bench/decisions_pending.json`) are part of every report. `docs/rules/CLAUDE-full-2026-10-10.md:252-263`

Related decisions: `docs/decisions/stay_responsive_during_long_work.md`,
`docs/decisions/finish_the_cycle_without_stopping.md`, `docs/decisions/report_runner_events_without_being_asked.md`,
`docs/decisions/quota_limit_schedule_resume_and_rerun.md`, `docs/decisions/explain_in_plain_language.md`.
