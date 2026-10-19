---
name: gpu_acceptance_by_reference_bead_experiment
description: "2026-10-18/19 - GPU tracking: identical-input CPU/GPU comparison is only a bug screen (tolerance A'); final acceptance is a real reference-bead CPU-vs-GPU ABBA (stuck beads should read fixed), plus magnet-height scan and rotation alignment"
metadata:
  node_type: memory
  type: project
  originSessionId: 352cf43e-6115-43ef-a77e-e8ccfae2d90c
  modified: 2026-10-19T01:34:04.519Z
---

User decisions on the GPU tracking path (2026-10-18/19):
- Compare CPU and GPU only with IDENTICAL inputs (same images, calibration, windows, starts) - "당연한거잖아" about a comparison that fed different files.
- Tolerances: real-bead x/y 1e-6 px, z 1e-4 um; exception A' for edge / low-stack-end rows x/y 1e-5 px, z 1 nm (10 nm refused - nucleosome unwrapping steps are 20-25 nm). good / pos / pos -1 must match; bead-less picks only judged on the good flag.
- "cpu도 완벽하진 않을거임. 실제 실험으로 정하는게 좋겠음": final acceptance = reference-bead CPU-vs-GPU ABBA; stuck beads should read fixed; two-stuck-bead difference, std, Allan; GPU passes if not worse.
- Same experiment: magnet-height artefact scan (CPU and GPU) and magnet-alignment check by rotation. Protocol to the user before any rig run.
- The DLL is our own file - edits freely allowed. The user wants GPU in the end (tens of beads later).
- Rotor: -5..+5 turns, speed 100, pulses converted to degrees (0.72 deg/pulse).

**Why:** CPU is not ground truth either; only real stuck beads show which tracker is better.
**How to apply:** do not stop at numeric CPU/GPU identity; plan the reference-bead experiment (lean task refprep). Repo record: docs/d1/gpu.md PD419. Related: [[measure_before_more_structure_checks]].
