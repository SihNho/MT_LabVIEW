---
type: narrative
status: historical
date: 2026-09-14
tags: [archive]
---

# Display-path cost on the fixture — 2026-09-14 (autonomous loop, unattended)

## What was tested

The main VI's image display route (diagram 99: `IMAQ ImageToArray` → `Flatten Pixmap.vi` → `Draw Flattened Pixmap.vi`
→ Picture indicator), rebuilt stage by stage as five harness VIs on a recorded 1280×1024 8-bit fixture frame set, so
each stage's cost is the difference between consecutive harnesses. Acquisition (`IMAQdx Get Image`) is **not** in the
chain — a file read replaces it (peer review). The IMAQ Image Display control route was **not** measured (no donor
control in the scripted fleet).

| harness | chain |
|---|---|
| disp0 | `IMAQ Create` → `IMAQ ReadFile(File Path)` — the loader (base) |
| disp1 | + `IMAQ ImageToArray` (U8) |
| disp2 | + `Flatten Pixmap.vi` |
| disp3 | + `Draw Flattened Pixmap.vi` → **Picture indicator** |
| disp4 | + `Draw Flattened Pixmap.vi`, output **unwired** (construction only) |

Built by script (`build_harness_display.py`, `derive_harness_disp4.py`; zero GUI; terminal names read off each node
with `node_terms`; saved only when every planned step succeeded — run 2 had saved an unwired tail, caught and fixed).

## Environment and method

- LabVIEW 2026 Q3, pid 1728; i5-10500 (6C/12T); fixture `G:\Data\SiHyeong\20260906 …\test\img*.tif`, 210 frames,
  asserted 1280×1024 mode L by PIL; frames alternate every run.
- One COM `Run` per frame, timed from Python (`perf_counter`), 10 warm + 200 timed per cell, median and p90.
  All 210 files pre-read once before any timed cell (run 1's first cell was a cold-cache artefact: 15.5 ms).
- Conditions: **closed** = front panel not open; **open** = front panel opened via COM (representative of the user
  running with the panel visible); **closed2** = the closed pass repeated last (reproducibility).
- Stage cost = median(dispk) − median(disp0) within a condition.

## Results (medians, ms per Run; `display_bench.json`)

| condition | disp0 base | disp1 | disp2 | disp3 (→Picture) | disp4 (no indicator) |
|---|---:|---:|---:|---:|---:|
| closed | 1.83 | 2.42 | 2.96 | 4.78 | 4.58 |
| open | 7.01 | 7.22 | 7.45 | **15.07** | 8.60 |
| closed2 | 1.88 | 2.46 | 3.02 | 4.76 | 4.52 |

| stage | closed | open |
|---|---:|---:|
| ImageToArray | +0.6 | +0.2 |
| Flatten Pixmap | +0.5 | +0.2 |
| Draw Flattened Pixmap (construction, disp4 − disp2) | +1.6 | +1.2 |
| Picture indicator write/paint (disp3 − disp4) | +0.2 | **+6.5** |
| whole route (disp3 − disp0) | **2.9** | **8.1** |

## Reading

1. **The visible paint dominates.** With the panel open, writing a 1280×1024 picture to the Picture indicator costs
   ≈6.5 ms per update — alone above the 6 ms/frame budget at 150 Hz. With the panel closed it is 0.2 ms.
2. **Construction is ~2.7 ms of CPU regardless** (ImageToArray 0.6 + Flatten 0.5 + Draw 1.6), i.e. ~45 % of the
   budget even when nothing is painted.
3. **Confound, stated:** the open-panel base rises from 1.8 to 7.0 ms — that is the cost of a COM `Run` on a VI whose
   panel is visible, not a per-frame cost of the real loop; only within-condition deltas are used above. One COM Run
   per frame can also exaggerate allocation/synchronisation relative to a persistent in-VI loop (peer review), so the
   absolute deltas are upper bounds; the ordering (paint ≫ construction ≫ copy) is robust across closed/open/closed2.

## What it decides

For restructure 4.6 the display must be a **separate, decimated loop** (`Last`-mode consumer; the 2026-09-12 ring
measurement already showed `Last` turns the cliff into a slope) — at ~10–20 Hz the paint costs 65–130 ms/s of one
core, at 150 Hz it cannot be paid. Whether the **IMAQ Image Display control** (image reference wired directly, no
ImageToArray/Flatten/Draw) is cheaper remains unmeasured and is the first thing to test when a donor control exists.

## Addendum 14:1x — the IMAQ Image Display route (INDEX row 25)

`HARNESS_dispI` = disp1's chain with ReadFile's `Image Out` also wired into an **IMAQ Image Display** indicator (donor:
NI's `Acquire Single Image (Snap).vi` copy; wired by the new `OpConnectCtl_v0`, since erdosmiller's Wire Indicators
cannot address a Vision control). Same method, same session (`run_dispI_bench.log`):

| condition | disp0 | disp1 | disp3 (Picture) | dispI (Image Display) | Picture route (disp3 − disp0) | Image Display (dispI − disp1) |
|---|---:|---:|---:|---:|---:|---:|
| closed | 1.87 | 2.41 | 4.74 | 3.44 | 2.87 | **1.03** |
| open | 6.86 | 7.06 | 14.87 | 13.98 | 8.01 | **6.92** |
| closed2 | 1.87 | 2.42 | 4.82 | 3.54 | 2.94 | **1.13** |

The native control **removes the picture construction** (≈1.9 ms CPU per frame saved) — its terminal write costs
~1.0 ms even with the panel closed — but **painting it while visible costs about the same (~7 ms per update)**. So the
decision above does not change: the display is a separate, decimated loop; the Image Display is the better route for
it (less CPU per shown frame, no ImageToArray/Flatten/Draw), and `Synchronous Display` remains unmeasured.

## Verification level

Functional numbers on the real fixture; harnesses structurally verified (ExecState 1, every planned wire present).
Not a run of the main VI itself. Peer reviews: `archive/peer/2026-09-14-display-path-harness-plan.md`,
`…display-harness-build-run2.md`, `…display-bench-results.md`. Raw: `run_display_bench.log`, `display_bench.json`.
