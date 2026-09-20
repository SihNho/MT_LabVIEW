---
type: narrative
status: historical
date: 2026-08-31
tags: [archive]
---

> **Correction 2026-08-26:** this document's lineage analysis argues V6 should build on
> `4.6_4ParallelLoop`. The **user has confirmed the base VI is `4.5_3StateClamping`**. Treat the
> lineage reasoning below as background, not as the decision.

# Overview

## What this is

The `2. Tracking` project is the control software for a **magnetic tweezers (MT) instrument** in
the Kim Lab ("KimLabMTroom"). A single main VI (`Min_Track N beads <version>.vi`) runs the entire
experiment: camera acquisition, real-time multi-bead tracking, stage/magnet motion control, force
calibration, live plotting, and data logging.

Magnetic tweezers apply a controlled force to a magnetic bead (here, M270 Dynabeads) tethered to a
surface via a molecule (DNA/protein), by moving a permanent magnet closer/farther/rotating it. The
bead's 3D position is tracked from camera images (XY from the image, Z from a diffraction-pattern
calibration curve), giving force-vs-extension data for single-molecule biophysics experiments.

## Experimental workflow (from `project-requirements/project-description.md`, added 2026-08-25)

Steps, as the user runs an actual experiment on `4.5_3StateClamping.vi`:

1. **Continuous acquisition** — user jogs the motor and watches the camera live to find candidate beads.
2. **Bead selection** — user clicks each target bead on the image, then presses `Done Picking Beads?`.
   The first click is the reference bead (a non-magnetic polystyrene bead, used to subtract stage drift).
3. **Bead radial-profile calibration** — *after* step 2, the ASI piezo stage sweeps in Z while bead
   extension is held fixed by the (now-constant) magnetic tension; the resulting off-focus diffraction
   pattern is captured and processed per selected bead, producing a `.cal` file used later for Z-tracking.
   (This is almost certainly what the sub-VIs `calibration- generate 1 I of r, reentrant.vi` /
   `...generate 2...` do — confirmed present as dependencies, see archive/VERSION_HISTORY.md.)
4. **Experiment** — the real continuous run: every frame, the image is processed into a numeric array
   alongside motor info (piezo/Z stage, linear/magnet-position stage, rotor), all continuously
   communicating. A time scheduler drives the motor. Per-bead tracking/analysis currently runs as a
   **sequential For loop across beads** — this is the piece the user wants parallelized.
5. **Save and termination** — `stop(end)` saves data and halts cleanly; a plain LabVIEW **Abort
   Execution** is used instead when the data isn't worth keeping.

**The user's own framing of the current loop structure** (this refines/partly supersedes the
`parallelization-requirement.md` description below): step 4 currently runs as exactly **two** parallel
While Loops:
- **Loop 1** — motor *writing* control only.
- **Loop 2** — everything else: motor *reading*, image acquisition/processing, scheduling, data
  saving, **and printing to the screen** (front-panel display updates — not called out in the original
  requirement doc, worth remembering as a 6th responsibility when splitting Loop 2 apart).

**Open question this raises:** the GUI investigation logged in archive/VERSION_HISTORY.md (the
MainCycle/SubCycle/`MOV.vi`/`VEL.vi` frame found by scrolling the block diagram) sits inside the
top-level Sequence Structure that appears to cover steps 1–3 (setup), not step 4. The actual Loop
1/Loop 2 pair for the *experiment* phase has not yet been visually located — it's likely later in the
diagram, possibly after the Sequence Structure ends, not one of its frames. Confirm before editing.

## Companion VIs in the same folder (not the main control loop)

These are offline analysis tools, not part of the acquisition program:
- `Min_Load N bead trace_Force-Ext*.vi` — load saved traces, plot Force-Extension, fit WLC
- `Min_Load N bead trace_Multiple files*.vi` — batch-load and Excel-export multiple trace files
- `Frame rate test/` — camera frame-rate benchmarking
- `old/` — superseded/legacy versions, kept for reference

## Main VI version lineage (see archive/VERSION_HISTORY.md for detail)

```
4.1 → 4.2 (autofocus fix) → 4.3
   → 4.4  ─┬─ EMCCD (camera-specific branch)
           ├─ MotorParallelLoop (motor control split into its own loop)
           └─ MotorParallelLoop_MagnetOrder (minor label/behavior variant)
   → 4.5  3StateClamping (force/position clamp generalized to an N-row cycle schedule)
   → 4.6  4ParallelLoop (diagram split into 4 parallel loops; no front-panel/API changes)
   → V6_ParallelLoop  ← you are here (folder empty as of 2026-08-24; next version not yet saved)
```

## Core hardware, as referenced by the software

| Role | Hardware / API evidence |
|---|---|
| Camera | NI-IMAQdx-compatible camera (`IMAQdx Open/Configure/Grab/Close`), one EMCCD-specific branch (4.4_EMCCD) |
| XY / rotation stage | ASI TG-1000 (`ASI TG-1000.lvlib`), used for XY translation + magnet rotation (twist) |
| Z / magnet motor | PI-style controller driven via low-level `MOV`/`POS?`/`VEL`/`TMN?`/`TMX?`/`SetCommand` commands (`Mercury_GCS_Configuration_Setup.vi`, a physical stage model `M-126.PD1` appears in strings) |
| Beads | M270 Dynabeads (`Magnet2Force v3_for M270.vi` is the force-calibration curve specifically for these beads) |

## What "the project" needs before V6 can start

`V6_ParallelLoop/` is empty except for this wiki. The most direct starting point for a V6 build is
`Min_Track N beads 4.6_KimLabMTroom_4ParallelLoop.vi` (Save As into this folder), since 4.6 is the
newest version and its name directly parallels "V6_ParallelLoop". **However**, see the open question
in `README.md` — `Requests.md` names 4.5 as the file to reference instead; this needs to be resolved
with the user before a V6 file is saved.

## V6 goal (from `project-requirements/parallelization-requirement.md`, added 2026-08-24; refined by
`project-description.md`, added 2026-08-25)

Goal: maximize CPU utilization and minimize frame dragging/lost frames during the **step-4 experiment
phase** (see "Experimental workflow" above), by splitting the existing "Loop 2" into several parallel
While Loops. Loop 2 today bundles:
1. Motor reading — flagged as one of the current frame-rate bottlenecks
2. Camera **acquisition** — pulling a frame off the camera into a buffer
3. Image **processing** — bandpass filtering + per-bead tracking kernel on that frame
4. Scheduler for the motor control plan
5. Data saving
6. Printing to the screen (front-panel display updates)

("Loop 1" — motor *writing* control — is already its own loop and is left alone.) Target: **7 total
parallel loops** (Loop 1 unchanged + 6 new loops for items 1-6 above).

**Acquisition/processing split (added 2026-08-25):** items 2-3 were originally scoped as one "camera
acquisition" loop, but the camera setup already uses **IMAQdx's own buffered/ring-buffer acquisition**
— evidenced by existing sub-VI `get buff image-lost frames.vi` and front-panel diagnostics
`Buffer Number Mode` / `Lost Frame Message` / `Total Lost Frames` / `Missing Frames?` (see
ARCHITECTURE.md §1, GLOSSARY.md "Camera / imaging"). That means the hardware/driver is *already*
decoupling "a frame becomes available" from "a frame gets analyzed" — splitting them into two loops is
just formalizing an existing seam rather than inventing one:
- **Acquisition loop**: tight loop, only calls the IMAQdx grab/wait-for-buffer step and hands the
  **buffer index/number** (not the image pixels themselves) to the Processing loop via a queue. Kept
  as lightweight as possible so it's never the thing that causes lost frames.
- **Processing loop**: dequeues a buffer index, fetches that specific buffer's image data
  (`IMAQdx Get Image.vi`), runs the bandpass (`make both cosine bandpass.vi`) and tracking kernel
  (`Track N beads four-fold over-kernel-v3.vi`), and hands results on to Scheduler/Merge&Save.
  Passing only the buffer index through the queue (not full image arrays) keeps inter-loop
  communication cheap regardless of frame size.

The task is to split items 1-6 above out into their own parallel While Loops, rather than running them
serially in Loop 2. This is a block-diagram restructuring — no new front-panel controls are implied.

**Ground rules that apply to this work** (see `Requests.md` / `README.md`): the reference VI must not
be modified directly; new sub-VIs go under LabVIEW's `user.lib\claudeDev`; and each change should be
logged in `archive/VERSION_HISTORY.md` as it's made.
