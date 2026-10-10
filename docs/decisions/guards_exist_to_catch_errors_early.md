---
name: guards-exist-to-catch-errors-early
description: "The user's 2026-10-04 framing — a new hook or check exists mainly to catch errors at the earliest possible moment (when a script/plan is written or launched, before LabVIEW) and so cut wasted time; proposals must lead with that, not with false-positive cleanup"
metadata:
  node_type: memory
  pinned: false
  originSessionId: b607b493-a66f-4081-b122-a7a95d2c2a67
  modified: 2026-10-03T23:46:33.511Z
type: decision
status: in-force
date: 2026-10-03
source: memory/guards_exist_to_catch_errors_early.md
---

On 2026-10-04 I proposed mandatory header flags in scripts (declared labview/hardware scope read by the hooks) and
described it mostly as a fix for hooks that wrongly blocked good commands. The user corrected the framing: "이번 훅을
넣는 가장 큰 이유는 초장에 에러 발생을 극소화하여 시간 낭비를 최소화하는게 목적임. 그에대한 내용이 잘 안보여".

The measured basis: in cycles 142-143 about 75-80 of 175 minutes went to failed work orders, and most of the
non-LabVIEW part (format errors, stale file copies, plan addresses that do not match the real graph, script crashes
on data shape) was knowable within seconds of the file being written.

## How I apply it

- When proposing any guard, check or hook, state first WHICH errors it catches, AT WHICH MOMENT (file written ->
  launch -> LabVIEW), and how many minutes per cycle that saves, using the cycle records. Cleanup of false blocks is
  a secondary benefit.
- Prefer the earliest checkpoint: a check that can run when the agent writes the file (and reports back in the same
  turn) beats one at launch, which beats one inside LabVIEW.
- Name what the guard cannot catch (e.g. LabVIEW scripting-function defects that only a scratch run reveals).
