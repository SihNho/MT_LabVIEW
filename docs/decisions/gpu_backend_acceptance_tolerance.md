---
name: gpu-backend-acceptance-tolerance
description: "The user's acceptance criterion for the GPU/CUDA tracking backend — 1e-6 px in x,y against the CPU kernel on the recorded fixture; for z the user later said a ~1e-4 difference is acceptable ('결과에 크게 반영되지 않을 것'); the algorithm steps must stay identical, only the executor changes"
metadata:
  pinned: false
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-07T12:26:55.938Z
type: decision
status: in-force
date: 2026-09-07
source: memory/gpu_backend_acceptance_tolerance.md
---

# GPU/CUDA backend: acceptance tolerance — 1e-6 px for x,y; ~1e-4 is fine for z

On 2026-09-07 the user asked for the bead-tracking kernel to be reproduced on the GPU (CUDA) and, when told
that a GPU port cannot be bit-identical to the CPU LabVIEW kernel (summation order, FFT implementation,
parallel reductions), set the acceptance criterion explicitly: **"허용 오차는 1e-6 please, 1e-6 um"** — i.e.
|x_gpu − x_cpu| < 1e-6 px, |y| likewise, |z_gpu − z_cpu| < 1e-6 µm, per bead per frame, on the recorded
fixture (10,043 frames, five beads).

Later the same day, while the NumPy reference was being matched stage by stage and the last z residual was
traced to LabVIEW storing the radial profile in single precision (a ~1e-4 intensity-unit difference that
maps to ~1e-6 µm in z), the user relaxed the z side: **"z 축에서 1e-4 차이는 괜찮은 것 같아. 결과에 크게
반영되지 않을 것 같은데"** — a difference of order 1e-4 in z does not matter for the science. So: do not
spend effort emulating LabVIEW's single-precision rounding order in the radial profile; x,y stay at 1e-6 px.

What this does and does not permit:
- It relaxes only the comparison. The computation itself must remain the original one (rule 1a: 원본의
  연산방법 자체를 바꾸면 안 된다): the same radial-profile / x,y-profile / parabola-fit / Hilbert-phase /
  quadratic-fit / I(r)-to-cal steps, constants and array sizes. Replacing an algorithm step with a "close
  enough" alternative is not covered by the tolerance.
- The reference is the CPU kernel's output through the fixture harness (HARNESS_compare.vi +
  tools/bench/run_fixture_compare.py), which is itself verified against the recorded .tra to 0.0.
- The user wants CPU (PARALLEL_kernel_v3) and GPU backends kept side by side with the same connector pane
  (see the earlier memory on keeping both backends); the GPU path is delivered as a LabVIEW subVI wrapping a
  CUDA DLL through a Call Library Function Node.
