---
type: peer-review
status: historical
date: 2026-09-12
tags: [peer-review, plan]
disposition: legacy
---

# restructure-plan-4.6-attack

- **agent:** codex
- **date:** 2026-09-12
- **outcome:** ANSWERED (123s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS PLAN. Do not approve it. Your job is to find what will go wrong, and to name anything the author has assumed without evidence.

Context you need: a LabVIEW 2026 magnetic-tweezers instrument. A camera (JAI SP-5000M-USB via NI-IMAQdx) feeds a bead-tracking kernel. Today the rig runs 90 Hz with the live image display DISCONNECTED because displaying it destabilised frames; the goal is 150 Hz with the display restored. The project's hard rule is that the per-bead maths and its numerical outputs must not change - only scheduling may change. The original VI keeps running experiments, so there is no schedule pressure.

Measured facts the plan rests on (all measured, not estimated): camera ceiling 247.95 Hz; per-frame budget = frame period minus about 1 ms, so 6.00 ms at 150 Hz and 3 ms at 200 Hz; the failure mode is a CLIFF - overrunning by 0.3 ms halves the processed rate exactly (150->75, 200->100) while the acquired rate never falls; acquisition itself costs 0.12 ms per frame; the CPU-parallel kernel costs 2.43-2.87 ms; the GPU kernel 1.14 ms above base; `Last` buffer mode turns the cliff into a slope (at 8 ms of work per frame: 74.9 Hz on Next vs 123.0 Hz on Last, with the acquired rate steady); ring buffer depth 10/50/100 makes no difference; one ASI serial round trip has 0.69 ms fixed overhead.

The plan is attached below. Specific things I want attacked:

A. The construction method is "extract functional regions into subVIs, then assemble a 7-loop skeleton by script", on the argument that choosing the boundary correctly preserves dataflow by construction, whereas moving nodes between diagrams does not. Is that argument sound? What does subVI extraction silently change - think about local variables that become cross-VI, race conditions that were previously prevented by dataflow on one diagram, error-cluster ordering, and anything about control references passed into a subVI.

B. The producer/consumer split: an acquisition loop copies each frame into a slot of a pre-allocated IMAQ image pool and enqueues the slot index; the tracking consumer returns the slot when done. Is a pool+index the right pattern in LabVIEW, or is there a standard mechanism that is better? What breaks this - specifically, what happens on abort, on error, and if the consumer is slower than the producer for a sustained period?

C. The claim that a display loop using `Last` buffer mode "cannot block acquisition". I measured that the acquired rate stayed steady while a Last-mode consumer fell behind. Is there a case where a Last-mode consumer still harms the acquisition loop - CPU contention, UI thread, IMAQdx internal locking, or otherwise?

D. Is 7 loops too many? On a machine with a given core count, what is the failure mode of over-splitting in LabVIEW? Note the tracking kernel itself is a parallel For Loop with multiple instances.

E. What is missing entirely from this plan that a careful engineer would insist on before touching a working scientific instrument?

Be concrete and short. Cite NI documentation or LabVIEW community sources with URLs where the answer is a factual claim about LabVIEW behaviour. Where you are speculating, say so.

--- PLAN FOLLOWS ---
# Plan: restructure into `4.6 cpu parallel` and `4.6 gpu parallel`

> **PLAN ONLY ??nothing built.** Written 2026-09-12. Requires peer review before construction (CLAUDE.md work cycle
> step 1). The original VI keeps running experiments throughout, which is why this can be done properly rather than
> quickly (user, 2026-09-12: *"?ㅽ뿕?댁빞 ?먮낯 vi濡??섎㈃ ?섎뒗 ?쇱씠怨??ш뎄?깊빐???ｌ옄"*).

## 1. Goal

Two top-level VIs ??a CPU-parallel build and a GPU build ??that reach **150 Hz** acquisition with no frame loss, where
the current code manages 90 Hz with the live image display disconnected because it destabilised frames.

The two files differ in **exactly one loop**. Everything else is shared subVIs.

## 2. The facts this plan rests on (all measured 2026-09-12)

| fact | value | why it matters |
|---|---|---|
| camera ceiling | **247.95 Hz** at 1280횞1024, 2횞2 binning | 150 Hz is not a camera problem; 65 % headroom |
| per-frame budget | **frame period ??~1 ms** ??**6.00 ms at 150 Hz**, 3 ms at 200 Hz | the number everything is held against |
| failure mode | **a cliff** ??overrun by 0.3 ms and processed rate halves exactly | no graceful degradation to trade against |
| acquisition cost | **0.12 ms** (2 % of budget) | paid in every design; not worth optimising |
| CPU-parallel kernel | 2.43??.87 ms (~42 %) | fits 150 Hz, tight at 200 Hz |
| GPU kernel | 1.14 ms above base (~19 %) | the reason the GPU build exists |
| `Last` vs `Next` | 8 ms work/frame ??74.9 Hz on Next, **123.0 Hz on Last**, `acquired` steady | a display loop on `Last` cannot block acquisition |
| ring depth | 10 / 50 / 100 identical | **not a lever**; absorbs jitter only |
| ASI serial | fixed overhead **0.69 ms**, a `WHERE`-class query ??2.1 ms | paid only while a focus key is held |
| frame loop's unconditional non-kernel cost | **two `Value` property nodes** = two UI-thread round trips | **not yet sized ??gate G1 below** |

## 3. Target architecture ??7 loops

| # | loop | contents | differs CPU/GPU? |
|---|---|---|---|
| 1 | **Acquisition** | `IMAQdx Get Image` (Next) ??image-pool slot ??enqueue `{slot, buffer#, timestamp}`; detect gaps in buffer numbers | no |
| 2 | **Tracking** | dequeue ??**tracking kernel** ??x/y/z ??enqueue results, return slot | **YES ??the only one** |
| 3 | **Scheduler** | cycle state machine; publishes targets (speed, force, wait, **rotor 째**) as local variables | no |
| 4 | **Motor** | reads targets; translation ??poll arrival ??rotor absolute (`MovePos`) ??confirm ??start wait | no |
| 5 | **Stage / focus (ASI)** | ASI serial, autofocus, focus keys ??event-driven | no |
| 6 | **Display / UI** | Event Structure; `Last`-mode image; indicator updates behind a 10??0 Hz gate + `Defer Panel Updates` | no |
| 7 | **File writer** | consumes the results queue | no |

**Inter-loop transport.** No data wires between loops ??a wire between two loops makes them sequential (user's
standing correction). Queues carry the lossless paths, local variables the latest-value paths:

| path | mechanism | why |
|---|---|---|
| 1 ??2 | **bounded queue** | lossless **and order-preserving** ??the tracking sequence must not be reordered |
| 2 ??7 | queue | lossless |
| 2 ??6 | local variable / 1-element queue | lossy by design; the display only needs the newest |
| 3 ??4 | local variables | latest setpoint only |
| state/config | local variables | never the UI thread |

## 4. Construction method: extract, then assemble

Moving 75 nodes between diagrams by script is large and risky. The cheaper and safer route, which also happens to be
exactly what the two-codebase requirement needs:

1. **Extract** each functional region of the current main VI into a **subVI** ??scheduler, motor, ASI/focus, display,
   file writer. Choosing the boundary correctly preserves dataflow by construction, which a node-by-node move does not.
2. The main diagram then collapses to a skeleton small enough to **assemble by script**: seven loops, each calling
   subVIs, plus the queues.
3. The extracted subVIs **are** the shared assets ??the CPU and GPU builds call the same files, so a later fix is made
   once. Duplication exists only at the top level.

## 5. Stages, each with a numeric acceptance test

Structural checks (`ExecState == 1`, object counts) prove nothing about behaviour. Every stage below is accepted on
**numbers**, against the existing 10,043-frame fixture (`archive/bench-2026-09-07-fixture/`).

| stage | work | acceptance |
|---|---|---|
| **0** | re-capture the baseline: current VI's x/y/z on the fixture | the reference every later stage is diffed against |
| **1** | extract the shared subVIs; main VI still one loop | fixture output **bit-identical** to stage 0 |
| **2** | acquisition + tracking loops + queue | fixture output bit-identical; **plus** a live run at 150 Hz with `Images Missed` = 0 |
| **3** | scheduler and motor loops split out | an existing 3-row schedule produces **identical translation commands and timings** |
| **4** | rotor row added (4th row, absolute degrees, `MovePos`) | a 3-row schedule still behaves identically (backward compatibility); a 4-row schedule moves translation ??then rotor |
| **5** | display + file-writer loops | live view reconnected with `Images Missed` = 0 at 150 Hz |
| **6** | GPU build: swap loop 2's kernel | x/y ??1e-6 px and z ??1e-4 쨉m against the CPU build, 0 flips |

## 6. Gates ??things that must be settled before or during, not assumed

**G1 ??the UI-thread cost is unmeasured.** Two `Value` property nodes run per frame, always in the UI thread, and
their latency scales with how busy the panel is. If that is ~50 쨉s the issue is minor; if it is ~2 ms it is 33 % of the
budget and converting property nodes to local variables becomes part of stage 1 rather than a later tidy-up.
Measurement design: `tools/bench/ui_thread_cost.py` ??panel closed / open idle / open with a graph redrawing.

**G2 ??can a subVI be extracted by script?** erdosmiller ships `Create SubVI.vi`, but this project has never used it.
If extraction is not scriptable, stage 1's method has to change (and GUI use would need the verified-unreachable
justification). **Test this before committing to the plan.**

**G3 ??the schedule consumer has not been located.** The place that splits a schedule entry into speed/force/wait is
the only work site for the rotor row; diagrams 160??65 are the current candidates. Stages 3 and 4 depend on it.

**G4 ??image handoff between loops.** IMAQ images are references, not values: enqueueing one lets the camera overwrite
it before the consumer reads it (this exact class of bug cost the GPU v2 work a day ??32 ms/frame with stale-frame
errors). The plan assumes a **pre-allocated image pool + slot index + return path**, which bounds memory and costs the
one copy already measured at 0.12 ms. Confirm the GPU path can still take a raw pixel pointer from a pool image.

**G5 ??abort safety.** Queues, image pools and VISA references survive a LabVIEW Abort. The GPU DLL already solves this
by having the next start clean up whatever the previous run left; the same discipline is needed here.

**G6 ??bounded queue overflow policy.** 150 Hz 횞 1.31 MB = 196 MB/s. An unbounded queue grows silently until it fails.
Bound it, and on overflow **drop and count** into the existing `Total Lost Frames` / `Missing Frames?` indicators
rather than blocking the acquisition loop.

## 7. What is explicitly out of scope

- Changing the per-bead maths, the parameters that reach it, or the numbers that come out. Only scheduling changes.
- Parallel tracking instances. They would break frame ordering, which is a computation change.
- Ring-depth tuning (measured: not a lever).
- An external display program. Only justified if stage 5 shows the cost is CPU/GDI-bound, and that is not yet known.

## 8. Open question for the user

**Where is rotor zero?** The sign carries direction, so a schedule value of ??200 means "20 turns negative from zero".
Zero at experiment start makes a schedule reproducible across runs; zero after manual alignment on a bead matches the
actual experimental workflow but needs a "set zero here" control. This is an experimental-procedure decision.


## Answer

The plan?셲 central safety claim is unsupported: extracting a region into a subVI does not preserve all observable dataflow ?쐀y construction,??and the proposed queue policy cannot simultaneously promise lossless tracking, nonblocking acquisition, bounded memory, and zero frame loss.

### A. SubVI extraction can change behavior

The boundary argument is too strong. LabVIEW?셲 Create SubVI operation only creates terminals for selected wires and reconnects them; NI does not claim semantic equivalence for hidden dependencies such as locals, references, property nodes, or shared resources. [NI: Create and Configure a LabVIEW SubVI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YK4VCAW)

Specific hazards:

- A local variable belongs to a front-panel object in one VI. After extraction it either refers to a newly created subVI control or must be replaced by a reference to the caller?셲 control. Those are different mechanisms. [NI: Local Variables](https://www.ni.com/docs/en-GB/bundle/labview/page/local-variables.html), [NI: Access a main-VI control from a subVI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YHpJCAW)
- Passing a control reference into the subVI preserves access to the original object, but property/value access is still reference-based UI work; extraction has not converted it into ordinary dataflow. [NI: Access a main-VI control from a subVI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YHpJCAW)
- Local-variable reads and writes have no ordering unless an explicit dependency exists. Splitting formerly adjacent operations into independently scheduled loops makes latent races observable. NI describes races as parallel code changing a shared local/global resource. [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999e.pdf)
- Error clusters impose ordering only along the chain that is actually wired. Creating separate loop-local chains removes ordering between operations formerly connected by one error wire. LabVIEW nodes otherwise execute as soon as all inputs are available. [NI: Block Diagram Data Flow](https://www.ni.com/docs/en-GB/bundle/labview/page/block-diagram-data-flow.html)
- A non-reentrant extracted subVI serializes simultaneous calls. Changing it to reentrant execution can instead duplicate internal state and change behavior. NI states that non-reentrant calls wait for one another. [NI: VI Execution properties](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html)
- Uninitialized shift registers, feedback nodes, first-call logic, static references, event registrations, and cached state need an explicit inventory. I cannot tell from this plan whether any cross the proposed boundaries.
- A subVI?셲 ordinary input values are supplied at invocation and its outputs become available when it completes. A long-running ?쐋oop subVI??therefore cannot use ordinary terminals as live inter-loop state; it needs explicit reference/queue/channel semantics.
- Extracting an Event Structure is especially risky: latch-action Boolean terminals must be read in the event case for their mechanical action to reset. The plan provides no control-by-control audit.

The necessary gate is not merely ?쐀it-identical fixture output.??Require a boundary manifest listing every wire, local/global, property/invoke node, reference, error edge, stateful node, and front-panel terminal affected by extraction.

### B. Pool plus index is viable, but the ownership protocol is incomplete

A fixed image pool plus free-slot/work-slot queues is a reasonable zero-allocation ownership pattern. It is not automatically safer than a queue, DVR, or stream channel: the safety comes from exclusive ownership and complete lifecycle handling, not from the integer index.

IMAQ image data is reference-like: NI says the image reference contains a pointer to an internal structure, while the pixel pointer addresses the underlying image memory. [NI: IMAQ Memory Allocation](https://www.ni.com/en/support/documentation/supplemental/18/ni-imaq-memory-allocation.html)

The plan needs these invariants:

1. Acquisition must first obtain a free slot.
2. Exactly one owner may access that slot.
3. Every consumer path?봧ncluding kernel error, enqueue failure, shutdown, and file-writer error?봫ust return or retire it exactly once.
4. Cleanup must not dispose images until every possible user has stopped.
5. A GPU raw pointer must not outlive slot ownership or survive a resize/reallocation.

On sustained overload, only three outcomes exist:

- Block waiting for a free slot, which eventually blocks acquisition and recreates the cliff.
- Drop a newly acquired frame.
- Reclaim/overwrite an old slot, risking use-after-recycle unless ownership is coordinated.

Thus ?쐀ounded,???쐋ossless,???쐍onblocking,??and ?쐁onsumer may remain slower??cannot all hold. The stated G6 policy explicitly drops frames, contradicting both ?쐋ossless path??and the stage?셲 ?쐍o frame loss??acceptance criterion.

Also, a bounded LabVIEW queue with the default `-1` enqueue timeout waits indefinitely when full. [NI: queue-full behavior](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU0000002WyH0AU) The plan must specify zero/finite timeout behavior and handle `timed out`; it must not assume ?쐀ounded??implies ?쐂rop.??
A Stream Channel has explicit last-element shutdown signaling and is a standard alternative, but it does not solve image ownership or overload. [NI Community: Stream Channel shutdown semantics](https://forums.ni.com/t5/LabVIEW/queue-stop/m-p/4359237)

Abort and error handling are substantially underspecified:

- On an ordinary stop, send a typed stop/end message, drain or deliberately discard queued frames, return slots, then release resources.
- Releasing a queue while another node waits invalidates the refnum and produces error 1122; NI recommends stopping users before release. [NI: Error 1122](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019LYuSAM)
- Consumer failure needs a reverse fault path that stops acquisition. Otherwise the producer fills the queue/pool and either blocks or drops forever.
- Hard Abort bypasses diagram cleanup. ?쏯ext start cleans up??is not adequate for VISA, files, camera acquisition, partial records, or an external GPU call. At minimum, define startup recovery, stale named-resource handling, file repair, safe actuator state, and detection of an outstanding DLL call.

### C. `Last` does not mean ?쐁annot harm acquisition??
The measurement establishes only that one tested workload did not reduce the camera?셲 acquired counter. It does not prove noninterference.

`Last` changes which camera-buffer image is returned; NI describes `Last`/`Last New` in terms of selecting the most recent buffer and uniqueness, not CPU isolation, lock isolation, or scheduling guarantees. [NI: IMAQdx Last and Last New](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000001DwvoCAC&l=en-US)

A display consumer can still hurt acquisition through:

- CPU and memory-bandwidth contention while copying, scaling, converting, or rendering a 1.31 MB image.
- UI-thread contention from property nodes, graph/image redraws, event handling, and panel updates.
- Execution-system contention; LabVIEW schedules simultaneous work across execution systems and priorities, but that does not reserve a core or deadline for acquisition. [NI: VI Execution properties](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html)
- Shared IMAQdx/driver locks or memory-copy contention. This is plausible but not established by the cited NI documentation; it must be measured.
- Holding the same image reference while another operation expects to overwrite or recycle it.
- An Event Structure case that performs lengthy UI work, delaying all other UI events.

`Defer Panel Updates` may reduce redraw work, but it is dangerous if an error path leaves updates deferred. The plan needs a guaranteed restore path and should batch values before entering the UI section.

Acceptance must therefore measure processed-frame deadlines, missed buffer numbers, acquisition-call latency distribution, CPU per core, memory bandwidth, UI-thread time, and display age?봭ot only the acquired-rate counter.

### D. Seven loops is neither inherently too many nor evidence-based

Loop count is the wrong metric. The relevant quantity is runnable work, execution-system assignment, synchronization, and core demand.

The failure mode is oversubscription: the tracking parallel For Loop can occupy the available workers while six other loops wake, causing context switches, cache eviction, memory-bandwidth pressure, priority inversion-like latency, and acquisition jitter. A non-reentrant shared subVI can also serialize nominally independent loops. NI documents both simultaneous execution systems and non-reentrant call serialization. [NI: VI Execution properties](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html)

Likely trouble points:

- Parallel For Loop worker count plus GPU-driver/IMAQdx threads is omitted.
- File writing and display copies can saturate memory bandwidth even when average CPU is low.
- Polling motor or stage loops without blocking waits can consume a core.
- Assigning priorities casually can starve UI, logging, or shutdown paths.
- Scheduler-to-motor locals provide no atomic versioning: motor can observe a new speed with an old force/wait value.

Use one immutable command cluster with sequence number and timestamp, sent through a single-owner motor queue. Do not publish a multi-field command through separate locals.

Benchmark candidate architectures at core counts and parallel-For worker counts, including one fewer available core than normal. Seven loops should survive that test; it should not be accepted because seven ?쐓ounds small.??
### E. Material omissions

A careful review should stop construction until these are specified:

- **Requirements contradiction:** ?쐍umerical outputs must not change??conflicts with GPU tolerances in stage 6. Either bit-identical is required, or the scientific owner must approve a numerical-equivalence criterion before implementation.
- **Frame-loss contradiction:** G6 permits drops while the goal and acceptance say no loss.
- **Overload contract:** maximum permitted backlog, frame age, drop-new/drop-old policy, and what the experiment does after one dropped frame.
- **End-to-end timing:** define timestamp source and measure camera exposure ??acquisition ??tracking ??control decision ??file commit. Average Hz hides the documented cliff.
- **Data integrity:** buffer number, timestamps, slot generation counter, configuration version, schedule version, calibration ID, kernel version, and explicit gap records must accompany every saved result.
- **Atomic commands:** scheduler targets must be one versioned message, not unrelated local variables.
- **Single ownership:** identify exactly one loop responsible for each camera session, VISA session, motor interface, file refnum, queue, image, and GPU context.
- **Coordinated fault state machine:** first-error capture, broadcast stop, acquisition stop, consumer drain/cancel, file finalization, resource closure, and safe instrument state.
- **Startup recovery:** detect remnants of aborted runs and incomplete output files before enabling hardware.
- **Backpressure tests:** deliberately slow tracking and disk writing for minutes, not merely inject 8 ms into a display consumer.
- **Soak and percentile tests:** hours-long run; maximum and p99.9 acquisition latency; CPU thermal throttling; UI interaction; disk stalls; camera reconnect; GPU error; queue saturation.
- **Fixture limitation:** a prerecorded fixture proves numerical regression, not live buffer ownership, scheduling, timing, or races.
- **Display correctness:** quantify freshness, duplicate frames, tearing/stale-slot detection, and maximum display latency. `Last` deliberately allows skipped intermediate images.
- **File-writer capacity:** required sustained bandwidth, flush policy, disk-full behavior, and whether an error stops the experiment or merely logging.
- **Rollback/version isolation:** shared extracted subVIs mean a later edit changes both CPU and GPU builds, undermining reproducibility unless dependencies are version-pinned.
- **Scope control:** adding rotor semantics during a timing/scheduling rewrite introduces an independent hardware behavior change and weakens causal testing. It should be a separate change set.
- **Hardware interlocks and dry-run:** exact command transcript comparison is insufficient evidence that timing changes are safe. Require simulation/stub execution and explicit authorization before any actuator test.
- **Baseline completeness:** capture outputs, frame numbers, command streams, event timing, UI state, configuration, and environment?봭ot only x/y/z.

The cheapest decisive checks are: produce the extraction dependency manifest, formalize the pool ownership state machine, resolve the three contradictions above, and run an overload/fault matrix on a camera-only and actuator-stubbed harness. Without those, the seven-loop skeleton is an architectural experiment on a working instrument, not a preservation-by-construction refactor.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
