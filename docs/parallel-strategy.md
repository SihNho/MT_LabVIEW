---
type: reference
status: current
date: 2026-09-02
tags: [docs]
---

# Parallelization strategy: loop-level now, graph-level only on evidence (2026-09-01)

Peer-checked against NI documentation: archive/peer/2026-09-01-loop-vs-graph-parallelism-labview.md.

**What we did is loop-level data parallelism**: the per-bead For loop with P=4 and auto-indexed
tunnels, one reentrant kernel per bead (`PARALLEL_kernel_v3.vi`). LabVIEW's compiler already
exploits graph-level parallelism between independent dataflow branches automatically (the
"clumper" schedules independent clumps on its multithreaded execution system); what it does NOT
do is overlap iterations of one loop, which is exactly the gap P=4 fills.

**The remaining graph-level lever is pipelining across frames** (producer/consumer with queues or
channel wires): acquisition of frame k+1 concurrent with analysis of k and file-write of k-1.
Initiation interval drops from A+B+W toward max(A,B,W); end-to-end latency does not drop and
usually rises.

**Decision rule (measure first, never restructure first):**
1. If worst-case A+B+W (+ margin, incl. I/O jitter) < camera period T_f, the camera is the
   bottleneck; pipelining cannot raise the frame rate and only adds latency, buffers, shutdown/
   error complexity and IMAQ image-lifetime hazards. Keep the single loop.
2. If occasional file-write stalls cost frames although the mean fits, split ONLY the write into
   a bounded producer/consumer queue with an explicit full-queue policy (determinism / fault
   containment, not throughput).
3. If analysis itself exceeds T_f even with P = bead count, the scaling path is the GPU backend
   (standing decision), not deeper pipelining; only a smaller B lowers max(A,B,W).

IMAQ hazard for any pipeline: an image wire is a pointer, so queuing a reference is not a
snapshot; a pipeline needs an ownership-controlled, preallocated image pool (copy per in-flight
frame, return after the last consumer). That cost is the bulk of a pipeline's price here.

Rule-1a note: pipelining is a scheduling change (allowed in principle) but it restructures the
main VI's loop, enlarging the equivalence surface that must be proven numerically.
