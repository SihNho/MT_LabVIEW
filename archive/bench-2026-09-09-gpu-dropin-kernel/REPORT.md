---
type: narrative
status: historical
date: 2026-09-09
tags: [archive]
---

# The GPU backend as a DROP-IN tracking kernel — GPU_kernel_v1 vs PARALLEL_kernel_v3, identical harnesses

Date 2026-09-09 15:0x–16:0x · rig PC (LabVIEW 2026 26.3.1f1 64-bit, RTX 2060, driver 616.64, SM clock locked 1365 MHz by the
logon task; memory 7000 MHz / P0 at the start of every repeat) · fixture cal002, 5 beads, 60 slices, 1280×1024 U8 frames ·
reference = the LabVIEW tracking kernel's own `.tra` output on the same frames.

## Why this benchmark exists

The 2026-09-09 morning benchmark measured the GPU through a bespoke harness (HARNESS_gpu2) whose front panel was shaped around
the DLL. The user then asked for the backend to be usable in the real acquisition loop, and finally as **one subVI whose setting
picks CPU-parallel or GPU**. Both need the GPU path to have the *tracking kernel's own connector pane*, so it can replace the
kernel at its single call site (MAIN_VI_MAP.md: node index 39, uid 5058). `GPU_kernel_v1.vi` is that drop-in, and this benchmark
measures it in exactly the harness the CPU rows use, so the comparison is like-for-like.

## What was measured

`tools/bench/gpuk_repeat.py`: three independent repeats, each a fresh LabVIEW, the current DLL deployed, then 200 chained frames
through **base** (IMAQ Create + ReadFile + windows, no kernel), **par** (PARALLEL_kernel_v3, P = 4) and **gpuk**
(GPU_kernel_v1), interleaved, all outputs compared with the reference. The DLL also logged its own per-frame time
(`MT_GPU_LOG`, new: the subVI passes `status_len` 0, so the status string is not available to LabVIEW).

## Result

| repeat | base | par | gpuk | **kernel: par** | **kernel: gpuk** | DLL internal (total / upload / kernel) |
|---|---|---|---|---|---|---|
| 1 | 4.96 | 7.68 | 7.62 | **2.72** | **2.65** | 1.65 / 0.40 / 1.12 |
| 2 | 4.96 | 7.68 | 7.84 | **2.71** | **2.88** | 1.68 / 0.40 / 1.13 |
| 3 | 4.92 | 7.48 | 8.11 | **2.55** | **3.19** | 1.63 / 0.40 / 1.11 |

All medians, ms/frame. Functional, every repeat: `par` worst deviation **0.00** (bit-identical to the reference),
`gpuk` worst deviation **2.93e-6 µm in z**, x and y at the 1e-7 level, **0** slice-index flips, **0** good-flag mismatches.

So the drop-in GPU kernel costs **2.65–3.19 ms/frame**, of which **1.65 ms is the DLL** (0.40 upload + 1.12 kernel) and
~1.0–1.5 ms is the LabVIEW side of the subVI (IMAQ pixel-pointer + size nodes, the CLFN call, the pane's data). The CPU-parallel
kernel costs 2.55–2.72 ms in the same harness. **At 5 beads the two backends are equivalent in speed**; the GPU's advantage is
that its per-frame cost is nearly independent of bead count (one kernel launch, one block per bead), which is the case the user
raised for growing bead numbers.

### One unreproduced outlier, recorded as a non-result

The first run of this comparison (before the DLL's own logging existed) gave `gpuk` **11.31 ms** with a quiet machine
(sd 0.23–0.66 ms). It has not reproduced in five subsequent runs (3.22, 2.22, 2.65, 2.88, 3.19) and the DLL reported 1.63–1.77 ms
in every run where it was logged. The suspected cause is the GPU power state (the memory clock drops at a low duty cycle —
docs/gpu-backend.md), which is why every repeat here records nvidia-smi clocks; all three started at P0 / 7000 MHz. Treat 11.31
as unexplained, not as the kernel's cost.

## How the drop-in was built (all by script, zero GUI)

`tools/recipes/build_gpu_kernel.py` copies PARALLEL_kernel_v3.vi (inheriting the pane and all 13 front-panel objects), strips the
diagram, and builds: IMAQ GetImagePixelPtr + IMAQ GetImageSize + one Call Library node on `mt2_track_simple_b`, with the pane's
own controls wired to the DLL's parameters and the pane's indicators wired from the DLL's outputs. Three obstacles, each now a
documented rule:

1. **A LabVIEW Boolean array cannot be wired to any explicit CLFN parameter type.** The kernel's `Bead is good? array in` is a
   Boolean array; wired to an Array/U8 parameter the wire is created and then deleted by Remove Bad Wires, leaving a required
   argument unwired and the VI silently broken. Isolated proof in `bool_wire_probe.log` (DBL→DBL kept, BOOL→U8 removed,
   I32→I32 kept). Fix: Parameter Type **Any** ("Adapt to Type") + Adapt Format **By Value** ("Handles by Value"); the DLL entry
   `mt2_track_simple_b` reads them as LabVIEW array handles.
2. **Two index spaces.** `create_indicator` addresses Nodes[] in creation order; `wire_indicators` addresses the index *within*
   the traversed class. Mixing them raises error 1055 at a To More Specific Class.
3. **Wiring a CLFN output to an existing pane indicator** needs a wire to branch from: create a temporary indicator on the
   terminal, branch the pane indicator onto that wire with `wire_indicators`, then delete the temporary one.

DLL changes in this session: `nb <= 0` means "as many beads as the calibration has"; an empty `cal path` falls back to
`MT_GPU_CAL` or `mt_track_cal.txt` beside the DLL; `MT_GPU_LOG=<file>` writes per-frame timings.

## Files

`gpuk_repeat.log` / `gpuk_repeat_results.json` (the three repeats), `gpuk_chain.log` (the first run, including the 11.31
outlier), `gpuk_diag2.log` (the run that split DLL vs LabVIEW time), `bool_wire_probe.log` (the Boolean-array proof),
`build_gpu_kernel.py`, `finish_gpu_kernel.py`, `gpuk_repeat.py`, `bool_wire_probe.py`, `clfn_params.py`,
`paraminfo_mt2_b.hex` (the Adapt-to-Type parameter list), `mt2.inc` (DLL source at the time of the run).

## Not done here

The frame-to-frame delay in the **real acquisition loop** (the user's actual question) is not measured: it requires running the
working copy of the main VI, which initialises the motor and the ASI piezo, so it waits for the user to be present.
