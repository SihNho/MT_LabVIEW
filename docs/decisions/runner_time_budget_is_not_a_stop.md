---
name: runner-routine-end-starts-the-next-runner
description: "The user's 2026-09-28 rule — when a cycle runner ends ROUTINELY (its time budget or cycle count ran out), the NEXT runner must start automatically; do not answer this by enlarging the budget. Enforced by tools/runner_supervisor.py."
metadata:
  node_type: memory
  pinned: false
  originSessionId: a5bcbf27-1eb1-4a4c-b234-98f27fbcff51
  modified: 2026-09-27T18:07:44.163Z
type: decision
status: in-force
date: 2026-09-27
source: memory/runner_time_budget_is_not_a_stop.md
---

# A routine runner end starts the next runner — automatically (user, 2026-09-28)

On 2026-09-27 the runner (`--cycles 8 --budget-min 480`) finished cycles 110–113 and ended at 02:20 on its time
budget; nothing restarted it and the user found it idle at 03:0x ("러너가 멈추면 자동으로 새 러너 돌려야하는거
아니야?"). I first answered by relaunching with a 48-hour budget, and the user corrected me: "러너가 멈추면 다음 러너를
돌리라니깐 시간 한도를 늘려버렸네?" — the budget is a rotation (a fresh runner every 8 h), and what they wanted was
the hand-over, not a longer runner.

## How I apply it

- The supervisor `tools/runner_supervisor.py` (under `bgrun --max-min 10080`, log `tools/bench/runner_supervisor.log`)
  waits for the running runner, and when its last `RUNNER STOP` is the graceful budget stop or `--cycles N
  exhausted`, launches the next one with `--cycles 0 --budget-min 480` under `bgrun --max-min 720`.
- Every other end is a real stop and the supervisor exits: STATUS STOP marker, repeated failure, usage limit,
  firefighter ceiling, pending decision, crash/TIMEOUT. A routine end after < 30 min is treated as a fault.
- Whenever I start a runner from the chat, make sure a supervisor is running too; never "fix" idle time by
  enlarging `--budget-min`.
- When the user asks for something, implement the mechanism they named; if I read it differently, ask in one line
  rather than substituting my own remedy.
