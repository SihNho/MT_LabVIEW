---
name: judge-changes-on-two-axes-speed-and-cost
description: "The user's 2026-09-28 instruction — when judging whether a process change helped, report project SPEED (deliverables per wall-clock hour) and COST (dollars per deliverable, and spend rate) as two separate axes and read them together as 2D data, never folded into one verdict"
metadata:
  node_type: memory
  pinned: false
  originSessionId: a5bcbf27-1eb1-4a4c-b234-98f27fbcff51
  modified: 2026-09-28T06:36:46.955Z
type: decision
status: in-force
date: 2026-09-28
source: memory/judge_changes_on_two_axes_speed_and_cost.md
---

# Speed and cost are two axes — read changes as 2D data (user, 2026-09-28)

After the acceleration items were applied I answered "did it speed up?" with a table that mixed time and cost into
one "faster, but cost not lower" verdict. The user corrected: "비용은 따로, 프로젝트 전반적인 진행 속도 따로. 그래서 2D
데이터로 해석해야함."

## How I apply it

- Axis 1, SPEED: saved build steps (deliverables) per wall-clock hour of runner time, including cycles that
  delivered nothing. Axis 2, COST: dollars per saved build step, plus the spend rate in dollars per hour.
- Report each period (before / after a change, or per cycle) as a point on both axes, and state the direction of the
  move in 2D: faster-and-cheaper, faster-but-dearer, etc. A trade (speed bought with parallel spend) is named as a
  trade, not as a gain.
- Say which cycles are missing a number (e.g. an orphaned cycle with no cost line) instead of silently dropping them,
  and label small samples as small.
