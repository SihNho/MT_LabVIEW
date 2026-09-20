---
type: reference
status: current
date: 2026-09-12
tags: [docs]
---

> **DRAFT / PROPOSAL — nothing here has been built, and no VI was modified to produce it.**
> Every number below is read from the working copy; every improvement is a suggestion awaiting the user's decision.

# The three While loops: what each one does, and where the frame budget goes

Step 0 of [t0-instrumentation-plan.md](t0-instrumentation-plan.md), completed 2026-09-12. Read-only throughout.
Data: `tools/bench/diagram_tree_main.json` (all 170 diagrams), `tools/bench/loop_contents.json` (the three loops in
detail). Method validated first on two VIs we built ourselves, so the diagram indices mean what we think they mean.

## The question this closes

[MAIN_VI_MAP.md](MAIN_VI_MAP.md) §4 listed "which of the 3 While loops each region belongs to" as unknown since
2026-08-30, and everything about loop multiplication depended on it. It is now answered.

## The map

All 170 diagrams were walked without a single failure, and all 63 structure nodes were placed, so the skeleton is
complete rather than sampled.

| While loop | diagram | nodes | subVIs | Property Nodes | role |
|---|---|---|---|---|---|
| A | 20 | 13 | 1 | 3 | **motor loop** — the one `Motor control v5` call |
| **B** | **43** | **75** | **6** | **10** | **the frame loop** — holds the tracking kernel |
| C | 99 | 22 | 5 | 2 | **display / user-interaction loop** — grab, pixmap, mouse, focus keys |

The tracking call site, uid 5058, sits **directly on diagram 43's body, not inside a case frame**, so it runs
unconditionally on every iteration. Loop B carries more nodes than A and C combined, and nests 10 Case Structures,
4 For Loops and 1 Event Structure inside itself.

Loop A being a single motor call matches the version history: `4.4_MotorParallelLoop` split motor control into its own
loop, and that is exactly what is there.

## What is inside the frame loop

The six subVIs, identified by their connector-pane terminals (uid 6810 independently matches the `get buff image-lost
frames` uid recorded in MAIN_VI_MAP §3b, which cross-checks the whole identification):

| uid | terminals that identify it | what it is | must it be inline? |
|---|---|---|---|
| 6810 | `Session In` | camera buffer bookkeeping | **yes** — it is the frame source |
| 22700 | `Image Out (duplicate)` | IMAQ image duplicate | probably — feeds the consumers |
| 5058 | `x,y,z array out`, `Array of cal clusters` | the tracking kernel | **yes** |
| 48 | `Focus inc reference`, `In position`, `VISA resource name` | ASI autofocus | **no** |
| 1114 | `Lp`, `Lc`, `Baseline`, `F-x in/out` | worm-like-chain fit | **no** |
| 376 | `total data array`, `file progress`, `selected path`, `saved file refnum` | trace file writing | **no** |

Also on that diagram: **10 Property Nodes, every one of them a `Value` access**, plus 2 timing primitives and 4
file-IO-flagged nodes.

## Why this explains the user's instinct

The user's account was that the motor path was badly delayed, that 115200 baud and a partial loop split were adopted to
fix it, and that one loop still seemed to carry too much. The map says the instinct was right and names the reasons.

1. **Three of the six per-frame subVIs do not have to be on the critical path.** Autofocus, the WLC fit and the trace
   writer all consume tracking results or drive slow hardware; none of them produces anything the next frame's
   acquisition or tracking needs.
2. **A `Value` property node costs a UI-thread switch.** There are 10 in the frame loop and 3 more in the motor loop.
   The UI thread is also where the front-panel graphs redraw, so the loops that were deliberately separated meet again
   there. This is the concrete mechanism behind "split the loops and it still feels serialized".
3. **The autofocus subVI is the worst single offender.** The audit in [motion-path-audit.md](motion-path-audit.md) found
   it contains the only fixed `Wait (ms)` on the whole motion path, five or more property-node `Value` accesses, and its
   own VISA traffic — and it sits in the frame loop.

## Improvements, cheapest and safest first

Nothing here has been implemented. Each item states what it costs to prove.

**1. Stop calling autofocus every frame.** It holds a fixed Wait, VISA traffic and UI-thread accesses, and focus does not
drift at frame rate. Gating it to every N frames, or moving it into loop C (which already owns the focus keys and
the same `Focus inc reference` terminals — uid 15921 there is the same VI), removes all of that from the frame budget.
This is the largest single win available and it changes no computation.

**2. Replace `Value` property nodes with wires or shift registers.** Ten in the frame loop. A property node reads or
writes through the UI thread; a wire does not. Where a control's value is only being read once per iteration, the
terminal itself is enough. This is mechanical, reversible, and does not touch the tracking maths. Expect it to be the
main lever on `t0` if `t0` turns out to be UI-bound.

**3. Move the trace writer to a consumer loop with a bounded queue.** This is exactly case 2 of the decision rule in
[parallel-strategy.md](parallel-strategy.md): split the write when write stalls cost frames, for determinism, not for
throughput. It needs an ownership-controlled image pool only if images cross the boundary — here only the xyz arrays do,
which makes it far cheaper than a full acquisition pipeline.

**4. Move the WLC fit off the per-frame path.** It is force-extension analysis for display; it does not need to run at
frame rate at all.

**5. Leave the acquisition pipeline alone until measured.** Per the decision rule, if worst-case acquisition plus
analysis plus write already fits inside the camera period, pipelining adds latency, buffers and IMAQ lifetime hazards
for no gain. That measurement is Step 1 to Step 3 of the plan and still pending.

## What this does NOT yet establish

- **The size of each cost.** This is a structural map, not a timing measurement. "Autofocus is in the frame loop" does
  not say whether it costs 0.2 ms or 4 ms. Steps 1 to 3 of the plan measure that, and only Step 4 in the real loop
  closes the isolation gap.
- **Which case frames are actually taken each iteration.** Ten Case Structures nest inside the frame loop; some of their
  contents run only in certain states, so the 75-node figure is an upper bound on per-iteration work.
- **The Wait's constant.** The fixed delay inside the autofocus VI was detected, not read.
