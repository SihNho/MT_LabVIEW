---
name: two-separate-codebases-cpu-and-gpu
description: "The CPU-parallel and GPU tracking paths ship as TWO separate top-level VIs, not one VI with a runtime backend switch — because the PC this runs on may change"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-12T08:30:49.609Z
type: decision
status: in-force
date: 2026-09-12
source: memory/tracking_backend_selectable_subvi.md
---

# Keep CPU and GPU as two separate codebases, not one switchable VI

**This reverses the earlier direction recorded in this same file.** Until 2026-09-12 the plan was one tracking subVI
whose backend was chosen by a saved setting (built as `TRACK_kernel_v1`, a Case Structure selecting CPU-parallel in
frame 0 and GPU in frame 1). The user replaced that on 2026-09-12:

> "우선. 언제든지 pc가 바뀔 여지가 있으므로 cpu only, gpu computing 두개 코드를 별도로 둘거야. 그러니 결국에는
> 4.6 cpu parallel, 4.6 gpu parallel 이렇게 다른 코드를 두개 짜야한다는 말. 나중에 옵션에 따라 왔다갔다 하지 말고."

So the deliverable is **two top-level VIs** — a CPU-parallel one and a GPU one — maintained side by side. The reason is
deployment, not performance: the machine this runs on may be swapped, and a rig without a suitable GPU should run the
CPU build directly rather than carry switching machinery it never uses. Do not build, or propose, a runtime option that
toggles between backends.

What this means in practice:

- Do not treat "add a backend selector" as the goal of new work. The two files differ **only** in the loop that calls
  the tracking kernel; everything else should be identical.
- Because two copies of one program drift apart, keep everything except the kernel call in **shared subVIs**, so a fix
  is made once. Duplication is accepted at the top level, not throughout.
- The earlier switchable kernel was not wasted: benchmarking it produced the measurement that the Case Structure is
  free on the CPU path and costs about +1 ms on the GPU path, and it proved the two backends produce equivalent
  numbers. Keep it as a benchmarking fixture, not as the shipped design.

The user's older standing point still holds separately and is not contradicted by this: the toolkit must keep
supporting Case Structures as a scripting capability ("내 생각에는 앞으로도 계속 case structure는 사용해야 할 것
같은데"). That is about what the scripting fleet can build, not about how the tracking program is shipped.
