---
type: archive
status: historical
date: 2026-09-15
tags: [status-overflow, cycle-7, reseed]
---

# Cycle 7's reseed measurements, and the NEXT list the outcome review superseded

Moved out of `STATUS.md` on 2026-09-15 when it passed 170 lines (rule 4: push narrative down a layer immediately).
The measurements below are still TRUE and still the basis of the reseed slice — they live in
`docs/stage2-assembly-step-e.md`, which is the active document for them. What is historical is the *plan* that
followed from them.

## Measured for the reseed logic (identity-checked; main VI byte-identical in every run)

- **Selector feeders:** `Less?.y` <- constant **I32 0** (so the lost-bead test is
  `min(pos in cal image out) < 0`); `And.y` <- control **`Auto-Reset`**; `Or.y` <- control **`Reset Tracking`**;
  `Equal?.y` <- control **`Limit of Program`**. Three of four are runtime controls, so the rebuild must take them
  as inputs (rule 1a).
- **Case #5540 has two frames**, both pure pass-throughs: **5582** forwards the left shift registers (previous
  state), **5592** forwards the loop's own initialisers (the calibration state). Both outputs feed **SubVI 5058 =
  `Track N beads four-fold over-kernel-v3.vi`** — the case selects the KERNEL'S INPUT, correcting an earlier note
  that placed it after the kernel.
- **Design (peer-reviewed):** a stateless `ReseedMux.vi` from two `Select` primitives, with the selector expression
  and the `# of Auto-Reset` counter evaluated once per frame at loop level; the periodic term stays in.

## What `min value` actually is (explained for the user, 2026-09-15)

Calibration photographs each bead at a series of heights, making a stack of images. During tracking, the bead's
current appearance is matched against that stack, and **the index of the closest slice is the bead's z**. So
`pos in cal image out` is the list of those indices, one per bead, and `min value` is the smallest index across all
beads. A negative value means some bead matched nothing in its calibration stack — that bead is lost. This is the
same event the user describes operationally: on a long run a bead comes unstuck and flies off.

## The NEXT list as it stood before the first outcome review

Superseded the same afternoon; items 1 and 2 were named as work to SKIP.

0. Cycle 7's retrospective done and annotated, so the cycle gate was open. Two standing corrections it left: ask
   peers to REFUTE (never "BRIEF CONFIRM"), and fill `why asked` / `verdict` in archived reviews.
1. Build `VI.Get Errors` (method 452) as an op — the reader that would end inferred broken-VI diagnoses.
   (`OpCaseFrames_v0`'s last failure: two property nodes created before either was wired, so the VI was broken at
   gate A; the recipe now builds one node at a time.)
2. Frame polarity: finish `OpCaseFrames_v0` (`Frames[]` 6363801, `Frame Names` 6365002) — structural confirmation
   of what the fixture already establishes functionally.
3. Census A — Case #10445: read its frames before collapsing it into an `Or`. **Still needed**, as part of the
   reseed slice rather than as its own cycle.
4. Build `ReseedMux.vi` + the loop-level selector, integrate into `Track_v6_CPU_queue_v0`, accept on all 10,043
   fixture frames exactly. Then live camera.

The replacement is in STATUS.md's LIVE NEXT: measure the seam first, then the minimum reseed, then live
acquisition, then the minimum scheduler/motor/save path that produces one real saved trace.
