---
type: narrative
status: historical
date: 2026-09-07
tags: [archive]
---

# Fixture acceptance of the parallel tracking kernel — 2026-09-07

## What the test is
Rule-1a gate: the parallel kernel (`PARALLEL_kernel_v3.vi`, P=4 For loop, one reentrant `Track 1 of N bds
xyz-kernel-reentrant.vi` per bead) must produce exactly the numbers of the original four-fold kernel
(`Track N beads four-fold over-kernel-v3.vi`, via the byte-identical `READONLY_fourfold_COPY.vi`) on the same
inputs. Inputs are real recorded data; no instrument is touched.

## Data (user-recorded, G:\Data\SiHyeong\20260906 Kimlab - 50bp 16X WT 90Hz 1p2 Ramp_Newbatch\test)
- 10,044 `imgNNNNN.tif` (1280×1024, 8-bit grey), written per frame by the working-copy main VI.
- `cal002`: LabVIEW-flattened calibration cluster (5 beads: xy, 5×60×119 stack, cross length 120 px, z step 0.1 µm,
  84 nm/px, 60 slices, 20 averages).
- `tra002-000`: 385-B text header + little-endian doubles: 1 lead value, then 10,043 rows × 18
  (frame, trans, rot, x1,y1,z1 … x5,y5,z5). Frame numbers = tif names (gaps = dropped frames).

## Harness (all built by VI Scripting from Python, zero GUI clicks)
- `HARNESS_loadcal.vi` = lab loader `Load and prep N cal images.vi` with its File Dialog replaced by a path control.
- `HARNESS_compare.vi` = loader + IMAQ Create/ReadFile + `make both cosine bandpass.vi` (cross length) → both kernels
  on identical Image / cal clusters / windows / cross size / x,y,z array / good flags / cal position.
- `run_fixture_compare.py`: per frame — run, assert v3 == four-fold bit-for-bit, compare both with the .tra row,
  feed the four-fold outputs back as the next frame's state (what the main VI's shift registers do).

## Criteria
PASS = every frame: v3 output identical to four-fold (exact float equality) AND max |kernel − .tra| ≈ 0.

## Results
- 03:0x (v3 as built 2026-09-01): FAIL. Four-fold vs .tra: 0.0000 on all beads (inputs reconstructed exactly).
  v3: every bead (−16.63, −21.24, 5.9) = four-fold(starting x,y = 0) → `starting x/y` unwired in the loop.
- 14:0x fix by script: two auto-indexed tunnels Decimate→kernel (OpConnect2 + set_index_mode) on a copy, swapped in
  (backup `PARALLEL_kernel_v3.vi.bak_20260907_prefix`).
- 14:1x: 20/20 frames identical, dev vs .tra 0.00000, 44 ms/frame (harness overhead incl.).
- Full run (10,043 frames): see `fixture_compare_full.log` / summary line appended below when done.

## Files
`run_fixture_compare.py`, `build_harness_compare.py`, `build_harness_loadcal.py`, `fix_v3_starting_xy.py`,
`harness_compare_labels.json`, `fixture_compare_results.jsonl` (per-frame rows), docs/keystone-op-spec.md §29–§34.

## Full run result (14:2x–14:5x, tools/bench/fixture_compare_full.log)
`SUMMARY frames=10043 identical=10043 different=0 worst_dev_vs_tra=1072.28 at frame 11801 mean_run=23 ms`
- **v3 == four-fold on all 10,043 frames (exact float equality on x,y,z, good flags and cal position).**
- Both kernels == .tra to 0.00000 on frames 4 … 11796 (10,017 frames).
- Frames 11797–11824 (the last 26 frames of the recording): ALL five beads are lost simultaneously (z at the last
  slice, good=False, kernel returns −1) — the end of the experiment. The recording marks −1 on 13 of those rows
  (11798, 11800, 11804, …) and the harness on the alternating rows, i.e. the same lost-bead events one frame
  apart: the main VI's bead-reset / good-flag state machine differs from the driver's plain feedback of the
  previous outputs. This is driver state semantics after total bead loss, not kernel arithmetic (both kernels
  agree exactly there too).
**Verdict: PASS** for rule 1a — the parallel kernel computes exactly what the original computes.

## Rerun with the main VI's reseed rule (16:1x–16:3x, tools/bench/fixture_compare_full2.log)
The driver now applies the tracking loop's Case-5540 rule read from the working copy (spec §35): after a frame
whose kernel output contains a lost bead (−1), the next frame is seeded with the calibration bead positions and
all-TRUE good flags. `SUMMARY frames=10043 identical=10043 different=0 worst_dev_vs_tra=0.00000 mean_run=19 ms`
— **every one of the 10,043 frames now matches the recording exactly, bead-loss frames included, and v3 ==
four-fold bit-for-bit throughout.** Final verdict: PASS with no residual.
