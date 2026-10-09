---
card: 156-a3-1
status: current
date: 2026-10-09
---
# Brief 156-a3-1 - OFFLINE measurement: why did the P5-2 step-1 scratch stop at op 16 (inner face #24360)? and which ops does the compiled plan check with E1?

Card 156-a2-2 ran the ONE step-1 scratch: ops 1-15 passed with E1 diff 0, op 16 (`tunnel` t_in1, acts 18-20, src {uid 24357, term_uid 24360})
stopped with `ADDRESS: #24360 is an INNER face of LoopTunnel #24357` (`tools/bench/diag_c156_p5s02a_scratch.log:254-255`, raised at
`tools/stagexec.py:1784-1787`). Read `tools/bench/diag_c156_a2_2_facts.md` first, then the peer file
`archive/peer/2026-10-09-c156-a2-2-p5s02a-innerface.md` (its section 4 is the test to run). No LabVIEW, no hardware, no GUI.

Two explanations are open and this card MEASURES, it does not choose:
- (E-A) the executor has no route for an inner LoopTunnel face at all (the offline gates accepted the plan, the executor cannot run it);
- (E-B) the sim keeps wire 24330 on #24360 after `mv_376` (fate "ambiguous", `sim/ring_p5s02a/summary.json` allow_either), the route check chose
  `cfw` on that, and LabVIEW dropped the wire, so the live terminal was unwired and `connect_route` fell to the triple route.

## Measurements (facts only)
1. Run the peer's test with stagexec 25a1494c UNCHANGED, by import in a new `tools/bench/diag_c156_a3_1_route.py`: load
   `tools/bench/sim/ring_p5s02a/step_15_tunnel.json` and call `stagexec.connect_route` for the op-16 wire (source #24360, sink #376 t5760 / the
   plan's action 19 and 20 endpoints; take the exact call shape from `stagexec.py:1489-1490` and `:2953` / `:3783`) (i) as stored and (ii) with
   only #24360's `wire_uid` set to 0. Quote the route returned or the exact stop text for each. Do the same for op 17 (source #24367).
2. From the scratch log and the resume record `tools/bench/resume/resume_plan_ring_p5s02a_20261009_153334.json`, quote every line that shows the
   LIVE state of #24360 / wire 24330 / #24357 after op 12 (mv_376) and at the op-16 read. If none exists, say "not logged" and name the logger
   function that would have to write it (file:line).
3. From the sim step files `step_09_create.json`, `step_10_move_in.json`, `step_15_tunnel.json`: what `stagesim` does with a wire whose
   sink moves into a Case (rule + file:line that sets fate "ambiguous"), which rows are in `allow_either`, and how `stagexec.py:2533-2534`
   uses it at an E1 checkpoint. Then list for EVERY plan op after a `move_in` whose source is in `allow_either`: op number, source uid, the
   route `connect_route` gives with the wire present and with it absent (offline, as in item 1).
4. Why ops 10, 11, 12 (`move_in`) are not E1 checkpoints: quote the rule that picks checkpoints (L1 compiled list ops 1,3,6,8,9,15,16,17,
   `diag_c156_p5s02a_scratch.log:49,55`; the code that builds it, file:line) and whether a recipe/plan field (not a tool edit) makes a
   `move_in` a checkpoint. Quote how the 155/154 plans (P5-1) checked their move ops.
5. Precedent: any earlier recorded LabVIEW run in which a node with a wired source moved into a Case/loop: did LabVIEW keep or drop the wire?
   Search `tools/bench/*facts.md` and `archive/peer/` by targeted grep only; quote file:line or "no precedent found" with the grep used.

## Rules
Write only `tools/bench/diag_c156_a3_1*` and `tools/bench/prep_c156_a3_1*`. No edit to any plan, recipe, pred, licence, stagexec, stagesim,
stagekit, stage_prerun, hooks, memory_model. Do not open or delete the work copy `D1_ring_p5s02a_20261009_152721.vi`. Shared helpers: call, do
not copy (`docs/script-writing.md`). No peer dispatch (the review exists). Failure budget 2.

## Report `tools/bench/diag_c156_a3_1_facts.md` (<= 45 lines)
The numbers and quotes above, tagged per measurement 1-5. Facts only. End with `OPEN:` lines (what the data leaves undecided). Do NOT propose
or apply a fix: the decision which fix (route both outcomes, per-terminal outcome record, re-route from the outer face, checkpoint list) is made
after this report.
