# restructure-in-copy-plan

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **date:** 2026-09-15
- **outcome:** ANSWERED (173s)
- **why asked:** Mandatory plan review before construction: the user had just approved restructuring inside a copy
  of the original with the loop splits ordered kernel -> ASI serial -> display -> scheduler/writer.
- **verdict:** PREMISE REFUTED, plan revised; the copied-original SHELL survives, the ORDERING does not. Verified
  against our own files the same hour. (1) The 5.06 ms "kernel + one serial round trip" is **not** the ordinary-frame
  cost: `docs/camera-acquisition-facts.md` line ~139 is headed *"ANSWERED: the frame loop does NOT transact serial
  every iteration (2026-09-12)"* — the ASI wrapper's unconditional top-level diagram is five nodes, of which the VISA
  case is a **gate only**; the real per-frame cost is **two UI-thread property reads**. I quoted the document's
  summation at line 183 and missed its own answer 44 lines earlier. So "move ASI out to win ~2.5 ms per frame" is
  void, and ASI-first ordering has no performance support. (2) I again overstated my own instrument: the 49 nets are
  labelled "NOT resolved here" **by my own script**, yet I reported them as "already running to the loop border";
  the richer census in `frame-loop-wire-graph.md` finds only **31** actual loop tunnels. (3) `save trace.vi` #376
  being in the slice proves the 22 nodes are a *reachability* slice, not a kernel component — lifting it would drag
  file ownership and accumulated `total data array` state into tracking; the proper seam is an immutable,
  frame-identified result message **before** the writer. (4) Case #10407 carries VISA **resource ownership** via
  `Outgoing Handle`, not just a wire — split carelessly it creates two VISA owners; the ASI loop must own the
  session exclusively and exchange sequenced commands. ADOPTED in place of my ordering: **measure the unconditional
  per-frame path, build one live vertical slice, then split whichever measured owner dominates.**

## Question

ATTACK THIS PLAN before any construction starts. It will drive the next several cycles, and I have already been wrong twice on this same topic today. PLAN: restructure the main VI INSIDE A COPY of it (never the original; rule 1), splitting loops in this order - (1) tracking kernel into its own loop using the already-verified Track_v6_CPU_queue_v0 core, (2) the ASI serial read out of the frame loop, (3) the front-panel/display updates out, (4) scheduler and file writer. Rejected alternatives: replace only the acquisition/tracking hot path (leaves the ASI serial and the property nodes in the frame loop, which is exactly what the budget measurement says to remove), and rebuild the seven-loop top level in an empty VI (discards bead picking, calibration, controls and workflow that must exist before anything can run). EVIDENCE I AM RELYING ON, attack any of it: docs/camera-acquisition-facts.md measures kernel plus one serial round trip at 5.06 ms of a 6.00 ms budget and claims moving the serial read and display out returns ~2.5 ms = 150 Hz to 200 Hz; docs/frame-loop-anatomy.md says the VI already has three While loops (20 motor, 43 frame, 99 display/UI) and that loop 43 holds 75 nodes, 6 subVIs, 10 property nodes, 10 Case structures, 4 For loops and 1 Event Structure; tools/bench/slice_cutset_acq_track.py (log in the same folder) computed the kernel slice at 22 of 75 nodes with 21 nets crossing to sibling nodes, 18 internal, 49 already running to the loop border, and 0 Locals, 0 Globals, 0 FeedbackNodes anywhere inside diagram 43. SPECIFIC THINGS TO ATTACK: (a) is in-place restructuring inside a copy actually easier than a fresh rebuild, or am I underestimating the cost of untangling 21 sibling couplings inside a diagram that Clean Up Diagram scrambled - see docs/restructure-plan-4.6.md section 4; (b) is the ordering right, or should the ASI serial come out FIRST since it is a blocking serial round trip while the kernel is pure computation; (c) save trace.vi #376 is inside the kernel slice and case #10407 exchanges Out position and Outgoing Handle with the ASI focus subVI #48 - do these two entanglements break the plan; (d) does moving the kernel out actually buy anything if the ASI serial stays, or does the frame loop simply become serial-bound; (e) what have I not measured that I am assuming.

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The plan?셲 strongest premise is wrong: **the 5.06 ms figure is not a normal-frame budget.** It adds an unconditional 2.43??.87 ms tracking kernel to a roughly 2.1??.56 ms serial transaction that the same report proves occurs only while a focus control is active. The report itself concludes, ?쐓erial does not block 150 Hz.??Therefore moving ASI cannot be credited with returning ~2.5 ms on ordinary frames, and ASI-first ordering is unsupported. See [camera-acquisition-facts.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/camera-acquisition-facts.md:140>) and its contradictory summation at [line 183](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/camera-acquisition-facts.md:183>).

### 1. Why the claim is wrong

The evidence conflates four different things:

- ?쏞alled every frame??is not ?쐏erforms serial I/O every frame.??The unconditional ASI wrapper executes two `Value` property reads and a case selector; its VISA motion/query nodes are conditional.
- The 10 property nodes are a structural census, not 10 unconditional UI-thread crossings. Only two inside the ASI wrapper have been shown unconditional.
- The 2.1 ms ASI `WHERE` cost is an estimate derived from one short `/` exchange, not a measured `WHERE` transaction.
- The 49 cut-set nets are **not established loop-border connections**. The script explicitly classifies every one-terminal-visible net as ?쐋oop tunnel, shift register, front-panel terminal or constant?봏OT resolved here.??Calling all 49 ?쏿lready running to the loop border??overstates the instrument. See [slice_cutset_acq_track.py](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/slice_cutset_acq_track.py:70>). The richer border census finds only 31 actual loop tunnels and leaves many half-edges attributable to shift registers or nested structures; see [frame-loop-wire-graph.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/frame-loop-wire-graph.md:217>).

NI confirms that VISA Read completion depends on requested byte count, termination configuration, and timeout, so a large requested count can indeed block?봟ut that establishes the possible cost of an executed read, not its execution frequency. [NI-VISA termination documentation](https://www.ni.com/en/support/documentation/supplemental/06/termination-characters-in-ni-visa.html)

### 2. Alternative explanation of the same evidence

The observed frame instability is more plausibly caused by the **unmeasured unconditional remainder**:

- two UI-thread property reads in the ASI wrapper;
- save/WLC/state-machine work on the frame loop;
- visible-panel drawing and UI contention;
- tail latency rather than median latency.

NI documents that property-node execution can involve the UI thread, while drawing and input handling also use that thread. That makes display activity a credible source of jitter without requiring per-frame serial traffic. [NI UI-thread documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000004AfbSAE&l=en-US)

Under this explanation, ASI causes intermittent missed frames only during focus operation. It is still architecturally sensible to give VISA a single owning loop, but it is not the steady-state 2.5 ms prize claimed here.

### 3. What would falsify the plan

A focus-idle live trace would falsify the proposed cost/order rationale if it showed:

- no VISA transactions during ordinary frames;
- negligible ASI-wrapper time compared with 2.1 ms;
- kernel-only separation failing to reduce buffer gaps or frame-loop p99 latency;
- queue depth growing or acquisition misses remaining unchanged after the kernel split.

Conversely, I would withdraw the serial-cost objection if focus-idle tracing showed an ASI transaction on essentially every frame and bypassing only that transaction reduced frame-loop p50/p99 by roughly 2 ms.

### 4. The entanglements are not harmless

`save trace.vi` #376 being in the forward slice proves that the 22-node slice is **not a kernel component**. It is a reachability slice containing downstream consumers. Moving that slice would wrongly drag file ownership and accumulated `total data array` state into tracking. The proper seam is an immutable, frame-identified tracking-result message before `save trace.vi`, not the whole forward slice.

Case #10407 is more serious than an extra wire. `Out position` is shared state, while `VISA out`/?쏰utgoing Handle??carries resource ownership and execution ordering. Splitting this across loops without a command/reply contract can create two VISA owners or stale position/handle pairings. The ASI loop should exclusively own the VISA session; other loops should exchange timestamped or sequenced commands/results. NI?셲 producer/consumer documentation supports queues for ordered cross-loop transfer but also notes that loop startup is not inherently synchronized. [NI Producer/Consumer Architecture](https://www.ni.com/en/support/documentation/supplemental/21/producer-consumer-architecture-in-labview0.html)

### Answers to the requested attacks

- **In-place versus fresh rebuild:** preserving the copied front panel, initialization, bead picking, and calibration is valuable, but ?쐇n-place is easier??is not demonstrated. Twenty-one resolved sibling nets plus 49 unresolved endpoints are 70 contracts to classify, not a cheap seam. The safer third option is a copied original as the application shell, while rebuilding one complete runtime island inside it from explicit contracts. Do not mechanically lift the 22-node slice.

- **Ordering:** do not move ASI first on performance grounds. First measure the unconditional path. Then build a minimal live vertical slice: acquisition ??owned image handoff ??queue core ??frame-identified result, including stop, error, reseed, and overload behavior. The queue core currently proves replay numerics only through the first 10,018 pre-loss frames; it does not prove live acquisition, shutdown, image ownership, or reseeding. See [STATUS.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/STATUS.md:56>).

- **Does kernel separation buy anything?** Possibly: queues can decouple acquisition from processing jitter while preserving FIFO order. They do not reduce total CPU cost, and sustained consumer deficit merely becomes backlog, blocking, or drops. NI explicitly describes that decoupling behavior; NI also warns that a full bounded queue with the default infinite enqueue timeout slows and blocks the producer. [NI Producer/Consumer Architecture](https://www.ni.com/en/support/documentation/supplemental/21/producer-consumer-architecture-in-labview0.html), [NI queue-full behavior](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU0000002WyH0AU)

- **Unmeasured assumptions:** per-state execution frequency; p99/p999 latency; unconditional cost of each property node; real `WHERE` latency and timeout behavior; queue occupancy and overload recovery; image-reference ownership; live reseeding after bead loss; stop/abort cleanup; save throughput and flush stalls; frame/result identity; ASI command/result freshness; subVI reentrancy; core oversubscription; and end-to-end exposure-to-file latency. NI notes that non-reentrant VIs serialize simultaneous calls, so reentrancy must be inventoried rather than assumed. [NI VI execution properties](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html)

**As written, the claim does not hold.** Retain the copied-original shell, but replace ?쐊ernel, then ASI, then display??with ?쐌easure unconditional latency, then construct one live vertical slice, then split whichever measured owner dominates.??What would change my mind is direct focus-idle evidence showing per-frame ASI traffic and an approximately 2 ms reduction when it alone is bypassed.

The cheapest discriminating test is one unchanged-copy A/B run with timestamps around `ASI_adjust focus-subvi.vi`: record frame-loop duration, buffer number/gaps, and wrapper duration for several thousand frames with focus controls untouched, then briefly active. Near-zero idle cost plus ~2 ms active cost confirms the alternative; ~2 ms on every idle frame confirms the plan?셲 ASI premise.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
