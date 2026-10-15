---
type: decision
kind: topic
status: current
date: 2026-10-15
parent: docs/d1/INDEX.md
tags: [d1, performance, loop-1.2, 150hz, bottleneck, gpu, pre-decided]
---

# Loop 1.2 performance at 150 Hz — where the time goes (from PD416)

416. **(chat ingest, 2026-10-15 — lean tasks bn150 and bn12rest; reports `V6_lean/tools/bench/lean_bench/lean_report_bn150.md`,
     `lean_report_bn12rest_fail1.md` (+ the retry in progress); measurement only, nothing fixed)**
     USER-RULES: U1 (observers are callee swaps of small subVI copies; the big VI is not edited; no computation changed).
     User 2026-10-15: "프레임레이트 측정 및 병렬화가 핵심이잖아"; "결국 여기서 GPU 활용 필요성이 다시 보이는거네".
     - **(a) Loop 1.7 (saving) never limits:** `save trace.vi` 1-2 us per call (max 33 us), results-queue depth max 1.
     - **(b) Loop 1.2 sets the 150 Hz ceiling:** ~9.4 ms per iteration measured with a 0.17 ms in-memory observer (frame
       period 6.75 ms at 150 Hz, 11.1 ms at 90 Hz - which is why B keeps up at 90 Hz and not at 150 Hz).
     - **(c) Largest single part: the per-pick Median Filter #29009 inside For #1359 = 4.13 ms per iteration (0.29 ms per
       pick x 14)**, ~44 % of 9.4 ms, ~10x the other Median Filter #30306 (0.43 ms). Tracking #5058 = 0.43-0.54 ms on a
       bead-less bench (~5 %); Magnet2Force + filter design < 0.02 ms. Untimed remainder ~4 ms: FIR #28233 (per pick, same
       history - NOT yet timed), UI property node #17289, the pick loop with its 1 ms Wait #11081.
     - **(d) What follows (findings, not decisions):** without #29009's time, 1.2 would be ~5.3 ms < 6.75 ms. U1 forbids
       changing the filter (window / input) - only SCHEDULING may change: run the For #1359 group (Force + filter design +
       median + FIR) off loop 1.2's per-frame path, with the same inputs and outputs, IF what reads its outputs allows it.
       That is the interface-contract step (INDEX "after P6"): who reads For #1359's outputs, when (display only, or the
       3-state clamp's control path?). With 15 real beads tracking grows by a linear estimate of ~6 ms (0.41 ms per bead, not
       measured) - then the GPU kernel (`docs/gpu-backend.md`: 1.1-2.1 ms for 5 beads) matters too; on the bead-less bench it
       would change nothing.
     - **(e) Open (task bn12rest retry, running 2026-10-15 14:09):** time FIR #28233 with exactly 6 swaps; read #29009's input
       length per pick and whether it GROWS with run time (a growing history would slow long experiments); why For #1359 runs
       14 times for 15 picks.
