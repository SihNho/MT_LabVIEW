---
name: locals-not-queues-focus-loop-own-clock
description: "The user's 2026-09-25 design rulings — loop-to-loop control signals go by local variables (latest value), never by queues (queues couple the loops); the ASI autofocus loop runs on its own clock, not in step with frame acquisition; autofocus means \"move when the first-clicked reference bead's z leaves its setpoint by more than a distance threshold\", the original's every-N-frames gate was only serial rate-limiting, and 'Frame rate' is never set to 1"
metadata:
  node_type: memory
  pinned: false
  originSessionId: 1e5293f3-09a7-4b72-9393-fcba8dd55703
  modified: 2026-09-25T10:27:09.550Z
type: decision
status: in-force
date: 2026-09-25
source: memory/locals_not_queues_focus_loop_own_clock.md
---

# Locals, not queues; the focus loop has its own clock (user, 2026-09-25)

When I proposed a queue to fix the three autofocus limits of the split VI, the user answered:

> "큐를 넣어버린다면 두 루프 사이에 상관관계가 생겨버린다는 것 같은데, 그런 리스크를 감당할 필요가 있는지 모르겠음.
> 그냥 Boolean 값 및 타겟 값을 local variable로 전달하는게 더 좋지 않을지? ASI autofocus 루프는 애초에 frame
> acquisition 루프와 동시에 돌 필요가 없을듯."
> "초점 루프는 … 특정 bead의 위치 값이 셋팅값과 달라질 때 발동하는걸로 알고 있음. 정확하게 같을 수는 없으니 distance
> threshold가 있음" · "첫 클릭한 reference bead 일거임 (처음 reference bead, 나머지 experimental bead (=magnetic bead))"
> · "'Frame rate' 보통 1로는 두지 않았던 것 같음"

## How I apply it

- Control and trigger signals between loops (focus requests, setpoints, enables, counters) are LOCAL variables the
  reader polls for the latest value. Queues only for lossless data streams (the file writer). Never detect an edge
  on a polled boolean; publish a comparable value instead.
- The focus loop runs on its own time cadence and decides from the reference bead's z vs setpoint with the
  original's threshold and step; the frame loop only publishes values. This is a scheduling change (allowed by
  rule 1a); the deviation test and step amount are copied exactly.
- The first clicked bead is the reference (non-magnetic) bead; the rest are magnetic experimental beads.
- The user's memory of a THRESHOLD trigger did not match the code: the offline read of Case #10407 (card chat-F1,
  `docs/autofocus-case-10407.md`) shows a proportional correction every firing, `clamp(idx_bead0 − slices/2 +
  'Focus Deviation from the Center', ±0.2)`, with the "deviation" control an additive offset and no compare. Rule 1a
  decides: copy the code; a threshold would be a new feature for the user to decide separately. When the user's
  recollection of a mechanism and the map disagree, read the map first and tell them plainly.
- Recorded as CLAUDE.md 1c'' and Pre-decided 148; enforced by `stage_prerun.py control_path_lint`.
