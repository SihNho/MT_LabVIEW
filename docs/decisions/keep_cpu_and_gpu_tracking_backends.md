---
name: keep-cpu-and-gpu-tracking-backends
description: "The user wants a GPU/CUDA tracking path maintained alongside the CPU-parallel one, because bead count may grow without bound — build to a swappable backend interface, don't pick one"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1ffa4eb9-19ac-4240-b7d7-6ef33fffb8c1
  modified: 2026-08-27T08:23:04.291Z
type: decision
status: in-force
date: 2026-08-27
source: memory/keep_cpu_and_gpu_tracking_backends.md
---

# Keep both a CPU and a GPU tracking backend — the user asked for it explicitly

On 2026-08-27, after being shown that CPU parallelisation alone would fix the currently observed
frame loss, the user declined to treat that as the end of the story: *"CPU 병렬화만 해도 훨씬
좋아질 것 같기는 한데, 그럼에도 불구하고 GPU 병렬화 코드도 따로 두고 싶어. 나중에 경우에 따라서는
무한히 많은 bead 쓸 수도 있잖아"* — build the CPU parallel path, but keep a separate GPU path too,
because the experiment may one day track arbitrarily many beads.

So do not present this as an either/or and do not quietly drop the GPU track because the CPU fix is
sufficient for today's bead counts. The two have opposite cost shapes — the CPU path has near-zero
fixed cost and a real per-bead cost, while a CUDA path pays a fixed per-frame transfer/launch cost
(a few hundred microseconds) and then almost nothing per bead — so which one wins depends entirely
on bead count, and the crossover has to be measured rather than argued.

The practical consequence for how code gets written: **define one backend interface and implement it
several times**, rather than forking the whole tracking chain per approach. A single connector-pane
signature (frames/ROIs plus per-bead calibration in, xyz array plus error out) with a serial
implementation kept as the numerical reference, a parallel-For-Loop implementation, and a
Call-Library-Function-Node implementation, dispatched by an enum, keeps all of them callable,
A/B-benchmarkable on identical input, and diffable bead-by-bead. Only the innermost compute should
swap.

This sits alongside, and does not reorder, the measurement-first principle: attribute the fixed
per-frame overhead before investing in either backend, since a large fixed cost caps the achievable
frame rate regardless of how the per-bead maths is computed.
