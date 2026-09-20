---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, stage2, producer-consumer]
---

# stage2-queue-core-recipe

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (115s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS RECIPE before it runs (LabVIEW 2026 VI Scripting over COM, zero GUI; rule 1a). Read tools/recipes/build_track_v6_queue.py whole, docs/stage2-assembly-step-c.md (v2 + the v2.1 simplification), your review archive/peer/2026-09-15-stage2-step-c-queue-core-plan-v2.md, and tools/recipes/build_track_v6_core.py (the passing step-B recipe whose helpers it imports; INDEX row 40).
Design now: the pool is a queue of IMAGE REFNUMS (Q_free/Q_img typed from a top-level IMAQ Create 'New Image'); the pool For loop creates 8 images (names from an indexed Pool Names[] tunnel) and enqueues each into Q_free; ACQ (For over Frame Paths): Dequeue(Q_free) -> ReadFile into that image -> Enqueue(Q_img, Image Out) -> Enqueue(Q_meta, path) error-chained; TRK (For, N from an indexed Frame Paths tunnel whose inner wire is DELETED): Dequeue(Q_img) -> kernel(image; 3 registers) ; Dequeue(Q_meta); Enqueue Q_res/Q_good/Q_pos/Q_rmeta chained; Enqueue(Q_free, image) LAST in the error chain; sink (For, same N trick): 4 chained Dequeues -> 4 auto-indexed outputs; 7 Releases chained from the sink's last 'error out' leaving through a last-value tunnel. All timeouts unwired (-1). A top-level kernel instance KT fed by a sample IMAQ Create + ReadFile(frame 0) is the DBL[]/Bool[]/I32[] type source AND a one-shot self-check (its outputs must equal reference row 0). Type source for strings: PathToStr.vi (Path To String copied by index).
Attack: (1) the 'count tunnel' trick: an auto-indexed input tunnel whose inner wire is deleted - does an UNWIRED inner terminal of an input tunnel leave the VI runnable, and does it still set N? (2) TRK dequeues Q_meta AFTER the kernel? No - it is chained Dequeue(Q_img).error out -> Dequeue(Q_meta).error in, then results; is the order of Q_img vs Q_meta dequeue irrelevant given FIFO + one consumer? (3) Enqueue(Q_free, image) with element from Dequeue(Q_img).element (a branch) and 'error in' from the LAST result enqueue: does the error chain guarantee the image is returned only after the kernel consumed it (kernel -> Enqueue(Q_res) data dependency -> chain)? Is there any path where the image is returned to Q_free while ReadFile in ACQ could overwrite it BEFORE the kernel reads it (image refs are mutable buffers!) - i.e. ACQ reads frame n+8 into an image while TRK still uses it? Prove the ownership argument or name the hole. (4) Releases chained from the sink's error-out tunnel: the Release of Q_free/Q_img runs after the sink - but TRK's last Enqueue(Q_free) may still be executing when the sink finishes: is a Release during a concurrent Enqueue an error (Release with force destroy? default FALSE - the queue is destroyed only when the last reference is released; the loops hold no extra refs...)? Recommend the safe ordering. (5) KT self-check: KT reads frame 0 into the SAMPLE image and runs the kernel with the same initial state as row 0 - must equal reference row 0; any reason the sample image differs from a pool image (rule 1a)? (6) any silent-wrong-VI path the gates miss, and the cheapest scratch test to run first. Read-only; cite what you read.


## Answer

Verdict: **do not run this recipe unchanged.** The image-ownership chain is sound, but shutdown has a real race, the count-tunnel trick is not yet proven, and several promised gates are absent from the implementation.

1. Count-tunnel trick: plausible, not proven

NI documents that an auto-indexed array input tunnel determines a For Loop?셲 iteration count without wiring `N`. It does not explicitly say whether the tunnel?셲 inner terminal may be left unwired while retaining that behavior. [NI auto-indexing documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG)

The recipe creates such a tunnel and deletes its inner wire at [build_track_v6_queue.py:93](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_track_v6_queue.py:93>). Its structural gate verifies only `IndexMode == 1` and no inner wire?봭ot the loop count.

It will probably remain runnable because the border still has a wired array input and only the unused scalar output is dangling, but that is an inference, not documented ground truth.

Cheapest first test:

- Scratch empty VI.
- String array ??indexed For-loop tunnel.
- Delete only the inner segment.
- Auto-index loop counter `i` to an output.
- Require `ExecState == 1`.
- Run with lengths 0, 1, and 3; require output lengths 0, 1, and 3.

Do this before assembling queues. It isolates the undocumented assumption in seconds.

2. Image/meta dequeue order is safe

The code does not actually place `Dequeue(Q_meta)` after the kernel. It chains:

`Dequeue(Q_img).error out ??Dequeue(Q_meta).error in`

while the image element independently feeds the kernel, at [build_track_v6_queue.py:201](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_track_v6_queue.py:201>). Therefore the kernel and metadata dequeue may execute concurrently after the image dequeue.

That is harmless on the success path:

- ACQ is the only producer for both queues.
- TRK is the only consumer.
- Each ACQ iteration publishes one image and then one matching metadata item.
- Each queue independently preserves FIFO order. [NI queue overview](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P7OfSAK&l=en-US)

TRK can receive image `n`, start its kernel, and wait for metadata `n`; it cannot receive metadata `n+1`. The `META == Frame Paths` gate is a useful runtime check, though it does not alone prove association with the separate result queues.

3. Image ownership is sound on the no-error path

The relevant chain is:

`Dequeue(Q_img).element`
??kernel image input  
??kernel output data  
??first result enqueue  
??remaining result enqueues by error chain  
??`Enqueue(Q_free, image)`

This is implemented at [build_track_v6_queue.py:227](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_track_v6_queue.py:227>).

Although the image wire branches directly to the return enqueue, that enqueue cannot execute until the preceding error chain reaches it. The chain cannot reach it until `Enqueue(Q_res)` receives the kernel output, and a subVI?셲 output is unavailable until that kernel call completes. Consequently:

- ACQ owns the image after `Dequeue(Q_free)`.
- Ownership transfers to `Q_img` only after `ReadFile` completes.
- TRK owns it after `Dequeue(Q_img)`.
- It is not returned to `Q_free` until the kernel and result publication complete.
- Only then can ACQ dequeue and overwrite it.

That is the required happens-before edge for mutable IMAQ buffers. NI confirms that an IMAQ image wire is a reference to reusable memory and that explicit execution order is required to avoid races. [NI IMAQ execution-order guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P8khSAC)

I see no success-path hole allowing ACQ to overwrite a buffer while the kernel is still reading it.

The limitation is error behavior: an error before the final enqueue can strand the image permanently and cause a downstream infinite dequeue. That is consistent with the design?셲 watchdog policy, but it must be described as ?쐓afe on the exact-once, no-error path,??not unconditionally safe.

4. Release ordering is unsafe

This is the blocking defect.

TRK publishes in this order:

`Q_res ??Q_good ??Q_pos ??Q_rmeta ??Q_free`

at [build_track_v6_queue.py:237](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_track_v6_queue.py:237>).

The sink finishes as soon as it dequeues the last `Q_rmeta` item. Therefore it can finish immediately after TRK?셲 `Enqueue(Q_rmeta)` but before TRK?셲 later `Enqueue(Q_free)`.

The release chain depends only on sink completion at [build_track_v6_queue.py:266](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_track_v6_queue.py:266>). There is no dependency on TRK-loop completion. Releasing `Q_free` last merely makes the race less likely; it does not remove it.

With only one `Obtain Queue` per queue, default `force destroy? = FALSE` does not protect this design: once the obtained reference is released, operations using that reference can become invalid. NI?셲 queue discussion notes that releasing/invalidating a queue wakes blocked dequeues with an error; force-destroy invalidates all references immediately. [NI queue reference behavior](https://forums.ni.com/t5/LabVIEW/Dequeue-question/m-p/494668)

Safe repair:

- Export TRK?셲 final `Enqueue(Q_free).error out` through a last-value tunnel.
- Export the sink?셲 final dequeue error similarly.
- Join both completion dependencies with `Merge Errors` or an equivalent two-input barrier.
- Begin all seven releases only after that join.
- Surface the final release error in a top-level indicator.

If introducing `Merge Errors` is inconvenient, an even simpler ordering is:

`TRK complete ??sink allowed to finish/release`

but that removes useful streaming concurrency if applied too early. The proper join preserves concurrency and only synchronizes teardown.

5. KT is equivalent in principle, but its gate is incomplete

The sample path is:

`IMAQ Create ??IMAQ ReadFile(frame 0) ??KT`

at [build_track_v6_queue.py:135](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_track_v6_queue.py:135>). Pool images use the same `IMAQ Create` implementation with distinct names. An image name identifies the backing buffer; it should not change decoded pixel data or kernel behavior. IMAQ may reuse/reallocate backing storage, which is precisely why the ownership ordering matters. [NI IMAQ buffer explanation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P8khSAC)

KT also receives the same calibration, window arrays, parameters, and initial state controls as the queued kernel. Thus its output should match reference row 0 under rule 1a.

But the recipe reads all three KT outputs and compares only `xyz`:

[build_track_v6_queue.py:312](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_track_v6_queue.py:312>)  
[build_track_v6_queue.py:317](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_track_v6_queue.py:317>)

It must also require:

- `kt["good"] == reference_row_0["good"]`
- `kt["pos"] == reference_row_0["pos"]`

Otherwise the advertised ?쏫T outputs equal row 0??gate is false.

6. Other silent-wrong or missing-gate paths

The documentation promises more than the recipe implements.

- No final `Q_free` census exists. The document says eight returned references will be dequeued, while the recipe immediately releases queues. See [stage2-assembly-step-c.md:49](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/stage2-assembly-step-c.md:49>) versus the release code above.
- Refnum identity cannot be read over COM, but the recipe does not even prove count eight by draining eight elements.
- No queue-error indicator is exposed. Automatic error handling is disabled, and the final release error is not returned, so some queue failures can be silent rather than either hanging or failing a gate.
- The recipe does not explicitly inspect/gate TRK parallel-iteration execution as the v2 review required. Shift registers should serialize it, but the property should still be checked.
- ?쏛ll three iteration counts equal N??is not directly gated. Sink row counts prove sink `N`; exact numeric output strongly implies TRK completed `N`, but ACQ count is not independently observed.
- The documented C0 eight-slot pool-image scratch gate is absent. The current 1????00 sequence tests pool use indirectly, and 200 frames crosses reuse many times, but it does not localize first-use failures to a particular image.
- With unique pool names, count eight plus successful 200-frame exact replay is strong evidence, but it still does not detect duplicate-reference seeding as directly as the old `{0??}` permutation gate could.

Recommended first-run order

1. Count-tunnel scratch test: lengths 0/1/3.
2. Fix teardown with a TRK+sink completion join.
3. Add KT `good` and `pos` comparisons.
4. Add final error indicator and require no error.
5. Explicitly gate TRK parallelism off.
6. Run 1 frame, 2 frames, then at least 9 frames to cross the first pool reuse.
7. Run 200 exact frames.
8. Only then consider `--full`.

The row-40 reference is solid: step B passed 1, 2, 200, and the full 10,043-frame run, with all 10,018 pre-loss rows bit-identical, as recorded in [INDEX.md:54](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/benchmarks/INDEX.md:54>). The queue recipe should not run until the shutdown race is repaired.

## Sources

(extract from answer)

## What was done with it

All points applied before the first run of `tools/recipes/build_track_v6_queue.py`: (1) the count-tunnel trick is
tested first on a scratch (`tools/bench/test_count_tunnel.py`: inner wire deleted, indexed output of the loop,
0/1/3 elements → 0/1/3 iterations, ExecState 1); (4) the teardown race is removed by a JOIN with no Merge Errors —
a DRAIN loop (8 dequeues of `Q_free`, N from `Pool Names`) takes its queue refnum from TRK's last
`Enqueue(Q_free).queue out` exported through a last-value tunnel (after TRK) and its `error in` from the sink's
exported `error out` (after the sink); `Release(Q_free)` takes its refnum from the drain's dequeue `queue out`
(after the drain) and the other six releases chain by error from it; the final release error is surfaced as an
indicator; (5) the KT self-check compares xyz, good AND pos; (6) the drain's `timed out?` array (8 × FALSE) is the
count-8 gate the document promised (refnum identity remains unreadable over COM — recorded). Points (2) and (3)
accepted as stated: safe on the exact-once, no-error path; an error is an intentional watchdog hang.
