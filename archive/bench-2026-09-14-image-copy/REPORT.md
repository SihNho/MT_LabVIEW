---
type: narrative
status: historical
date: 2026-09-14
tags: [archive]
---

# Reference-safe image copy cost (IMAQ Copy) — 2026-09-14 (autonomous loop)

## Question (restructure gate G4)

An IMAQ image is a reference to a buffer the camera ring reuses; a consumer that runs later than the acquisition loop
(a decimated display, the file writer) must either copy the image at selection time or risk reading overwritten pixels
(NI: copy the acquisition image and release the ring reference so acquisition continues — peer review). What does that
copy cost per 1280×1024 U8 frame?

## Harnesses (script-built, zero GUI; `build_harness_copy.py`)

| harness | chain |
|---|---|
| copy0 | `IMAQ Create` (A) → `IMAQ ReadFile(File Path)`; `IMAQ Create` (B) — two allocations, no copy |
| copy1 | + `IMAQ Copy` (A → B) from `LVAddons\nivision\1\vi.lib\vision\Management.llb` (run 1 looked in the runtime's Basics.llb: error 7) |

## Method

One COM `Run` per frame timed from Python (`perf_counter`), 210 fixture frames pre-read, 10 warm + 200 timed, panels
closed, two passes; the display bench's disp0/disp1 re-timed in the same session. Cost = median(copy1) − median(copy0).
**Label: cold first copy** — each Run creates B afresh, so the copy pays B's first 1.3 MB pixel allocation (peer
review: `IMAQ Create` allocates lazily). A steady-state cell (N copies inside one Run) was designed but not built
(needs a For loop with a scripted N — open).

## Results (`copy_bench.json`)

| pass | copy0 | copy1 | **IMAQ Copy** | disp0 | disp1 | ImageToArray | 2nd Create |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1.91 | 2.31 | **0.41 ms** | 1.85 | 2.39 | 0.54 | 0.06 |
| 2 | 1.87 | 2.29 | **0.42 ms** | 1.80 | 2.41 | 0.60 | 0.07 |

## Reading

- A reference-safe copy of a frame costs **≤ 0.4 ms** (upper bound; steady state without the allocation is smaller).
  At a 10–20 Hz display it is 4–8 ms per second; copying every saved frame at 150 Hz is ~60 ms/s ≈ 6 % of one core.
- `IMAQ ImageToArray` (0.55–0.6 ms) is more expensive than `IMAQ Copy` and produces a LabVIEW array that the display
  route then flattens and draws (see `bench-2026-09-14-display-path`).
- G4 design consequence: **copy-on-demand at selection time** (display: newest frame when the display loop wants one;
  writer: every frame committed to saving) into a bounded pool, and never pass a bare ring reference to a consumer that
  can stall. The 0.12 ms "acquisition copy" in the plan is a different thing (the driver's own transfer).

## Steady-state cell (added 14:3x; `build_harness_copyloop2.py`, `run_copyloop_bench.py`, `copyloop_bench.json`)

Harness `HARNESS_copyloop` = copy1 + `IMAQ GetImageSize` on A + a For loop whose count terminal is wired from
`Y Resolution` (= 1024 for the fixture) with `IMAQ Copy` A→B inside (B enters the loop from the outer copy's
`Image Dst Out`, so the outer, allocating copy always runs first). `HARNESS_copyloop0` = the same VI with the inner copy
deleted (1024 empty iterations). Steady-state cost = (median(copyloop) − median(copyloop0)) / 1024.

How the loop got its N (the earlier OPEN item): erdosmiller `Create For Loop` with `Control Names` does **not** wire an
existing control (measured: loop created, no tunnel — `build_harness_copyloop.log`, reviewed); the empty loop node's
`Node.Terminals[]` holds exactly ONE unnamed sink, which is the count tunnel's outside terminal (peer:
`ForLoop:Loop Count → Tunnel:Outside Terminal`; the typed route needs a ForLoop-class reference we cannot cast yet).
`Terminal.Connect Wire` from the I32 source onto it put the same wire (uid 346) on both ends and ExecState went 0 → 1
(`build_harness_copyloop2.log`).

| pass | copy0 | copy1 | copyloop0 | copyloop | cold Copy | **steady Copy** | empty 1024-iteration loop |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1.81 | 2.23 | 2.39 | 54.16 | 0.42 | **0.0506 ms** | 0.16 |
| 2 | 1.83 | 2.19 | 2.35 | 55.13 | 0.36 | **0.0515 ms** | 0.16 |

60 timed + 5 warm Runs per cell, A-B-A-B order, panels closed. **A steady-state `IMAQ Copy` of a 1280×1024 U8 frame
costs ≈ 0.05 ms (≈ 26 GB/s, the buffer is cache-resident); the cold first copy's 0.4 ms is almost entirely the
destination's first allocation.** Copying every frame at 150 Hz is therefore ≈ 8 ms/s of one core, not 60.

**Linearity in N (peer's request; run 14:37, `copyloop_bench.json`):** a second pair with N = `X Resolution` = 1280
(`HARNESS_copyloopX` / `copyloopX0`, same recipe with an argv switch), six cells A-B-A-B, two passes:

| pass | steady Copy N=1024 | steady Copy N=1280 | slopes within 5 % | T1280 − T1024 (predicted 256 × slope) |
|---|---:|---:|---|---:|
| 1 | 0.0508 ms | 0.0501 ms | **PASS** | 12.09 ms (13.02) |
| 2 | 0.0506 ms | 0.0518 ms | **PASS** | 14.47 ms (12.96) |

The baseline-subtracted per-copy slope is the same at both N (primary criterion, peer review
`…copyloop-linearity-plan.md`); the ±1 ms secondary prediction on the difference held in pass 1 and missed by 1.5 ms in
pass 2, within the ~3 ms the reviewer showed two independent 5 % slopes allow. The peer's point that the 26 GB/s payload
rate is cache-regime bandwidth for a 2.6 MB A+B footprint (not evidence of a skipped copy) is adopted; a per-iteration
sentinel-pixel correctness harness was suggested and NOT built (NI documents `IMAQ Copy` as an unconditional transfer).

## Verification level

Functional numbers on the real fixture, two consistent passes; harness structure verified (ExecState 1, all planned
wires). Steady-state in-loop copy: functional, two passes (section above). IMAQ Image Display route: see
`bench-2026-09-14-display-path` (INDEX row 25). Peer reviews: `archive/peer/2026-09-14-imaq-copy-handoff-plan.md`,
`…copy-harness-build-run1.md`, `…copyloop-forloop-tunnels-plan.md`, `…copyloop-gate-controlnames-fail.md`,
`…copyloop2-forloop-terminals-unnamed.md`.
