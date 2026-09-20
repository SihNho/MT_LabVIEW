---
type: reference
status: current
date: 2026-09-14
tags: [docs, stage2, plan]
---

# Stage 2 — acquisition + tracking loops + queue (construction plan, 2026-09-14 20:5x)

User (20:3x): *"재구성이 중요하겠는데 이거 진행하도록."* Stage 2 of [restructure-plan-4.6.md](restructure-plan-4.6.md) §5:
a NEW top-level VI whose acquisition loop and tracking loop talk through a bounded queue; accepted on **bit-identical
x/y/z on the fixture** and a **live 150 Hz run with `Images Missed` = 0**. The original main VI is the specification and
is never edited. Everything is built by script (recipes under `tools/recipes/`), one reviewed batch per step.

## What the original does today (measured, docs/frame-loop-wire-graph.md, main-vi-subvi-identity.md)

- Camera session opened in the startup frames (diagram 87: `IMAQdx Open Camera` → `Configure Grab`; `IMAQ Create` for
  the working image); grab started; frame loop (WhileLoop uid 637, diagram 43) does per iteration:
  `get buff image-lost frames.vi` (Session In, Image In, `Buffer to extract` ← LastBufferNumber+1 via shift register
  `LastBufferNumber`) → `Image Out`, `Missed frames?`, `current image number`; then
  `Track N beads four-fold over-kernel-v3.vi` (10 inputs: `Image In`, `x,y,z array`, `Bead is good? array in`,
  `pos in cal image in`, `cross size`, `# of bead 4 packs`, `4 pack remainder`, `Array of cal clusters`,
  `Real-space cosine window`, `Cosine bandpass for Hilbert`) → `x,y,z array out`, `Bead is good? array out`,
  `pos in cal image out` (three of the 14 shift registers carry these across frames); then `save trace.vi`
  (`current frame data array in` ← the frame's results, `total data array in/out` shift register, file refnum,
  `frame index`) and the display path (`IMAQ ImageToArray` → Flatten → Draw, diagram 99 loop = a separate loop today),
  plus motor/focus/UI reads via implicit `Value` nodes (88, all named) and locals.
- The per-frame state = 14 shift registers, each with its initialiser and reader named (wire-graph doc, measured
  sections). Stage 2 carries exactly the tracking-related ones across iterations of the NEW tracking loop:
  `x,y,z array out`, `Bead is good? array out`, `pos in cal image out` (kernel feedback), `LastBufferNumber`
  (acquisition), `total data array out`/`error out`/`file number` (save — stage 5, but the queue element must carry
  what save needs: frame index, buffer number, timestamp, x/y/z, good-flags).

## Target of stage 2 (a subset of the 7-loop design)

```
[loop 1 ACQ]  IMAQdx Get Image (Next / Buffer#) ─▶ IMAQ Copy into pool slot ─▶ enqueue Q_img {slot, buffer#, t}
                    (fixture mode: IMAQ ReadFile of frame k instead of IMAQdx)
[loop 2 TRK]  dequeue Q_img ─▶ kernel (PARALLEL_kernel_v3clean, P=4) with the 3 feedback shift registers
              ─▶ enqueue Q_res {frame, buffer#, t, x/y/z[], good[]} ; return slot
[sink]        dequeue Q_res ─▶ (stage 2: append to an array indicator / write a CSV for the fixture diff;
              stage 5: the real file writer + display)
```

- **Image pool**: N `IMAQ Create` images (N = 8) created before the loops; slot index travels in the queue element;
  the copy is `IMAQ Copy` (0.05 ms steady, INDEX rows 23/26). The acquisition image itself is never handed out.
- **Q_img**: bounded (N−1), element = cluster `{slot:I32, buffer:U32, t:DBL}`; enqueue with timeout 0 → on `timed out`
  the frame is counted as dropped by the tracker (never blocks acquisition). Q_res: unbounded-ish (lossless to the sink).
  > **SUPERSEDED — the acquisition side of this line is dead (lint, 2026-09-16).** Overload policy is
  > **latest-wins**, not drop-new (user, 2026-09-15), and the whole image-pool eviction question was then cancelled:
  > the camera free-runs into the driver's ring buffer, so acquisition uses **`Buffer Number Mode = Last`** and a
  > full pool means *skip this read* — the driver's ring IS the latest-wins queue. **Q_res is unchanged and still
  > correct** (lossless, FIFO, tracking → file writer). The `t:DBL` field is also retired: the **buffer number is
  > the time axis**, never a software timestamp. See STATUS.md, "OVERLOAD POLICY" and "the camera free-runs".
- **Kernel**: `PARALLEL_kernel_v3clean.vi` (bit-identical to the four-fold reference on the fixture, INDEX row 15/24) —
  the CPU build; the GPU build swaps it in stage 6.
- **Fixture mode**: a Boolean `Replay?` control; loop 1 reads `img%05d.tif` from the fixture folder at full speed
  (or paced); `buffer#` = frame index. This is what the numeric acceptance runs on, with no hardware.
- **Live mode**: `IMAQdx Open Camera` (alias from the original: read from the startup frames), `Configure Grab`,
  `Grab`, `Get Image (Buffer Number, Next)`; `Images Missed` = buffer-number gaps counted in loop 1.

## Changes required by the peer review (`archive/peer/2026-09-14-stage2-construction-plan.md`) — adopted

1. **Pool ownership is a queue, not arithmetic.** `slot = k mod 8` can overwrite a slot the tracker still reads. A
   bounded **`Q_free`** seeded with slots 0..7 is the pool authority: acquisition dequeues a free slot → copies →
   enqueues `Q_img` (timeout 0); on `timed out` it returns the slot to `Q_free` at once; the tracker returns the slot
   after the kernel. Invariant asserted in the test: `free + queued + processing = 8`.
2. **Buffer selection keeps the original contract.** The original asks for logical `LastBufferNumber + 1`; the new
   loop uses IMAQdx `Get Image` in **Buffer Number** mode with that number and advances from the *returned* buffer
   number (`Next` ignores Buffer Number In — not equivalent). Record `{requested, returned}`; gap = returned − previous − 1
   with rollover handling; the original subVI's overwrite behaviour (oldest / newest / error) is characterised first.
3. **Kernel state faithfully.** Cases #5540 (before the kernel: selects/transforms `x,y,z` and `Bead is good?`) and
   #2222 (after: `Correction Factor` on x/y/z) are reproduced case-for-case; the accepted/saved x/y/z is whichever the
   original saves — read from the graph before building (their selectors and per-case inner wires: a reporter pass on
   diagrams of #5540 / #2222). All per-frame kernel inputs are sampled at the same point as the original; the queue
   element is `{sequence, returned buffer#, acquisition timestamp, slot}` — never derive frame identity from the
   tracker's iteration count.
4. **Fixture replay is lossless and unpaced**: read a frame only after a free slot is obtained, block until accepted;
   correctness, not TIFF throughput, is what it tests. Never preload into the 8-image pool.
5. **Toolkit order: empty VI → While loop → integer queues → cluster/Bundle.** The While test stops deterministically
   after exactly 3 iterations (no manual Stop); the queue tests cover bounded-full timeout, FIFO order, release order
   (stop users → drain → release) and the free-slot invariant. `Obtain Queue` needs a wired sample for the element type.
6. **Live instrumentation (minimum):** requested/returned buffer numbers, gap count/size, overwrite/error count;
   acquisition-call duration count/p99.9/max; acquisition→dequeue and acquisition→kernel-done latency p99.9/max;
   `Q_img` high-water mark, enqueue timeouts, dropped frames, longest full interval; acquired/copied/enqueued/dequeued/
   processed/returned counts; slot invariant violations; `Q_res` high-water mark (never silently unbounded).
   Enqueue timeout 0 everywhere; `timed out?` checked on every call. Acceptance = zero gaps, zero drops, zero slot
   violations, processed = acquired; the slowed-tracker test shows counted drops with acquisition still at 150 Hz.

7. **Stop conditions are evaluated INSIDE the loop.** A front-panel Boolean's terminal wired into a While loop from the
   top level becomes an input tunnel read once before the loop runs (NI: the infinite-loop mistake); the stage-2 VI
   stops its loops from a Boolean read every iteration — a local variable of `Stop` inside each loop, or the control's
   terminal moved into one loop and locals in the others (`OpExitWhile_v0`'s by-name `Stop Condition` is the wiring
   primitive; the test uses a control already TRUE, so it terminates after one iteration by design).

8. **No composite queue elements in stage-2 v0 (decided 22:1x).** `Create Bundle by Name` needs a typed cluster
   terminal, and `Create Build Array` needs all its inputs as terminals of ONE node — neither exists without a donor.
   Instead each direction uses **two lock-stepped queues from the same producer in the same iteration**: `Q_img`
   (bounded N−1, element = slot I32) + `Q_meta` (unbounded, element = returned buffer# as DBL, written right after
   `Q_img` succeeded; on `Q_img` timeout nothing is written to either and the slot goes back to `Q_free`). Single
   producer, single consumer, FIFO ⇒ the pairs stay aligned. The results direction: `Q_res` (the kernel's
   `x,y,z array out`, a DBL array) + `Q_res_meta` (buffer# DBL) the same way; the sequence number is the acquisition
   loop's own counter carried in `Q_meta`'s order. Composite elements (clusters) return when a donor cluster exists.

## Toolkit gaps to close first (each = one op + one functional test, in this order)

| gap | route | test |
|---|---|---|
| **While loop creation** | `OpWhileLoop_v0` = OpForLoop_v0 with erdosmiller `Create While Loop.vi` (conditional terminal, tunnels by control names) | scratch VI: one loop, stop button wired, ExecState 1, runs 3 iterations with a counter |
| **Queue nodes** | `OpQueue_v0` family from erdosmiller `Create Obtain Queue / Enqueue Element / Dequeue Element / Release Queue.vi` (element type from a wired sample) | two loops passing 100 integers, order preserved, count 100 |
| **Bundle / Unbundle by name** | erdosmiller `Create Bundle by Name / Unbundle by Name.vi` (needs a typedef or a sample cluster: use a cluster CONTROL created from a donor) | round trip of `{slot, buffer, t}` |
| **New VI from nothing** | copy a minimal runnable VI (`HARNESS_base.vi`) and delete its diagram objects; or `OpFP_v0`/`conpane` for the pane | empty VI, ExecState 1 |
| IMAQdx / IMAQ nodes | `drop_subvi` of the vi.lib VIs (proven for IMAQ Create/ReadFile/Copy/GetImageSize) | — |
| Event structure (stage 5) | erdosmiller `Create Event Structure.vi` — not needed in stage 2 | — |

## Build order for the stage-2 VI (`claudeDev\Track_v6_CPU.vi`)

1. Empty VI + front panel: `Replay?`, `Fixture folder`, `Frames` (N), `Stop`, indicators `Frames processed`,
   `Images Missed`, `x/y/z` (last), `Results` (2-D array for the fixture diff).
2. Pool: 8× `IMAQ Create` (names `pool0..7`) into an array of image refs (Build Array — erdosmiller `Create Build Array.vi`).
3. Loop 1 (While): case `Replay?` → ReadFile(frame k) / IMAQdx Get Image → `IMAQ Copy` into slot (k mod 8) → Bundle →
   Enqueue(Q_img, timeout 0) → `Stop` or last frame ends the loop.
4. Loop 2 (While): Dequeue(Q_img, timeout 100 ms) → Index the pool → kernel with 3 shift registers (initial values
   from the same sources the original uses: `x,y,z array` initial control, `Bead is good?` initial, `pos in cal image`
   initial; parameters `cross size`, `# of bead 4 packs`, `4 pack remainder`, `Array of cal clusters`, windows — the
   same controls/loaded calibration as HARNESS_par uses today) → Bundle → Enqueue(Q_res).
5. Sink loop: Dequeue(Q_res) → append to `Results`; on the fixture, dump to CSV (Python compares with the reference
   `archive/bench-2026-09-07-fixture/` x/y/z, bit-for-bit).
6. Shutdown: stop loops → drain → release queues → IMAQdx Close (live) → dispose pool.

## Acceptance for stage 2 (from the plan, unchanged)

- Fixture: **the first 10,018 of the 10,043 frames** — x/y/z **bit-identical** to the reference produced by the
  original kernel path (the same reference HARNESS_par matched), 0 flips. **Bit-identity is claimed only up to the
  first bead loss (frame 10,018), not across all 10,043.** This is `STATUS.md`'s "**Say it exactly**" wording
  (`STATUS.md:60-62`), and STATUS is the authority here. *was: "Fixture: 10,043 frames, x/y/z **bit-identical** to
  the reference … 0 flips."* — **corrected 2026-09-16**, resolving
  `archive/ingest/2026-09-16-ingest-2026-09-16.md` PAIR 3 (lines 98–100): this line was the over-claiming side.
- Live: 150 Hz, `Images Missed` = 0 over ≥ 60 s, acquisition-call latency p99.9 and max recorded, buffer-number gaps 0,
  back-pressure test (tracking slowed deliberately → Q_img drops counted, acquisition keeps 150 Hz).

## Tonight's slice

Toolkit gap 1 (While loop op) and gap 4 (empty VI), each with its functional test; the queue op next. Every step:
plan line here → peer review → recipe → batch → test → INDEX row.
