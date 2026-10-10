---
name: fable-firefighter-cycle-on-trigger
description: "The user's 2026-09-18 decision — when the runner sees the same step blocked repeatedly, a \"firefighter\" cycle is fired automatically with Fable (low effort) in place of Opus max, and it must be able to EXECUTE, not only judge"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: b5d0cc76-fda8-4724-8899-5a019fc98595
  modified: 2026-09-18T04:16:29.809Z
type: decision
status: in-force
date: 2026-09-18
source: memory/fable_firefighter_cycle_on_trigger.md
---

# When a step keeps failing, the next cycle is a Fable firefighter — fired by a trigger, not by a person

On 2026-09-18 the cycle runner (Opus, effort max, one fresh session per cycle) had been stuck on one component for
two days — the same recipe failing at the same place across consecutive cycles. The user proposed a "firefighter":

> *"기존 구조로 처리가 잘 안되는 부분은 Fable, low로 소방수 파견하는 건 어떻게 생각함?"*

and then sharpened it: judgement alone is not enough (*"단순히 판단만으로는 부족한게 아닌가"*). The choice was
between swapping the top model of the cycle to Fable, or dispatching an auxiliary Fable sub-session — and the
firefighter must fire automatically: *"트리거링 걸리면 발동하도록"*.

## What this fixes

- **The firefighter needs execution, not a memo.** An auxiliary sub-session that returns a diagnosis to an Opus
  session repeats the pattern that was failing. So the firefighter takes over a whole cycle (delegating, running,
  deciding, retrospective) with Fable at low effort, and the runner returns to Opus max afterwards.
- **Fired by a mechanical trigger**, read by the runner from its own records (the same step failing in two
  consecutive cycles), never by a session deciding it feels stuck and never by the user having to ask.
- **Repeating the same mistake counts too** (user, same day: *"동일 실수 반복하는 것도 판단 조건에 들어가야 할 것
  같은데?"*). A recipe renamed v1 → v2 that dies at the same gate is the same failure, so the trigger also
  compares the first failing gate line across cycles, and fires when a retrospective names
  `repeated-failure-class`. Counting only file names had let a rename reset the count to zero.
- **A ladder of two, then the user** (user, same day: *"Low로 첫번, 그 다음 middle로. 그래도 안되면 나한테 판단
  요청"*): the first firefighter cycle runs Fable at low effort; if the same recipe still fails, the next cycle
  is Fable at medium; if it fails again the runner stops and asks the user. There is never a third firefighter. This does not relax the standing "minimise Fable" cost rule — it is the one
  place the user chose to spend Fable, and only on trigger.
- The standing order "build no more process devices" still applies inside a firefighter cycle.
