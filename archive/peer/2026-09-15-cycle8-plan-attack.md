# cycle8-plan-attack

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **date:** 2026-09-15
- **outcome:** ANSWERED (395s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

THE PLAN (attack it; it will drive the next several cycles and I have been wrong three times today on adjacent
readings, each time by quoting a summary without reading the section that qualified it).

GOAL, set by the user today: acceptance is the requirement in project-requirements/parallelization-requirement.md
in FULL - camera acquisition, tracking, motor reading, the scheduler and data merging/saving each running in its own
parallel loop. The main VI today has three While loops: diagram 20 (motor control), diagram 43 (the frame loop,
which holds everything else), diagram 99 (display/UI). The target is the seven-loop architecture in
docs/restructure-plan-4.6.md section 3.

METHOD: do the restructuring INSIDE A COPY of the original VI (rule 1: the original is never modified), so bead
picking, calibration, the controls and the experiment workflow survive rather than being rebuilt.

OVERLOAD POLICY, decided by the user today: acquisition -> tracking is LOSSY and LATEST-WINS (pool exhausted =>
abandon the oldest unprocessed frame, reuse its slot, never block acquisition), while tracking -> file writer stays
LOSSLESS and FIFO, and every result carries its frame number so gaps are explicit. The user's reason was the rigor
of the time series: a result computed from a stale frame is a sample attached to the wrong moment.

WORK QUEUE, all of it possible with the rig DISASSEMBLED (reassembly costs the user 2+ hours of sample prep, so
every rig-bound measurement is deferred and batched into one later session):
 1. OpOwnerChain_v0 - a reader taking a UID and returning its owner UID and class. Donor: the existing
    OpWireSource_v5 with its Wire cast removed. The semantics are already MEASURED and recorded at docs/NAMES.md
    line 823: a node's Generic.Owner is its frame Diagram, and that Diagram's Owner is the structure.
 2. The full diagram hierarchy for all 170 diagrams -> docs/diagram-hierarchy.md plus JSON.
    tools/bench/diagram_tree_main.json already has each diagram's owner CLASS and node uid list, but NO parent
    link, so nobody knows what is nested inside what.
 3. Which loop encloses the 11 PI motor / rotor call sites (MOV.vi x7 on diagrams 3,36,40,69,121,125,129; VEL.vi x4
    on 5,69,91,129; POS?/TMN?/TMX?/GOH on 5,91; Magnet2Force on 42,74). The requirement calls motor READING a
    frame-rate bottleneck, and I have not established which loop those sites are in.
 4. Census of Case #10445's frames, and the frame loop's TRUE membership - my earlier "6 subVIs in the frame loop"
    counted only diagram 43's body, not its 10 nested Case structures, 4 For loops and 1 Event structure.
 5. The unconditional per-frame path: what executes every iteration versus conditionally.
 6. Fixture timing: instrument a copy, replay all 10,043 recorded frames, report p50 AND p99 per stage.
 7. One vertical slice: acquisition -> owned image handoff -> queue core -> frame-identified result, including stop,
    error, reseed and overload. Reseed is testable on the fixture's 13 real lost-bead frames.

WHAT IS ALREADY BUILT AND VERIFIED: Track_v6_CPU_queue_v0.vi runs all 10,043 fixture frames in 7.5 s with the first
10,018 (those before the first bead loss) bit-identical to the reference; it is a replay artefact with FOR loops and
no live acquisition. A fleet of ~168 scripting op VIs exists.
ATTACK SPECIFICALLY:
(a) MOVING CODE, not reading it. Every measurement so far has been read-only. Step 7 onward requires relocating
    existing nodes out of diagram 43 into new loops inside the same VI. Does LabVIEW VI Scripting actually support
    moving a node to a DIFFERENT diagram, and does our documented toolkit (docs/toolkit-capabilities.md) have it?
    If it does not, the whole in-place method collapses and I have not noticed. What is the evidence either way?
(b) Is the queue order right? Should the hierarchy come before or after a first structural experiment?
(c) The user says the kernel path is already trusted from repeated testing, so acceptance moved to full
    parallelisation. Does that trust survive the move from replay (FOR loops, recorded TIFFs) to live-shaped code?
(d) What in this plan cannot be validated without the rig, beyond the stage-3 schedule timing I already know about?
(e) What is the single biggest risk in this plan that I have not named at all?

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The plan is wrong as sequenced: it assumes the new latest-wins policy is compatible with the existing image-pool ownership design, but that design still says ?쐍o free slot ??drop the new frame.??Reusing the oldest queued slot is a different state machine. Until that is specified and stress-tested, the system can produce exactly the forbidden failure: descriptor `{frame=N, slot=S}` reaching tracking after slot `S` has been overwritten with frame `M`.

### 1. Strongest reason the plan is wrong

The overload-policy change invalidated [frame-ownership-design.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/frame-ownership-design.md>):

- The existing design requires acquisition to obtain a free slot before filling it.
- When none is free, it drops the new frame.
- The new policy instead evicts the oldest unprocessed frame and immediately reuses that frame?셲 slot.

That reuse is safe only if eviction and recovery of the corresponding slot descriptor are atomic with respect to tracking?셲 dequeue. LabVIEW?셲 Lossy Enqueue can help because it removes the oldest queued element without blocking and returns both the overflowed element and an `overflow?` flag?봟ut the plan does not yet say how acquisition obtains the destination slot before copying, handles slots already owned by tracking, or prevents stale descriptor/slot reuse. [NI?셲 Lossy Enqueue specification](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/lossy-enqueue-element.html)

This is the largest unnamed risk. Step 7 says ?쐇ncluding overload,??but overload is now an architectural redesign, not merely another test case.

A workable shape may require an extra FILLING slot and rotation: acquire into the one slot not owned by either queue or tracking, lossy-enqueue its descriptor, and?봮n overflow?봴se the returned old descriptor?셲 slot as the next FILLING slot. Generation numbers or pixel sentinels should detect accidental reuse. NI specifically warns that IMAQ image values are references to reusable memory and can display/process the wrong image when buffers are overwritten without explicit ordering. [NI image-buffer race explanation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAovSAG)

### 2. Alternative explanations of the evidence

Two apparent successes/failures have less favorable explanations:

- The earlier ?쐌oving a node broke the VI??result does not prove reparenting failed. [toolkit-capabilities.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/toolkit-capabilities.md>) records that the VI was already broken because the newly created For Loop had no `N`; the probe also capped both node counts at 40 and therefore did not establish whether ownership changed.
- The 10,018 bit-identical frames can be explained by the fixture supplying stable, contiguous TIFF inputs with no forced queue overflow. It establishes kernel numerics before bead loss, not live handoff correctness. A live IMAQ image is reusable referenced memory, unlike an immutable TIFF file already read for that iteration. [NI on IMAQ image references and execution ordering](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P8khSAC)

### 3. What would falsify the plan?셲 claims

Any one of these observations falsifies the relevant claim:

- Under forced overload, tracking receives `{frame=N, slot=S}` while the pixels in `S` carry a sentinel for another frame.
- A slot is returned twice, never returned, or reused while tracking owns it.
- A representative moved fragment cannot be saved/reopened runnable with its owners, terminal types, case membership, and data dependencies preserved.
- After an injected gap immediately before a lost-bead condition, the new code?셲 reseed/state trajectory differs from an explicitly specified gap-aware reference.

Conversely, my ownership objection would be defeated by a prolonged forced-overload run showing monotonically ordered result IDs, exact accounting of every discarded ID, zero pixel/descriptor mismatches, constant pool cardinality, and clean stop/error drainage.

### 4. Answers to (a)??e)

**(a) LabVIEW supports changing diagrams; the present toolkit does not yet provide the general operation required.**

NI documents `GObject.Move` with an optional `owner`: specifying an owner moves the object into that owner; specifying an owner in another VI makes a copy. Thus a destination subdiagram is supported in principle. [NI `GObject.Move`](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/move.html) NI also documents pasting clipboard contents onto an `AbstractDiagram`. [NI `AbstractDiagram.Paste`](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/abstractdiagram/pasteselection.html)

Locally, however:

- `move_object()` leaves `owner` unwired, so it only changes position within the current diagram.
- `move_out()` hardcodes the destination as the top-level block diagram and explicitly says the attached wires break.
- `copy_by_index()` copies an object from a donor; it is not an existing-node relocation into an arbitrary subdiagram.
- Direct construction inside a specified diagram is tested, but that rebuilds nodes rather than relocating the existing fragment.

Therefore the in-copy method does **not** collapse because LabVIEW lacks the operation. It remains unproven because the fleet lacks a verified `source UID ??arbitrary destination Diagram UID` relocation operation and, more importantly, a verified way to preserve or reconstruct the fragment?셲 crossing wires and structure semantics.

**(b) A structural feasibility experiment must precede the 170-diagram hierarchy.**

Recommended order:

1. Minimal `MoveToDiagram`/selection-paste experiment on a disposable synthetic VI.
2. Repeat on one representative but harmless fragment in a copy of the main VI, compile-only.
3. If both pass, build the complete hierarchy and use it to select real extraction boundaries.
4. Then census, unconditional-path analysis, timing, and construction.

The hierarchy is valuable, but it cannot establish whether the construction method works. Spending several cycles cataloguing 170 diagrams before testing the indispensable mutation primitive is backwards.

**(c) Kernel trust survives only as a narrow numerical claim.**

Trust currently covers the kernel given the same ordered inputs and state, through the first 10,018 pre-loss frames. It does not cover:

- asynchronous producer/consumer scheduling;
- explicit frame gaps;
- reused IMAQ memory;
- reseed behavior after arbitrary gaps;
- error and stop propagation;
- timestamps and frame identity;
- output ordering and lossless writer drainage.

LabVIEW?셲 dataflow rules mean changing wiring and loop boundaries can change execution ordering even when the individual mathematical nodes are unchanged. [NI dataflow execution model](https://www.ni.com/docs/en-GB/bundle/labview/page/block-diagram-data-flow.html)

**(d) Additional validation that still needs the assembled rig**

Beyond scheduler/motor-command timing:

- Camera throughput, jitter, returned buffer-number behavior, driver overwrites, and `Images Missed` at 150 Hz.
- Whether acquisition timestamps correspond closely enough to physical exposure/capture time.
- PI motor-reading latency and its interaction with other motor traffic.
- Actual ASI focus-command frequency, latency, and exclusive VISA ownership during focus activity.
- Live reseed after gaps, motion, blur, and bead loss patterns not represented by the 13 fixture events.
- End-to-end picking/calibration/experiment workflow against real images.
- Real hardware error behavior: timeouts, unavailable buffers, and device communication failures.

Synthetic load can validate writer throughput, queue drainage, UI contention, and pool invariants without the rig; it cannot validate the device/driver timing distribution.

**(e) Biggest unnamed risk**

The latest-wins decision silently superseded the already-reviewed free/work-queue ownership protocol. Unless that protocol is redesigned first, a frame number in the result does not guarantee that tracking actually processed that frame?셲 pixels.

I do not believe the current plan holds as written. I would change my mind after a representative cross-diagram relocation survives save/reopen and the revised ownership protocol passes forced-overload invariants.

**Cheapest discriminating test:** before hierarchy work, run an entirely synthetic image-pool test with a deliberately slow consumer, unique frame IDs embedded both in each descriptor and its pixels, and enough production to force hundreds of evictions; fail on the first ID mismatch, duplicate/lost slot return, unexplained gap, or shutdown leak.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
