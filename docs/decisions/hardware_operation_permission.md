---
name: hardware-operation-permission
description: "Hardware access is governed by the RIG STATE, in three levels — disassembled (everything, ASI included), assembled (camera only), experiment running (nothing) — and the ASI piezo is never given its own separate rule"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 6564f349-1de2-4ed3-9a30-327eb21b9046
  modified: 2026-09-16T04:54:15.334Z
type: decision
status: in-force
date: 2026-09-16
source: memory/hardware_operation_permission.md
---

# Hardware access follows the rig's state, and the ASI is not a special case

**The user replaced the earlier permission rules with a state machine on 2026-09-16:**

> *"모터 접근 및 카메라 접근을 '리그 분해 / 리그 조립 / 실험중' 상태에 따라 다르게 두는게 맞는듯.
> 리그 분해 → 모든 모터 및 카메라 접근 허용. 리그 조립 → 카메라 접근만 허용. 실험중 → 모든 모터 및 카메라
> 접근 불가. 이는 Piezo stage인 ASI 컨트롤러를 포함하는 내용 (ASI와 다른 모터를 구분하여 권한 두지 말것)."*

| rig state | motors (PI translation, rotor, magnet) | **ASI piezo stage** | camera |
|---|---|---|---|
| **분해 — disassembled** | allowed | **allowed, same as any motor** | allowed |
| **조립 — assembled** | forbidden | forbidden | allowed |
| **실험중 — experiment running** | forbidden | forbidden | **forbidden** |

## The part that is a correction, not just a table

**Stop writing separate rules for the ASI piezo.** Until this message the project treated it as "the one
instrument that can physically break the rig" and carved it out of every hardware permission — I had just written
that carve-out into a plan document as a hard blocker. The user's instruction is explicit: *do not distinguish the
ASI from the other motors when assigning permission.* It rises and falls with the rest of the hardware according
to the rig state, and nothing else.

That does not make collisions impossible; it makes the **rig state**, rather than the instrument's identity, the
thing that decides. When the rig is apart there is nothing to collide with, which is why the distinction stopped
earning its keep.

## How the state is known

**Only the user announces a state change**, and the announcement is the boundary — never infer a transition from
silence, from a quiet period, or from how long the work has run. Reassembly costs the user 2+ hours of sample
prep, so "disassembled" is a window that is cheap now and expensive later: hardware measurements belong in it, and
deferring them to a supervised session is backwards. Do not re-request permission per incident inside a state the
user has already declared (*"Don't need to hassle around me before I tell you."*, 2026-09-16).

## What this supersedes

- The 2026-08-27 blanket motor ban.
- The 2026-09-13 "full hardware permission, conditioned on the piezo being detached".
- The standing "never actuate the ASI piezo stage" rule, which was pinned and is now retired — see
  `hardware_never_operate_asi_piezo_stage.md`, kept only as a pointer.
