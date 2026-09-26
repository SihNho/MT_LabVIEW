---
type: reference
status: current
date: 2026-08-26
tags: [docs]
---

# Glossary

Front-panel controls and domain terms found in the VI strings, one line each. Grouped roughly by
subsystem. Not exhaustive — see ARCHITECTURE.md for sub-VI names.

## Cycling / force clamp
- **CycleSchedule** — 2D array (table) of clamp steps; each row is one force/position "state" the magnet cycles through
- **Mag Arr** — array of magnet Z-positions, one per schedule row
- **Force Arr** — array of target forces, one per schedule row (derived from Mag Arr via calibration)
- **MainCycle** / **SubCycle** — counters tracking progress through the overall experiment cycle and the current sub-step within it
- **Total cycle #** / **Set # of Cycles** — total planned repeats of the schedule
- **Initial Time at Start** — timestamp captured when a new schedule step begins (replaces 4.4's per-setpoint `Initial Time at Max/Min Pos`)
- **Reached clamp** — status indicator: true once the magnet has settled at the current step's setpoint
- **Force ramp: Min force start=finish** / **Force clamp: Min force start=/=finish** — two mode descriptions for a force-control ring (ramp = returns to starting force; clamp = holds independently at each end)

## Tracking
- **Track File Path** / **Cal File Path** — where trace data / calibration data are read or written
- **Cal Zero** — calibration reference/zero point control
- **Bead # %d** — per-bead index label
- **Pixel distance (nm)** — camera pixel-to-nm conversion factor
- **Cross length (pixels)** — size of the tracking cross-correlation kernel/ROI
- **# FD points** / **# DT points** — number of points used in focus-detection / distance-tracking calibration

## Motion / stage
- **Trans Pos (mm)** / **Trans Speed (mm/s)** / **Trans Step (mm)** — XY translation stage position/speed/jog step
- **Rot pos (deg)** / **Rot Speed** / **Rot Step (deg)** — rotation stage (magnet twist) position/speed/jog step
- **1 R-Turn** / **1 L-Turn** — one full turn jog buttons (right/left) for the rotation stage
- **HOME** — send stage to home position
- **Max Trans Pos** / **Max Travel Limit** — travel-limit safety bound
- **Mag Position** — current magnet Z-axis position

## Camera / imaging
- **Frame rate** — camera acquisition rate
- **Lost Frame Message** / **Total Lost Frames** / **Missing Frames?** — dropped-frame diagnostics
- **Buffer Number Mode** — IMAQdx buffer indexing mode

## Autofocus
- **AUTO FOCUS** / **Auto-Focus** — autofocus subsystem toggle
- **Focus Pos (Track)** / **Focus Pos (Cal)** / **Focus Pos (Start)** — focus position at various pipeline stages
- **Limit of Auto-Focus** — safety bound on focus travel
- **Limit of Program** — **the maximum number of auto-resets allowed in one run** (user, 2026-09-15; this entry
  previously said "safety bounds on focus travel", which was wrong and had been copied into
  `stage2-assembly-step-e.md`). Its purpose is operational: an MT run can be left going overnight, and a bead
  quite often comes unstuck and flies off. Each loss triggers an auto-reset; when the reset count reaches this
  limit the program **stops and saves the data collected so far**, rather than grinding on with no beads.
  Measured in the diagram: `Equal?` compares it with `# of Auto-Reset` — the test is **equality**, not "greater
  than", so the limit is hit exactly, not exceeded.
- **Auto-reset counter** / **Auto-reset zero** / **# of Auto-Reset** — periodic re-homing of the focus/position system (program auto-ends once this counter hits its limit, per an in-VI comment: "~27mins/100000")

## Plots
- **Force (pN) vs Extension (nm)** — main force-extension live graph
- **Extension (nm) vs Time (Frame #)** — extension-over-time live graph

## Per-room parameters (from an in-VI comment listing what must be re-tuned per imaging room)
`Max Trans Pos`, `CCD height/width`, `Cross length`, `Frame rate`, `# FD points`, `# DT points`,
`Com port/rate`, `Trans name`, `Rot speed`, `Limit of Auto-Focus`, `Limit of Program`

## VI Scripting terms

- **driver VI** — a VI whose purpose is to *edit another VI* (not a hardware driver). You press Run on
  it and it reaches into a target VI to add loops, drop subVIs, wire terminals. Ours:
  `ScriptDriver_DropForLoop.vi`, `KernelBuilder_v1.vi`.
- **target VI** — the VI being edited by a driver; the deliverable.
- **`P` terminal** — a For Loop's "number of generated parallel loop instances" terminal. It only
  exists once iteration parallelism is enabled, so its presence proves a loop is parallelised.
- **auto-indexed tunnel** — a loop tunnel (drawn `[ ]`) that takes one array element per iteration on
  input, or collects one result per iteration on output. The parallel-safe alternative to a shift
  register.
- **shift register** — a loop tunnel pair (drawn `▼`/`▲`) carrying a value from one iteration to the
  next. Creates a loop-carried dependency, which **forbids** iteration parallelism.

## Internal project terms (coined in this project, 2026-09; explained here once so reports can use plain words)
The user asked (2026-09-26) that reports use standard words. These terms stay in file names, logs and code because
renaming working machinery is riskier than glossing them.
- **verb / 동사** — one scripting FUNCTION: a Python function in `tools/gscript.py` or `tools/stagekit.py` (e.g. `move_into_frame`, `connect`) plus the op VIs (subVIs under `claudeDev\ops\`) it calls over COM. Plain word: 스크립팅 함수.
- **op / op VI** — one of our scripting subVIs (`OpConnect…_v0.vi` etc.), called by a verb. Plain word: 스크립팅 subVI.
- **leg** — ONE real measurement run of a VI (e.g. 15 beads, 120 s, 90 Hz). Plain word: 실측 1회 / 구동 1회.
- **bed** — the current working VI a cycle builds on (e.g. `D1_l2_a1_….vi`). Plain word: 현재 작업 VI.
- **stage** — one scripted build step that starts from a saved VI and saves a new one (`tools/recipes/stage_*.py`). Plain word: 빌드 단계.
- **card** — one JSON file of the session protocol (`task/1`, `result/1`, `cycle/1`, `next/1`, `steer/1`). Plain word: 작업 지시 / 결과 파일.
- **rung** — one step of an escalation ladder (which model/effort a retried card goes to). Plain word: 상승 단계.
- **firefighter / 소방수** — a cycle or card re-run on a different model after repeated failure.
- **material / judgement session** — sub-session that measures/builds vs the session that decides (CLAUDE.md §3).
- **gate** — a check in a script or hook that refuses to continue (e.g. `guard_bash`, a `PASS/FAIL` line). Plain word: 검사 / 관문.
- **pre-run** — the offline check of a stage plan against the VI's graph before LabVIEW runs it. Plain word: 사전 검사.
- **ABBA** — run order original, new, new, original to cancel drift in a comparison.
