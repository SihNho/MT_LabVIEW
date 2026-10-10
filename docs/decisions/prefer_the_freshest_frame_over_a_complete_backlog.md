---
name: prefer-the-freshest-frame-over-a-complete-backlog
description: "The user's 2026-09-15 overload decision — when tracking falls behind, discard the backlog and take the newest frame, because a stale sample corrupts the time series while an explicit gap does not"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1c79eb01-7150-4a78-9689-e6d4f34f7800
  modified: 2026-09-28T06:41:34.773Z
type: decision
status: in-force
date: 2026-09-28
source: memory/prefer_the_freshest_frame_over_a_complete_backlog.md
---

# When tracking falls behind, throw the backlog away and take the newest frame

**2026-09-28: I re-asked this as a new decision (pool "full ⇒ skip the newest read" vs latest-wins) and the user
pointed back here: "위에 프레임 관련해서는 내가 말한 내용이 있음. 다시 찾아봐. 우선순위가 있는데".** The priority order is
(1) no corruption (image and buffer number change together, consumer verifies), (2) latest-wins, (3) the sequential
fallback. Before putting any frame-handling question to the user, search this memory and `docs/decisions.md` first;
`docs/d1-build-plan.md` §9's "full Q_work ⇒ skip this read" contradicts rule (2) and must not be treated as decided.

Asked what the parallel design should do when the image pool runs out — block acquisition, or drop frames — the
user chose neither of the framings I offered and gave the principle instead:

> *"큐를 버리고 새로 들어오는 프레임을 읽는 것이 가장 바람직함. 이는 시계열 데이터의 엄밀성을 위함."*

Discard the queue, read the incoming frame. The reason is the **rigor of the time series**: a tracking result
computed from a frame that is already old is a sample attached to the wrong moment, and that is worse than no
sample at all. A gap is honest and can be handled downstream; a late sample silently distorts the time base.
(My own inference, stated as one: this matters even more because the rig runs force clamping, which is a feedback
loop — feeding it a stale bead position would not merely mislabel data, it would act on it. Not the user's stated
reason, and not verified.)

## What this settles in the design

- **Acquisition → tracking is LOSSY and LATEST-WINS.** When the image pool is exhausted, the oldest unprocessed
  frame is abandoned and its slot reused for the incoming one. Acquisition is never blocked.
- **Tracking → file writer stays LOSSLESS and FIFO.** A result that was actually computed must never be dropped or
  reordered. The two links have opposite policies on purpose.
- **Every result carries its frame number**, so the gaps are explicit in the saved trace rather than implied by a
  row count. This coincides with what a plan review independently demanded: an immutable, frame-identified result
  message as the tracking seam.
- It also revises `docs/restructure-plan-4.6.md`, whose transport table called the acquisition → tracking link
  "lossless **and** order-preserving". Order-preserving still holds; lossless does not.

## The invariant the user named, and the fallback they authorised (same day, after peer review)

Both plan reviewers found that evict-oldest is a different ownership state machine from the reviewed design, and
that it admits a specific corruption: a descriptor `{frame=N, slot=S}` can reach tracking after slot S has been
refilled, so the kernel computes a result **labelled N from another frame's pixels** — worse than a gap, and
invisible on the fixture, where nothing ever overflows. The user went straight to the invariant:

> *"2번의 프레임 로스가 치명적이지 않기 위해서는 Buffer number가 갱신되어야 한다는 점인데, 만약 buffer number
> 갱신이 어려운 상황인데 IMAQ 메모리만 바뀌었다 라고 한다면 정말 데이터 커럽션으로 봐야할듯."*

So the acceptance rule is: **the image memory and its buffer number must change together, and the consumer must
verify them.** A gap is fine; an image whose number does not match its pixels is not. Usefully, the identity
already exists in the original — `get buff image-lost frames.vi` carries `Buffer to extract`, `current image
number` and `Missed frames?`, paired with `LastBufferNumber` on the case that feeds it.

**And the authorised fallback, which matters more than the mechanism:**

> *"2번이 문제가 된다면 Acquisition 및 추적은 동일 루프에 두고 시퀀셜 처리를 하는 것도 괜찮을 것 같음."*

If the handoff cannot be made provably safe, **acquisition and tracking may stay together in one sequential
loop.** That is not a failure of the project: the parallelisation the requirement asks for is mostly about getting
motor reading, the scheduler, saving and display *out* of the frame loop, and none of that depends on splitting
acquisition from tracking. Do not treat acquisition-parallel-to-tracking as mandatory.

## Why this is not a violation of "never change the original's computation"

The original is sequential and already loses frames when an iteration runs long — the subVI in its frame loop is
literally named `get buff image-lost frames.vi`. So taking the newest buffer and recording what was missed is what
the original does; the parallel version keeps that behaviour and merely makes the loss explicit and counted. On the
fixture there is no overflow at all (the pace is ours), so replay stays bit-identical and the acceptance test is
unaffected.
