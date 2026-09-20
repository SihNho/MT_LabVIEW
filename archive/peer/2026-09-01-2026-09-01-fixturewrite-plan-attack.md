---
type: peer-review
status: historical
date: 2026-09-01
tags: [peer-review, plan, fixture]
disposition: legacy
---

# 2026-09-01-fixturewrite-plan-attack

- **agent:** codex
- **date:** 2026-09-01
- **outcome:** ANSWERED (45s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this LabVIEW modification plan (LabVIEW 2026, magnetic-tweezers tracking VI). Cite NI sources.

CONTEXT: A working copy of the experiment main VI has, in its last sequence frame, a while loop containing image acquisition (IMAQdx-based subVI returning an IMAQ image refnum), image analysis (bead tracking kernel), and data writing (.tra trace file, one row per loop iteration). GOAL: record a regression fixture - after acquisition, ALSO write each frame's image as an individual TIFF into the same directory as the .tra, named by zero-padded frame number, so .cal/.tra/imgNNNNN.tif line up per frame.

PLAN: a small subVI 'FixtureWrite.vi' (inputs: IMAQ image refnum, frame number I32, directory path, enable boolean; internally Format Into String %05d -> Build Path -> IMAQ Write TIFF File 2.vi inside a case structure on enable), dropped into that while loop with the image wire BRANCHED to it right after acquisition.

QUESTIONS/ATTACKS: (1) TIMING: the loop presumably paces the experiment; IMAQ Write TIFF of a 512x512-2048x2048 U16 frame to a local SSD - typical ms cost, and is it enough to disturb a soft-timed loop at low frame rate? Should the write be moved to a parallel consumer loop via queue instead (producer/consumer), and is that overkill for a deliberately slowed fixture run? (2) IMAGE BUFFER RACE: the acquisition subVI may reuse/overwrite the IMAQ buffer on the NEXT iteration - if FixtureWrite executes in the same iteration before next acquisition, is a branch of the image WIRE safe, or must we IMAQ Copy to a private buffer before writing? What does NI document about Grab buffers and wire branches of image refnums? (3) FILE NAME/PATH: Format Into String %05d + Build Path - any pitfalls (path type vs string, non-ASCII directory names)? (4) TIFF specifics for U16 via IMAQ Write TIFF File 2: byte order, NI-private tags - fine for LabVIEW-only replay? Compression default? (5) Frame-number source: using the while loop's i terminal vs the .tra row counter - if the .tra writer skips/buffers rows, i may desync from tra rows; what should be used as the authoritative frame index? (6) Anything about writing files inside the ANALYSIS loop that could corrupt the .tra timing columns (the experiment records timestamps)? Answer tersely, ranked by severity.

## Answer

The plan is acceptable only for a deliberately slow, synchronous fixture run. The main flaw is assuming that branching an IMAQ image wire creates an independent image.

1. **Critical ??image aliasing and execution order.** An IMAQ image wire carries a reference to reusable memory, not pixel data. Branching it does **not** copy or lock the image. NI explicitly warns that IMAQ references break ordinary dataflow assumptions and can race when branches access changing buffers ([NI: Define Execution Order with IMAQ Images](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P8khSAC&l=en-US); [NI: IMAQ memory allocation](https://www.ni.com/en/support/documentation/supplemental/18/ni-imaq-memory-allocation.html)).

   In one while-loop iteration, the next acquisition cannot begin until every node in the current iteration completes. Therefore synchronous TIFF writing is protected from the *next iteration*. But the TIFF writer and analysis branch may execute concurrently. If any analysis VI modifies its source in place?봶hich Vision VIs can do when no separate destination is wired?봳he saved TIFF may contain processed or partially modified pixels ([NI Vision manual](https://download.ni.com/support/manuals/371007a.pdf)).

   Establish explicit ordering with the error chain: acquisition ??TIFF write ??analysis, if the fixture must store raw acquisition pixels. Alternatively copy immediately into a preallocated private IMAQ image and write that copy. Merely placing nodes visually ?쏿fter??acquisition is insufficient.

2. **Critical if parallelized ??do not enqueue the same IMAQ reference.** A consumer queue containing the acquisition image refnum preserves only the pointer; the producer can overwrite that memory before the consumer writes it. Queue a private copied image per outstanding frame, or convert/copy pixels into owned data before enqueueing. NI?셲 producer/consumer guidance confirms that queues decouple rates, while NI?셲 IMAQ guidance confirms that image wires reference mutable memory ([NI producer/consumer architecture](https://www.ni.com/en/support/documentation/supplemental/21/producer-consumer-architecture-in-labview0.html); [NI execution-order warning](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P8khSAC&l=en-US)).

   A bounded queue, shutdown drain, writer-error propagation, and explicit disposal/reuse of private buffers are mandatory. Otherwise a slow writer causes growing memory use or silent frame loss. NI recommends producer/consumer processing where post-processing or file I/O must not slow continuous acquisition ([NI Vision acquisition post-processing](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000001DnYICA0)).

3. **High ??frame identity should not be the loop `i`.** Use the same accepted-record index actually written into the `.tra` row, preferably bundled with camera buffer/frame identity and timestamp at acquisition. Loop `i` counts attempts, including iterations later rejected or not logged. Conversely, using the writer?셲 eventual row count makes asynchronous correlation awkward. Treat one immutable record `{fixture index, camera buffer number, acquisition timestamp, trace row, image}` as the unit.

   Also note that `%05d` is a **minimum** width, not a five-digit limit: frame 100000 becomes six digits, and negative values introduce `-`. Decide whether this is allowed.

4. **High ??timestamps and loop timing will change.** A synchronous TIFF write adds encode, filesystem, and occasional SSD/OS latency directly to the iteration. NI explicitly states that putting acquisition and processing together slows acquisition to the processing rate ([NI producer/consumer architecture](https://www.ni.com/en/support/documentation/supplemental/21/producer-consumer-architecture-in-labview0.html)). There is no defensible ?쐔ypical milliseconds??value without benchmarking this exact image size, compression, SSD, antivirus and flush behavior.

   If timestamps are sampled after writing, the TIFF latency contaminates both timestamps and derived intervals. Capture the acquisition timestamp immediately after frame retrieval, before analysis or file I/O. For a deliberately slowed fixture, synchronous writing is reasonable only if measured worst-case iteration time remains comfortably below the intended period and the fixture explicitly records actual acquisition times.

5. **Medium ??TIFF defaults need to be explicit.** Do not rely on connector-pane defaults. Wire TIFF options explicitly. NI documents the default compression as **none**; ZIP and RLE are available, while JPEG is invalid for 16-bit monochrome images ([NI Community answer quoting the `IMAQ Write TIFF File 2` help](https://forums.ni.com/t5/LabVIEW/IMAQ-Write-Tiff-File-JPEG-Quality-Factor/td-p/622109)). For deterministic U16 fixtures, use uncompressed or lossless ZIP, then validate exact pixel equality by writing and reading representative frames.

   I found no current public NI documentation establishing the byte-order or private-tag behavior of the 2026 VI. For LabVIEW-only replay, settle this cheaply with a ramp/checkerboard U16 round trip including values `0`, `255`, `256`, `32767`, `32768`, and `65535`; do not assume interoperability from the `.tif` extension alone.

6. **Medium ??path handling and failures.** Derive the directory by stripping the actual `.tra` file path, rather than trusting a separately supplied directory. Use a path wire into `Build Path`; NI recommends path types because they use platform-appropriate syntax ([NI LabVIEW Development Guidelines](https://download.ni.com/support/manuals/321393d.pdf)). `img%05d.tif` itself contains only safe ASCII characters; the parent path may be non-ASCII, so test the actual Korean-path case rather than assuming the Vision file VI?셲 behavior.

   Wire and handle the TIFF error output. Disk-full, missing-directory, permission, or filename-collision errors must stop the fixture or mark the corresponding `.tra` row invalid?봭ever silently continue and claim an aligned dataset.

**Recommendation:** Start with synchronous acquisition ??TIFF ??analysis using an explicit error dependency, because it gives the simplest alignment for a slowed fixture. Benchmark full-run worst-case cadence. Move to producer/consumer only if timing disturbance is unacceptable, and then queue owned pixel copies plus immutable frame metadata?봭ot acquisition image references.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
