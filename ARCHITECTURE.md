---
type: reference
status: current
date: 2026-09-13
tags: []
---

# Architecture

Based on the sub-VI dependency list embedded in `Min_Track N beads 4.6_KimLabMTroom_4ParallelLoop.vi`
(and consistent across 4.4/4.5/4.6). Grouped by function; sub-VI names are exact.

## 1. Camera / image acquisition
- `IMAQdx Open Camera.vi`, `IMAQdx Configure Grab.vi`, `IMAQdx Grab.vi`, `IMAQdx Get Image.vi`,
  `IMAQdx Stop Acquisition.vi`, `IMAQdx Close Camera.vi` — NI Vision Acquisition Software (`$NI_Vision_Acquisition_Software.lvlib`)
- `get buff image-lost frames.vi` — dropped-frame / buffer bookkeeping
- `Flatten Pixmap.vi`, `Draw Flattened Pixmap.vi`, `grayscale color table.vi` — live image display
- `rect coord from center.vi`, `Draw Grayed Out Rect.vi`, `Draw Circle by Radius.vi`, `Draw Text at Point.vi` — on-image bead/ROI annotation overlays

## 2. Bead tracking (core algorithm)
- `Track N beads four-fold over-kernel-v3.vi` — the tracking kernel (4x-oversampled)
- `make both cosine bandpass.vi`, `choose bandpass v2.vi`, `proc cal image-make bandpass.vi` — radial bandpass filtering used by the tracking algorithm
- `calibration- generate 1 I of r, reentrant.vi`, `calibration- generate 2 I of r, reentrant.vi` — build per-bead radial-intensity-vs-Z calibration curves (reentrant = runs in parallel per bead)
- `build cal image.vi`, `prep cal image.vi` — calibration image stack prep
- `check N bead pos v3-kimlab.vi` — tracking-quality/sanity check per bead
- `Median Filter.vi` — position smoothing

## 3. Motion control
- Stage (ASI TG-1000, XY + rotation): `Configure.vi`, `Initialize.vi`, `Move Axis to Position.vi`, `Move Axis Relative.vi`, `Get Current Position.vi`, `Close.vi`, `GOH.vi` (go-home), `VEL.vi`
- Z/magnet motor (PI-style low-level protocol): `MOV.vi`, `POS?.vi`, `SetCommand.vi`, `TMN?.vi`/`TMX?.vi` (travel min/max limits), `Mercury_GCS_Configuration_Setup.vi`
- `SiHyeong Modified Motor control v5_No Recording.vi` — higher-level motor control wrapper (lab-member-modified)
- `Global motor pos.vi` — a VI Global used to share the current motor/magnet position across loops (see §5)
- `ASI_adjust focus-subvi.vi` — autofocus adjustment via the stage
- `Max Trans Pos.vi` — translation travel-limit lookup

### The `Cal Zero` controls are the MAGNET MOTOR, not a calibration zero (user, 2026-09-13)

Recorded because the name invites exactly the wrong reading — a file-string scan turned these up next to
`"Returns focal position to value PRIOR to acquiring image stack"`, and they were provisionally mis-read here as the
Z-calibration/LUT stack zero. The user corrected it: they are **PI magnet-motor position presets**, set near the very
start of a run.

| control | what it actually is |
|---|---|
| `Cal Zero` | PI motor position **0** |
| `+ Cal Zero` | moves the motor to a position **between 36 and 38**, depending on the setting |
| `- Cal Zero` | **legacy** — from a pre-revision version of the code, not used since the user's revision |

Two consequences. First, `Cal Zero` has **nothing to do with the rotor**, so the hunt for the rotor's zero must not
follow it; the rotor candidates are `start angle(0)`, `Auto-reset zero`, `last rot pos` and `Current pos rot?`.
Second, `- Cal Zero` is dead code — but "the user believes it is unused" is not the same as "no wire reaches it", and
rule 1a forbids changing behaviour, so during the restructuring it must be shown unreachable by wire topology before
it is dropped, not removed on the strength of this note.

## 4. Force / physics
- `Magnet2Force v3_for M270.vi` — magnet-position → force conversion, calibrated for M270 beads
- `WLC function sub.vi` — worm-like-chain model fitting for force-extension analysis

## 5. Cross-loop / shared state (evidence for inter-loop communication design)
No LabVIEW Queue, Notifier, Semaphore, or Rendezvous primitives appear anywhere in the decompiled
text of 4.4/4.5/4.6. This means inter-loop communication is almost certainly done through **VI
Globals / shared front-panel references** (e.g. `Global motor pos.vi`) rather than a
producer/consumer queue architecture. This is worth confirming by opening the block diagram — if
true, it's a common source of race conditions when adding more parallel loops, and worth
reconsidering if V6 adds further parallelism.

## 6. Cycling / force-clamp state machine
- Front-panel controls: `CycleSchedule` (2D array, has `NumCol` + row index — a user-edited table of clamp steps), `Mag Arr`, `Force Arr`, `MainCycle`, `SubCycle`, `Total cycle #`, `Set # of Cycles`
- An Event Structure case exists specifically for `"CycleSchedule": Value Change`
- See archive/VERSION_HISTORY.md — this replaced a hardcoded 2-point (min/max) scheme in 4.4, generalized in 4.5 to a variable number of rows (3 in this build), and appears unchanged going into 4.6

## 7. Data / plotting / logging
- `save trace.vi`, `save N xyz traces.vi` — trace logging
- `N bead plot Z.vi`, `N bead plot dZ.vi` — live Z / ΔZ plots
- Live graphs: "Force (pN) vs Extension (nm)", "Extension (nm) vs Time (Frame #)"
- `exp-ref management.vi` — experiment/reference-bead bookkeeping

## 8. Filtering / signal processing (NI Advanced Analysis Library)
- `NI_AALBase.lvlib Smoothing Filter Coefficients.vi`, `FIR Filter.vi`, `FIR Filter (DBL).vi`

## 9. Error handling
- `Simple Error Handler.vi` used throughout; standard LabVIEW error cluster (`error in`/`error out`) wiring implied by boilerplate help strings found in the binary

## Parallel-loop evolution (4.4 → 4.6)

| Version | What changed structurally | Evidence |
|---|---|---|
| 4.4 base | single main loop (implied by absence of "ParallelLoop" naming) | — |
| 4.4_MotorParallelLoop | motor control split into its own parallel loop | filename + near-zero front-panel text diff vs 4.4_EMCCD (i.e., a diagram restructure, not a UI change) |
| 4.4_MotorParallelLoop_MagnetOrder | same, plus `Force titration gap` renamed to `Mag titration gap` | string diff shows exactly this one label rename |
| 4.6_4ParallelLoop | diagram split into 4 parallel loops total | filename; diff vs 4.5 shows almost no front-panel/control changes (one new string: "x of center, rel to picture") — strongly suggests a loop-structure refactor with the front-panel API left intact |

**Caveat, now PARTLY RESOLVED (2026-08-30):** this section is a functional grouping, not wiring.
The actual call graph and the main VI's structural skeleton are measured in
**[docs/MAIN_VI_MAP.md](docs/MAIN_VI_MAP.md)** — and the "4 parallel loops" figure above was inferred from a
*filename*: the 4.5 baseline actually contains **3 While loops** (plus 2 Event structures, 17 For
loops, 37 Case structures, 4 Sequences, 97 subVI nodes). Which loop contains what is still open.

## 10. Performance model and the tracking backends

### 10.1 Where the time actually goes (from the user's field data, 2026-08-27)

Measured behaviour of the **current, un-parallelised** code at **150 Hz** (a 6.67 ms frame budget):
2 beads track with essentially no frame loss, 3 beads is where loss begins, and 8 beads loses about a
third of frames — i.e. ~100 fps sustained, so ~10.0 ms per processed frame. Fitting the obvious model
`t_frame = t0 + N · t_bead` to those three points is strikingly consistent:

| beads | predicted | observed |
|---|---|---|
| 2 | 6.0 ms | no loss (fits in 6.67) ✓ |
| 3 | 6.67 ms | exactly at the threshold ✓ |
| 8 | 10.0 ms | 1/3 loss ✓ |

→ **`t0 ≈ 4.7 ms` fixed, `t_bead ≈ 0.67 ms` per bead.**

The consequence is uncomfortable and important: **the fixed per-frame cost consumes about 70 % of the
frame budget before a single bead is tracked**, and it is *not* what the parallelisation work
addresses. Even with infinite parallelism the rig cannot exceed roughly **214 Hz** until `t0` is found
and cut. Prime suspects, in order: front-panel **display** (Intensity Graph colour-mapping is CPU
work), IMAQ→array conversion and copies, per-frame file logging, and UI-thread marshalling.

Three consequences follow, and they set the work order:

1. **Parallelising the kernel does fix the stated 8-bead symptom** — `4.67 + 5.33/4 = 6.0 ms`, back
   under budget at 150 Hz — so finishing that work is worth it.
2. **Attacking `t0` is both higher-leverage and cheaper.** Both together would put 8 beads at ~2.3 ms
   (≈430 Hz), or ~30 beads at 150 Hz.
3. **A CUDA rewrite without fixing `t0` buys at most ~2×** and still hits the 214 Hz wall, so the DLL
   work should wait.

Model caveats: it assumes drop-while-busy loss semantics, a linear per-bead cost (supported — a pure
four-fold step function would have made 2 and 3 beads cost the same, which contradicts the data), and
an approximate threshold reading at 3 beads. **The next action here is a measurement, not a build:**
tick counts around grab / convert / track / display / log, one instrumented run.

### 10.2 Two backends, kept side by side (user decision, 2026-08-27)

The user asked that a GPU path be maintained alongside the CPU one, because bead count may grow
without bound. This is structurally right rather than redundant, because the two have opposite cost
shapes:

| backend | fixed cost per frame | marginal cost per bead | wins when |
|---|---|---|---|
| CPU serial (today) | 0 | 0.67 ms | N ≤ 2 |
| CPU parallel, P=4 | ~0 (thread pool pre-spawned) | ~0.17 ms | small–mid N |
| GPU (CUDA DLL) | ~0.3–0.5 ms (one H2D + launch + sync) | ~0.005–0.02 ms | large N |

The GPU path is a **loss** at 2–8 beads and a **rout** at 50+. Crossover is estimated at 15–25 beads
and must be measured, not assumed.

**Design rule — one connector pane, several implementations.** Define a single backend signature
(image/ROI array plus per-bead calibration in → xyz array plus `error out`) and implement it as
`..._serial` (the existing code, kept as the numerical reference), `..._par` (For Loop with `P`), and
`..._cuda` (Call Library Function Node), dispatched by an enum in a thin wrapper. All three stay
callable, A/B-benchmarkable on identical frames, and diffable bead-by-bead. **Only the innermost
compute swaps** — do not fork the whole over-kernel per backend.

Note that with the runtime `P` terminal wired to a front-panel control, `..._par` at `P = 1` already
covers the serial case, so `..._serial` earns its place as an untouched correctness reference rather
than as a performance option.

### 10.3 Constraints the GPU path must honour

Recorded now so the CPU work does not foreclose them:

- **Transfer the whole frame once per frame, never per-bead ROIs.** One H2D of a 1 MB frame is
  ~0.1 ms over PCIe 3.0 ×16; N small copies would reintroduce an O(N) cost and discard the entire
  point. Crop ROIs *on the device*. D2H is only N×3 doubles — negligible.
- **One batched kernel over all beads**, with batched cuFFT (`cufftPlanMany`) for the XY
  cross-correlation, so bead count appears as a batch dimension rather than a loop.
- **The CUDA context must live on a DLL-owned persistent worker thread** with a job queue; do not let
  LabVIEW's thread pool create and destroy contexts. Set the Call Library node to *Run in any thread*
  only once the DLL is proven thread-safe.
- **Pinned (page-locked) host staging buffer**, allocated by the DLL, written by IMAQ — this is what
  keeps H2D at full PCIe speed and allows async overlap.
- The RTX 2060 is consumer silicon: **no GPUDirect RDMA**, so every frame is host-staged, and its
  6 GB is shared with anything else on the GPU (e.g. the UI-TARS grounder).
- **Numerical equivalence gate:** the CUDA backend ships only after matching the serial backend
  bead-by-bead on recorded frames, to a stated tolerance.
- A crash inside the DLL takes down LabVIEW **and the running experiment** — this is instrument
  control, so the failure mode is lost experiment time, not a restarted process.

Ordering, unchanged: **attribute `t0` → CPU `P>1` → fix `t0` → CUDA.**
