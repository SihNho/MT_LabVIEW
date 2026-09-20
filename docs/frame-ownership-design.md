---
type: reference
status: current
date: 2026-09-13
tags: [docs]
---

# Frame ownership, faults and shutdown — gates G4, G7, G8

> Design for the 7-loop restructuring. Written 2026-09-13. **Not built.** These three gates are one problem seen from
> three sides: how a frame crosses between loops, who owns it while it is in flight, and what happens when something
> goes wrong. Deciding them mid-build means rebuilding, which is why the work order puts them before construction.

## Why this is not optional detail

Peer review named the hazard precisely: *"'bounded', 'lossless', 'nonblocking' and 'the consumer may be slower' cannot
all hold."* Under sustained overload there are only three outcomes — block the producer, drop the new frame, or recycle
a slot someone may still be reading. Any design that does not choose loses frames silently or corrupts one.

And the rig has already been burned by exactly this class of bug: the GPU v2 work lost a day to **32 ms/frame plus
stale-frame errors** because an IMAQ image reference was held while the camera overwrote the buffer underneath it.

## G4 — how a frame crosses a loop boundary

**An IMAQ image is a reference, not a value.** Enqueue the reference and the camera overwrites the pixels before the
consumer reads them. Three options, and why one wins:

| option | memory | copies | verdict |
|---|---|---|---|
| enqueue the pixel array by value | unbounded — 196 MB/s at 150 Hz | 1 | a lagging consumer grows the queue until it fails |
| enqueue the buffer NUMBER, consumer re-fetches | none | 0 | consumer must beat the ring wrap; the cliff comes back |
| **pre-allocated image pool + slot index** | **bounded by pool size** | **1 (measured ≈ 0.05 ms steady state — see below)** | **chosen** |

The pool costs one copy per frame. **Two measured numbers have been quoted for that copy; both are real, and they
are measurements of different things** (reconciled 2026-09-16, resolving
`archive/ingest/2026-09-16-ingest-2026-09-16.md` PAIR 6, lines 113–115):

| value | date | what was actually measured | source |
|---|---|---|---|
| **≈ 0.05 ms** ← **REPRESENTATIVE (newer, and it is the copy)** | **2026-09-14** | steady-state `IMAQ Copy` of a 1280×1024 U8 frame, 1024 copies inside one Run, linearity in N checked | `archive/benchmarks/INDEX.md:47` row 26; `archive/bench-2026-09-14-image-copy/` |
| ≤ 0.4 ms (0.41/0.42) | 2026-09-14 | the **cold** first copy — includes the destination's first 1.3 MB allocation; an upper bound, not the per-frame cost | `archive/benchmarks/INDEX.md:44` row 23 |
| 0.12 ms | 2026-09-12 | **acquisition itself**, median 122.6 µs/frame at 10.70 GB/s — *not* the pool copy; `restructure-plan-4.6.md:28` labels this row "acquisition cost" correctly | `archive/benchmarks/INDEX.md:40` row 19 |

So the line that used to stand here — *"that copy is already measured at **0.12 ms** — 2 % of the 6.00 ms budget
at 150 Hz"* — carried the **acquisition** figure under the copy's name. The copy is **≈ 0.05 ms ≈ 0.8 % of the
6.00 ms budget at 150 Hz** (≈ 8 ms/s of copying), and acquisition costs a further 0.12 ms ≈ 2 %. Bounded memory
and a copy we can afford still beats an unbounded queue or a race — by a wider margin than the old line claimed.

**Pool sizing.** 1.31 MB per image; 100 slots is 131 MB against 64 GB. Depth is nearly free — but note the measurement:
**ring depth does not buy throughput** (10/50/100 buffers all failed at the same delay). Depth absorbs *jitter* only.
Start at 20 slots and treat any growth as a symptom to investigate, not a fix.

## G7 — the ownership state machine

The index is not what makes a pool safe; the lifecycle is. Each slot is in exactly one state:

```
   FREE ──acquisition takes it──> FILLING ──enqueued──> OWNED BY TRACKING
    ^                                                         │
    └──────────── returned, exactly once ─────────────────────┘
```

Invariants, all of which must hold or the pool is unsafe:

1. Acquisition **obtains a free slot first**; if none is free it does not wait (see G8's overload rule).
2. **Exactly one loop may touch a slot's pixels at a time.** The index in the queue *is* the transfer of ownership.
3. **Every exit path returns the slot exactly once** — normal completion, kernel error, enqueue timeout, shutdown,
   file-writer error. A slot leaked on an error path shrinks the pool until acquisition starves; a slot returned twice
   hands the same memory to two owners.
4. Images are **disposed only after every possible user has stopped** — not when the loop that created them exits.
5. **A GPU raw pixel pointer must not outlive slot ownership**, and must not survive a pool reallocation. This is the
   exact shape of the bug that cost the GPU v2 work a day.

Implementation note: two queues, not one. A `free` queue of slot indices and a `work` queue of filled ones. Acquisition
dequeues from `free` and enqueues to `work`; tracking does the reverse. The pool size is then enforced by construction —
there is no way to have more frames in flight than slots.

## G8 — faults and shutdown

**Queue mechanics that must be specified, not assumed.** A bounded LabVIEW queue's default enqueue timeout is `-1`:
it **waits forever** when full. "Bounded" does not mean "drops". Every enqueue uses a finite timeout and handles the
`timed out` output. Releasing a queue while another node waits on it raises **error 1122**, so shutdown order is
always **stop the users → drain → release**.

**Overload rule (resolves the contradiction the peer review found).**

- *Design point:* the consumer is faster than the camera — 2.6 ms of work against a 6.00 ms budget — so the queue
  absorbs **jitter**, not a deficit. Under the designed load nothing is dropped.
> **SUPERSEDED TWICE — do not build the safety valve below (lint, 2026-09-16).** (1) The user decided the overload
> policy is **latest-wins: discard the backlog and take the newest frame**, not drop-new (2026-09-15) — drop-new
> leaves the tracker *contiguous but lagged*, which is the one thing a time series must not be. (2) The eviction
> machinery that decision implied was then **cancelled entirely**: the camera free-runs into the driver's ring
> buffer, so the design is `IMAQdx Get Image` with **`Buffer Number Mode = Last`**, and "no free slot" simply means
> *do not read this iteration*. There is no pool eviction, no `Lossy Enqueue Element`, no generation number. See
> STATUS.md, "OVERLOAD POLICY" and "the camera free-runs". The paragraph below is kept as the superseded text.

- *Safety valve:* if no free slot is available, acquisition **drops the new frame and counts it**, never blocks. The
  count feeds the existing `Total Lost Frames` / `Missing Frames?` indicators.
- *A drop is a failure report, not a mode.* Acceptance is **zero drops under the designed load**; any drop is a defect
  to investigate.

**Fault propagation.** A consumer that dies must stop acquisition, or the producer fills the pool forever. First error
wins: capture it, broadcast stop, let each loop drain and release its own resources.

**Abort.** The user stops experiments with LabVIEW's Abort button, which **bypasses diagram cleanup entirely** — no
shutdown sequence runs. "The next start cleans up" is only acceptable if it is concrete, so it must cover: stale named
queues, undisposed IMAQ images, an open camera session, open file refnums with partial records, VISA sessions, and an
outstanding GPU DLL call. The GPU DLL already does this (`mt2_open` closes any context the DLL still holds); the same
discipline extends to the rest.

**Single ownership, named.** Exactly one loop owns each of: the camera session, each VISA session, the motor
interface, each file refnum, each queue, the image pool, the GPU context. Written down, because "obviously only one
loop touches it" is how the `Focus position` global nearly gained a second writer.

## What still has to be measured before this is final

- **G9, the core budget — narrowed 2026-09-13, and deferred to stage 5.**

  The machine is an **Intel i5-10500: 6 physical cores, 12 logical, 64 GB**. The user stated the experiment runs with
  **LabVIEW alone** — no ChatGPT, no Claude, no DeviceMonitor — so the original worry ("what if another application
  takes a core?") does not apply, and the "benchmark with one fewer core" cell is dropped.

  What remains is **contention we create ourselves**:

  | consumer | cores |
  |---|---|
  | tracking kernel, parallel instances | ~4 on the **CPU** build — but see the note below; the figure is the tool's default, not a read-back |
  | the other six loops | mostly **blocked**, and a blocked LabVIEW loop does not hold a core — acquisition waits on `Get Image`, motor on a serial reply, scheduler until Start, file on a queue, display behind a 10–20 Hz gate |
  | not removable | the two NI services (`NI.Discovery.V1.Service`, `NI.NigelLocalService` — IMAQdx may depend on them), Windows itself, and **LabVIEW's own UI thread while it redraws** |

  So loop *count* is indeed the wrong metric: the dangerous instant is when **tracking's instances, a 1.31 MB
  display redraw, and a disk write all land together**. That cannot be measured before stage 5 exists — there is
  nothing yet to overlap. **Recorded as a design constraint, measured at stage 5**, where the acceptance already
  includes per-core CPU and the p99.9 acquisition latency.

  **The GPU build has a much easier core budget, and this is a new reason to prefer it.** Kernel structure read
  2026-09-13:

  | kernel | ForLoop | SubVI | cores it wants |
  |---|---|---|---|
  | our CPU kernel (`PARALLEL_kernel_v3`) | **1** (the parallel For Loop) | 1 | ~4 instances |
  | **our GPU kernel (`GPU_kernel_v1`)** | **0** | 2 | ~1 thread + the GPU driver's |
  | original kernel | 1 | 6 | — |

  The GPU path has **no For Loop at all** — one DLL call handles every bead — so it does not consume CPU parallel
  instances. On a 6-core machine that leaves roughly 5 cores for the other six loops instead of 2. Until now the GPU
  build was justified only by "150 Hz and above needs it"; **core headroom is a second, independent reason.**

  *Not established:* the actual parallel-instance count of the CPU kernel. The `P` terminal did not surface as a node
  terminal, so **4 comes from `loop_kernel`'s default argument, not from reading the VI.** Read it before relying on
  the arithmetic above.
- **The array-crossing cost.** A subVI *call* is ~100 ns, but a 1.31 MB image crossing a boundary may be copied. If it
  is expensive the rule becomes "split on scalars and references, never on images" — which constrains where loop
  boundaries may fall.

Neither blocks writing this design down; both block trusting it.
