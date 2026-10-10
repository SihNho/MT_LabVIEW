---
name: gpu-is-the-default-top-level-vi
description: "The user's 2026-09-16 direction — build the seven-loop top-level VI on the GPU tracking path FIRST and treat it as the default; the CPU-parallel top level is a later, additional deliverable"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1c79eb01-7150-4a78-9689-e6d4f34f7800
  modified: 2026-09-16T03:53:05.669Z
type: decision
status: in-force
date: 2026-09-16
source: memory/gpu_is_the_default_top_level_vi.md
---

# The GPU path is the default top-level VI, and it is built first

Asked whether the GPU top level should be built in the pre-rig window, the user answered (2026-09-16):

> *"tracking은 기본적으로 GPU 기준으로 최상위 vi 작성할 것. [이후 CPU 병렬 vi도 추후 작성 필요하기는 함]"*

So the ordering is settled, and it is the opposite of how the work had been queued. Every plan until then treated
the **CPU-parallel** build as the main line — `Track_v6_CPU_core_v0.vi` and `Track_v6_CPU_queue_v0.vi` were the
artefacts that existed, so the seven-loop top level was implicitly going to be assembled around them, with the GPU
kernel "swapped in" at a final stage. That is now backwards: **the GPU path is the default**, and the CPU-parallel
top level is an additional deliverable that follows.

This refines, and does not replace, the earlier decision that the two paths ship as **two separate top-level VIs**
rather than one VI with a runtime backend switch (the machine this runs on may change). Both still ship. What
changed is which one is built first and treated as the reference.

## Why it matters for planning

- The loop architecture, the queue seams and the frame-identified result message are shared, but the **tracking
  loop's contents differ** — that is the one loop the CPU/GPU split touches. Building CPU-first would mean writing
  that loop twice and re-validating the whole top level around the second one.
- Acceptance work should be planned against the GPU build as the primary subject. The agreed GPU tolerance
  (x/y ≤ 1e-6 px, z ≈ 1e-4 µm against the CPU kernel on the recorded fixture) is the acceptance for the tracking
  loop, not a final-stage afterthought.
- Do not schedule the GPU build as "stage 6" or "last". If a plan puts the GPU work after every CPU stage, it
  contradicts this direction.
