---
type: reference
status: current
date: 2026-09-12
tags: [docs, plan]
---

# Plan: attribute `t0`, the fixed per-frame cost — design only, nothing executed

Written 2026-09-11 at the user's request ("설계만 짜봐"), with the camera disconnected and no hardware available.
Nothing here has been run. This is the plan the loop-multiplication decision depends on.

## Why this comes before any loop restructuring

[ARCHITECTURE.md](../ARCHITECTURE.md) §10 fits the user's field data to `t_frame = t0 + N · t_bead` and gets
**t0 ≈ 4.7 ms** fixed and **0.67 ms per bead**, against a 6.67 ms budget at 150 Hz. Two consequences:

- the fixed cost eats about 70 % of the frame budget before a single bead is tracked;
- even with a free kernel the rig cannot pass roughly **214 Hz** until `t0` is cut.

The kernel work is done. `t0` is now the whole remaining budget, and **it has never been measured** — 4.7 ms is
back-calculated from frame-loss thresholds, not instrumented. Pipelining converts a sum into a max, so its payoff equals
the size of the work that can leave the critical path. That size is exactly what this plan measures. Restructuring first
would be guessing.

## Step 0 — which subVIs are actually on the per-frame path (read-only, scriptable, no hardware)

**The failure mode this prevents:** measuring a VI that runs once per clamp cycle as if it ran every frame.

The main VI has 3 While loops, 97 SubVI nodes and 23 distinct project VIs; [MAIN_VI_MAP.md](MAIN_VI_MAP.md) §4 lists
"which While loop holds what" as still unknown. Resolve it by UID matching, the technique already proven for loop
subdiagrams: enumerate each While loop's subdiagram and collect the SubVI node UIDs inside it, then intersect with the
97-node report. Output: a table of `subVI → enclosing While loop → enclosing Case frame`.

The per-frame set is then the loop that contains the tracking call site (node 39, uid 5058), minus anything sitting in a
Case frame that only runs on a state change.

Deliverable: `docs/per-frame-path.md`, a list of VIs with "every frame" / "per cycle" / "on event" against each.
Everything after this step measures only the "every frame" list.

## Step 0b — the serialization audit: why splitting loops may not have helped (read-only, no hardware)

Added 2026-09-11 after the user supplied the decisive piece of history: *the motor path was badly delayed, 115200 baud and
a partial loop split were done deliberately to fix it, and it still feels like one loop carries too much.*

**Transmission was never the bottleneck.** At 115200 8N1 a byte costs 87 µs, so a 10-byte command plus a 10-byte reply is
under 2 ms of wire time. Raising the baud rate could only ever remove that much, which is why it did not help.

**Measured on this PC, 2026-09-11 (registry read, no hardware attached):**

| port | driver | LatencyTimer |
|---|---|---|
| COM3, COM4 | Sunix serial card (`SNX_SerialPort`) | n/a |
| COM5, COM6 | FTDI `VID_0403 PID_6001` | **16 ms (the driver default)** |
| COM8, COM9 | `VID_0D4D` | not set |

An FTDI latency timer of 16 ms means a short reply can wait in the chip's buffer up to 16 ms before Windows delivers it —
more than two whole frame budgets at 150 Hz, and **independent of baud rate**. The motor is on COM3 per
[MAIN_VI_MAP.md](MAIN_VI_MAP.md) §3b, so it is not the FTDI path; what sits on COM5/COM6 must be identified (the main
VI carries a comment block with the COM map, and ASI Tiger/TG-1000 controllers commonly present as FTDI). If a device
that is queried per frame lives there, it alone could account for much of `t0`.
Remedy if confirmed: Device Manager → that port → Port Settings → Advanced → Latency Timer 16 → 1 ms. No code change,
reversible, free.

**Why a separate motor loop can still stall the frame loop.** Three mechanisms, to be checked by script:

1. **A non-reentrant subVI shared between loops becomes an accidental mutex.** The second caller blocks until the first
   returns; if the first is inside a serial round trip, the frame loop stops for that long. Audit: for every VI called
   from more than one While loop, read `Execution:Reentrancy Type` (VI property **288**, already in
   docs/vi-server-ids.json) and flag every non-reentrant one. This is the highest-value check in the whole plan.
2. **UI-thread serialization.** Anything running in the UI thread queues behind all other UI work, including the
   Intensity Graph redraw — which would couple the motor loop to the display cost measured in Step 2.
3. **Execution-system thread starvation.** A blocking VISA read holds a thread from the execution system's pool.

Note: `Global motor pos.vi` is 4,700 bytes, the size of a pure VI Global rather than a shift-register functional global,
so it is probably not acting as a hidden mutex. It remains a race-condition carrier, and no new global writers may be
added (MAIN_VI_MAP §3).

Deliverable: a table of every multi-loop-shared subVI with its reentrancy setting and execution thread, plus the COM map
read out of the main VI's comment block.

**Partly answered already — see [motion-path-audit.md](motion-path-audit.md) (2026-09-12).** The FTDI lead is closed: the
user confirmed both instruments are RS-232 into the Sunix card, whose latency is about 0.35 ms. The audit of every VI on
the motor/stage path found no fixed Wait in PI's command VIs, exactly one in the lab's own `ASI_adjust focus-subvi.vi`,
**19 front-panel property-node `Value` accesses in the lab code** (a UI-thread cost that would re-serialize loops that
were deliberately split), a controller-error query after each PI MOV/VEL command (two round trips per command), and a
size-1 semaphore plus a byte-count VISA Read inside ASI's `Send Serial Command.vi`. `Global motor pos.vi` was confirmed a
pure VI Global, so it is not a hidden mutex. The remaining question for this step is therefore narrower: **how many of
those property-node accesses sit on the per-frame path, and do they share a loop with the display?**

## Step 1 — per-VI cost, camera-free (can run as soon as Step 0 lands)

Method is the one already validated on the kernel: `HARNESS_<name>` = `HARNESS_base` plus the one VI under test, driven
from the recorded fixture, interleaved against `base` on the same frames, cost = `median(harness) − median(base)`.

Candidates, all hardware-free:

| group | VIs | why suspected |
|---|---|---|
| conversion | `Omars IMAQ ImageToArray.vi` | runs per frame per bead group; array copy of a 1280×1024 frame |
| display | `Flatten Pixmap.vi`, `Draw Flattened Pixmap.vi`, `grayscale color table.vi`, `rect coord from center.vi`, `Draw Grayed Out Rect.vi`, `Draw Circle by Radius.vi`, `Draw Text at Point.vi` | ARCHITECTURE §10 names display as suspect #1 |
| plots | `N bead plot Z.vi`, `N bead plot dZ.vi` | redraw per frame |
| logging | `save trace.vi`, `save N xyz traces.vi` | file I/O on the critical path |
| checks | `check N bead pos v3-kimlab.vi`, `Median Filter.vi`, FIR filter VIs | per-bead post-processing |

Each needs its input contract read first (`fp_labels` + `Get Outputs` probes) and realistic inputs assembled from the
fixture: frames for the image inputs, the reference `.tra` rows for xyz arrays, `cal002` for calibration clusters.

Deliverable: a table of ms/frame per group, plus their sum.

## Step 2 — the rendering component, panel visible (no hardware)

A VI run over COM does not display its front panel, and an Intensity Graph only costs what it costs when it is actually
drawn. Step 1 therefore **underestimates display**, which is the prime suspect.

Repeat the display and plot cells with the harness front panel opened and on screen (`open_panel(..., activate=True)`),
and report both numbers. The difference bounds the rendering component. State it as a bound, not a value: an
always-on-top panel in a benchmark is still not the real experiment's window layout.

## Step 3 — acquisition (needs the camera, not the motor)

Blocked today: the camera is disconnected. The camera is otherwise permitted hardware.

Measure two things with no tracking and no display: the achievable frame interval of a bare IMAQdx grab loop, and the
cost of `get buff image-lost frames.vi` per frame. This gives the acquisition term and the true camera period `T_f`,
which the decision rule below needs.

## Step 4 — in-situ cross-check (needs the user present; motor and piezo initialise)

**Non-negotiable, not optional.** This session proved that a VI measured in isolation can behave differently in place:
`TRACK_kernel_v1` costs 1.3–1.8 ms more inside its case wrapper than the same GPU kernel called directly, and the DLL's
own timing was identical in both — a host-side copy the harness could never have shown
(archive/bench-2026-09-10-track-kernel-timing/REPORT.md). So every Step 1 number is a **lower bound** on the in-situ cost.

Instrument the working copy with tick counts bracketing the per-frame regions Step 0 identified, run it once under the
user's supervision, and compare the measured frame delay against the sum from Steps 1–3. Running the main VI executes its
initialisation frame, which contains the PI motor's `GOH` (go home) and the ASI stage's `MOVE AXIS TO POS`, i.e. real
motion — which is why this step waits for the user and never runs unattended.

**Prediction contract:** the sum from Steps 1–3 plus the measured kernel should land near the field-derived
`4.7 + N · 0.67` ms. A large shortfall means a cost exists that isolated measurement cannot see, and the gap itself
becomes the next target.

## Measurement hygiene, learned the hard way this session

Bake these into the driver, not into anyone's memory:

1. **Only within-pass comparisons are valid.** The same `gpuk` harness read 1.98, 2.63 and 2.20 ms/frame in three
   conditions. Two numbers may be compared only if they came from the same `run_timing` pass.
2. **Never touch the VI under test through VI Server before timing it.** It loads the front-panel data space and adds
   about 9 ms per call. Configure, restart LabVIEW, then measure.
3. **Warm the OS file cache** before each cell (260 MB for 200 frames, 0.2 s once warm).
4. **Auto-flag non-results:** if `base` is slower than any loaded harness, the cell is contention-spoiled — mark it and
   do not report it. Log which known contaminants are running.
5. **Fresh LabVIEW per repeat**, GPU clocks recorded before and after, three repeats minimum.

## Decision rule this produces (restating [parallel-strategy.md](parallel-strategy.md) with the new numbers)

Let A = acquisition, B = analysis, W = display + logging, `T_f` = camera period.

| finding | action |
|---|---|
| worst-case `A + B + W` < `T_f` | camera is the bottleneck. Do **not** restructure; pipelining only adds latency, buffers and IMAQ lifetime hazards |
| `W` is large and off the critical path | split **only** display and logging into a consumer loop with a bounded queue. This is where loop multiplication actually pays |
| conversion dominates | prefer the GPU backend: `GPU_kernel_v1` already takes the raw IMAQ pixel pointer and skips `Omars IMAQ ImageToArray` entirely |
| `t0` is spread thin with no dominant term | no restructuring is justified; the ~214 Hz ceiling stands and the next lever is elsewhere |

## Risks this plan does not remove

- **Isolation bias.** Step 1 numbers are lower bounds; only Step 4 closes that gap.
- **Race exposure.** The main VI carries no Queue, Notifier or Semaphore anywhere; its 3 loops share state through VI
  Globals such as `Global motor pos.vi`. Any new loop must not add a global writer.
- **IMAQ image lifetime.** An image wire is a pointer, not a snapshot. Any pipeline needs a preallocated, ownership-
  controlled image pool, and that is the bulk of a pipeline's real cost.
- **Equivalence surface.** The kernel swap touched one node and its connector pane was the whole contract. Loop
  restructuring is a scheduling change (permitted) but the numbers that must be proven identical cover far more of the VI.
