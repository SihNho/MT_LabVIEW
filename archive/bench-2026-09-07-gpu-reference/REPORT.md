---
type: narrative
status: historical
date: 2026-09-08
tags: [archive]
---

# Benchmark report — NumPy / CuPy (CUDA) port of the tracking kernel vs the LabVIEW kernel (2026-09-07)

## What was tested
The bead-tracking kernel `Track 1 of N bds xyz-kernel-reentrant.vi` (and its nine analysis subVIs) re-implemented
step by step (rule 1a: same algorithm, constants, array sizes) as (1) a float64 NumPy reference (`tools/gpu/ref_numpy.py`)
and (2) a batched CuPy/CUDA port (`tools/gpu/ref_cupy.py`), compared with the LabVIEW kernel's own output on the
recorded fixture. Spec source: the VIs' wiring read headlessly (`tools/bench/spec_wiring*.json`), plus two facts found by
script-built subVI harnesses (weighted quadratic fit [2,4,5,4,2]; single-precision radial profile). Reading aid only:
the UCSB Saleh-lab C/CUDA port (BSD, 2013) found in `zz_LabView VI\GPU Track Algo (Saleh Lab)`.

## Environment
Windows 10, Python 3.10, NumPy 1.26.4, CuPy 13.6.0 (cupy-cuda11x + pip nvidia-*-cu11 libraries, CUDA runtime 11.8),
GeForce RTX 2060 6 GB, NVIDIA driver 457.51 (CUDA 11.1; the 11.8 runtime runs through minor-version compatibility),
no CUDA toolkit installed. LabVIEW 2026 Q3 for the reference only.

## Data and reference
Fixture `G:\Data\SiHyeong\20260906 Kimlab - 50bp 16X WT 90Hz 1p2 Ramp_Newbatch\test`: 10,044 frames (1280×1024 8-bit),
cal002 (5 beads, 60 slices, cross 120), tra002-000. Reference = the LabVIEW kernel run by the fixture harness
(`tools/bench/fixture_compare_results.jsonl`, session 2026-09-07 16:00, verified == .tra to 0.0). The kernel inputs
LabVIEW computes (cosine windows, per-bead cal clusters) were captured over COM (`tools/gpu/harness_inputs.npz`).

## Criteria
User: |dx|,|dy| < 1e-6 px; z originally 1e-6 um, relaxed the same day to ~1e-4 um ("1e-4 차이는 괜찮아").

## Results
| comparison | frames | worst |dx| (px) | worst |dy| (px) | worst |dz| (um) | note |
|---|---|---|---|---|---|
| NumPy vs LabVIEW | 10,043 (all) | 4.8e-7 | 4.5e-7 | 6.4e-6 (*) | (*) plus ONE frame (1937, bead 5): cal-slice SSD near-tie 0.353483 vs 0.353494 → index 25 vs 26, dz 4.7e-3 um |
| NumPy vs LabVIEW | 1,005 (every 10th) | 4.4e-7 | 4.5e-7 | 6.4e-6 | 0 failing |
| CuPy vs NumPy | 201 (every 50th) | 4.6e-12 | 4.1e-12 | 2.2e-15 | identical up to FFT rounding |
| CuPy vs LabVIEW | 201 (every 50th) | 4.4e-7 | 1.6e-7 | 3.8e-6 | 0 near-tie flips |

Timing (5 beads per frame unless stated; RTX 2060; Python-level launches, no fused kernels):
| executor | per frame | per bead |
|---|---|---|
| LabVIEW kernel in the harness (four-fold, 2026-09-07 16:3x) | 19 ms | 3.8 ms |
| NumPy reference (CPU, single thread) | 7.6 ms | 1.5 ms |
| CuPy, 5 beads in one batch | 16.7 ms | 3.3 ms |
| CuPy, 100 beads in one batch | 19.0 ms | 0.19 ms |
| CuPy, 500 beads in one batch | 39.5 ms | 0.079 ms |
| CuPy, unbatched per frame incl. full-image H2D | 119 ms | — |

Reading: with 5 beads the GPU is launch-overhead bound (~40 kernel launches) and no faster than the CPU; the GPU wins
from ~50 beads per frame (0.19 ms/bead at 100, 0.08 at 500 — 40× the LabVIEW per-bead cost). A compiled CUDA DLL
with fused per-bead kernels would cut the fixed ~15 ms overhead to ~1–2 ms and is the deliverable form for LabVIEW
(Call Library Function Node); it needs the CUDA toolkit (nvcc) + MSVC on this PC, or a build on another machine.

## Known deviation
Slice-index near-ties: when two calibration slices have SSD within ~1e-5 (LabVIEW's single-precision radial profile
vs our double), the chosen index can differ by one and z by a few 1e-3 um (1 frame of 10,043 in this recording).
Inherent to any implementation that is not bit-identical to LabVIEW.

## Files
`tools/gpu/{fixture,ref_numpy,ref_cupy,check_all,check_cupy,cuda_env}.py`, `tools/bench/{spec_read*,spec_dump,
capture_harness_inputs,subvi_harness,blackbox_z,quad_probe,radial_probe*}.py`, logs copied here.

## Addendum 2026-09-08 00:5x — the user's three-way comparison, measured IN LabVIEW (fixture, 200 frames, 5 beads)
Method: three script-built harnesses (`tools/recipes/build_harness_variant.py`) sharing loader + IMAQ ReadFile + cosine
windows: HARNESS_base (no kernel), HARNESS_seq (original four-fold sequential kernel READONLY_fourfold_COPY),
HARNESS_par (PARALLEL_kernel_v3 with the dead four-fold code removed, P=4). Same frames/inputs, interleaved order,
`tools/bench/run_timing.py`; kernel time = median(harness) − median(base) so COM Run + file read + windows cancel.
Outputs of both kernels == the LabVIEW reference (worst |dev| 0.0) → the cleaned v3 is functionally verified.

| executor | harness median | kernel (median − base) | per bead | speed-up vs sequential |
|---|---|---|---|---|
| (base: COM + IMAQ ReadFile + windows) | 5.56 ms | — | — | — |
| 1. original VI, sequential (four-fold) | 13.71 ms | **8.15 ms/frame** | 1.63 ms | 1.0× |
| 2. new VI, CPU parallel (v3 clean, P=4) | 7.98 ms | **2.43 ms/frame** | 0.49 ms | **3.35×** |
| 3. GPU (CUDA DLL in LabVIEW, 2026-09-08) | 14.7–16.4 ms | **≈ 9.5 ms/frame** (DLL itself 5.2 ms; 1.5 ms from Python) | ≈1.9 ms | ≈0.85× — see ../bench-2026-09-08-gpu-in-labview/REPORT.md |
| (Python CuPy prototype, 5 beads, not in LabVIEW) | — | 16.7 ms (launch-overhead bound) | 3.3 ms | 0.5× |
| (Python CuPy prototype, 500 beads batch) | — | 39.5 ms | 0.079 ms | 20× per bead |

Means are inflated by rare outliers (sd 17–46 ms: Windows scheduling / first-frame file cache); medians are the estimate.
Dead code found and removed from v3 (`tools/bench/v3_structure.json`): For Loop 248 (2 × 2-bead kernels per 4-pack) and
Case 107 (0–3-bead remainder) — six kernel instances that still executed; the timed v3 has only the P=4 loop.
