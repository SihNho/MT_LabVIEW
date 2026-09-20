---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, producer-consumer]
---

# opqueue-fail1-duplicate-error-out

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (43s)
- **why asked:** failed prediction in build_opqueue.log run 1 (the creator has two error out terminals; the by-name wire hit the refnum one)
- **verdict:** unverified

## Question

FAILED PREDICTION check (brief). tools/bench/build_opqueue.log (tools/recipes/build_opqueue.py obtain): placing erdosmiller 'Create Obtain Queue.vi' into a copy of our OpExitLoop_v0 left the op broken (ExecState 0) although every step reported success. The creator's connector (tools/bench/probe_queue_vis.log) has FOUR error terminals: 9 'error in' and 10 'error out' (terminal REFNUMS for the error terminals of the queue node it creates) and 11 'error in (no error)' / 15 'error out' (the creator VI's own error chain). MY EXPLANATION: wiring 'error out' BY NAME picked index 10 (the refnum output) and connected it to Clear Errors' 'error in (no error)' - a refnum into an error-cluster input = broken wire; the creator's own error out (15) stayed unwired (the census after the build shows wire 534 on terminal 10 and 0 on 15). FIX: wire the creator's own chain by TERMINAL INDEX (connect_terminals on the top-level Nodes[] - valid here, all nodes are top-level): 15 -> Clear Errors, and the 'error out' indicator via connect_ctl from 15; leave 9/10 (the created node's error refnums) unwired - they are optional. ATTACK: (a) agree; (b) are the created node's error terminals (9/10) needed for the queue node to compile in the TARGET VI (an Obtain Queue with unwired error in/out is fine in LabVIEW - correct?); (c) anything about 'element data type' (a terminal ref) - does the created Obtain Queue take the TYPE from that terminal or must a constant be wired into it in the target?

## Answer

(a) **Agree, strongly.** The census is nearly dispositive: wire 534 on terminal 10, none on terminal 15, plus `ExecState 0`, exactly matches a queue-node error-terminal refnum being wired into Clear Errors??error-cluster input. Connecting by label was unsafe because `"error out"` is ambiguous. Using top-level terminal index **15** for the creator VI?셲 error chain is the correct repair.

(b) **No.** The generated Obtain Queue node?셲 error terminals 9/10 are not required for compilation. NI describes `error in` as the standard error input and lists `error out` as an output; neither establishes the queue?셲 type. Leaving them unwired may sacrifice sequencing/error propagation, but it does not inherently break the target VI. [NI Obtain Queue reference](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/obtain-queue.html)

(c) **The element-data-type question is the caveat.** Obtain Queue?셲 queue-refnum type is determined by its **element data type input**; NI explicitly says that input specifies the type stored in the queue, and NI?셲 procedure wires a value/type constant before deriving the typed queue refnum. [NI Obtain Queue reference](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/obtain-queue.html), [NI queue-refnum procedure](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000001DduISAS&l=en-US)

My inference: the creator?셲 ?쐃lement data type??**terminal reference is probably the scripting-time type template**, allowing it to instantiate/adapt the generated Obtain Queue node. If so, you do not additionally wire that creator terminal reference into the target?봧t is not target data. But the resulting target Obtain Queue must still have a concrete element type, either baked into the created node by the creator or established by wiring a constant/control to its target `element data type` input. An untyped/unwired generated node is not safe to assume correct.

So the failed prediction is confirmed for the error-chain wiring, with one independent check remaining: census the generated node?셲 `element data type` terminal and queue-out datatype. If no target wire exists, verify that the queue-out refnum is already specialized to the intended type; otherwise add an intended-type constant. Erdos Miller documents the package as a VI-Scripting code-generation library, but its public overview does not specify this helper?셲 exact terminal-ref contract. [Erdos Miller LV-Scripting](https://github.com/erdosmiller/lv-scripting)

## Sources

(extract from answer)

## What was done with it

Wired the creator's own error out (terminal 15) by index; all four ops built and the functional test passed 7/7 with typed queues (element 1280 dequeued). The created Obtain node's element data type input IS wired by the creator (census: wire 346), answering the reviewer's caveat. Verdict: correct.
