---
type: narrative
status: historical
date: 2026-09-09
tags: [archive]
---

# GPU DLL inside LabVIEW — row 3 of the three-way comparison (2026-09-08)

## What was tested
The CUDA tracking DLL (`tools/gpu/cuda/mt_track.cu`, fused kernels + cuFFT, numerically accepted against the LabVIEW kernel on
2026-09-07) called **from LabVIEW 2026** through a Call Library Function Node, on the same fixture frames, driver and harness
scheme as rows 1–2 (archive/bench-2026-09-07-gpu-reference/REPORT.md addendum). Question: kernel time per frame in LabVIEW,
and whether the outputs still match the LabVIEW reference.

## Environment
Windows 10, LabVIEW 2026 Q3 (64-bit), RTX 2060 6 GB, NVIDIA 616.64, CUDA 12.6.3 (cudart64_12 + cufft64_11 next to the DLL),
VS Build Tools 2022; fixture G:\Data\SiHyeong\20260906 …\test (1280×1024 8-bit frames, cal002, 5 beads, cross 120, 60 slices).
No instrument was touched (motor/piezo never actuated).

## Harness (script-built, zero GUI)
`HARNESS_gpu.vi` (claudeDev) = HARNESS_loadcal + IMAQ Create/ReadFile + `make both cosine bandpass` + Omars IMAQ ImageToArray
(+ 'Optional Rectangle' control = whole image) → **Build Array (1 input, 2-D→3-D)** → the Saleh-lab CLFN copied out of
`TrackBatchOfImagesWithGPU.vi` (path in = "Debug\GPU Tracking.dll"). The node's parameter types are fixed by the donor
(I32 arrays, U8 3-D image, SGL 2-D outputs, DBL calibration clusters, C string, SGL window) — see docs/gpu-backend.md for the
contract the DLL adopted (integer x,y in via 'X Array'; x,y,z out losslessly encoded as 3 SGL integers each in 'X Output').
Timing: `tools/bench/run_timing.py --n=200 --harness=base --harness=gpu`, interleaved with HARNESS_base (no kernel), state
chained frame to frame exactly like rows 1–2; kernel time = median(harness) − median(base). The DLL also reports its own
elapsed time (QueryPerformanceCounter) and per-phase times in the status string.

## Criteria
Outputs vs the LabVIEW reference (fixture_compare_results.jsonl): x,y within 1e-6 px, z within ~1e-4 µm (user's tolerance).

## Results (200 frames, 5 beads; medians — means carry Windows-scheduling outliers)

| run | base | gpu harness | **gpu − base** | DLL-internal | phases (u / k / d / event) | outputs vs reference |
|---|---|---|---|---|---|---|
| chain 8 (first working) | 7.98 | 16.42 | 8.44 | — | — | 2.93e-6 |
| chain 9 (big-array indicator wires removed) | 4.84 | 11.59 | 6.76 | — | — | 2.93e-6 |
| chain 10 | 5.84 | 16.19 | 10.35 | 5.43 | — | 2.93e-6 |
| chain 11 | 5.27 | 14.69 | 9.42 | 5.25 | 1.58 / 3.40 / 0.18 / — | 2.93e-6 |
| chain 12 | 5.60 | 16.07 | 10.47 | 5.35 | 1.71 / 3.43 / 0.21 / 3.33, ui=1 | 2.93e-6 |
| chain 13 (CUDA on a DLL worker thread) | 6.21 | 15.73 | 9.53 | 5.21 | 1.56 / 3.42 / 0.19 / 3.31 | 2.93e-6 |
| (same DLL from Python, tight loop or 5–20 ms gaps) | — | — | — | **1.4–1.7** | 0.34 / 0.96 / 0.11 / 0.89 | 2.5e-6 |

(ms per frame; u = host→device upload of the 1.3 MB image, k = kernels+FFTs to sync, d = readback, event = cudaEvent GPU time.)

**Three-way table, in LabVIEW, 5 beads:**

| executor | kernel (median − base) | per bead | vs sequential |
|---|---|---|---|
| 1. original VI, sequential (four-fold) | 8.15 ms/frame | 1.63 ms | 1.0× |
| 2. new VI, CPU parallel (v3, P=4) | **2.43 ms/frame** | 0.49 ms | **3.35×** |
| 3. GPU (CUDA DLL via CLFN) | **≈ 9.5 ms/frame** (6.8–10.5 across runs; DLL itself 5.2–5.4) | ≈1.9 ms | ≈0.85× |

Functional: the GPU path reproduces the LabVIEW reference on all 200 chained frames (x,y exact to 1e-6 px; worst |dz| 2.93e-6 µm).

## Interpretation (with the failed-prediction review, archive/peer/2026-09-08-cuda-dll-slower-in-labview.md)
- At 5 beads the GPU path is **slower than the CPU-parallel VI** and about equal to the original: the work is ~25 GPU API calls per frame (9 kernel launches, 6 cuFFT executions, 9 memcpys — the
  algorithm is a sequential pipeline FFT→window→IFFT→peak ×3 then radial FFT/IFFT), so per-call overhead dominates (already seen in Python: GPU wins only from ~50 beads/frame).
- Inside LabVIEW the DLL runs **3.5× slower than the identical call from Python** (5.3 vs 1.5 ms), uniformly in every phase,
  and the cudaEvent GPU time itself is 3.3 vs 0.9 ms. Ruled out by measurement: GPU clock ramp-down between calls (Python with
  5–20 ms gaps stays at 1.66 ms); the CLFN's UI-thread execution (ui=1) as the cause — moving the CUDA work to a DLL-owned
  worker thread changed nothing. Remaining explanation: a per-call host-side delay inside the LabVIEW process (~25 API calls per frame) — cause not
  determined (CPU contention with LabVIEW's UI/execution threads, thread/process priority, or per-process WDDM scheduling).
  NOTE: LabVIEW draws its panels on the CPU (GDI), so "LabVIEW's own GPU use" is NOT a valid explanation (user's correction,
  2026-09-08). Cheapest discriminators: a one-launch micro-benchmark inside the DLL in both processes; raising the DLL
  worker's thread priority; calling the DLL from Python with busy background threads.
- The remaining harness overhead (gpu − base − DLL ≈ 4 ms) is LabVIEW-side: ImageToArray copy, Build Array copy, the CLFN call
  and the SGL coercions. Removing the placeholder indicator wires (1.3 MB image copy) saved ~1.7 ms.

## What would make the GPU row competitive (not done)
Fewer launches (one kernel per frame doing the whole per-bead pipeline in shared memory with an in-kernel 120-point FFT: 1 launch + 2 memcpys instead of ~25 calls; ~50 beads amortise the current launch floor), pinned host memory for the image,
a zero-copy image path (IMAQ pixel pointer instead of ImageToArray + Build Array), "Run in any thread" on the CLFN
(CallLibrary.'Any Thread?' 636D403 — scriptable per the LabVIEW Wiki, unverified here), and the per-launch-delay question above.

## Files
Logs `gpu_chain8..13.log` (each: restart, deploy, [smoke], 200-frame timing), `gpu_dump_chain.log` (raw handle dump that fixed
the layout), DLL sources (`mt_track.cu`, `cal_file.inc`, `dump.inc`, `mt_track.def`, `build.bat`), offline test `test_dll_lv3.py`,
timing driver `run_timing.py`, harness labels. Toolkit ops built for this row: OpBuildBA_v0 (Build Array placer), plus the
findings in docs/gpu-backend.md (fixed CLFN types, byte-dumped handle layout, junk-Invoke rule).

## Addendum 12:1x — fused single-launch kernel, and the root cause of the in-LabVIEW slowdown

| run | what | gpu − base | DLL-internal | phases u / k / event | note |
|---|---|---|---|---|---|
| chain 14 | fused v1 (direct DFT) | 8.30 | 6.28 | 1.59 / 4.43 / 4.38 | one launch per frame: no faster → launch count exonerated |
| chain 15 | classic + CPU probe | 13.15 | 5.16 | 1.53 / 3.38 / 3.33, CPU probe 6.11 ms (Python 6.19) | host thread at full speed |
| chain 16 | fused v2 (two-stage DFT) | 6.85 | 5.31 | 1.56 / 3.50 / 3.45 | offline: 1.41 ms, event 0.89 (= cuFFT path) |
| Python, 15 ms gaps, 12 s, nvidia-smi sampling | classic | — | **5.50** | event 3.40 | **P8 / 360 MHz 77 % of samples** — reproduces LabVIEW's number outside LabVIEW |

Root cause: the GPU clock governor holds P8 (360 MHz SM) under LabVIEW's duty cycle (~1 ms of GPU work per ~15 ms frame);
1365/360 = 3.8× is the measured ratio in every phase. LabVIEW holds only a compute context (nvidia-smi type C), priority and
affinity equal Python's. Fix = driver policy (NVIDIA Control Panel "Prefer maximum performance" for LabVIEW.exe, or admin
`nvidia-smi -lgc`), pending the user; re-timing follows. The fused kernel (fused.inc) is numerically identical to the 25-call
path (2.3e-13) and stays the default: at P2 clocks it should give ≈ 1.4 ms DLL time in LabVIEW as well.

## Addendum 2026-09-09 — with the GPU clock locked (`nvidia-smi -lgc 1365,1905`, admin, by the user)

| run | clocks | gpu − base | DLL-internal | upload / kernel / GPU event |
|---|---|---|---|---|
| chain 18 | governor (P8 at LabVIEW's duty cycle) | 10.70 | 5.13 | 1.54 / 3.38 / 3.33 |
| chain 17 | clocks up by coincidence (busy machine) | (6.70, noisy base) | 1.73 | 0.50 / 0.94 / 0.88 |
| **chain 19** | **SM locked 1365 MHz** (mem still governor: 810 ↔ 6801) | **5.41** | **2.12** | 0.96 / 0.96 / 0.90 |
| (Python tight loop, reference) | P2 1905 / 6801 | — | 1.12 | 0.33 / — / 0.64 |

The kernels now run at full speed inside LabVIEW (event 0.90 ms = Python); the upload is still 3× slower than in a tight loop
because the memory clock cannot be locked on this card (`nvidia-smi -lmc`: "Setting locked Memory clocks is not supported"
for the RTX 2060, 2026-09-09) — P5 810 MHz between frames is the floor. FINAL row 3: 5.41 ms/frame, DLL 2.12 ms. The remaining gpu − base − DLL ≈ 3.3 ms is LabVIEW-side (ImageToArray + Build Array copies, CLFN call, SGL coercions).

**Three-way table, in LabVIEW, 5 beads (updated):** sequential 8.15 · CPU-parallel v3 **2.43** · GPU DLL 5.41 (DLL itself 2.12;
1.1 possible with the memory clock up). At 5 beads the CPU-parallel VI stays the fastest; the GPU path's per-bead cost is now
~0.2 ms of GPU time plus ~4 ms of fixed LabVIEW/DLL overhead, so it wins only when bead count grows (≈ 20+ beads).
Root-cause chain (launch count → host thread → UI thread → graphics context → **GPU P-state / memory clock**) and the failed
keep-alive attempts are in docs/gpu-backend.md; nvidia-smi samples in `nvsmi_lowduty_pstate.csv`; `regime_test.py` reproduces
the duty-cycle effect from Python in 60 s.

## Addendum 2026-09-09 (2) — memory clock held up by a DLL keep-alive (SM lock + 64 MB D2D copy per ms on a side stream)

`nvidia-smi -lmc` is unsupported on the RTX 2060, so the DLL keeps the memory clock at P2 itself: a host thread issues a
64 MB device-to-device copy every ~1 ms (opt-in: MT_GPU_KEEPALIVE=1 in LabVIEW's environment, or `mt_gpu_keepalive(1)`).
Python sweep (`keepalive_mem_test.py`, 15 ms gaps, SM locked): none 2.32 ms / 27 W · 8 MB/ms 2.30 (still P5) · **64 MB/ms 1.64 ms,
34 W** · 128 MB continuous 2.56 ms, 80 W (steals bandwidth).

| run | clocks | gpu − base | DLL-internal | upload / kernel / event |
|---|---|---|---|---|
| chain 19 | SM locked | 5.41 | 2.12 | 0.96 / 0.96 / 0.90 |
| **chain 20** | **SM locked + keep-alive 64 MB/ms** | see log (base 5.56, gpu 10.70 → **5.14**) | **1.58** | 0.41 / 0.91 / 0.88 |

The DLL now runs inside LabVIEW as fast as in a tight Python loop (1.58 vs 1.12–1.4 ms). What remains of the GPU row
(≈ 5.1 ms) is LabVIEW-side: ImageToArray + Build Array copies of the 1.3 MB frame and the CLFN call (~3.5 ms). Final three-way
(5 beads): sequential 8.15 · CPU-parallel 2.43 · GPU 5.1 (DLL 1.6).
