---
name: report-runner-events-without-being-asked
description: "The user expects a progress report every 30 minutes while the runner runs and a report at EVERY cycle end, without asking — and on 2026-09-23 ruled that this must be hook-enforced, never memory-enforced"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 1e5293f3-09a7-4b72-9393-fcba8dd55703
  modified: 2026-09-27T22:10:26.834Z
type: decision
status: in-force
date: 2026-09-27
source: memory/report_runner_events_without_being_asked.md
---

# Runner events are reported unprompted, every 30 minutes and at every cycle end — by a hook, not by memory

**2026-09-25 evening, the user's standing situation: "보통은 내가 원격으로 러너 확인 및 지침을 줌. 그러니 클로드 세션으로
확인 필요함. 훅 경로 변경하도록."** The user is usually NOT at the lab PC; they read the runner and give
instructions through the Claude session from elsewhere. So a Windows toast or a local file is not a report. The
report has to land in the Claude conversation (and on their phone when mobile push is enabled). Path in force:
the runner writes `HEARTBEAT` lines + `heartbeat_latest.md` at cycle end (mechanical); an APP-LEVEL scheduled
task `runner-cycle-report` (every 30 min, persists across sessions, its completion notifies the main session)
turns new events into a Korean report and acks the gate; the main session relays it verbatim and calls
PushNotification. `report_gate` remains the floor when the user speaks first.

On 2026-09-18 a firefighter cycle succeeded and the runner then stopped for a re-plan; the user learned both only
by asking ("우선 나한테 알려줘야지"). On 2026-09-23 it happened again: the runner ended a cycle at 02:38 and the chat
said nothing until the user asked at 03:19. The user's ruling:

> "30분 간격으로 진행상황 보고하는거, 그리고 사이클 종료시마다 보고하는 걸 안하고있네. 훅으로 안걸려있음? 그러면
> 훅으로 넣어야함"

A ScheduleWakeup I had set for the heartbeat never fired, and the cycle-end report existed only as a rule I
remembered. Both are now mechanical, and that is the standing expectation for any unattended run.

## How I apply it

- **2026-09-28: the scheduled task FAILED for a third reason** — its prompt hard-coded the OLD main session id, and
  `send_message` was blocked inside scheduled runs, so cycles 110–113 were never delivered; the user asked "러너
  리포트는 어디로 갔음". Whenever a NEW main chat session takes over the runner, update the task's target session id
  (`update_scheduled_task`, prompt) in the same turn, and keep `mcp__ccd_session_mgmt__send_message` in the project
  allow list. Check a real delivery after the next cycle end instead of trusting "succeeded" run statuses.
- **Same day, after that fix also failed** (send_message still refused inside scheduled runs; completion
  notifications never arrived): the scheduled task is PAUSED and the main chat keeps a backgrounded waiter running —
  `py tools/bgrun.py --max-min 35 --log tools/bench/wait_runner_event.log -- py -u tools/wait_runner_event.py
  --max-min 30`. Its exit (new runner event or 30-min tick) wakes the chat; report, `report_gate.py --ack`, and start
  the next waiter in the same turn. Never let the chain lapse while a runner is alive.

- **2026-09-25: the session cron (CronCreate) FAILED TOO** — a `29,59 * * * *` job existed all afternoon and never
  fired once between 13:29 and 18:51 (it only fires "while the REPL is idle", which this desktop session apparently
  never was); the user found out by asking ("자동 리포트 훅이 작동 안하는것같음"). Third failure of an
  in-session timer (ScheduleWakeup 09-23, cron 09-25). **Never rely on CronCreate/ScheduleWakeup for the heartbeat
  again.** Use the app-level scheduled task (`mcp__scheduled-tasks__create_scheduled_task`, runs as its own session
  even while this one is busy) or a runner-side reporter cell; and the report_gate hook remains the floor.
- **(superseded) Whenever the cycle runner is started from an interactive session, create a session cron (CronCreate, every
  30 min, e.g. `7,37 * * * *`) in the same turn** whose prompt reads the runner log and reports: which cycle is
  running and since when, the latest diagnostic/review/build result, whether the runner is alive. Delete it when
  the runner log shows RUNNER STOP and BGRUN END.
- **`tools/hooks/report_gate.py`** is registered as a Stop hook and a UserPromptSubmit hook in
  `.claude/settings.json`. It compares the `CYCLE n |` / `RUNNER STOP |` / `BGRUN END` lines of the newest
  `tools/bench/cycle_runner_main_*.log` against `tools/bench/report_ack.json`; an unacknowledged line blocks the
  turn from ending (exit 2) until the chat reports it and runs `py tools/hooks/report_gate.py --ack`. Runner cells
  are exempt through the `CYCLE_SESSION=1` env var the runner sets.
- A cycle-end report says: cycle number, exit code, cost, what the cycle delivered (files, gate counts), what
  `## NEXT` now says, and whether the runner continues or stopped and why.
- Never rely on a wake-up I scheduled once or on remembering to check; if a reporting rule is broken twice it
  moves into a hook, like every other procedural rule in this project.
