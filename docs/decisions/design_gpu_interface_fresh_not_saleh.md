---
name: design-gpu-interface-fresh-not-saleh
description: "The user's direction (2026-09-09) for the GPU tracking path - do not imitate the Saleh-lab donor's DLL interface or node; design our own optimal interface from scratch (single call per frame, raw image pointer, DBL outputs)"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-09T03:26:28.720Z
type: decision
status: in-force
date: 2026-09-09
source: memory/design_gpu_interface_fresh_not_saleh.md
---

# Design the GPU interface ourselves; do not copy the Saleh-lab donor

On 2026-09-09, after the GPU row of the three-way benchmark had been measured through a Call Library
Function Node copied from the Saleh-lab 2013 demo (`TrackBatchOfImagesWithGPU.vi`), the user said:
*"Saleh꺼 따라하지 마. 어차피 새로 만드는 판인데. 최적으로 짜보자고"* — stop following the Saleh
design; since we are building anew anyway, build the optimal version.

What this means for the work:

- The donor node's fixed parameter types (SGL 2-D outputs, I32 arrays, 3-D U8 image array, the
  workarounds that followed: 3-float encoding of x,y,z, ImageToArray + Build Array copies) were a
  measurement expedient, not the design. They are not to be carried into the deliverable.
- The deliverable interface is ours: one DLL call per frame, the frame passed as the IMAQ buffer's
  raw pixel pointer + line width (no LabVIEW-side copies), x,y,z as DBL arrays in and out, a
  persistent context handle, calibration loaded once. The CLFN is configured by script to those
  types (CallLibrary Parameter Info) rather than inherited from any donor.
- The user asked the question that led here — why copy the image at all instead of one copy and
  everything else inside the kernel — so minimising CPU↔GPU traffic and LabVIEW-side copies is the
  explicit optimisation target.

- **Split the data by lifetime (user, 2026-09-09, before the HARNESS_gpu2 work resumed):** some inputs
  are fixed before the acquisition while-loop starts (calibration, windows, image geometry, bead
  count, flags) and some change every frame (the image, the previous x/y/z, the good flags). The
  user pointed out that if the DLL call is a bottleneck, re-sending the fixed data each frame is a
  large part of it and should be simplified away: *"frame마다 갱신되는게 있고 while loop 돌기 전에
  fix되는 데이터가 있잖아 … 데이터 전달에서 생기는 병목도 큰거 아니야? 이 부분은 간략화시키면 좋을 것"*.
  So the interface is open-once / track-per-frame / close-after (`mt2_open` → `mt2_track` → `mt2_close`);
  the per-frame call carries only what changed, and the one-node convenience form (`mt2_track_simple`)
  is acceptable only because its fixed arguments are scalars whose cost is negligible.

The Saleh C source remains a reading aid for the algorithm (it is the same subVI set), nothing more.
