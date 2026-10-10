---
name: consecutive-runs-wait-by-condition
description: "The user's 2026-09-26 requirement for measurement drivers that run several VIs back to back — after each run ends, wait long enough for the machine to settle but not longer; implement as a measured settle condition with a cap, never a fixed long sleep"
metadata:
  pinned: false
type: decision
status: in-force
date: 2026-09-26
source: memory/consecutive_runs_wait_by_condition.md
---

# Between consecutive real runs, wait by condition: enough, but not too long (user, 2026-09-26)

While discussing why measurement cycles take so long (each 120 s run costs ~7 min because LabVIEW is restarted
and beads re-picked for every run), the user understood the driver as "run, stop, run, stop, …" and added:

> "코드 종료 이후 충분히 그러나 너무 길지는 않게 기달려주는 과정이 필요하겠음"

Starting the next run before the camera has stopped acquiring and the VI has released its resources would mix
shutdown effects into the next run's frame-loss count; a fixed long sleep would put the fixed cost back.

## How I apply it

- A driver that runs several VIs in one LabVIEW instance (or restarts between them) waits after each run on a
  MEASURED settle condition polled about once a second: VI execution state idle, camera session closed (IMAQdx
  session gone / acquisition stopped), LabVIEW handle count stable across two consecutive reads.
- The wait has a cap (start ~30 s). Reaching the cap invalidates the next run's numbers: log it as a non-result,
  restart LabVIEW, and rerun that run from the beginning.
- The measured settle time is written into the run's json so the cap and the condition can be tuned from data,
  the same way the retry cap is.
