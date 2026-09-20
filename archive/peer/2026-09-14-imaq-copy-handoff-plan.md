---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, plan]
---

# imaq-copy-handoff-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (54s)
- **why asked:** plan review before measuring the image-handoff copy cost (restructure gate G4).
- **verdict:** ACTED ON. (1) the per-Run harness (HARNESS_copy0/1) is kept but LABELLED "cold first-copy cost (includes B's first 1.3 MB allocation)"; a steady-state cell is added as HARNESS_copyloop (one Run: A read once, B sized by one untimed copy, then a For loop auto-indexed on an N-row array control repeating IMAQ Copy A→B; baseline = the same loop without the copy; cost = ΔT/N). (2) G4 re-stated in the plan as a ring-LIFETIME decision: a reference handed to a decimated display/save consumer must be copied at selection time (NI: release the ring reference so acquisition continues); display may instead call Get Image with most-recent semantics in its own loop. (3) the ImageToArray 0.6 ms comparison is quoted only as the same per-Run method's number, not as a steady-state figure. VI identity: vision\Basics.llb\IMAQ Copy (Vision pixel copy, Image Src → Image Dst), confirmed by its terminals at build time.

## Question

PLAN REVIEW (attack; brief; cite NI Vision docs). GOAL (restructure gate G4 'image handoff between loops' + work-order measurement 'array-crossing cost'): IMAQ images are references; handing the acquisition loop's image to the tracking/display/save loops either (a) passes the reference (zero copy, but the camera's ring buffer may overwrite it), (b) copies the image into a per-consumer buffer with IMAQ Copy (safe, costs a memcpy), or (c) converts to a LabVIEW array (IMAQ ImageToArray - measured today 0.6 ms for 1280x1024 U8, archive/bench-2026-09-14-display-path/REPORT.md) and passes the array (a LabVIEW copy per wire branch). PLAN: HARNESS_copy_v0 = IMAQ Create(A) -> IMAQ ReadFile(fixture, File Path control) -> IMAQ Create(B) -> IMAQ Copy(A -> B); timed like the display bench (one COM Run per frame from Python, 200 frames, base = the same VI without IMAQ Copy = disp0 already exists, panels closed, files pre-read); reported as the per-frame cost of one reference-safe copy, to be compared with ImageToArray 0.6 ms. Also a second cell with IMAQ Copy into an image created ONCE outside the timed run is not possible in this per-Run design (each Run re-creates) - so 'Create B' cost is included in both base and copy cells? no: base has ONE Create; the copy cell has TWO Creates + Copy -> cost(Copy) is overestimated by one IMAQ Create; I would add a cell 'two Creates, no Copy' to subtract it. ATTACK: (1) is IMAQ Copy the right primitive for a per-consumer buffer (vs IMAQ Copy Image? 'IMAQ Copy' in Basics.llb duplicates pixel data into an existing image - correct?), and is a fresh IMAQ Create per Run realistic (allocation of a 1.3 MB buffer each Run - would LabVIEW/NI-IMAQ's image pool make it cheap or expensive, and does that pollute the measurement?); (2) is the G4 question really about copy cost, or about the RING SEMANTICS (a reference handed to a slow consumer gets overwritten by the camera: IMAQdx Get Image with a buffer number vs 'Next'/'Last' modes) - what NI documents about buffer ownership for IMAQdx Get Image, and whether a copy is REQUIRED for a decimated display/save consumer; (3) the cheapest set of cells that decides G4 design (reference pass + copy-on-demand vs copy-always), stated as a prediction contract.

## Answer

Verdict: the current harness does not isolate steady-state copy cost, and G4 is primarily a lifetime/ring-semantics decision?봭ot a raw memcpy comparison.

1. Primitive and benchmark attack

- Confirm the exact VI identity. NI marks the NI-IMAQ acquisition VI named **IMAQ Copy** as deprecated. For a Vision image-to-image pixel copy, use the current Vision Development Module equivalent?봳ypically **IMAQ ImageToImage 2**?봮r verify from Context Help that the selected VI copies pixels from a source image into a distinct destination image. Do not infer semantics from ?쐂uplicate image??outputs; those commonly remain references to the same image. [NI: Deprecated NI-IMAQ VIs](https://www.ni.com/docs/en-US/bundle/ni-imaq-vi-ref/page/niimaqvireference/deprecated_vis.html), [NI Vision reference: whole-image duplication versus region copying](https://docs-be.ni.com/bundle/322567a/raw/resource/enus/322567a.pdf)

- `two Creates, no Copy` is not a valid subtraction for destination allocation. NI says `IMAQ Create` initially creates an image reference to a zero-length, uninitialized buffer; pixel storage is resized later by operations such as `IMAQ ReadFile`. Therefore, the second bare Create may be cheap while the first copy into B pays B?셲 first 1.3 MB allocation. [NI: IMAQ Memory Allocation](https://www.ni.com/en/support/documentation/supplemental/18/ni-imaq-memory-allocation.html)

- Consequently, `copy ??two Creates` still measures approximately **first-use allocation + pixel copy**, not steady-state copy. The image pool/OS behavior is irrelevant to the main flaw: even if repeated allocations are cached, that is lifecycle-dependent noise rather than the deployed operation.

- One COM Run per frame also injects Run/VI setup variance. It may match the display benchmark mechanically, but it does not model persistent acquisition and consumer loops.

Use a single Run containing a timed loop:

1. Read A once before timing.
2. Create B once.
3. Perform one untimed A?묪 copy to size/warm B.
4. Time \(N\) repeated A?묪 copies.
5. Baseline with the identical loop and sequencing but no copy.
6. Report median/run, tail percentile, and `(copy-loop ??baseline-loop)/N`.

Keep the current per-Run test only if you explicitly label it **cold first-copy cost**.

2. G4 is fundamentally about ring lifetime

A reference crossing a queue does not freeze its pixels. NI describes the image reference as a pointer to an internal image structure, not the pixel buffer itself. In continuous acquisition, driver buffers are reused; an old requested frame can become unavailable or be substituted according to overwrite policy. [NI: image-reference representation](https://www.ni.com/en/support/documentation/supplemental/18/ni-imaq-memory-allocation.html), [NI engineer explanation of ring rollover and overwrite modes](https://forums.ni.com/t5/LabVIEW/quot-buffer-number-in-quot-confusion-with-IMAQdx-get-image/m-p/826711)

NI explicitly recommends copying an acquisition-buffer image for later processing and releasing the ring reference so acquisition can continue. [NI: image no longer configured in ring](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YRU6CAO&l=en-US)

Therefore:

- A bare ring-backed reference is safe only while the consumer is guaranteed to finish before that physical slot is reused.
- Decimation reduces queue traffic but does not extend buffer lifetime. A display/save consumer can still stall after accepting a reference.
- `Next`, `Last`, and `Last New` select which acquired frame is returned; they do not grant permanent ownership. `Last New` waits for a frame not previously returned, while `New` waits for each new input. [NI: Last versus Last New](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000001DwvoCAC&l=en-US)
- For ?쐓ave every selected frame,??copy at selection time. For ?쐓how newest available frame,??either copy the chosen frame or let the display loop call `Get Image` itself using most-recent semantics?봧f that architecture and camera-session access are acceptable.

3. Cheapest decisive cells

I would use three cells, not the proposed cold-run trio:

| Cell | Measurement | Decision answered |
|---|---|---|
| C0 | Persistent-loop baseline | Timing floor |
| C1 | Warm, preallocated B; repeated A?묪 copy | True steady-state cost per safe handoff |
| C2 | Real acquisition stress: enqueue ring references to an intentionally delayed consumer; stamp/check frame number or deterministic pixels and record unavailable/substituted/corrupt frames | Whether reference-only handoff satisfies the actual lifetime contract |

Optional C3: copy only every \(D\)th frame into a small preallocated consumer-buffer pool under the same stress. This validates the proposed production policy, including pool exhaustion/backpressure.

Prediction contract:

- **Reference-only passes** only if C2 has zero mismatches/unavailable substitutions throughout a run longer than the worst credible consumer stall, with explicit buffer-number checking and overwrite mode set to fail rather than silently substitute.
- **Copy-on-demand wins** if C2 fails and `C1 횞 selected-consumer rate` fits the acquisition-loop budget with margin.
- **Copy-always is justified** only if every acquired frame must leave the acquisition loop, or if selection occurs downstream and ring lifetime cannot be bounded.
- For display, predict copy-on-decimated-demand.
- For save, predict copy of every frame committed to saving, into a bounded pool with an explicit drop/block policy.
- Do not compare C1 directly with the 0.6 ms ImageToArray result unless both are warm, internal-loop measurements at the same dimensions/type. Also, ?쐎ne LabVIEW copy per array wire branch??is not guaranteed merely by branching: LabVIEW may reuse buffers until a branch requires independent mutation. Treat actual array copies as a profiler/benchmark question, not a wiring axiom.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
