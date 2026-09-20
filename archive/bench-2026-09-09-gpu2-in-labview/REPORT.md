---
type: narrative
status: historical
date: 2026-09-09
tags: [archive]
---

# GPU tracking, our interface (v2) called from LabVIEW — HARNESS_gpu2 vs HARNESS_base, 200 chained frames

Date 2026-09-09 13:3x · rig PC (Windows 10, LabVIEW 2026 26.3.1f1 64-bit, RTX 2060, driver 616.64, SM clock locked 1365–1905 MHz
by the logon task, P0 during the run) · fixture `G:\Data\SiHyeong\20260906 ... \test` (cal002, 5 beads, 60 slices, zstep 0.1 µm,
1280×1024 U8 frames) · reference = the LabVIEW tracking kernel's own output on the same frames (`.tra`).

## What was tested

Row 3 of the three-way comparison, re-done with the interface designed for this rig (user 2026-09-09: *"Saleh꺼 따라하지 마 …
최적으로"*), instead of the Saleh-lab donor node used on 2026-09-08:

- **HARNESS_gpu2.vi** (built entirely by script, `tools/recipes/build_harness_gpu2.py`): IMAQ Create → IMAQ ReadFile → IMAQ
  GetImagePixelPtr → **one Call Library Function Node** `mt2_track_simple` (claudeDev\Debug\mt_track.dll; 15 parameters configured by
  `gscript.build_clfn` through NI's import-wizard scripting VIs). The frame is passed as the IMAQ buffer's raw pixel pointer + line
  width — no LabVIEW-side image copy; x,y,z in/out as DBL arrays; calibration and windows loaded on the GPU once by the DLL.
- **HARNESS_base.vi**: the same IMAQ Create + ReadFile without any kernel (file read + COM Run overhead).
- Driver `tools/bench/run_gpu2.py`: per frame the chained state (previous frame's x,y,z and good flags from the reference), both
  harnesses run in alternating order, outputs compared with the reference per bead (skipping beads the reference lost).

## Result

| | median ms/frame | mean | sd |
|---|---|---|---|
| HARNESS_gpu2 (file read + GPU call) | **5.70** | 11.19 | 16.17 |
| HARNESS_base (file read only) | 4.56 | | |
| **GPU v2 in LabVIEW = gpu2 − base** | **1.14** | | |
| DLL-internal (status string `t=`) | 1.62 (upload `u=` 0.38, kernel `k=` 1.11, GPU events `e=` 0.88) | | |

Numbers are from the shipped (abort-safe) build; the first run of the same harness, before the abort-safety changes, gave
1.12 ms/frame with DLL 1.64 — identical within run-to-run scatter.

Functional (200 frames, 5 beads, vs the LabVIEW reference): worst |dx| 4.9e-7 px, |dy| 2.5e-7 px, |dz| 2.9e-6 µm, **0** slice-index
flips, **0** good-flag mismatches. Acceptance (1e-6 px x,y; ~1e-4 µm z) met.

Both harnesses were slow for the first ~50 frames (gpu2 9.25 / base 7.35 ms medians, then 5.34 / 3.86) — a LabVIEW/COM warm-up
common to both; the paired difference is flat (1.17 → 1.16 ms).

### Three-way comparison, final (LabVIEW, 200 frames, 5 beads, ms/frame above the base harness)

| path | ms/frame | notes |
|---|---|---|
| original sequential (four-fold) | 8.15 | 2026-09-08 |
| CPU-parallel v3 (P = 4) | 2.43 | 2026-09-08 |
| GPU DLL through the Saleh donor node | 5.14 | 2026-09-08 (DLL 1.58; ~3.5 ms of LabVIEW-side copies) |
| **GPU DLL, our interface v2** | **1.14** | this report (DLL 1.62 incl. 0.38 upload) |

## What it took (facts, all in docs/gpu-backend.md / docs/NAMES.md)

1. NI `Create.vi` kills LabVIEW when its `Parameter Info` global is empty → OpCLFNParams_v0 fills it from flattened bytes
   (layout decoded from the type descriptor; composer `tools/gpu/clfn_params.py`).
2. The deployed DLL predated the v2 API; a DLL file name with a space (`GPU Tracking.dll`) leaves a scripted CLFN broken → `mt_track.dll`.
3. IMAQ GetImagePixelPtr's `Function` ring is a required input; a scripted CLFN's argument inputs are required until wired.
4. Pinning LabVIEW's IMAQ buffer (`cudaHostRegister`) gave 32 ms/frame and stale-frame results → DLL-owned pinned staging buffer.

## Abort safety (the rig's real stop gesture)

The experiment VI is normally stopped with LabVIEW's Abort button, so `mt2_close` never runs. Abort ends the VI, not the process:
the CLFN call returns normally (~2 ms), the DLL stays loaded, the GPU context survives. Two nets cover what Abort skips —
`mt2_open` closes any context the DLL still holds (single-context policy), and the keep-alive thread parks itself after
`mt_gpu_keepalive_idle` ms without a track call and wakes on the next one. Verified (`test_abort.log`): 12 open-without-close
cycles → **0 MB** GPU-memory drift with unchanged results; keep-alive state 1 → 2 (parked, 2.5 s idle) → 1 (next track).

## Files

`gpu2_chain.log` (restart → deploy → run), `run_gpu2_results.json` (per-frame times, both harnesses), `harness_gpu2_labels.json`,
`paraminfo_mt2.hex` (the 15-record Parameter Info), `run_gpu2.py`, `build_harness_gpu2.py`, `clfn_params.py`, `mt2.inc`
(DLL v2 source at the time of the run; full source tools/gpu/cuda/).
