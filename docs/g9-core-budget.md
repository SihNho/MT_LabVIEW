---
type: reference
status: current
date: 2026-09-14
tags: [docs]
---

# G9 — core budget (facts as of 2026-09-14; kernel-level gate PASSED 14:2x — INDEX row 24; loop-level waits for stage 2)

Gate G9 of [restructure-plan-4.6.md](restructure-plan-4.6.md) asks whether the seven-loop design fits the machine,
"accounting for parallel-For workers plus IMAQdx and GPU driver threads", benchmarked at the normal core count **and
with one fewer core**. This file holds what is measured or read off the machine; the benchmark rows stay empty until run.

## Measured / read off the machine

| item | value | how |
|---|---|---|
| CPU | Intel Core i5-10500 @ 3.10 GHz | `wmic cpu` |
| physical cores / logical processors | **6 / 12** | `wmic cpu`, `os.cpu_count()` |
| CPU tracking kernel (`PARALLEL_kernel_v3`, inside `TRACK_kernel_v1` frame 0) parallel For instances | **P = 4** | build recipe / benchmark reports (INDEX rows 15–18) |
| kernel time per frame, 5 beads | CPU-parallel 2.55–2.72 ms; GPU drop-in 2.65–3.19 ms (DLL 1.65) | `archive/bench-2026-09-09-gpu-dropin-kernel` |
| frame budget at 150 Hz | ~6 ms (frame period − 1 ms, measured cliff) | `docs/camera-acquisition-facts.md` |
| loops in the 4.6 design | 7 (acquire · track · save · display · motor · rotor/scheduler · UI/events) | plan §4 |

## Arithmetic (not a measurement)

At 150 Hz the tracking loop alone occupies **4 workers × ~2.6 ms per 6.67 ms** ≈ 1.6 core-equivalents when the kernel
runs; the other six loops are lightweight except **display** (ImageToArray → Flatten Pixmap → Draw, MEASURED 14:xx: 2.7 ms CPU + ≈6.5 ms visible paint, INDEX rows 22 / 25 — the
next measurement) and **save** (file I/O, bursty). IMAQdx acquisition is 0.12 ms/frame of CPU (2 %). So on 6 physical
cores the design is not oversubscribed *on paper* even with the GPU driver thread; hyper-threading adds no headroom for
the kernel's SIMD-heavy workers. **What paper cannot say** — and G9 demands — is how the loops behave under contention:
UI-thread `Value` property nodes (106 today; 88 implicit) serialise onto the single UI thread, and any non-reentrant
subVI shared by two loops serialises them (both focus subVIs are non-reentrant by design; keep one caller each).

## Measured 2026-09-14 14:2x — the kernel-level gate (`archive/bench-2026-09-14-g9-core-budget/`, INDEX row 24)

Three-way timing (base / par P=4 / gpuk, 200 interleaved fixture frames) with the LabVIEW process affinity set A-B-A:
12 LPs → 10 LPs (one physical core removed, siblings (10,11) per `cpu_topology.py`) → 12 LPs, no restart.

| condition | base | par | gpuk | par kernel | gpuk kernel |
|---|---:|---:|---:|---:|---:|
| A 12 LPs | 2.94 | 4.89 | 5.01 | 1.95 | 2.07 |
| **B 10 LPs (5 cores)** | 2.90 | 4.86 | 4.87 | **1.96** | 1.97 |
| A' 12 LPs | 2.92 | 4.88 | 4.94 | 1.96 | 2.02 |

**+0.3 % on the par kernel at five cores → G9 PASS for the kernel in isolation** (gate: > +10 % fails; peer review).
Outputs bit-identical (par) / 2.9e-6 µm (gpuk) against the reference in all three. Caveat: one COM Run per frame, the
kernel alone — the seven concurrent loops cannot be tested until stage 2 exists.

## Still to run

- The loop-level G9 on the rebuilt VI (per-loop CPU, display and writer active, 6 vs 5 cores).
- The display-path cost (next measurement in the work order) — it decides whether display needs its own core.
- Per-loop CPU time once stage 2 exists (only the rebuilt VI can be instrumented per loop).

_Facts recorded 2026-09-14 during the autonomous loop; nothing here changes a decision until the benchmark rows exist._

## Parallelism state of the ORIGINAL main VI — measured 2026-09-14 18:1x (`OpLoopCast_v1`, INDEX row 30)

None of the 17 For loops has iteration parallelism enabled. One loop (uid 22786, a For loop with 3 shift registers
inside the Sequence frame of diagram 158) stores `Number of Static Parallel Instances` = 12 while
`Is Parallelism Enabled?` is FALSE — a dormant setting someone once tried; it has no effect today. The three While
loops (frame loop 637 and two others) are sequential by class. Consequence for G9: every core the restructured VI uses
beyond one is new load; the kernel-level budget (row 24) is the only parallelism measured so far. The scripted
`PARALLEL_kernel_v3` loop reads enabled / P = 4, so rows 15 and 24 were genuine parallel runs.
