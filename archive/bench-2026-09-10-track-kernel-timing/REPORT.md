---
type: narrative
status: historical
date: 2026-09-10
tags: [archive]
---

# TRACK_kernel_v1 timing: what the backend switch costs, measured against the bare kernels

Date 2026-09-10 18:5x–19:0x · rig PC (LabVIEW 2026 26.3.1f1 64-bit, i5-10500, RTX 2060, SM clock locked 1365 MHz by the logon
task) · fixture cal002, 5 beads, 60 slices, 1280×1024 U8 frames · reference = the LabVIEW tracking kernel's own `.tra` output.
Driver `tools/bench/track_bench.py`, 3 repeats × 2 backends × 200 chained frames, fresh LabVIEW per repeat.

## Why this benchmark exists

INDEX row 17 proved TRACK_kernel_v1 runs both backends correctly, but its timing rows were unusable because the machine was
busy. The open question was simple: **does wrapping the two kernels in a Case Structure cost anything?** If it does, the
convenience of one selectable subVI has a price the rig pays on every frame.

## Method

Each repeat: restart LabVIEW, deploy the DLL and its calibration fallback, pull all 200 frame files into the OS cache, record
nvidia-smi clocks, then run `base` (no kernel), `par` (PARALLEL_kernel_v3), `gpuk` (GPU_kernel_v1) and `track`
(TRACK_kernel_v1) interleaved on the same frames. Kernel time = median(harness) − median(base). The backend is the saved
default of TRACK's `index` control, set once per block in its own COM session, after which LabVIEW is restarted (a VI-Server
touch of a subVI inflates its call by ~9 ms, docs/NAMES.md).

## Result

Kernel ms/frame, median of 200 frames per repeat.

| backend | rep | base | par | gpuk | track | **K par** | **K gpuk** | **K track** |
|---|---|---|---|---|---|---|---|---|
| 0 = CPU frame | 1 | 4.83 | 7.13 | 6.92 | 7.62 | 2.30 | 2.09 | **2.79** |
| 0 | 2 | 4.75 | 7.67 | 6.86 | 7.59 | 2.92 | 2.11 | **2.84** |
| 0 | 3 | 4.94 | 7.82 | 6.76 | 7.81 | 2.87 | 1.82 | **2.87** |
| 1 = GPU frame | 1 | 4.74 | 7.26 | 6.80 | 7.88 | 2.52 | 2.06 | **3.14** |
| 1 | 2 | 4.77 | 7.40 | 6.75 | 7.81 | 2.63 | 1.98 | **3.04** |
| 1 | 3 | 4.87 | 7.60 | 6.82 | 7.82 | 2.73 | 1.95 | **2.94** |

Medians of the three repeats:

| backend | track | the same kernel, bare | overhead |
|---|---|---|---|
| 0 (CPU) | 2.84 | par 2.87 | **0.0** |
| 1 (GPU) | 3.04 | gpuk 1.98 | **+1.06** |

Functional, every repeat: `par` deviation **0.00** against the reference; `gpuk` **2.93e-6 µm in z**; `track` **0.00** with
backend 0 and **2.93e-6** with backend 1, i.e. bit-identical to whichever kernel its frame contains.

## What it means

**The Case Structure itself is free.** On the CPU backend the selectable kernel matches the bare kernel within run-to-run
variation, which is about 0.25 ms on this machine. Shipping one subVI with a switch costs nothing on the path the rig uses today.

**The GPU frame carries about 1 ms.** That is reproducible across three repeats and larger than the variation, but its cause is
NOT established here. It is not the case structure, or backend 0 would show it too. The obvious next test is to split the DLL's
own time from the LabVIEW side with the per-frame DLL log, which failed to record this run (see below).

At 5 beads the practical ranking is unchanged: CPU-parallel and GPU are equivalent, and the GPU's advantage remains that its
cost is nearly bead-count independent (INDEX row 16).

## Two non-results and a bug, recorded

1. **The first attempt (18:4x) is void.** It produced `base` 26.68 ms against `par` 10.83, i.e. the harness with no kernel
   slower than the harness with one, and kernel times came out negative. Standard deviations were 71 to 294 ms. Cause: CPU
   contention. HWMonitor had been left running from the power-supply diagnosis at roughly 12% of a core, alongside a browser
   and Ollama. The run was stopped, not reported as data.
2. **The disk hypothesis was wrong.** The suspicion was that the fixture, which lives on G: (a Storage Space backed by a 4 TB
   spinning HDD), made `base` pay a physical read while the other three hit the cache, since `base` always runs first for each
   frame. A cache-warming pass was added and it completes in **0.2 s for 262 MB**, proving the frames were already in RAM. The
   warming is kept because it makes the condition explicit and costs nothing, but contention, not the disk, was the culprit.
   `track_bench.py` now also flags any repeat where `base` is slower than a kernel row as a non-result automatically.
3. **The DLL per-frame log did not record.** `MT_GPU_LOG` was set after `lv_restart` rather than before, so LabVIEW never
   inherited it and every `dll_ms` came back null. Fixed in the driver; the DLL-internal split is missing from this run only.

Side observation: the GPU memory clock reads 7000 MHz in P0 before every repeat and 6801 MHz in P2 after it. The logon task
locks the SM clock only, not memory.

## Follow-up: where the GPU frame's extra millisecond lives (same day, 20:0x)

The +1.06 ms was chased with `tools/bench/gpu_overhead_probe.py`: three 200-frame cells, each a fresh LabVIEW with the
frames pre-cached and the DLL's own per-frame log enabled (the `MT_GPU_LOG` ordering bug above is fixed, so the log records).

| cell | gpuk kernel ms | track kernel ms | DLL internal median ms (total / upload / kernel) |
|---|---|---|---|
| A `gpuk` alone | 2.63 | | 1.668 / 0.394 / 1.127 |
| B `track` alone | | 4.47 | 1.686 / 0.401 / 1.074 |
| C both, one session | 2.20 | **3.55** | 1.615 / 0.401 / 1.024 |

**The hypothesis under test was wrong.** The benchmark calls the GPU twice per frame on backend 1, once through `gpuk` and
once through `track`, with `track` always second, so the extra millisecond looked like the price of being the second caller.
Cell B removes the other caller entirely and `track` is still slower; cell C reproduces the gap inside one session.

**The DLL is not involved.** Its self-reported time is 1.62 to 1.69 ms in all three cells, upload and kernel included. So the
whole difference is on the LabVIEW side of the wrapper: `gpuk` spends 0.6 to 1.0 ms there, `track` spends 1.9 to 2.8 ms.

**The surviving explanation is a host-side data copy in TRACK's GPU frame**, the candidate a peer review named
(archive/peer/2026-09-10-track-gpu-frame-1ms.md): a case tunnel or a non-const CLFN pointer parameter extends a value's
lifetime, so LabVIEW's compiler cannot reuse the buffer and inserts a copy. It stays a hypothesis. Localizing it needs
LabVIEW's edit-time **Show Buffer Allocations**, which has no scripting API, and it is not worth that today because the
deployment route below costs nothing.

**Also learned: absolute kernel times are not comparable across cells.** `gpuk` measured 1.98 in the row-18 runs, 2.63 alone
and 2.20 in cell C. Only comparisons made inside one pass mean anything, which is exactly why cell C is the one that counts.

**Deployment consequence.** `PARALLEL_kernel_v3.vi` and `GPU_kernel_v1.vi` are separate subVIs that already share the
tracking kernel's connector pane, and the main VI has a single kernel call site (MAIN_VI_MAP node 39, uid 5058). Swapping
which subVI sits there costs **zero** overhead and is the intended way to choose a backend. TRACK_kernel_v1 stays useful for
the CPU path, where it costs nothing, and as a convenience when 1.4 ms does not matter.

## Files

`track_bench.log` (full log including the void first attempt) · `track_bench_results.json` · `track_bench.py` (the driver, with
the cache-warm, contaminant check and automatic non-result flag).
