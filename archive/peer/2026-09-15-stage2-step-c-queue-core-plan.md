---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, stage2, producer-consumer, plan]
---

# stage2-step-c-queue-core-plan

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (143s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS PLAN, do not confirm it (LabVIEW 2026 VI Scripting over COM, zero GUI; rule 1a: kernel maths untouched). Read docs/stage2-assembly-step-c.md (the plan), docs/stage2-plan.md items 1/2/4/8, docs/stage2-assembly-step-b.md (the step that just passed: INDEX row 40, For-loop replay core bit-identical on the fixture), docs/toolkit-capabilities.md "Overnight additions", and archive/peer/2026-09-14-opqueue-test-run-hang.md (the queue test that hung).
Attack: (1) the queue topology for REPLAY: Q_free bounded 8 seeded 0..7, Q_img bounded 7 + Q_meta unbounded lock-stepped (path string as the frame identity), Q_res/Q_good/Q_pos lock-stepped results, tracker stops on Dequeue(Q_img) timeout after the acquisition For loop ends - name a deadlock, ordering hazard, or lost-frame path; is "Q_img can never be full because the producer blocks on Q_free (8 slots > depth 7)" actually an invariant? (2) LabVIEW data flow between two parallel loops in ONE VI: the acquisition For loop and the tracking While loop only share queue refnums - will they run concurrently (no data dependency), and does the sink For loop (dequeue N results) correctly wait for the tracker? What if the sink starts before results exist (Dequeue with timeout -1 blocks: fine) - name the failure if the tracker exits early. (3) IMAQ ReadFile INTO a pool image (image refnum from Index Array(pool, slot)): ReadFile's 'Image' input is the destination buffer - any resize/type side effect that changes pixel data vs the single working image used in step B (rule 1a)? (4) Obtain Queue typed from a node OUTPUT only: the plan makes a one-node sub-VI to get a String output - is there a simpler typed source (e.g. Path To String's output; the kernel outputs for arrays; IMAQ GetImageSize 'X Resolution' for I32)? (5) the new op OpExitWhileNode_v0 (Stop Condition from Get Outputs(node,'timed out?')): any pitfall (the name 'timed out?' exact; Boolean type; 'Stop if True' default)? (6) Which single scratch test first? Cite what you read; read-only.


## Answer

Verdict: reject Step C as written. It has at least two deterministic correctness holes and one likely deadlock. The Step-B bit-identical result does not protect the queued version.

1. Queue topology: the claimed invariant is false

?쏣ight slots > queue depth seven, therefore `Q_img` can never be full??is backwards.

A reachable state is:

```text
Q_img = 7 queued slots
ACQ   = owns the eighth slot after Dequeue(Q_free)
Q_free = 0
```

The producer then performs `Enqueue(Q_img, timeout=0)` against a full seven-element queue. NI documents that a bounded queue is full at its configured maximum and an enqueue must wait or time out until an element is removed. [NI Obtain Queue documentation](https://www.ni.com/docs/ja-JP/bundle/labview-api-ref/page/functions/obtain-queue.html)

Consequences:

- The eighth enqueue can time out. If its slot is not returned to `Q_free` in the timeout case, replay deadlocks later.
- The pseudocode in Step C shows `Enqueue(Q_meta,path)` unconditionally after `Enqueue(Q_img,slot)`. Unless a Case structure gates both metadata enqueue and slot return from `timed out?`, it creates a metadata-only ghost and permanently misaligns the pair.
- Even when `Q_img` succeeds, two independent queue operations are not atomic. An error, abort, or bad refnum between the two enqueues leaves `Q_img` ahead of `Q_meta`; the tracker can then block forever on metadata.
- The same atomicity defect exists in the `Q_res/Q_good/Q_pos` triple. One failed enqueue makes the sink consume different frames across the three queues or block forever.
- Step C enqueues `Q_meta`, but its TRK pseudocode never dequeues it. It therefore discards the proposed frame identity and leaves `Q_meta` growing unbounded.
- Step C also drops plan item 8?셲 result metadata queue. Array order alone is not the required `{sequence/frame identity, result}` contract. Repeated paths would additionally make a path string a poor unique event identity.

For lossless replay, make `Q_img` capacity 8 and use blocking enqueue, or retain capacity 7 but treat timeout as a fully tested drop transaction. Separate ?쐋ock-stepped??queues remain non-atomic either way; counts and sequence IDs must be checked at both ends.

2. Parallel-loop dataflow is valid, but shutdown is not

After the Obtain nodes produce their queue refnums, independent ACQ, TRK, and sink structures can execute concurrently. LabVIEW executes nodes when their inputs are ready, and independent loops can run simultaneously; diagram position supplies no ordering. [NI block-diagram dataflow](https://www.ni.com/docs/en-GB/bundle/labview/page/block-diagram-data-flow.html)

The sink may start first and block on `Dequeue(-1)`; that part is valid. The fatal path is:

1. TRK experiences any `Q_img` gap longer than `T`?봲low first ReadFile, filesystem pause, temporary producer delay, or producer error.
2. TRK exits even though ACQ has not finished.
3. ACQ consumes the remaining free slots and ultimately blocks on `Q_free` or loses an enqueue.
4. The sink waits permanently for its hard-coded `N` results.
5. Queue releases downstream of the sink never execute.

A timeout is evidence that the queue was empty for `T`, not evidence that the producer has finished. Use an explicit end-of-stream token or a separately synchronized ?쐏roducer finished??condition, then exit only when producer-finished **and** `Q_img` is drained.

There is an additional deterministic bug: wiring `Dequeue.timed out?` only to the While conditional terminal does not prevent the rest of that iteration from executing. A While condition is evaluated after the body iteration. [NI While-loop behavior](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YJYUCA4) On timeout, the element output is its default value, so without a Case structure TRK can process default slot `0`, enqueue a phantom result, and return slot `0` twice. The stop Boolean must also select a Case that skips indexing, kernel execution, result enqueues, and slot return.

This matches the earlier authorized hang report: an empty-producer path plus `Dequeue(-1)` produced an indefinite run, despite `ExecState=1`, in [2026-09-14-opqueue-test-run-hang.md](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/archive/peer/2026-09-14-opqueue-test-run-hang.md).

3. `IMAQ ReadFile` into pooled images is not yet covered by rule 1a

The wiring direction is plausible: NI?셲 example connects both `Image` and `File Path` inputs to `IMAQ ReadFile`. [NI IMAQ ReadFile example](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU000000Cwuf0AC&l=en-US)

But bit identity is not established merely because the input is a destination reference. NI documents that Vision image storage is dynamically allocated when operations alter image size, while image creation establishes properties such as type and border. [NI image allocation discussion](https://download.ni.com/support/manuals/323023a.pdf) Thus every pool image must be created with exactly the Step-B working image?셲 type and border contract. ReadFile may resize/reallocate storage; that alone should not change decoded pixels, but a type mismatch could cause conversion or an invalid-image-type error.

The necessary gate is an eight-slot scratch comparison:

- read the same TIFF successively into the Step-B working image and each pool image;
- compare dimensions, image type, border and every pixel?봮r a collision-resistant hash of the extracted pixel bytes;
- then compare one-frame kernel outputs bit-for-bit.

Until that passes, ?쐊ernel maths untouched??does not prove ?쐊ernel input unchanged.??
4. The proposed `StrId.vi` is unnecessary

Simpler typed sources already exist:

- `Q_res`: kernel DBL-array output.
- `Q_good`: kernel Boolean-array output.
- `Q_pos`: kernel I32-array output.
- `Q_free/Q_img`: `IMAQ GetImageSize.X Resolution`, already measured as an I32 source in the passing queue test and named in [NAMES.md](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/NAMES.md).
- `Q_meta`: copy a `Path To String` primitive and use its String output. Since `StrToPath.vi` already supplies a Path output, `StrToPath.path ??Path To String ??String sample` avoids creating another identity subVI.

The restriction is the current op?셲 ?쐍amed node output??interface, not an Obtain Queue requirement. Obtain Queue only needs a wired sample determining the element type.

5. `OpExitWhileNode_v0` pitfalls

The recorded exact terminal name is indeed `timed out?`; [NAMES.md](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/NAMES.md) and the passing queue logs agree. It is Boolean, and a new While loop defaults to Stop if True. [NI While-loop configuration](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YJYUCA4)

Still gate all of these:

- exact case-sensitive output-name lookup;
- selected node is the intended Dequeue, not another node with `timed out?`;
- source and conditional-terminal wire UIDs match;
- conditional mode is explicitly read/set to Stop if True?봡o not depend on the donor/default;
- timeout iteration performs no work, because the stop terminal alone does not short-circuit an iteration.

6. First scratch test

Do **not** start with the proposed ?쐃mpty queue returns within approximately T??test. It can pass while silently processing default slot zero.

First test this exact contract:

> Empty `Q_img`, `Dequeue timeout=200 ms`, timeout-driven Case around all work, and `OpExitWhileNode_v0`. Require one loop iteration, zero kernel/work-side-effect count, zero result enqueues, unchanged `Q_free`, `timed out?=TRUE`, and return within a bounded interval.

That single test attacks the newest primitive and the most dangerous mistaken assumption. After it passes, test a delayed producer where the first item arrives after more than `T`; that should demonstrate why timeout cannot serve as end-of-stream.

Files reviewed: [Step C](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/stage2-assembly-step-c.md), [stage-2 plan](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/stage2-plan.md), [Step B](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/stage2-assembly-step-b.md), and [toolkit capabilities](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/toolkit-capabilities.md).

## Sources

(extract from answer)

## What was done with it

Rejected plan withdrawn. All six points accepted: the "8 > 7" invariant was backwards; a timeout is not
end-of-stream; a While stop terminal does not short-circuit the timed-out iteration (a Case would be needed);
the lock-stepped queue pairs are not atomic; `Q_meta` was never consumed; pool-image type/border equality is a
rule-1a gate, not an assumption; `StrId.vi` unnecessary (typed samples: kernel outputs, `GetImageSize.X Resolution`,
`Path To String`). **Step C v2 (docs/stage2-assembly-step-c.md, rewritten):** in REPLAY every loop is a FOR loop
over the known N — ACQ (dequeue free slot, ReadFile into it, blocking enqueue to `Q_img` of capacity 8 + `Q_meta`),
TRK (blocking dequeue, kernel with registers, enqueue results + meta pass-through, return slot), sink (N dequeues)
— so there is no stop logic, no timeout, no phantom iteration and no drop transaction; alignment of the paired
queues is asserted by count and by the pass-through frame identity at the sink. The While-loop tracker with an
end-of-stream token and a timeout-gated Case is deferred to the live-camera step, where it is unavoidable. A
pool-image gate (8 slots × one frame, kernel outputs bit-identical to the working-image path) precedes assembly.
Re-review: `…-stage2-step-c-queue-core-plan-v2.md`.
