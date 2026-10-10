---
name: stop-runner-at-weekly-90
description: "The user's 2026-10-02 instruction — stop the cycle runner (gracefully) when weekly all-models usage reaches 90 %; enforced by tools/usage_stop_watch.py, which writes the STATUS STOP line itself"
metadata:
  node_type: memory
  pinned: false
  originSessionId: b607b493-a66f-4081-b122-a7a95d2c2a67
  modified: 2026-10-02T03:58:41.360Z
type: decision
status: in-force
date: 2026-10-02
source: memory/stop_runner_at_weekly_90.md
---

# Stop the runner at 90 % weekly usage (user, 2026-10-02)

> "주간 사용량 90퍼센트 되면 사이클 진행 멈춰줘"

This is a user-set limit, not one of the self-imposed usage gates retired on 2026-09-29 (those stay retired). It was
given at 80 % weekly with 2 days 18 hours to the reset, while the user was remote.

## How I apply it

- Mechanical, not by my attention: `tools/usage_stop_watch.py` (bgrun, log `logs_usage_stop_watch.log` at the project
  root) probes every 10 min with one tiny haiku `claude -p` call and reads `rate_limit_event` seven_day utilization;
  at >= 0.90 it inserts a graceful `STOP` line at the top of STATUS.md and exits. The runner then finishes the cycle in
  progress (so usage can overshoot by a few %), closes LabVIEW, releases motor limits and exits; the supervisor does
  not relaunch on a real stop.
- Restart only when the user says so (normally after the weekly reset). When restarting, start the watcher again if
  the user still wants the limit.
- Cloud-session credit work does not count toward the weekly window.
