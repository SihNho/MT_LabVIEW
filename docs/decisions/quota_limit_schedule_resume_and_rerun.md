---
name: quota-limit-schedule-resume-and-rerun
description: "When the usage limit is about to be hit (~95%) or is hit during unattended work, schedule a wake-up 2 minutes after the quota renewal time and continue the same work; any benchmark interrupted mid-run is rerun from scratch, never resumed"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-14T00:44:16.783Z
type: decision
status: in-force
date: 2026-09-14
source: memory/quota_limit_schedule_resume_and_rerun.md
---

# Usage limit during unattended work: schedule a wake-up after renewal, then continue — and rerun interrupted benchmarks

Standing instruction from the user, 2026-09-04, given while an overnight benchmark run was being
prepared: *"만약 중간에 이용한도가 꽉 차면 (95% 초과할 것 같으면) 리뉴얼 시점보다 2분 이후로 일정
예약 걸어두고 하던 작업 이어가도록. (벤치 중간에 멈췄다면 해당 벤치는 다시 돌리도록)"*

So, whenever long autonomous work (benchmarks, batch builds) is running:

- **Watch the usage limit.** If it looks like the session will pass ~95 % of its quota, or a
  rate-limit / usage-limit error arrives, do not stop and wait for the user and do not just end
  the turn. Read the renewal time from the limit message and **schedule a wake-up 2 minutes after
  the renewal time** (ScheduleWakeup / a cron-style scheduled task — whichever the harness offers),
  then continue exactly the work that was in progress. (Re-confirmed 2026-09-14: the user first said
  "at the refresh instant", then corrected themselves — *"아 미안 이미 있었구나 갱신 +2 분으로 해줘"* — so
  +2 minutes stands.) ScheduleWakeup reaches at most one hour ahead, so a 5-hour window needs a
  cron-style scheduled task carrying the loop prompt.
- **An interrupted benchmark is invalid.** A benchmark cell or run that was cut off mid-way is
  **rerun from the beginning** after the wake-up, never continued from a partial state — the
  numbers of a half-run (tokens, seconds, pass counts) are not comparable with complete runs.
  Record the interrupted attempt as a non-result (what was interrupted, when) rather than
  discarding it.
- Keep STATUS.md current before the pause so the resumed session knows which run to repeat.

The same message also carried a second standing point: the user does **not** want to be asked to
send a message merely so the harness can register something (e.g. a fresh subagent definition):
*"자동화는 불가능한거야? 기다리지 말고"* — find the scripted route (a CLI subprocess, a scheduled
task, a different tool) instead of waiting on a user turn.
