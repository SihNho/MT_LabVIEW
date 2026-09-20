---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, stage2, producer-consumer, plan]
---

# stage2-step-c-queue-core-plan-v2

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (113s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RE-REVIEW (attack, do not confirm). LabVIEW 2026 VI Scripting over COM, zero GUI; rule 1a. Read docs/stage2-assembly-step-c.md (v2, rewritten after your rejection archive/peer/2026-09-15-stage2-step-c-queue-core-plan.md), docs/stage2-plan.md items 1/2/4/8, and INDEX row 40 in archive/benchmarks/INDEX.md (the For-loop replay core: all 10,018 pre-loss frames bit-identical, full run 192 s).
v2: in REPLAY all three loops (ACQ, TRK, sink) are FOR loops over the same N (Frame Paths length), running in parallel through queues with BLOCKING calls (timeout -1): Q_free capacity 8 seeded 0..7, Q_img capacity 8 (= pool size, so the producer can never block on a full Q_img), Q_meta (path string) produced in the same ACQ iteration and consumed in the same TRK iteration, passed through to Q_rmeta and read by the sink; sink gate META[n] == Frame Paths[n]; final Q_free count 8. No timeouts, no Cases, no end-of-stream signal. A pool-image gate (8 slots x one frame, kernel outputs bit-identical) precedes assembly.
Attack: (1) any deadlock or ordering hole left: e.g. sink dequeues Q_res before TRK enqueued it (blocks, fine) - but is there a scenario where a loop blocks forever with N fixed? Consider LabVIEW scheduling of three parallel For loops in one VI (each iteration is a clump) and the fact that ACQ's Dequeue(Q_free) blocks while TRK holds slots - with 8 slots and N >= 8 is progress guaranteed? (2) Is 'Q_img capacity 8 cannot block the producer' correct now: Q_img holds at most (8 - slots held by ACQ/TRK) items - prove or refute. (3) The paired queues: with blocking calls and one producer/one consumer per queue, is the same-iteration production/consumption enough to guarantee alignment, and is META == Frame Paths a sufficient check? (4) IMAQ ReadFile into 8 different pool images each created by IMAQ Create with identical defaults - what could make the decoded image differ from step B's single working image (border, type, name uniqueness, reallocation on first read)? Is the 8-slot one-frame gate sufficient, and should the gate also run a multi-frame sequence where consecutive frames land in different slots (it will, by construction)? (5) rule 1a: the kernel receives the same image data and the same fed-back state - what about the ORDER of frames reaching the kernel: guaranteed FIFO across queues so frame n's state feeds frame n+1? (6) Which single scratch test first, and any cheaper structure you would prefer for the replay acceptance. Read-only; cite what you read.


## Answer

Verdict: v2 is deadlock-free only under an explicit success-path assumption. The nominal token cycle is sound, but the document still overstates liveness and understates the risks of independent paired queues and first-use image allocation.

1. Deadlock/liveness

For successful operations, terminating kernel calls, valid queue references, and non-parallelized loop iterations, progress is guaranteed:

- Let `F`, `A`, `I`, and `T` be slots in `Q_free`, held by ACQ, queued in `Q_img`, and held by TRK.
- The ownership invariant is `F + A + I + T = 8`.
- If ACQ blocks on `Q_free`, then `F=0`, so at least one slot is in `Q_img` or TRK.
- TRK can consume a queued slot, or finish its current kernel call and return its slot.
- TRK does not depend on the sink to return a slot because result queues are unbounded.
- Therefore scheduling alone cannot create a circular wait. LabVIEW permits independent loops to execute concurrently under dataflow, and a blocked node does not require its sibling loop to finish first. [NI dataflow documentation](https://www.ni.com/docs/en-GB/bundle/labview/page/block-diagram-data-flow.html)

But ?쐍othing can hang??is false. Any iteration that fails before completing its exact enqueue/dequeue count can leave a downstream `Dequeue(-1)` waiting forever. Examples:

- `IMAQ ReadFile` errors before publishing `Q_img`.
- A queue operation receives an upstream error and does not perform its transaction.
- The kernel errors or fails to return.
- A queue is released early or the reference is invalid.
- An auto-indexed input other than `Frame Paths` shortens one loop.

NI confirms that `-1` waits indefinitely; it is not a correctness detector. [NI queue timeout documentation](https://download.ni.com/support/manuals/321526b.pdf)

So revise lines 25??0 from an unconditional safety claim to:

> On the no-error path, with all three loops executing exactly N iterations and every operation completing once, the queue graph has no circular wait. Any operation error or transaction-count mismatch may produce an intentional watchdog-detected hang.

Also gate:

- All three completed iteration counts equal `N`.
- All queue operations have no error.
- No unintended auto-indexed tunnel determines a smaller `N`.
- TRK?셲 For-loop parallelism is explicitly off; its shift registers should enforce serialization, but inspect/gate the property anyway.
- Final `Q_free` is not merely count 8 but exactly the permutation `{0??}`. Count 8 alone cannot detect duplicate-slot/lost-slot corruption.

The proposed structure is documented at [stage2-assembly-step-c.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/stage2-assembly-step-c.md:9>); the ownership requirement originates in [stage2-plan.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/stage2-plan.md:50>).

2. Can `Q_img` block when its capacity is 8?

Not on the valid-ownership path. The strongest proof examines the instant before ACQ enqueues:

- ACQ must already hold one slot, so `A ??1`.
- Therefore `I ??8 ??A ??F ??T ??7`.
- Thus at least one position is available in capacity-8 `Q_img`.
- Enqueue transfers one slot from `A` to `I`, after which occupancy can become 8, but that enqueue did not encounter a full queue.

The proposed expression ?쏿t most `8 ??slots held by ACQ/TRK`??is a valid loose upper bound, but the exact equation also subtracts free slots:

`I = 8 ??F ??A ??T`.

This proof depends on no duplicate seeding, no double-return, and no enqueue without first acquiring a slot. NI confirms a bounded queue with timeout `-1` waits if it actually is full. [NI bounded-queue behavior](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU0000002WyH0AU)

3. Paired queues and alignment

Same-iteration placement is insufficient unless you also establish these facts:

- Each For loop?셲 iterations are sequential.
- Each producer performs exactly one enqueue to every member of the pair per iteration.
- Each consumer performs exactly one dequeue from every member per iteration.
- Nothing else accesses those queues.
- Error flow cannot skip one operation while allowing its partner to execute.

Under those conditions, independent FIFO sequences remain positionally aligned even if `Enqueue(Q_img)` and `Enqueue(Q_meta)` execute in either wall-clock order. TRK might obtain the image slot and then wait for metadata, but it will receive metadata item `n`; one producer preserves the order within each queue. NI defines LabVIEW queues as FIFO. [NI queue overview](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P7OfSAK&l=en-US)

The hole is partial publication. ?쏶ame iteration??is not an atomic transaction. Make the second enqueue data-dependent on the first?봭ormally through the error chain?봞nd treat any error as fatal. Do the same for all TRK result queues. Otherwise one failed enqueue can permanently offset or hang the paired streams.

`META[n] == Frame Paths[n]` is necessary and strong for order, duplication, and omission of metadata. It is not by itself proof that `XYZ[n]`, `GOOD[n]`, and `POS[n]` belong to that metadata because those are separate queues. That association follows only from the exact-once/FIFO assumptions above. Prefer one composite result element when tooling permits.

4. Eight IMAQ images

The named risks are real:

- Every simultaneously existing IMAQ image requires a unique name. [NI Vision manual](https://download.ni.com/support/manuals/371007a.pdf)
- `IMAQ Create` establishes image properties including type and border, but initially does not allocate pixel storage. The default border is three pixels. [NI Vision manual](https://download.ni.com/support/manuals/371007a.pdf)
- `IMAQ ReadFile` internally configures/allocates its destination buffer. [NI memory-allocation documentation](https://www.ni.com/en/support/documentation/supplemental/18/ni-imaq-memory-allocation.html)
- IMAQ image wires are references to mutable buffers, so ownership and execution order matter. [NI image execution-order guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P8khSAC)

A one-frame-per-slot gate proves cold first-use equivalence for those eight files/slots, but not reuse equivalence. It misses:

- slot 0 being overwritten with frame 8 after earlier processing;
- consecutive kernel states crossing slot boundaries;
- alternating buffer addresses affecting an illicit retained image reference;
- mixed file dimensions/types causing later reallocation;
- ownership errors that only appear after pool wraparound.

Yes, add a multi-frame gate. Consecutive frames must land in different slots, and the test must cross the first reuse boundary. Minimum meaningful sequence is 9 frames; 16??7 is better. A 200-frame exact comparison is already part of acceptance and gives much stronger coverage cheaply.

5. Rule 1a and frame order

On the success path, yes:

- ACQ enqueues slots and metadata in frame-path iteration order.
- `Q_img` and `Q_meta` are FIFO.
- TRK has one consumer and processes one dequeued item per sequential iteration.
- Its three shift registers serialize the feedback, so frame `n` produces the state consumed by frame `n+1`.
- The sink?셲 FIFO queues preserve result order.

This should be stated as a tested invariant, not inferred only from `META`. Gate `META == Frame Paths`, ensure TRK parallel-iteration execution is disabled, and compare all state outputs at every frame. Row 40 establishes that the current single-image For-loop reference is exact through all 10,018 pre-loss frames and ran the full fixture in 192 seconds: [benchmark INDEX row 40](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/benchmarks/INDEX.md:54>).

6. First scratch test and cheaper acceptance structure

The first scratch should be a sequential round-robin pool-image kernel test, not eight isolated one-frame runs:

- Use the unchanged step-B For-loop kernel and feedback registers.
- Replace its single image with `pool[i mod 8]`.
- Run at least 17 consecutive frames, covering cold allocation and two reuses of slot 0.
- Compare `XYZ/GOOD/POS` bit-for-bit at every frame.
- Record frame path and slot sequence.
- Then run the existing 200-frame gate.

This isolates the largest new rule-1a risk without queues, sink, or scheduler effects. If it fails, assembly would only obscure the cause.

For replay acceptance, I would initially omit the sink loop and the four result queues. Let the TRK For loop auto-index `XYZ/GOOD/POS/META` directly out of its boundary. That still tests the essential ACQ??Q_img/Q_meta`?뭈RK pipeline, pool ownership, FIFO ordering, and state feedback, while removing the non-atomic four-queue result transaction. Add the sink/result queues in a separate scratch once the two-loop core passes.

Final disposition: approve the token-capacity argument, reject the unconditional no-hang claim, require explicit partial-publication/error gates, strengthen final slot census to permutation equality, and replace the eight isolated image tests with a consecutive round-robin sequence crossing pool reuse.

## Sources

(extract from answer)

## What was done with it

Accepted; v2 stands with three tightenings written into docs/stage2-assembly-step-c.md: (1) the liveness claim is
conditional — on the no-error path with all three loops at exactly N iterations there is no circular wait, and any
operation error becomes an intentional hang caught by the bgrun deadline; gates: iteration counts == N, no queue
errors, TRK parallelism off, final `Q_free` drained == the exact permutation {0..7}; (2) paired enqueues
(`Q_img`→`Q_meta`, the result triple + `Q_rmeta`) are ERROR-CHAINED so a failed first enqueue prevents the
second; (3) the pool gate is one frame × 8 slots for cold first use, and the 200-frame exact run (≥ 25 pool
wraparounds) covers reuse. The ownership proof (I = 8 − F − A − T ≤ 7 at the instant before ACQ enqueues) is
recorded. Recipe: `tools/recipes/test_pool_images.py` (C0) then `build_track_v6_queue.py`.
