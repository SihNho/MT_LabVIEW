---
name: wait-for-start-after-design-discussion
description: "The user's 2026-09-28 correction — when a design discussion reaches agreement, record it but do NOT relaunch the runner or push the direction into STATUS/NEXT until the user explicitly says start (\"내가 시작 시키면 진행하도록\")"
metadata:
  node_type: memory
  pinned: false
  originSessionId: a5bcbf27-1eb1-4a4c-b234-98f27fbcff51
  modified: 2026-09-28T07:23:03.560Z
type: decision
status: in-force
date: 2026-09-28
source: memory/wait_for_start_after_design_discussion.md
---

# Agreement in a discussion is not a start signal (user, 2026-09-28)

During the frame-handoff discussion (pool vs option C vs the user's ring-buffer sketch) the user answered my four
points, and I immediately began writing the design into the docs and announced a runner relaunch. The user stopped
me: "멈춰" / "내가 시작 시키면 진행하도록".

## How I apply it

- When a discussion converges, summarise the agreed design and STOP. Recording it in a scratch/design note is fine
  only if said so; changing STATUS, next.json, beds, or relaunching the runner waits for an explicit start
  ("진행해", "시작").
- This is the same rule as CLAUDE.md §3 "start/stop is explicit, never inferred", applied to the end of a design
  discussion, where it is easiest to forget. It does not override "approved means do it now" for proposals the user
  explicitly approves with words like "좋아, 진행" — agreement on points of a design is not that.
