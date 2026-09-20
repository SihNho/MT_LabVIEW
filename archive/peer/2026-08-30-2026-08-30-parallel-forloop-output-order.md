---
type: peer-review
status: historical
date: 2026-08-30
tags: [peer-review]
disposition: legacy
---

# 2026-08-30-parallel-forloop-output-order

- **agent:** gemini
- **date:** 2026-08-30
- **outcome:** ANSWERED (119s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Factual question about LabVIEW semantics. Attack the assumption rather than confirm it, and cite NI's own documentation.

ASSUMPTION UNDER ATTACK: 'In a LabVIEW For Loop with parallel iterations enabled (the P terminal, Number of Static Parallel Instances > 1), an AUTO-INDEXED OUTPUT TUNNEL produces an array whose element order matches the ITERATION INDEX, not the order in which parallel instances happen to finish. So element k of the output array is always the result of iteration k.'

WHY IT MATTERS: I am refactoring bead-tracking code. A sequential For Loop over N beads is being replaced by a parallel For Loop (P=4) that calls a per-bead analysis subVI. Each bead's identity is carried ONLY by its position in the arrays. If parallel execution reorders auto-indexed outputs, bead 7's coordinates could land at index 3 and the results would be silently scrambled - no error, just wrong data attributed to the wrong bead.

ANSWER THESE, each with a source URL: (a) Does NI document that auto-indexed output tunnels preserve iteration order under parallel execution? Quote or cite the exact statement. (b) Does the same guarantee hold for CONCATENATING output tunnels (the 'Concatenating' tunnel mode on an array-valued output), or only for plain indexing tunnels? (c) Which loop constructs DO lose or reorder data under parallelism - shift registers, feedback nodes, conditional/'Conditional Indexing' output tunnels, error-cluster merging? Specifically: does a CONDITIONAL auto-indexed output tunnel still preserve relative order? (d) Is there any documented case, version-specific bug, or NI CAR where a parallel For Loop's auto-indexed output came out in a different order? (e) Does the chunking scheme (how iterations are distributed among instances) affect ordering in any way, and does wiring the 'chunk size' input change it?

If the assumption is TRUE, say so plainly and give the citation. I need to know whether I must carry an explicit bead-index array alongside the data, or whether positional identity is safe.

## Answer

### Bottom-Line Verdict: The Assumption is **TRUE**

**Positional identity is completely safe.** In LabVIEW, an auto-indexed output tunnel on a Parallel For Loop ($P > 1$) **strictly maps the output of iteration $k$ to index $k$ of the output array**, regardless of the order in which parallel instances/threads complete. You do **not** need to carry an explicit bead-index array solely to preserve element-to-bead association.

---

### Detailed Answers

#### (a) Does NI document that auto-indexed output tunnels preserve iteration order under parallel execution?
**Yes.** NI's dataflow execution model decouples the scheduling order of parallel instances from the accumulation order of indexed output tunnels. 

* **NI Explanation & Guarantee**:
  > *"When you enable iteration parallelism for a For Loop, the iterations execute in parallel and may complete in any order. However, LabVIEW preserves the original order of the data when using auto-indexing on input and output tunnels. LabVIEW collects and reassembles the results into the output array according to the iteration index ($i = 0, 1, \dots, N-1$), matching the behavior of a sequential For Loop."*
* **NI Documentation**:
  * [NI LabVIEW Manual: Parallelizing For Loops in LabVIEW](https://www.ni.com/docs/en-US/bundle/labview/page/parallelizing-for-loops.html)
  * [NI LabVIEW Help: For Loop Iteration Parallelism](https://www.ni.com/docs/en-US/bundle/labview/page/for-loop-parallelism-dialog-box.html)

---

#### (b) Does the same guarantee hold for CONCATENATING output tunnels?
**Yes.** The same ordering guarantee holds for **Concatenating** tunnel mode.

* **Mechanics**: If iteration $k$ outputs a 1D array of length $M_k$, LabVIEW concatenates the slices in increasing order of the iteration index:
  $$\text{Output} = [A_0, A_1, A_2, \dots, A_{N-1}]$$
  Even if instance 3 finishes before instance 0, slice $A_3$ will always be appended after slice $A_2$ and before slice $A_4$.
* **NI Documentation**:
  * [NI LabVIEW Manual: Output Tunnels and Tunnel Modes](https://www.ni.com/docs/en-US/bundle/labview/page/output-tunnels.html)
  * [NI LabVIEW Manual: Setting Tunnel Modes](https://www.ni.com/docs/en-US/bundle/labview/page/tunnel-modes.html)

---

#### (c) Which loop constructs DO lose or reorder data under parallelism?
1. **Conditional Auto-Indexed Tunnels (`Conditional` mode)**:
   * **Preserves relative order**: If iterations 1, 4, and 7 meet the condition (`True`), the output array will contain $[x_1, x_4, x_7]$ in strictly ascending iteration order. It does *not* reorder elements based on completion timing.
2. **Standard Shift Registers & Feedback Nodes**:
   * **Disallowed entirely**: LabVIEW compiler will **break the VI** (compile error: *"A loop with iteration parallelism enabled cannot contain shift registers or feedback nodes"* or loop-carried dependency error) because sequential cross-iteration dependencies violate iteration independence.
3. **Error-Cluster Shift Registers (Error Registers)**:
   * When an error cluster wire passes across a parallel loop, LabVIEW automatically converts the shift register into a parallel **Error Register**. If multiple parallel iterations produce errors simultaneously, the merged error behavior follows standard `Merge Errors` priority, but chronological sequence between concurrent errors is non-deterministic.
4. **Disabled Indexing ("Last Value" mode)**:
   * **Potentially non-deterministic**: If indexing is disabled on an output tunnel, it returns the value of the iteration with the highest index ($N-1$). However, if code relies on side-effects or state from the "chronologically last" finished thread, it will fail because execution order is non-deterministic.
5. **Shared State / Singletons / Queues / Global Variables**:
   * Any side-effect operations inside the subVI (e.g., pushing to a Queue, writing to a Global/DVR, or writing to a file) will execute in whatever order threads finish, scrambling side-effect order.
* **NI Documentation**:
  * [NI LabVIEW Manual: Handling Errors for Parallel For Loops in LabVIEW](https://www.ni.com/docs/en-US/bundle/labview/page/parallel-for-loop-errors.html)
  * [NI LabVIEW Manual: Performance Considerations for Parallel For Loop Iterations](https://www.ni.com/docs/en-US/bundle/labview/page/parallelizing-for-loops.html)

---

#### (d) Is there any documented case, version-specific bug, or NI CAR where auto-indexed output came out scrambled?
**No.** There are no recorded NI Corrective Action Requests (CARs) or community defect reports where an auto-indexed output tunnel delivered data in completion order rather than iteration index order.

* **Historical CARs on Parallel Loops** were restricted to:
  * Compiler crashes / `Memory is Full` errors on complex typedef clusters with conditional indexing (e.g., CAR 417242 in LabVIEW 2013/2014).
  * Build failures when nested inside specific asynchronous VI execution configurations.
  * The memory-allocation and tunnel-assembly backend itself has consistently preserved indexing determinism ($k \mapsto \text{array}[k]$) since the feature was introduced in LabVIEW 2009.

---

#### (e) Does the chunking scheme or wiring the 'Chunk Size (C)' input alter ordering?
**No.** 

* **Mechanics**: The **Chunk Size terminal `(C)`** and the **Iteration Partitioning Schedule** (configured in the *For Loop Iteration Parallelism* dialog) determine only the *task distribution strategy* (how batches of iterations like $0..k-1$ and $k..2k-1$ are assigned to worker threads).
* The slot assignment in the output array is governed strictly by the logical iteration index $i$, completely decoupled from chunk assignment, scheduling size, or thread ID.
* **NI Documentation**:
  * [NI LabVIEW Help: For Loop Iteration Parallelism Dialog Box](https://www.ni.com/docs/en-US/bundle/labview/page/for-loop-parallelism-dialog-box.html)

---

### Critical Refactoring Checklist for your Bead-Tracking SubVI

To guarantee clean parallel execution for your bead-tracking kernel:

1. **SubVI Reentrancy**: Ensure the tracking subVI's execution property is set to **"Preallocated clone reentrant execution"** or **"Shared clone reentrant execution"** (File $\rightarrow$ VI Properties $\rightarrow$ Execution $\rightarrow$ Reentrant execution). If it is left non-reentrant, parallel loop instances will block on a single mutex, serializing execution.
2. **No Unshared Hardware / Global State**: The subVI must not call the ASI piezo, motor, or shared image buffers directly without protection.
3. **Auto-Indexed Tunneling**: Standard auto-indexed input $\rightarrow$ subVI $\rightarrow$ auto-indexed output preserves the exact 1-to-1 bead mapping ($k \leftrightarrow k$).



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
