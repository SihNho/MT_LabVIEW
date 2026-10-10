---
name: camera-free-runs-never-gate-it
description: "The camera runs its own acquisition loop independently of the PC by design, because PC-driven frame control is not trusted — so no software mechanism may ever throttle, block or otherwise affect frame acquisition"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 1c79eb01-7150-4a78-9689-e6d4f34f7800
  modified: 2026-09-15T08:42:54.078Z
type: decision
status: in-force
date: 2026-09-15
source: memory/camera_free_runs_never_gate_it.md
---

# The camera free-runs. Nothing we build may touch its acquisition.

Stated by the user on 2026-09-15, as a hard constraint on the parallel design:

> *"카메라는 기본적으로 자신의 루프를 컴퓨터와 독립적으로 돌아야 하며 그렇게 돌고 있음. 컴퓨터를 통한 카메라
> 프레임 컨트롤을 신뢰할 수 없기 때문임. 따라서 Lossy Enqueue Element 혹은 기타 다른 어떠한 방법도 카메라 frame
> acquisition에 영향을 주어서는 안됨."*

The camera acquires on its own clock into the driver's ring buffer. The PC is a **reader**, never a gate. This is
deliberate: PC-side frame control is not trusted on this rig, so a design that can stall, pace or otherwise
influence acquisition is wrong even if it never actually stalls in testing.

## What this settles about the overload question

It removes the problem rather than solving it. I had been designing an image pool with eviction — which oldest
frame to discard, how to recover its slot atomically, whether `Lossy Enqueue Element` is needed. **The driver's
ring buffer already is that queue, and it already implements latest-wins**: if the software falls behind, the
camera overwrites the oldest buffers and the buffer numbers jump. Asking the driver for the newest available
buffer, rather than the next sequential one, gets the user's "discard the backlog, read the newest frame" for free,
with the gap reported as a jump in buffer number.

So the design rule is: **read out, never gate.** Our loops may only choose *which* buffer to read and may drop
their own work; they may never make acquisition wait on us. Any mechanism whose failure mode is "the producer
blocks" is disqualified at the acquisition boundary — including a plain bounded `Enqueue`, which blocks when full.
That applies to the acquisition boundary only; a queue between our own loops (tracking to file writer) is fine.

## The buffer number is the CLOCK, not just an identity

The user added the fact that settles the sampling question (2026-09-15):

> *"시간 간격은 컴퓨터 루프와는 별개로 프레임이 같다면 동일함. 카메라 루프의 acquisition 정보에 frame rate을
> 별도의 하드웨어로 통제하기 때문. 그러니 데이터 전달에서 생기는 시간 불균일은 크게 중요하지 않음."*

The frame rate is set by hardware, independently of the PC loop, so **frame N always happened at N / framerate**.
Delivery jitter on our side changes when we *see* a frame, never when it was *taken*. The consequence matters for
analysis: skipping frames does not produce irregularly sampled data — it produces a **uniform grid with holes**,
which spectral analysis handles far more easily than true irregular sampling. So do not design around "even
spacing" of the processing loop, and do not timestamp results in software: **record the buffer number and let it
be the time axis.** (I had raised uniform spacing as an argument for `Buffer Number Mode = Next`; this retires it.)

## Why it also keeps the data honest

The buffer number is what makes a gap legible, and it comes from the camera side, not from us. Combined with the
user's other ruling — that the pixels and the buffer number must change together or it is corruption — the
consumer's job is to read a buffer, carry its number with it, and verify the pair before using the result.
