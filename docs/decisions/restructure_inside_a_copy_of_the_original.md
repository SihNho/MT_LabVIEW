---
name: restructure-inside-a-copy-of-the-original
description: "The user's 2026-09-15 decision — do the seven-loop restructuring INSIDE a copy of the original VI rather than in an empty one, and order the loop splits by the measured frame budget, not by convenience"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1c79eb01-7150-4a78-9689-e6d4f34f7800
  modified: 2026-09-15T07:27:53.375Z
type: decision
status: in-force
date: 2026-09-15
source: memory/restructure_inside_a_copy_of_the_original.md
---

# Restructure inside a copy of the original, and split the loops in the measured order

On 2026-09-15 the user settled the strategy question that had been open since the project's first outcome review.
Two earlier candidates were both wrong, and the user's own objection is what produced the answer.

## What was rejected, and why

**"Replace only the acquisition/tracking hot path in a copy of the original."** This came from the outcome review,
which could read the documents but not the diagram. The user asked the question that killed it: *"A안은 모터
병렬화 포기한다는거 아니야?"* Measurement then showed the objection was right in substance and worse than feared —
the ASI serial subVI (#48) and the ten front-panel property nodes sit **outside** the kernel's slice, so a
hot-path-only swap leaves them in the frame loop, and `docs/camera-acquisition-facts.md` had already measured that
**kernel + one serial round trip is 5.06 ms of the 6.00 ms budget**, and that moving the serial read and the display
updates out is worth **~2.5 ms — the difference between 150 Hz and 200 Hz**. A hot-path-only change leaves exactly
the two things the measurement says to remove.

**"Rebuild the seven-loop top level fresh in an empty VI."** This had been the standing plan. It is not wrong, but
it throws away bead picking, calibration, the controls, the buttons and the established experiment workflow, all of
which have to be rebuilt before anything can be run at all — and after 22 days the project still had no runnable
experimental VI.

## The decision

**Do the restructuring inside a COPY of the original VI** (never the original itself — rule 1 is unchanged), and
split the loops in the order the frame budget dictates:

1. the tracking kernel into its own loop (the verified queue core already exists);
2. **the ASI serial read out of the frame loop** — half of the 2.5 ms;
3. **the front-panel/display updates out** — the other half;
4. scheduler and file writer.

Step 1 alone makes the VI runnable for an experiment; steps 2 and 3 are what actually buys 150 Hz -> 200 Hz.

## Why working inside a copy is feasible, measured rather than assumed

`tools/bench/slice_cutset_acq_track.py`, computed offline from the existing wire-graph JSON: the kernel's slice is
**22 of the frame loop's 75 nodes**; **21 nets** cross from it to sibling nodes; **0 Locals, 0 Globals, 0 Feedback
nodes** anywhere inside; the Event Structure and the ASI focus subVI are both **outside** the slice. The one
property node inside is the `min value` race, which the user separately decided to replace with direct dataflow.
The earlier "77 crossings" figure was the wrong metric on the wrong region and is void.

Note also what the main VI already has: three While loops, not one — motor control (diagram 20) and display/user
interaction (diagram 99) are already separate. The work is to get the remaining four out of the frame loop
(diagram 43).

## The meta-lesson worth keeping

The decisive objection came from the user, not from my own devil's-advocate pass — the health check in
`devils_advocate_before_acting_on_a_diagnosis.md` says that means the internal pass was not running. In this case
the failure was specific: I compared two strategies on *interface width* while the project's own measured frame
budget already said the deciding question was *which costs share a loop*.
