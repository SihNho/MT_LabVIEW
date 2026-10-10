---
name: three-way-benchmark-in-labview
description: "The user's required final comparison for the tracking kernel: (1) the original sequential VI, (2) the new CPU-parallel VI, (3) the GPU/CUDA DLL — measured inside LabVIEW on the fixture with no motor operation; DLL build-toolchain installs (driver, VS Build Tools, CUDA Toolkit) are approved"
metadata:
  pinned: false
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-07T12:51:50.146Z
type: decision
status: in-force
date: 2026-09-07
source: memory/three_way_benchmark_in_labview.md
---

# The performance comparison the user wants: three executors, measured in LabVIEW

Stated 2026-09-07 after seeing a first NumPy/CuPy timing table that lacked the CPU-parallel VI:
*"내 생각에는 3가지 비교가 이렇게 나와야해 — 1. 기존 vi 방식 (sequential) 2. 이번 새 vi 방식 (cpu parallel)
3. GPU 병렬. dll 만들기 위한 권한을 허가할테니 최종적으로 LabVIEW 테스트 (모터 가동 불가) 해서 봐야겠어"*

What this fixes for every later benchmark of the tracking kernel:

1. **The three rows are fixed**: the original four-fold sequential kernel VI, the new PARALLEL_kernel_v3 (P=4 CPU
   parallel), and the GPU path (CUDA DLL called from a LabVIEW wrapper subVI). Python-side timings (NumPy, CuPy
   prototype) are development aids, not the comparison the user wants.
2. **Measured inside LabVIEW**, all three on the same fixture inputs (recorded images + cal002), with the kernel call
   timed separately from file loading and COM round trips. Motors and the piezo stage are never actuated
   (standing rule 1b) — the "LabVIEW test" is the offline fixture run, then the user's own live check.
3. **Toolchain installs for the DLL are approved** (NVIDIA driver update, Visual Studio Build Tools, CUDA Toolkit):
   run them, but each needs a UAC click, so bundle them into one elevated script and tell the user when the prompt
   appears — unattended UAC prompts time out after ~2 minutes.
