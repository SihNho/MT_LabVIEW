---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, producer-consumer]
---

# opqueue-test-run-hang

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (80s)
- **why asked:** the queue test run (test_opqueue.log) did not return within 60 s after all four nodes built structurally
- **verdict:** unverified

## Question

FAILED PREDICTION check (brief). tools/bench/test_opqueue.log (tools/bench/test_opqueue.py): four scripted LabVIEW queue nodes placed on a scratch VI (copy of HARNESS_copyloop: top level IMAQ Create/ReadFile/Create/Copy/GetImageSize + a For loop N=1024 with an inner IMAQ Copy). Placed: Obtain Queue (element data type <- GetImageSize.'Y Resolution', I32) top level; Enqueue inside the For loop body (queue <- Obtain.'queue out' via a tunnel, element <- GetImageSize.'X Resolution' via a tunnel, timeout default -1); Dequeue on the top level (queue <- Obtain.'queue out', timeout default -1) with indicators on 'element' and 'timed out?'; Release (queue <- Dequeue.'queue out'). ExecState 1. PREDICTED: one COM Run returns quickly with element = 1280. OBSERVED: the Run did not return within 60 s (no modal dialog), client killed by the deadline. MY EXPLANATIONS, ranked: (1) dataflow: the Dequeue (timeout -1) is scheduled in parallel with the loop and waits; the loop enqueues 1024 elements... it should return - UNLESS the loop never starts because the tunnel bringing Obtain's queue refnum into the loop was created but its OUTER side is not wired to Obtain (the creator wired inside the frame only) - yet ExecState 1 argues all tunnels are wired; (2) the Release runs right after the first Dequeue while the loop keeps enqueuing into a released queue - errors, not a hang; (3) the For loop's own IMAQ Copy path with an unset 'File Path' (the scratch's ReadFile has no file: error, and with auto error handling OFF the loop still runs). Which of these can produce an INDEFINITE wait? Also: does an Enqueue Element with timeout -1 on an UNBOUNDED queue ever block? Could Obtain Queue with 'name' unwired and 'create if not found' default create a queue whose refnum differs between the branches (no - same wire)? Suggest the cheapest discriminating census (which wires exist on the tunnels' outer terminals; the loop node's Terminals[] and tunnels() reads) before the next run, and whether a LabVIEW restart is required after a deadline-killed Run (our rule says yes).

## Answer

The prediction failed only if no enqueue ever completed. A correctly wired, unbounded queue cannot explain the 60-second wait.

- **Explanation 1 is the only listed mechanism capable of an indefinite wait.** `Dequeue(timeout=-1)` waits forever if the producer never supplies an element. But a genuinely undefined For-loop tunnel normally makes the VI nonexecutable, so a successful top-level Run weakens the ?쐎uter side absent??variant. NI explicitly identifies undefined loop tunnels as a broken-VI cause. [NI: broken run arrow / undefined tunnel](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000001DdHkSAK)

- **Explanation 2 should produce an error, not a permanent wait.** Release is data-dependent on the first Dequeue, so it cannot execute until Dequeue has already returned. Subsequent Enqueues can race the Release and receive an invalid-refnum error; releasing a queue also wakes operations waiting on it with error 1122. [NI: error 1122](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019LYuSAM), [NI: enqueue/dequeue after Release](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019PrlSAE)

- **Explanation 3 ordinarily returns an IMAQ error rather than waiting indefinitely.** I would still verify that the baseline scratch VI without queue nodes returns, because a blocking upstream IMAQ call would prevent `GetImageSize`, hence Obtain and both queue branches, from becoming runnable. This is an inference from the supplied dataflow, not evidence that IMAQ is actually blocking.

- **Enqueue with `timeout=-1` on an unbounded queue does not block for capacity.** Obtain Queue?셲 default maximum size is `-1`, meaning unlimited; Enqueue waits only when a bounded queue is full. [NI Obtain Queue reference](https://www.ni.com/docs/ja-JP/bundle/labview-api-ref/page/functions/obtain-queue.html)

- **The unwired name is irrelevant here.** There is one Obtain call and its single output wire is branched. No second refnum is obtained. Named-queue lookup semantics only matter across separate Obtain calls. [NI Obtain Queue reference](https://www.ni.com/docs/ja-JP/bundle/labview-api-ref/page/functions/obtain-queue.html)

Cheapest pre-run census:

1. Enumerate the For loop?셲 `Terminals[]` and tunnel objects.
2. For each tunnel, report both boundary terminals separately:
   - terminal ID/type/direction,
   - connected wire ID,
   - wire source terminal,
   - all sink terminals.
3. Require these exact paths:
   - `Obtain.queue out ??queue tunnel outer ??queue tunnel inner ??Enqueue.queue`
   - `GetImageSize.X Resolution ??element tunnel outer ??element tunnel inner ??Enqueue.element`
4. Also confirm:
   - `Obtain.queue out ??Dequeue.queue`
   - `Dequeue.queue out ??Release.queue`
   - loop `N ??1024`
5. Census Enqueue?셲 upstream readiness, especially any error input or other required terminal accidentally connected to a non-returning node.

Do not trust ?쐔unnel exists??or `ExecState` alone; prove both terminal-side wire connections and their endpoints.

After the deadline-killed COM client: **yes, follow your restart rule.** Killing the caller does not prove the top-level VI stopped; a `Dequeue(-1)` may remain active indefinitely. NI defines a running top-level hierarchy separately from an idle loaded VI. [NI execution-state documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YIEJCA4) A controlled LabVIEW restart is the cleanest way to discard the orphaned execution and queue state before the next run.

## Sources

(extract from answer)

## What was done with it

Confirmed by the rerun (test_opqueue.log 22:03): the loop's N came from GetImageSize on an errored ReadFile (no File Path) = 0, so no enqueue ever happened and Dequeue(-1) waited - explanation 1's 'producer never supplies' variant, not a tunnel defect (the census the reviewer asked for shows every path: 478 -> 462, 490 -> 465). LabVIEW was restarted per rule; the test now sets File Path and a finite dequeue timeout; 7/7 PASS. Verdict: correct.
