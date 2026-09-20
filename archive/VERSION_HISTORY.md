---
type: narrative
status: historical
date: 2026-09-15
tags: [archive]
---

# Version History

All dates are file `LastWriteTime` on disk as of 2026-08-24 (not necessarily authoring order —
see the note at the bottom). Sizes are bytes.

| Version | File | Last modified | Size |
|---|---|---|---|
| 4.1 | `Min_Track N beads 4.1_KimLabMTroom.vi` | 2024-10-11 15:19 | 470,370 |
| 4.2 | `Min_Track N beads 4.2 Autofocus fix_room3.vi` | 2024-06-24 17:38 | 467,641 |
| 4.3 | `Min_Track N beads 4.3_KimLabMTroom.vi` | 2024-12-05 19:27 | 462,882 |
| 4.4 (EMCCD) | `Min_Track N beads 4.4_KimLabMTroom_EMCCD.vi` | 2025-09-18 13:15 | 1,019,144 |
| 4.4 (MotorParallelLoop) | `Min_Track N beads 4.4_KimLabMTroom_MotorParallelLoop.vi` | 2025-09-18 13:17 | 468,604 |
| 4.4 (MotorParallelLoop_MagnetOrder) | `Min_Track N beads 4.4_KimLabMTroom_MotorParallelLoop_MagnetOrder.vi` | 2025-02-05 22:42 | 468,916 |
| 4.5 | `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` | 2026-08-24 17:14 | 471,337 |
| 4.6 | `Min_Track N beads 4.6_KimLabMTroom_4ParallelLoop.vi` | 2026-07-15 09:51 | 469,560 |

**Timestamp anomaly:** 4.6's mtime (2026-07-15) is *earlier* than 4.5's (2026-08-24, today). Version
numbers still indicate 4.5 → 4.6 is the intended order; the mtime gap likely just means 4.5 was
re-saved/touched most recently (possibly while it was being reviewed earlier today) without 4.6
being touched again. Don't infer development order from these dates alone.

## 4.1 → 4.3
Not diffed in detail for this wiki (no specific question drove it). Revisit if needed — the same
`tools/diff_vi.py` approach applies.

## 4.3/4.4-base → 4.4_EMCCD
Adds EMCCD-camera-specific controls not present in the non-EMCCD branch: `Set EM mode`, `fan on
full`, `fan on low`, `Change Acq condition.vi`, an Express VI-based `Display Message to User`
dialog, and an `Error Code Enum typedef.ctl`. This is a **separate camera-support branch**, not a
strict ancestor of 4.5/4.6 — confirmed because diffing 4.4_EMCCD against both 4.5 and against
4.4_MotorParallelLoop shows the exact same EMCCD-only strings disappearing in both, meaning 4.5/4.6
descend from the non-EMCCD 4.4 line, not from 4.4_EMCCD.

## 4.4 (base) → 4.4_MotorParallelLoop
Motor control moved into its own parallel loop. Confirmed structural (not UI) change: diffing
against 4.4_EMCCD turns up no new front-panel text beyond the filename itself and two generic
array-type help strings — i.e. no new controls were added, consistent with a block-diagram-only
refactor.

## 4.4_MotorParallelLoop → 4.4_MotorParallelLoop_MagnetOrder
One concrete change found: the control/label `Force titration gap` was renamed to `Mag titration
gap` (magnet-position framing instead of force framing). Otherwise no other readable front-panel
differences — likely a minor variant exploring ordering/sequencing of magnet moves.

## 4.4 → 4.5 (3StateClamping)
This is the best-evidenced change in the project. 4.4 clamped between exactly two fixed setpoints,
using controls: `Force titration gap`, `Real Max force`, `Initial Time at Max Pos`, `Initial Time
at Min Pos`. All four are gone in 4.5. In their place:
- `CycleSchedule` — a 2D array control (has a `NumCol` control and row-index wiring), i.e. a
  user-editable table of clamp steps
- `Mag Arr`, `Force Arr` — companion arrays (magnet position / force per step)
- `MainCycle`, `SubCycle` — loop counters that iterate through the schedule
- `Initial Time at Start` — single generic replacement for the old per-setpoint time trackers
- An Event Structure case specifically for `"CycleSchedule": Value Change`

**Conclusion:** 4.5 generalized a hardcoded 2-point force/position clamp into an N-row schedule
table, and this particular build has it populated/labeled for 3 rows — hence "3StateClamping". No
new sub-VI dependency was added, so this is implemented in the main VI's own diagram logic (arrays
+ case/event structures), not via a new sub-VI.

*(Re-verified against the current on-disk 4.5 file at 17:14 today — the file changed slightly since
first read this session (+52 bytes), but all the evidence strings above are still present. If 4.5
changes again, re-run `tools/diff_vi.py` against 4.4_EMCCD.vi before trusting this section.)*

## 4.5 → 4.6 (4ParallelLoop)
Almost no front-panel/control text differs — the only new readable string is `"x of center, rel to
picture"`. This strongly suggests 4.6 is a **diagram-only restructuring** (splitting execution into
4 parallel loops) that preserves the 4.5 front-panel API and clamp-schedule behavior unchanged. No
new sub-VI dependencies were introduced either.

## 4.6 → V6_ParallelLoop
`V6_ParallelLoop/` is an empty folder as of 2026-08-24 — no VI has been saved into it yet. This
wiki was requested/created before any V6 code exists, so there is nothing to diff yet. When a V6 VI
is saved here, run:
```
py tools/diff_vi.py "..\Min_Track N beads 4.6_KimLabMTroom_4ParallelLoop.vi" "<new V6 file>.vi" diff_4.6_vs_v6.txt
```
and update this file with the result.

## V6 planning — 2026-08-24 (no VI yet; two new requirement documents added)

Still no VI saved into `V6_ParallelLoop/`, but two markdown files landed in this folder later the
same day the wiki was first written, setting ground rules and the concrete task for V6:

**`Requests.md`** (20:18) — ground rules for any LLM/session working on this project:
- Reference (read-only, never modify) `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi`
- New paths/references should follow that file's conventions
- New sub-VIs must be written to `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev`, not into this folder
- A history of changes should be kept here (this file) to minimize re-troubleshooting across chats/sessions/LLMs

**Discrepancy noted:** this names **4.5** as the reference file, while this wiki's own lineage
analysis (OVERVIEW.md) pointed at **4.6_4ParallelLoop** as the natural V6 starting point (newer,
and already has motor control in its own parallel loop — which matches the requirement below,
which assumes motor control is "already parallelized"). Not yet resolved with the user — flag before
any sub-VI work begins.

**`project-requirements/parallelization-requirement.md`** (20:27) — the concrete V6 task: split the
while loop that runs after "Done Picking Beads?" (records per-bead radial intensity profile via
multiple `For` loops) into several parallel `While` loops. That loop currently bundles: (1) motor
control — already parallelized, (2) motor reading — called out as a current frame-rate bottleneck,
(3) camera acquisition, (4) scheduler for the motor control plan, (5) merging/saving data. Goal is to
split (2)-(5) into their own parallel loops to raise CPU utilization and reduce frame dragging.

No VI evidence has been gathered yet for the "Done Picking Beads?" case/loop specifically — it wasn't
surfaced by the existing string-extraction passes (which focused on the cycling/clamp subsystem). If work
starts here, re-run `tools/decompress_vi.py` on the 4.5 (or 4.6, pending the discrepancy above) file
and grep for "Done Picking Beads" to locate the actual case/loop before modifying anything.

## V6 investigation — 2026-08-24 evening (live GUI session, first look at the real block diagram)

The 4.5-vs-4.6 baseline question was resolved in this session: user chose **4.5** as the reference.
A byte-identical working copy was made at `2. Tracking/Min_Track N beads V6_ParallelLoop.vi` (sibling
of 4.5, **not** inside `V6_ParallelLoop/` — a first attempt placed it inside this folder, one level
deeper, which broke every relative-path sub-VI dependency and cascaded through ~40 "Find the VI Named"
dialogs; moving it back to sibling depth resolved cleanly with zero missing dependencies). LabVIEW
2026 turned out to be actually installed on this machine (contradicting `ANALYSIS_METHOD.md`'s "no
LabVIEW available" assumption — worth fixing there too), and was driven live via screenshot + simulated
mouse/keyboard (PrintWindow for reliable window capture; the Alt-key foreground-lock workaround to get
real keyboard focus; right-click-down → drag to menu item → release, since LabVIEW's context menus open
on mouse-down, not mouse-up).

Findings from that session, opening the actual block diagram:
- `Done Picking Beads?` (front-panel boolean) was confirmed via **Find Terminal** to wire directly into
  a While Loop's **Stop-if-True** conditional terminal — i.e. it ends whatever loop runs during bead
  selection.
- The VI's whole top-level diagram is one large **Sequence Structure**, roughly 8-9 frames wide.
  Frames identified in order: the bead-picking loop → the `Done Picking Beads?`-gated stop → a
  bandpass-filter-setup frame (comment: *"Makes filters needed for the tracking routine"*) → a frame
  with `MainCycle`/`SubCycle`/`Start Moving?`/`Target` wired to `MOV.vi`/`VEL.vi` → several further
  frames, then the sequence ends.
- Text-searched the diagram for `"Motor"` (1 hit, inside library VI `GCSTranslateError.vi` — not
  useful) and `"radial"` (9 hits, all internal to `calibration- generate 1/2 I of r, reentrant.vi` —
  confirms these sub-VIs exist as dependencies, but not where they're *called from* in the main VI).

**Correction, per `project-requirements/project-description.md` (added 2026-08-25) — see
OVERVIEW.md "Experimental workflow":** the Sequence Structure scrolled through above almost certainly
covers workflow steps 1-3 (manual acquisition, bead selection, per-bead radial-profile *calibration*
producing a one-time `.cal` file) — **not** step 4, the continuous experiment loop that is the actual
parallelization target. The `MainCycle`/`SubCycle`/motor frame found is plausibly still part of this
setup sequence (the cycling/clamp state machine), not step 4's "Loop 2". The user's own description
names exactly **two** step-4 While Loops — Loop 1 (motor writing only, already separate) and Loop 2
(motor reading + camera acquisition/processing + scheduling + data saving + **printing to the
screen**) — which still needs to be visually located, likely outside/after the Sequence Structure
rather than as one of its frames. Resume the search there before doing any diagram surgery.

## Kernel investigation — 2026-08-25 (Track N beads four-fold over-kernel-v3.vi)

Separate thread from the main-VI loop hunt above: the user asked to rebuild
`Track N beads four-fold over-kernel-v3.vi` (the per-bead tracking kernel called from within the main
VI's experiment loop) so it processes beads in a genuinely parallel For Loop instead of sequentially.

Opened the actual kernel VI (scratch copy, original at
`zz_LabView VI\background VIs\Track N beads four-fold over-kernel-v3.vi` untouched) in LabVIEW.
Confirmed via its connector pane that it already takes the whole `Image` in once, plus per-bead arrays
(`Array of cal clusters`, `x,y,z array`, `pos in cal image in`, `# of bead 4 packs`,
`4 pack remainder`), and outputs per-bead arrays (`x,y,z array out`, `Bead is good? array out`,
`pos in cal image out`) — i.e. the connector pane already has the shape the user wants; the problem is
purely in how the body executes.

On the block diagram, the outer For Loop (over `# of bead 4 packs`) **already has an `N`/`P` terminal
pair** — `P` is LabVIEW's "number of generated parallel loop instances" terminal, only present once
"Configure Iteration Parallelism" has been enabled on that loop — but `P` was unwired (shown hollow,
vs. `N`'s solid wired appearance), meaning the parallel machinery exists but isn't actually driven, so
the loop runs with effectively one instance. The neighboring structure to its right (with a `◄3►`
selector in its border) is a Case Structure handling the `4 pack remainder`, not a second loop.

Each pack iteration calls two reentrant sub-kernels, confirmed via connector-pane string diffs:
- `Track 1 of N bds xyz-kernel-reentrant.vi` — **single-bead only** (every I/O suffixed "1":
  `Calibration cluster 1`, `starting x/y 1`, `X/Y/Z pos 1`, `Bead 1 is good?`). Takes the whole `Image`
  and crops its own ROI internally via `rect coord from center.vi`. No cross-bead coupling.
- `Track 2 of N bds xyz-kernel-reentrant-v2.vi` — **bundles two beads per call** (`Calibration cluster
  1` *and* `2`, `X/Y pos 1` *and* `2` both present as separate inputs in the same connector pane). The
  user visually inspected its diagram and confirmed the two beads are tracked sequentially/coupled
  inside this one call (plausibly the shared complex-FFT bandpass trick common in this style of
  diffraction tracking — packing two real profiles into one complex transform — though the exact
  wiring wasn't fully traced).

**Decision:** the four-fold/Track-2-pairing scheme is not a safe unit to parallelize on (two beads'
data already entangled per call). Build the new parallel kernel around **`Track 1 of N bds
xyz-kernel-reentrant.vi` only**, one call per bead per iteration, in a fresh parallel For Loop. Full
current plan and next steps: see `STATUS.md` (kept up to date; this entry is the historical record of
how the decision was reached).

Nothing was modified or saved during this investigation — only a scratch copy was opened, and LabVIEW
was closed with no changes. New VI work per this decision has not yet started.
