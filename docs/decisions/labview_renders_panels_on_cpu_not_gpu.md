---
name: labview-renders-panels-on-cpu-not-gpu
description: "The user corrected a diagnosis on 2026-09-08 - LabVIEW draws its front panels on the CPU (GDI), not the GPU, so never explain in-process GPU slowness by \"LabVIEW's own GPU use\"; the frame drops seen on the rig come from CPU display work"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-08T02:32:27.095Z
type: decision
status: in-force
date: 2026-09-08
source: memory/labview_renders_panels_on_cpu_not_gpu.md
---

# LabVIEW panel rendering is CPU work, not GPU work

On 2026-09-08, while explaining why the CUDA tracking DLL ran ~3.7× slower inside the LabVIEW
process than from Python, I attributed it to "WDDM contention with LabVIEW's own GPU rendering". The
user corrected this: *"랩뷰에서는 gpu 사용 안하는거 아니었어? 그래서 화면 움직이면 프레임 드랍
생기는게 디스플레이 계산에도 cpu 사용하기 때문이라고 알고 있는데"* — LabVIEW does not render its
front panels on the GPU; the display work is CPU-side (GDI, on the UI thread), which is exactly why
moving windows during an acquisition causes frame drops on this rig.

The user was right and the correction stands as a fact for this project:

- Never explain GPU/CUDA slowness inside the LabVIEW process by LabVIEW drawing on the GPU. Valid
  candidate causes are host-side: CPU contention with LabVIEW's UI and execution threads, thread or
  process priority, or per-process GPU scheduling by Windows (WDDM) — the last is independent of
  drawing.
- The measured facts behind this: the same DLL takes 1.5 ms from Python and 5.2 ms from LabVIEW,
  uniformly in every phase, with cudaEvent GPU time 0.9 vs 3.3 ms; a DLL-owned worker thread did not
  help; GPU clock ramp-down was excluded. The cause is an open item, to be settled by a one-launch
  micro-benchmark in both processes, a higher-priority worker thread, or Python with busy threads.
- The rig-level consequence the user already knows: keeping the LabVIEW UI quiet during acquisition
  matters because display work competes for the CPU, not the GPU.
