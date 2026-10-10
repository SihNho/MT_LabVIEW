---
name: plan-everything-possible-before-the-rig
description: "The user's 2026-09-16 standing instruction — until they say otherwise, every plan must cover ALL work achievable right up to rig reassembly, not just the next narrow prep step"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1c79eb01-7150-4a78-9689-e6d4f34f7800
  modified: 2026-09-16T03:36:54.073Z
type: decision
status: in-force
date: 2026-09-16
source: memory/plan_everything_possible_before_the_rig.md
---

# Plan everything that can be done before the rig goes back together

On 2026-09-16 I presented cycle 10 as a measurement cycle — run an existing recipe, finish the diagram hierarchy,
one scoped latency measurement — and asked whether to run it. The user rejected the framing outright:

> *"사이클 10 계획은 평행루프 준비작업만 있는 것 같은데, 내가 명시하기 전까지는 rig 조립 직전까지 할 수 있는
> 모든 플랜이 필요함. 전체 플랜 및 세부 플랜 다시 준비할 것."*

The instruction is about **scope**, and the scoping words widen rather than narrow: *until I say otherwise*, and
*every plan that can be done*. So a cycle plan is not "the next safe increment" — it is **everything the
disassembled-rig window permits**, planned at both levels: a master plan and the detailed sub-plans under it.

## Why the narrow framing was wrong here

Two things made "prep work only" look reasonable and it was not:

- The rig being **disassembled is the window, not the obstacle.** Motor operation is permitted in this window
  (the user reversed the motor ban for exactly this reason), so serial latency, motor read cost and autofocus
  behaviour are available *now* and stop being available the moment the rig is reassembled.
- "Needs the rig" had been applied far too broadly. Live camera acquisition, for instance, does not need beads —
  only a working camera — so the acceptance test that turns a replay artefact into something runnable had been
  parked in a future session for no measured reason.

The general error: treating *any* hardware dependency as one undifferentiated "rig session". Separate what needs
**beads and a mounted sample** from what needs only **motors, serial or the camera**, and schedule the second group
into the open window.

## How to apply it

When asked to plan, enumerate the full reachable set first and only then decide ordering. Do not present a plan
whose implicit boundary is "this is the part I was confident about" — that boundary is invisible to the user and
reads as the whole scope. If something genuinely cannot be done before reassembly, say which physical thing is
missing (beads, a mounted channel), not just "needs the rig".

This is a standing instruction, not a one-cycle preference: it holds **until the user announces reassembly**, which
is the same announcement that closes the hardware-permission window.
