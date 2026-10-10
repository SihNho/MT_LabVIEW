---
name: graceful-shutdown-finish-the-cycle
description: "The user's 2026-09-21 rule — a time cap on the unattended cycle runner must never kill work mid-cycle; the runner finishes the cycle in progress (retrospective, STATUS NEXT) and then exits, so the next cycle starts from a consistent state"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: b5d0cc76-fda8-4724-8899-5a019fc98595
  modified: 2026-09-21T03:00:43.750Z
type: decision
status: in-force
date: 2026-09-21
source: memory/graceful_shutdown_finish_the_cycle.md
---

# A deadline ends the runner between cycles, never in the middle of one

On 2026-09-21 the process-level deadline that wraps the cycle runner (`bgrun.py --max-min 600`) fired while a
cycle was 17 minutes in. It killed the judgement session and its sub-processes outright, left a failing log with no
review, no retrospective and no STATUS NEXT, and the next launch was then refused by the project's own gates
because of exactly that debris. The user's ruling:

> *"강제 종료에 대한 규칙은 바꿔야겠는데? 그냥 셧다운 하지 말고 진행 작업들 마무리하고 종료하는 방향으로.
> 그래야 다음 싸이클에 정상적으로 작동하지."*

## How I apply it

- **The runner carries its own soft budget** (`cycle_runner.py --budget-min`, default 480 min), checked only
  BETWEEN cycles. Once it is exceeded no new cycle is started, but the cycle already running always finishes:
  its retrospective lands, STATUS NEXT is written, git is committed, and only then does the runner exit with a
  `RUNNER STOP | graceful` line.
- **The hard process cap is the last resort, not the schedule.** When the runner is launched under `bgrun`, its
  `--max-min` must be set comfortably above the soft budget plus the longest plausible cycle (about three
  hours), so it fires only if something is truly hung.
- **Relaunching after a graceful stop is routine** and needs no repair; relaunching after a hard kill is what
  produced the deadlock, and is the situation this rule exists to avoid.
- The same principle applies to any other unattended loop I build here: an orderly stop that leaves the
  hand-off state consistent is worth more than a prompt one.
