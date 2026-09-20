---
type: reference
status: current
date: 2026-09-12
tags: [docs]
---

# Main VI map — call graph, structure, and what it means

**Purpose.** `ARCHITECTURE.md` groups the rig's sub-VIs by *function*, but says outright that string
extraction "can't see which loops exist or how they're bounded". This document fills that gap: the
actual **call graph**, the **structural skeleton** of the main VI, and the **meaning** of the parts
that matter to the parallelization. Built 2026-08-30 at the user's direction — *"원본 메인 vi 및
subvi 연결관계, 프로세스 흐름을 디테일하게 파악하고 구조화하며 의미를 이해"* — so that the direction
of the work is chosen from understanding rather than assumption.

## How this was produced, and what it does *not* prove

| evidence | tool | what it proves | what it cannot prove |
|---|---|---|---|
| call graph | `scratchpad/callgraph.py` — offline byte scan of every `.vi`, names resolved against an index of all 450 VIs under `zz_LabView VI` | VI **A references** VI B | how many call sites, and **which loop/case frame** they sit in |
| structure counts | `OpReport_v3` over COM on a **Claude-made copy** | exact object counts and owner *class* per structure type | which specific structure contains which node (owner is a class name, not an identity) |
| connector panes | `Wire Inputs`/`Get Outputs` probes by name | whether a name is a real pane terminal | nothing about values |

**No original was modified.** The call graph is a pure byte read; the structural counts ran against
`Min_Track N beads V6_ParallelLoop.vi`, the working copy an early Claude session cloned from 4.5.

## 1. The call graph

The main VI references **23 project-local VIs** directly (plus ~30 NI-library ones: IMAQdx, ASI
stage, PI motor, filters, drawing). Grouped by role, with their own children indented:

```
Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi
│
├─ TRACKING  (the path this project is replacing)
│   └─ Track N beads four-fold over-kernel-v3.vi
│        ├─ Track 1 of N bds xyz-kernel-reentrant.vi      1 bead  / call
│        └─ Track 2 of N bds xyz-kernel-reentrant-v2.vi   2 beads / call
│             └─ both call the SAME ten analysis VIs:
│                  Omars IMAQ ImageToArray · rect coord from center
│                  tracking-calculate radial profile-openv2
│                  tracking-prep avgx,y profiles · tracking-average x,y in cross
│                  tracking-find avg profile center → tracking-fit parabola to avg profile
│                  tracking-calculate phase in neighborhood
│                  tracking- quadratic fit to phase nghbrd
│                  Tracking-prep I of r · Tracking-fit prepped I of r to cal
│
├─ CALIBRATION  (produces the cal clusters the tracker consumes)
│   ├─ calibration- generate 1 I of r, reentrant.vi       1 bead  ─┐ same 1-vs-2 bead
│   ├─ calibration- generate 2 I of r, reentrant.vi       2 beads ─┘ pairing as tracking
│   │     └─ draw circle on picture-in place.vi → Omar's Flatten/Draw Flattened Pixmap.vi
│   ├─ build cal image.vi → Power Spectrum.vi → generate spectra v2.vi, random resample.vi
│   ├─ make both cosine bandpass.vi          ← BANDPASS IS BUILT HERE
│   ├─ choose bandpass v2.vi                 ←   and selected here
│   │     └─ prep cal image.vi → proc cal image-make bandpass.vi
│   └─ check N bead pos v3-kimlab.vi
│
├─ MOTION / HARDWARE
│   ├─ ASI_adjust focus-subvi.vi        (piezo stage focus — see rule 1b: allowed while DISASSEMBLED)
│   ├─ Motor control v5_No Recording.vi (magnet motor — same rule, no separate carve-out)
│   ├─ Max Trans Pos.vi                 (travel-limit lookup)
│   └─ Global motor pos.vi              (VI Global — cross-loop shared state)
│
├─ PHYSICS
│   ├─ Magnet2Force v3_for M270.vi      (magnet position → force)
│   └─ WLC function sub.vi              (worm-like-chain fit)
│
└─ DISPLAY / IO
    ├─ N bead plot Z.vi · N bead plot dZ.vi · grayscale color table.vi
    ├─ get buff image-lost frames.vi    (dropped-frame bookkeeping)
    ├─ save trace.vi · save N xyz traces.vi
    ├─ exp-ref management.vi            (experiment / reference-bead bookkeeping)
    └─ rect coord from center.vi        (shared with the tracking kernels)
```

## 2. The structural skeleton of the main VI

Measured on the working copy:

| object | count | reading |
|---|---|---|
| **WhileLoop** | **3** | the parallel loops. **All three report `owner = Diagram`, i.e. none sits on the top-level diagram** — they are nested inside other structures (there are 4 Sequences, so the classic init → run → cleanup frame layout is the likely container). Positions are far apart: (2804,136), (2633,927) and (−14942,652) — that last one is in a distant region of the canvas. |
| **EventStructure** | 2 | UI event handling — consistent with the documented `"CycleSchedule": Value Change` event case. |
| ForLoop | 17 | per-bead / per-row iteration throughout. |
| CaseStructure | 37 | state and mode branching — the 3-state clamping logic lives here. |
| Sequence | 4 | execution-order framing. |
| SubVI nodes | 97 | 23 distinct VIs, so most are called from several places. |
| Wire | 1898 | scale reference: the tracking kernel alone has 251. |

**This is the first hard evidence about loop count.** `ARCHITECTURE.md` inferred "4 parallel loops"
for 4.6 from the *filename*; the 4.5 line actually carries **3** While loops. Since our baseline is
4.5 (user-confirmed), three is the number to design against.

## 3. What the map settles

**Bandpass lives in calibration, not tracking — now with call-graph evidence.** The main VI calls
`make both cosine bandpass.vi` and `choose bandpass v2.vi` → `prep cal image.vi` →
`proc cal image-make bandpass.vi`. **None of these is reachable from the tracking kernel**, whose
entire subtree is the ten analysis VIs listed above. Combined with the connector-pane probes
(`Cosine bandpass` is a *field of the calibration cluster*, not a standalone terminal on any kernel
pane), the picture is consistent and complete:

> The user sets forget radius and bandpass during calibration → those VIs build/choose the bandpass
> → the result is bundled into the cal cluster with the prepped `I(r)` arrays and `# slices in stack`
> → the tracker receives the finished cluster per bead and never recomputes it.

So the parallel kernel inherits the bandpass automatically by auto-indexing `Array of cal clusters`.

**Calibration mirrors tracking's 1-bead/2-bead pairing.** `calibration- generate 1 I of r` and
`generate 2 I of r` are the calibration twins of `Track 1`/`Track 2`. The pairing is therefore a
house pattern for batching beads, not something specific to the tracking maths — which supports the
finding that replacing `Track 2` with repeated `Track 1` calls preserves the analysis model.

**Cross-loop state is a VI Global.** `Global motor pos.vi` is called directly by the main VI, and no
Queue/Notifier/Semaphore appears anywhere. With 3 While loops already sharing state through globals,
**adding parallelism must not add new global writers** — see the skill's rule that variables are
race-prone inside parallelised loops, where wires are not.

## 3b. Process flow — regions of the diagram, seen directly (2026-08-30)

The diagram is a **very wide, one-screen-tall horizontal strip** (LabVIEW's `View ▸ Navigation
Window` shows the whole thing at once and is the right tool for this VI — repeated zoom-out is not).
Walking it produced these regions. **Caveat: nested subdiagrams do not share one coordinate space,
so reported x/y cannot be used to place a node in the strip** — the regions below were identified by
looking, not by arithmetic.

**① Initialisation frame (far left).** `Piezo stage initialization` (ASI TG-1000: INITIALIZE, MOVE
AXIS TO POS, GET CURRENT POS, `Focus Pos (Start)`) · `Initialize camera` (IMAQdx, `Grayscale (U8)`,
Height/Width) · motor serial bring-up (`COM3 115200`, `M-126.PD1`, PI `GOH`/`VEL`/`TMX?`/`TMN?`,
`Trans Speed`, `Max Travel Limit`) · calibration-image parameters (`# images in stack`,
`# to avg per image`, `z step between images`, `cross length`) · `Make the grayscale color table` ·
`pixel distance (nm)` and the `Intensity vs Radius` graph scales. A comment block records the COM
port map for the motor and rotator.

**② Experiment / UI region.** Contains the **Event structure** — the case seen is
`[2] "CycleSchedule": Value Change` — together with the force-clamp cycle table (`CycleSchedule`,
`NumCol`, `Mag Position`, `Mag Arr`, `Force Arr`, `Set # of Cycles`, `Total cycle #`,
`Estimated end time (min)`, `Cycle Start Time`, `Start Cycles`) and the autofocus/auto-reset logic
(`Auto-Reset`, `# of Auto-Reset`, `Auto-reset zero`, `Reset Tracking`, `Limit of Auto-Focus`,
`Focus Step (F1)`, `± Inc (PgUp/PgDn)`, `Move Focus`), plus `IMAQdx LastBufferNumber` and
`x,y pos array`.

**③ Motor / clamping state machine.** `MainCycle`, `SubCycle`, `Single Cycle Num`, `Start Moving?`,
`Reached clamp`, `Target`, `Time span after start (min)`, `Initial Time at Start`, driving PI `VEL`
and `MOV` — this is the **3-state clamping** the base VI is named after. `save trace`,
`File progress`, `Trans Pos (mm)` and `Rot pos (deg)` sit alongside.

**④ The tracking call site — exactly ONE.** Probing all 97 SubVI nodes for the output
`x,y,z array out` (unique to the four-fold kernel) returns **a single node**: index 39, uid 5058,
position (3811, 1474), `owner = Diagram` (nested inside a structure, not on the top level).

> **This is the single most useful fact for the swap: the tracking kernel is called once.** The
> drop-in replacement therefore touches exactly one node, and the connector pane measured in
> `STATUS.md` is the entire contract. It also means the per-frame tracking cost is incurred at one
> place, which is where `ARCHITECTURE.md` §10's instrumentation should bracket.

## 4. What is still unknown

1. ~~**Which of the 3 While loops each region belongs to.**~~ — **ANSWERED 2026-09-12, see
   [frame-loop-anatomy.md](frame-loop-anatomy.md).** All 170 diagrams were walked with `net_map`
   (whose per-node first field is the node UID) paired with `report("Diagram")` for each diagram's
   owning structure class; the method was validated first on two VIs we built ourselves. Result:
   loop A = diagram 20 (13 nodes, the single `Motor control v5` call), **loop B = diagram 43, the
   FRAME loop** (75 nodes, 6 subVIs, 10 Property Nodes, and uid 5058 sits directly on its body so
   the kernel runs unconditionally every iteration), loop C = diagram 99 (22 nodes: grab, pixmap,
   mouse and focus keys).
2. ~~Where the four-fold kernel is called from~~ — **ANSWERED: one call site**, §3b ④. Which loop and
   case frame encloses it is part of question 1.
3. **What the 3-state clamping state machine sequences in detail** — region ③ is located and its
   controls named, but the state transitions have not been traced.
4. **Where `t0`, the ~4.7 ms fixed per-frame cost, is spent** — `ARCHITECTURE.md` §10 says the next
   action there is a measurement, and this map now gives the candidate call sites to instrument:
   `get buff image-lost frames`, the pixmap/display chain, `save trace`/`save N xyz traces`.

## 5. Consequence for direction

The replacement's contract is unchanged and now better evidenced: **same connector pane, same
per-bead analysis model, same numbers.** Nothing in the map contradicts the plan to parallelise over
beads inside the four-fold kernel's slot. What the map adds is a warning and a target: the warning is
that the surrounding code is a **3-loop, globals-coupled** design, so the swap must stay strictly
inside the kernel's connector pane; the target is that §10's `t0` — not the kernel — is where the
remaining frame budget is, and this map names the call sites to measure.
