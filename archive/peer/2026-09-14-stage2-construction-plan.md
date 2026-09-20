---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, stage2, plan]
---

# stage2-construction-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (123s)
- **why asked:** plan review of docs/stage2-plan.md before building the stage-2 VI (acquisition + tracking loops + queue)
- **verdict:** unverified

## Question

PLAN REVIEW (attack; the plan is docs/stage2-plan.md in the project dir - read it). Context: LabVIEW 2026 magnetic-tweezers tracking VI restructuring; stage 2 = a NEW top-level VI with an acquisition loop and a tracking loop joined by a bounded queue, built entirely by VI Scripting from Python (our toolkit: For loops with auto-indexed tunnels and parallel instances, case structures, subVI drops, wiring by name, control/indicator creation from terminals, connector panes; MISSING: While loops, queue primitives, bundle/unbundle, an empty VI). Acceptance: bit-identical x/y/z on a 10,043-frame fixture vs the original kernel path, and live 150 Hz with Images Missed = 0. ATTACK the plan on: (a) the queue element design {slot, buffer#, t} with an image POOL of 8 IMAQ images and IMAQ Copy per frame (0.05 ms measured) - any reason to hand IMAQdx buffers directly instead, and how the original's 'get buff image-lost frames.vi' (Buffer to extract = LastBufferNumber+1) should map onto IMAQdx Get Image Buffer Number / Next semantics without changing what image each frame index sees; (b) bit-identity risk: the kernel feedback (x,y,z array, Bead is good?, pos in cal image) are shift registers in the original - in the new tracking loop they must be shift registers too, initialised from the same sources; anything else in the original frame path that feeds the kernel and that a queue-based split could reorder or drop (e.g. the 'Bead is good?' case structures #5540/#2222 between kernel and feedback); (c) fixture mode via IMAQ ReadFile in loop 1: is reading TIFFs at 150 Hz realistic or should the fixture be preloaded into the pool/array; (d) the toolkit gap order (While loop op first, then queues, then bundle) and whether erdosmiller's Create Obtain Queue.vi needs a sample element wire for the type; (e) what the minimal live acceptance instrumentation must include (buffer-number gaps, p99.9 latency, back-pressure) given LabVIEW's queue timeout semantics (enqueue timeout -1 waits forever). One page max, concrete.

## Answer

## Plan review ??changes required before build

1. **Keep the eight-image copy pool; do not hand driver buffers to tracking.** IMAQ images and camera buffers are references to mutable memory, and the acquisition ring can overwrite a buffer while another loop still processes it. Copying into owned images gives the tracker a stable snapshot; the measured 0.05 ms cost is only 0.75% of a 6.67 ms frame budget. NI?셲 description of circular acquisition confirms that logical buffer numbers continually increase while physical storage is reused. [NI buffer discussion](https://forums.ni.com/t5/LabVIEW/Continuous-Acquisition-IMAQdx-calling-a-past-buffer/m-p/3778330)

   **Fatal flaw:** `slot = k mod 8` does not establish ownership. Acquisition can overwrite `pool0` while tracking still uses it. Add a bounded `Q_free` seeded with slots 0??:

   `dequeue free slot ??copy ??enqueue Q_img ??tracking ??return slot`

   If `Q_img` enqueue times out, acquisition must return that slot immediately. Assert `free + queued + processing = 8`. This makes `Q_free`, not arithmetic, the pool authority.

2. **Preserve the original buffer-selection contract explicitly.** The original requests logical `LastBufferNumber + 1`. The closest mapping is IMAQdx **Buffer Number mode** with that exact number, then advance state from the actual returned buffer number. ?쏯ext??ignores `Buffer Number In`, so substituting it is not proven equivalent. [NI employee explanation](https://forums.ni.com/t5/Machine-Vision/quot-buffer-number-in-quot-confusion-with-IMAQdx-get-image/m-p/826711)

   Before choosing either mode, characterize the original subVI?셲 overwrite behavior. IMAQdx can return the oldest available, newest available, or an error when the requested frame has already been overwritten, depending on overwrite configuration. [NI buffer/overwrite explanation](https://forums.ni.com/t5/Machine-Vision/quot-buffer-number-in-quot-confusion-with-IMAQdx-get-image/m-p/826711) Record `{requested, returned}` and define a gap as `returned ??previous_returned ??1`, with rollover handling?봊?뗢딲AQdx buffer numbering has a finite rollover distinct from older NI-IMAQ numbering. [NI migration note](https://www.ni.com/en/support/documentation/supplemental/18/converting-a-camera-link-application-from-the-ni-imaq-api-to-the.html)

3. **The kernel state has not yet been copied faithfully.** The three feedback values need tracking-loop shift registers, but direct `SR ??kernel ??SR` is insufficient. The measured graph shows case #5540 transforms/selects `x,y,z` and `Bead is good?` before the kernel; it must be reproduced case-for-case. Case #2222 consumes the kernel?셲 x/y/z with `Correction Factor`, so the plan must establish whether accepted/saved x/y/z is the raw kernel output or #2222?셲 downstream value. See [frame-loop-wire-graph.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/frame-loop-wire-graph.md:14>).

   Block construction until reporter output identifies every selector and every case?셲 internal wires for #5540 and #2222. Also freeze all per-frame kernel inputs at the same sampling point as the original. Reading mutable UI/calibration values in another loop can move a change across a frame boundary. Queue `{sequence, actual buffer#, acquisition timestamp, slot}`; never derive frame identity later from tracking-loop iteration count. A dropped live frame necessarily skips one feedback transition, so bit identity is meaningful only with zero acquisition and queue drops.

4. **Fixture replay should test correctness, not TIFF throughput.** Do not require TIFF reads to sustain 150 Hz without measurement; TIFF decoding and filesystem latency are unrelated to camera-path acceptance. NI documents TIFF as an encoded file format but gives no 150 Hz performance guarantee. [NI image-file documentation](https://www.ni.com/en/support/documentation/supplemental/06/reading-and-writing-image-files.html)

   Run the 10,043-frame correctness fixture losslessly and unpaced: read only after obtaining a free pool slot, then block until accepted. Do not preload into only eight images?봳hat merely recreates overwrite. If paced replay is later required, benchmark warm-cache `IMAQ ReadFile`; otherwise preload all decoded frames only after calculating and accepting the memory requirement, or use a measured sequential raw/container format.

5. **Change the toolkit order:** `empty VI ??While loop ??integer queues ??cluster/Bundle`. The empty runnable target is prerequisite infrastructure, not gap 4. The While test should stop deterministically at exactly three iterations?봡o not depend on a manually changing Stop control. Queue tests must cover bounded-full timeout, FIFO order, release/shutdown, and the free-slot invariant.

   Yes: Obtain Queue requires a wired sample/constant to establish the element type before its typed queue refnum can be created. [NI instructions](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000001DduISAS&l=en-US) Treat the exact erdosmiller creator-VI connector pane as unverified until its reporter output is available; the public repository description alone does not document that VI?셲 terminals. [erdosmiller LV-Scripting repository](https://github.com/erdosmiller/lv-scripting)

6. **Minimum live instrumentation:**

   - requested and returned buffer number; gap count/size and overwrite/error count;
   - acquisition-call duration: count, p99.9, maximum, plus run duration;
   - acquisition-to-dequeue and acquisition-to-kernel-finish latency: p99.9/max;
   - `Q_img` occupancy high-water mark, enqueue timeouts, dropped frames, and longest full interval;
   - acquired/copied/enqueued/dequeued/processed/returned-slot counts;
   - slot double-use/invariant violations;
   - sink backlog or `Q_res` high-water mark?봧t must not remain silently unbounded.

Use enqueue timeout `0` for the deliberate live drop policy and check `timed out?` every call. Timeout `??` waits indefinitely when a bounded queue is full and would convert tracker back-pressure into acquisition loss. [NI queue semantics](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU0000002WyH0AU) The acceptance run needs zero buffer gaps, zero enqueue drops, zero slot violations, and `processed = acquired`; the slowed-tracker test should show queue saturation and counted drops while acquisition cadence remains at 150 Hz.

## Sources

(extract from answer)

## What was done with it

All six changes adopted into docs/stage2-plan.md (items 1-6) plus two of our own (7: stop evaluated inside the loop; 8: two lock-stepped queues instead of composite elements). The toolkit was built in the reviewer's order - empty VI, While loop, stop by control, queues (INDEX rows 32-35, all functional) - with the queue tests covering FIFO/typing/tunnel crossing; bounded-full timeout and release-order tests are scheduled with the assembly. Verdict: correct and adopted.
