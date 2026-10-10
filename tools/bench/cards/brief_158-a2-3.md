---
card: 158-a2-3
status: current
date: 2026-10-10
---
# Brief 158-a2-3 (assignment 158-2) - OFFLINE MEASUREMENT: why did the P5-2 step-1 scratch fail D / CEN2 / TD / PB after ops 16/17 went through?

Card 158-a2-2 ran ONE scratch: all 17 ops executed, E1 diff 0 at every checkpoint, ops 16/17 took `connect_term_uid`, then the
whole-run gates failed (D new wires 21 vs sim 22; CEN2 Wire 12 / Outer 6 / Inner 10 vs declared 1/1/2; TD unwired (25223,1,InnerTerminal);
PB extra open pairs (376,'cal cluster path'), (376,'file size')). Read `tools/bench/diag_c158_a2_2_facts.md`, then the hypothesis review
`archive/peer/2026-10-10-c158-a2-2-p5s02a-loopface.md` (answer + section 4). **This card MEASURES; it decides nothing and edits nothing.**
No LabVIEW, no tool / recipe / plan / pred / licence / hook edit. New files only: `tools/bench/diag_c158_a2_3_*`.

## Measure (offline, read-only calls into existing functions; a script of inputs and calls, `docs/script-writing.md`)
1. The review's section-4 test, exactly: (1) build the simulated end graph frame-keyed from `tools/bench/sim/ring_p5s02a/step_23_wire.json`
   (`stagekit.pred_end_graph`) and the S1 graph (`stagekit.s1_frame_graph()`); (2) print `vigraph.effective_sources` for #376
   'cal cluster path' and 'file size' on both; (3) put the REAL uids into the simulated state using the op-16/17 bindings in
   `tools/bench/diag_c156_p5s02a_scratch.log` (sim tunnels -44/-49 -> real 31546/31557, sim frames -29/-30 -> real 31506/31517; verify
   these bindings from the log first and quote the lines), rebuild and print again; (4) report whether the tag flips and whether the two PB
   rows appear. Also run the real graph (`diag_c156_p5s02a_scratch.json`, block `real_end_rows`) through the same `effective_sources` call.
2. Wire accounting for D / TD: count the real and simulated end wires by (source terminal, sink terminal) pairs instead of by uid, and
   list the pairs present on one side only (expected by the review: the 24091 dangling end). State the numbers and whether `lost` 12 and
   `new` 21 / 22 reconcile.
3. CEN2: quote the declared census (`plan_ring_p5s02a_pred.json:23-47`) and the measured whole-run census; state whether the declared side
   covers only the Case op, and which gate line (file:line) produces the CEN2 FAIL for a plan whose census is `UNPREDICTED`.
4. The FATE question: the three wires 24091 / 24153 / 24330 were dropped at the op-12 read and the sim kept them; quote which of the
   five wires into #376 'selected path' / 'cal cluster path' / 'file size' etc. exist at the end, real vs sim (pairs, from the json).

## Report `tools/bench/diag_c158_a2_3_facts.md` (<= 45 lines)
Facts only, each as file:line or command + output; one line per test with its yes/no; an `OPEN:` line per unresolved thing. Do NOT write
"the fix is ..." and do NOT propose gate edits: that is the judgement session's. Failure budget 2.
