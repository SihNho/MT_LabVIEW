---
type: peer-review
status: historical
date: 2026-09-13
tags: [peer-review]
disposition: legacy
---

# subvi-call-cost

- **agent:** codex
- **date:** 2026-09-13
- **outcome:** ANSWERED (134s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FACT QUESTION about LabVIEW performance. I need published figures and mechanisms, not opinions, and I will measure on my own rig afterwards - your answer is the cross-check.

CONTEXT: LabVIEW 2026 on Windows, a magnetic-tweezers instrument. A camera feeds a bead-tracking loop. The per-frame budget at 150 Hz is 6.00 ms (measured), the tracking kernel already uses 2.43-2.87 ms of it, and the failure mode is a cliff - exceeding the budget by 0.3 ms halves the processed frame rate exactly. I am about to refactor a large single-loop diagram into several loops and many subVIs, so I must know what a subVI CALL costs before committing to that method.

QUESTIONS:

1. What is the measured per-call overhead of a LabVIEW subVI call versus the same code written inline on the caller's diagram? Give published numbers with sources if they exist (NI docs, NI Week / GDevCon presentations, LAVA or NI forum benchmarks). Order of magnitude matters most: is it nanoseconds, microseconds, or tens of microseconds on a modern desktop?

2. How much of that is removed by the **Inline subVI** option (VI Properties >> Execution >> "Inline subVI into calling VIs")? What are its restrictions - which VIs cannot be inlined?

3. Does **reentrancy** change call cost? Specifically: non-reentrant vs "shared clone reentrant" vs "preallocated clone reentrant" - which is cheapest per call, and does a non-reentrant subVI called from several parallel loops serialise them?

4. **Data copies at the boundary.** If a subVI takes a large array (say a 1280x1024 U8 image, 1.31 MB) as an input and returns it, does LabVIEW copy the buffer, and under what conditions does it avoid the copy? Does it differ for an IMAQ image reference versus a native LabVIEW array? What about "in place" behaviour when the array is passed through and modified?

5. Is there a documented cost to the structures themselves - a Case Structure, a For Loop, a Flat Sequence - as opposed to subVI calls? I measured wrapping a kernel in a Case Structure as free on a CPU path but +1.06 ms on a GPU path, and never explained the difference.

6. Anything else that dominates at the microsecond scale in a tight acquisition loop and that a person refactoring for readability would not expect - e.g. debugging enabled, automatic error handling, front panel loaded in memory, non-inlined express VIs.

Cite sources with URLs. Where you do not have a measured figure, say so explicitly rather than estimating - I would rather record "unknown" than a number I cannot trace.


## Answer

## Bottom line

For a statically linked, already-loaded, simple subVI on a contemporary desktop, the best traceable benchmark I found puts the bare call cost at roughly **0.09 쨉s?봞bout 90 ns**, not tens of microseconds. A published community benchmark measured **86 ns for a normal subVI**, **98 ns for a static LabVIEW-class method**, and **304 ns for dynamic dispatch**; its equivalent Case Structure added approximately **6 ns**. [NI Community benchmark](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Allow-Inlining-and-Preallocation-of-Dynamic-Dispatch-Method-VIs/idi-p/2031778)

NI?셲 older documentation says ?쐔ens of microseconds,??but gives neither test code nor hardware and appears inconsistent with the above modern compiled-code benchmark. [NI Community reproduction of NI?셲 ?쏶ubVI Overhead??help](https://forums.ni.com/t5/LabVIEW/Inline-subvi/td-p/1279078)

Therefore, for your decision:

- A few ordinary static subVI calls per frame are overwhelmingly unlikely to consume 0.3 ms.
- Array copies, synchronization, UI-thread work, allocation, GPU transfers/synchronization, or serialization through a non-reentrant VI are much more credible millisecond-scale risks.
- Benchmark your exact LabVIEW 2026 build, because NI publishes no current guaranteed call-latency figure.

## 1. Published subVI-call figures

The strongest numerical evidence I found is:

| Operation | Published measurement |
|---|---:|
| Normal static subVI | 86 ns |
| Static LVOOP method | 98 ns |
| Dynamic-dispatch LVOOP method | 304 ns |
| Case dispatch added to a normal call | about 6 ns |

These figures come from a user benchmark posted to NI?셲 forum, not an NI specification. [NI Community benchmark](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Allow-Inlining-and-Preallocation-of-Dynamic-Dispatch-Method-VIs/idi-p/2031778)

A recent third-party benchmark reports a comparable result: an increment took about 30 ns inline and about 100 ns through a normal subVI, implying approximately **70 ns call overhead**. It reports approximately 20 ns overhead for subroutine priority and zero measurable extra cost after inlining. This is not an NI source and does not identify the processor or exact LabVIEW version clearly enough to treat it as authoritative. [Published third-party benchmark](https://industrialmonitordirect.com/blogs/knowledgebase/optimizing-labview-vi-execution-speed-on-windows-targets)

The older NI help text says normal call overhead is ?쐎n the order of tens of microseconds.??It also recommends putting a repeated loop inside the subVI or using subroutine priority. The page supplies no benchmark methodology, processor, LabVIEW version, or separation between call setup and data movement. [NI Community copy of NI help](https://forums.ni.com/t5/LabVIEW/Inline-subvi/td-p/1279078), [archived NI Real-Time manual](https://download.ni.com/support/manuals/322154e.pdf)

So the defensible conclusion is:

- **Modern static call, scalar data, warm code:** order of **100 ns**, based on community measurements.
- **Current NI-guaranteed figure:** **unknown**.
- **Calls involving data copies, dynamic dispatch, VI Server, unloaded panels, or allocation:** not represented by that 100 ns figure.

The 7 쨉s result sometimes cited from LAVA is not a bare-call benchmark: the tested subVI processed roughly 20,000 elements. [LAVA discussion](https://lavag.org/topic/13520-inlining-a-subvi-that-uses-the-in-place-memory-structure/)

## 2. Inline subVI

Inlining inserts the subVI?셲 compiled code into the caller, eliminating the runtime call boundary and permitting optimization across that boundary. NI explicitly describes inlining as removing the computer-side subVI/copy overhead. [NI explanation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YNjRCAW&l=en-US)

For an empty or extremely small scalar subVI, the measured removed portion is therefore approximately **the whole 70??0 ns call cost**. For real code, the result can differ because inlining may also change constant folding, dead-code elimination, scheduling, and buffer reuse. NI documents compiler transformations including removal of unreachable Case Structures, dead-code elimination, and loop unrolling. [NI compiler description](https://www.ni.com/en/support/documentation/supplemental/10/ni-labview-compiler--under-the-hood.html)

Published restrictions include:

- No recursion.
- Calls to the VI must be static.
- No automatic error handling inside the inlined VI.
- No debugging support.
- No dialog-box functions.
- The inlined code ignores the subVI?셲 own reentrancy, priority, and preferred-execution-system settings.
- Historically, Property and Invoke Nodes were disallowed; NI reports that some property/invoke inlining support was added in LabVIEW 2019, so the exact LabVIEW 2026 acceptance test is authoritative for a particular node.
- UI-dependent items such as local variables and static front-panel references have historically prevented inlining.

Sources: [NI Community quotation of the restrictions](https://forums.ni.com/t5/LabVIEW/Inline-subvi/m-p/1279098), [NI employee on property/invoke restrictions](https://forums.ni.com/t5/LabVIEW/Why-exactly-can-t-I-inline-this/td-p/3126562), [LabVIEW 2019 change record](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Inlineable-property-nodes-Invoke-nodes-when-apporopriate/idi-p/3127807), [NI employee on local variables and the UI thread](https://forums.ni.com/t5/LabVIEW/Local-Variables-and-INLINING/m-p/2845800).

I did not find a definitive current NI page enumerating every LabVIEW 2026 restriction. The practical check is whether enabling Inline leaves the VI runnable and what the Error List identifies.

## 3. Reentrancy and serialization

NI?셲 documented behavior is unambiguous:

- **Non-reentrant:** one data space; simultaneous calls are serialized. Consequently, if several parallel loops call the same non-reentrant instance, only one call can execute at a time.
- **Shared-clone reentrant:** LabVIEW maintains a clone pool, initially containing one clone, and creates more clones on demand when the pool is exhausted. NI warns that the on-demand creation introduces jitter.
- **Preallocated-clone reentrant:** LabVIEW allocates a dedicated clone for each call site in advance. NI describes this as minimizing call overhead and jitter, at the cost of more memory.

[NI execution-property documentation](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html), [NI parallel-call explanation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000001DkL6CAK&l=en-US)

The correct ranking depends on what ?쐁heapest??means:

- For **parallel deterministic calls**, preallocated clone is NI?셲 documented lowest-overhead/lowest-jitter choice.
- Shared clone may equal it after warm-up when a suitable clone is immediately available, but NI does not publish steady-state timing.
- An uncontended non-reentrant call may require the least memory, but I found no published measurement proving it has the lowest raw per-call latency.
- Under contention, non-reentrant is potentially by far the most expensive because callers wait for the current execution to finish.

Inline VIs have no independent reentrancy behavior: their code becomes part of each caller, and NI says the original reentrancy setting is ignored. [NI Community quotation of NI help](https://forums.ni.com/t5/LabVIEW/Inline-subvi/m-p/1279098)

## 4. Data copies at a subVI boundary

### Native LabVIEW arrays

Passing an array through a subVI does **not inherently copy it**. LabVIEW can reuse the input buffer as the output buffer when dataflow proves the original value is no longer needed. Passing data in and out normally does not by itself force allocation. [NI Community discussion](https://forums.ni.com/t5/LabVIEW/Request-Deallocation/td-p/1941563)

A copy or separate buffer becomes necessary when, for example:

- Another live branch still requires the original value.
- The input and output cannot safely alias.
- The output differs in size or representation.
- The subVI retains the input in state while also returning a separately usable result.
- UI display or front-panel access requires a separate representation.
- An operation is not implemented in place.

NI explains that splitting a wire can require a copy when independent downstream versions are necessary; it does not mean every wire branch immediately copies the buffer. [NI multithreading and memory explanation](https://www.ni.com/en/support/documentation/supplemental/07/multithreaded-features-of-labview-functions-and-drivers.html)

For reliable in-place pass-through:

- Use matching required input/output terminals.
- Put the relevant input/output terminals at the root level of the subVI diagram.
- Return the transformed input through the corresponding output.
- Avoid retaining a second live version in a shift register, feedback node, local variable, indicator, or parallel branch.
- Use the In Place Element Structure where you need to express explicit destructive update semantics.

An NI employee states that root-level terminals and required inputs are necessary for subVI inplaceness. [NI Community, NI employee](https://forums.ni.com/t5/LabVIEW/Inline-subvi-s-and-memory-usage/m-p/2777038)

Use **Tools ??Profile ??Show Buffer Allocations on the caller**. NI documents this tool, but its marks identify potential allocation sites; runtime conditional reuse can make a marked site cheaper than it appears. [NI profiling documentation](https://www.ni.com/en/support/documentation/supplemental/16/investigating-memory-growth-issues-in-labview-code-modules-calle.html), [NI Community explanation](https://forums.ni.com/t5/LabVIEW/Preventing-buffer-allocation-for-subVI-controls/m-p/3202791)

For your 1.31 MB U8 array, the boundary alone need not copy 1.31 MB. If a copy is forced, its measured cost will depend on allocation state and memory hierarchy; I found no trustworthy LabVIEW-specific published timing for that exact size.

### IMAQ image references

An IMAQ image wire is fundamentally different. The LabVIEW value contains a reference/pointer to an IMAQ-managed image structure, not the pixel buffer itself. Passing that reference through a subVI does not copy 1.31 MB of pixels. [NI-IMAQ memory documentation](https://www.ni.com/en/support/documentation/supplemental/18/ni-imaq-memory-allocation.html)

NI also documents that:

- IMAQ buffers are created and reused explicitly.
- An Image Display normally points to the existing image and does not copy it.
- Enabling Snapshot makes a copy.
- For processing VIs with `Image Src`, optional `Image Dst`, and `Image Dst Out`, leaving destination unwired commonly causes the output to refer to the source buffer; wiring a destination selects that buffer instead.

[NI display/reference explanation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019MAKSA2), [NI source/destination behavior](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAovSAG&l=en-US)

The price is reference semantics: parallel operations can race on the same IMAQ buffer. NI explicitly warns that IMAQ images break ordinary value-dataflow expectations and require explicit execution ordering. [NI IMAQ execution-order guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P8khSAC)

## 5. Case, For Loop, and Flat Sequence costs

I found no current NI table giving fixed CPU costs for these structures.

What is published:

- The community benchmark above measured approximately **6 ns** for Case dispatch in its specific test. [NI Community benchmark](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Allow-Inlining-and-Preallocation-of-Dynamic-Dispatch-Method-VIs/idi-p/2031778)
- NI confirms loops have overhead and that the compiler can reduce it by unrolling.
- NI confirms an unreachable Case Structure can be removed entirely during compilation.
- A Flat Sequence expresses dependency/order; NI publishes no standalone timing for an empty frame.

[NI compiler documentation](https://www.ni.com/en/support/documentation/supplemental/10/ni-labview-compiler--under-the-hood.html), [NI structures documentation](https://www.ni.com/docs/ar-SO/bundle/labview/page/loops-and-other-structures.html)

Thus, your CPU result?봀ase wrapper effectively free?봧s plausible. A genuine **+1.06 ms GPU-path difference cannot credibly be attributed to CPU Case dispatch**. That magnitude more likely indicates the wrapper changed something about GPU command scheduling, synchronization, transfer, allocation, buffer lifetime, or compiler optimization. That is an inference, not a documented diagnosis. I found no NI source documenting a millisecond Case Structure penalty on a GPU path.

A cheap discriminating test is to benchmark separately:

1. Empty Case around only the GPU call.
2. Case around GPU input preparation but not the call.
3. Case around result retrieval only.
4. Always-true Case versus a runtime selector.
5. Warm iterations versus the first iteration.
6. Buffer-allocation display before and after.
7. GPU work followed by an explicit synchronization/result-read at the same location in both variants.

If only the explicit result-read moves by approximately 1 ms, the original measurement was probably charging asynchronous GPU completion to a different diagram location rather than measuring Case dispatch itself.

## 6. Other unexpected microsecond-to-millisecond costs

The most important suspects are:

- **Debugging enabled.** NI says disabling Allow Debugging reduces memory and improves performance slightly; it publishes no general timing. [NI execution properties](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html)
- **Front-panel indicators, graphs, and property/invoke nodes.** These can force UI-thread work and redraw invalidation. Overlapping controls can make redraw up to 100 times more expensive, according to NI. [NI front-panel performance guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kHjFSAU&l=en-US)
- **Opening a subVI front panel.** Large controls/indicators may require display copies; closed, unused panels are materially safer for performance. [NI Community buffer-allocation discussion](https://forums.ni.com/t5/LabVIEW/Preventing-buffer-allocation-for-subVI-controls/m-p/3202791)
- **Dynamic dispatch.** The cited benchmark measured 304 ns versus 86 ns for a static call. [NI Community benchmark](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Allow-Inlining-and-Preallocation-of-Dynamic-Dispatch-Method-VIs/idi-p/2031778)
- **Shared-clone creation.** NI explicitly identifies on-demand clone creation as a source of jitter. [NI execution properties](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html)
- **Non-reentrant dependencies anywhere below the parallel branch.** A shared non-reentrant analysis or driver VI can serialize otherwise parallel callers. [NI multithreading guidance](https://www.ni.com/en/support/documentation/supplemental/07/multithreaded-features-of-labview-functions-and-drivers.html)
- **Array allocation, resize, conversion, and UI copies.** These can dwarf the call instruction, particularly with megapixel arrays. [NI memory-profiling guidance](https://www.ni.com/en/support/documentation/supplemental/16/investigating-memory-growth-issues-in-labview-code-modules-calle.html)
- **Automatic error handling.** It can suspend execution and open an error dialog in the development environment; the Run-Time Engine does not support it. I found no published normal-path timing. [NI execution properties](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html)
- **Express VIs:** I found no defensible generic ?쏣xpress VI overhead??figure. Their generated implementation must be profiled individually; ?쏣xpress??alone does not define a runtime mechanism.

My cross-check verdict is that **static subVI modularization itself is a nanosecond-scale concern on a modern desktop**. For a 6 ms frame budget, protect against non-reentrant serialization and megabyte-buffer copies first; inline only very small, very frequently called leaf VIs after measuring.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
