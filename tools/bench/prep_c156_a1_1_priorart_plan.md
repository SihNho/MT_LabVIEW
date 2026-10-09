---
card: 156-a1-1
status: current
date: 2026-10-09
---
# Plan under review: RING P5-2 step 1 RE-MADE (card 156-a1-1) - offline plan, not launched

Design: `docs/d1/ring-p5.md` PD374(b)(c)(d), PD376(d), PD379(a)-(e). P5-1 is adopted (`claudeDev\D1_ring_p5s01_20261009_124542.vi` 7f2582ae, real
graph `tools/bench/graph_ring_p5s01_20261009_125622.json` 6716c499). This re-makes cycle 155's P5-2 plan (`tools/bench/plan_ring_p5s02.json`
285cb59a, reviewed in `archive/peer/2026-10-09-priorart-priorart-c155-a4-1-p5s02.md`, verdict novel) with PD379's changes. Maker
`tools/bench/prep_c156_a1_1_mk.py` (log `tools/bench/prep_c156_a1_1_mk2.log`), all-groups plan `tools/bench/plan_ring_p5s02r_all.json` (60 actions,
groups A..J; K3/K4 GAP), cut at a GROUP boundary with MAIN <= 675.

Step 1 (`tools/bench/plan_ring_p5s02a.json`, actions 1..23 / 17 ops, MAIN 672.1 at start 603.4) = groups A B C D E F1 F2 - the SAME rows as
cycle 155's step 1 actions 1..23 (refnum SR on 1.7 + Dequeue + Release on 686; I32 100 timeout; Case on 'timed out?'; move_in #376 / #3052 / #3453
into its False frame + 2 re-wires; Dequeue element -> #376 t5; in-tunnels #24357 / #24361 inner faces -> case tunnels -> #376). Cycle 155's step 1
also held F3 and G's first tunnel group (actions 24..29, MAIN 680.0, splitting G); PD379(c) forbids the split and lowers the limit to 675.

Changes vs cycle 155 (all in groups OUTSIDE step 1): J = Equal?(counter after the iteration, local 'records final') -> loop 1.7 cond directly (no
'>= 0', no And; loop #23041 is Stop if True, `tools/bench/diag_c138_5_facts.md:37-38`); K3/K4 = new SRs for #376 t3/t4 with the pass wire written as
the case in-tunnel's one group out-wire - refused by stagesim (`tools/stagesim.py:1536`, GAP, not in any step).

Prior-art finding A4 of the 155 review (cycles 97/98: `move_into_frame` into case frames left termless nodes and loose-end wires,
`docs/d1-loop12-17-split-plan.md:1504-1509,1531-1534`) is carried: the pred `tools/bench/plan_ring_p5s02a_pred.json` lists the three move_in ops
(#376 / #3052 / #3453, ops 10-12) as E1 checkpoints with step files; the scratch run quotes graph == sim after each. A3 needs no action (PD379(e)).

NEW vs earlier launches: `move_in` into a frame of a case this plan creates; Dequeue / Release Queue by the `primitive` route (DonorQueue_v0);
case tunnel groups whose outside source is a BASE loop tunnel's inner face. Offline: pass A + REALSIM 0 PROVISIONAL, route check PASS, X8 / X17 clean,
X11 CLEAN. Files: recipe `tools/recipes/stage_d1_ring_p5s02a.py`, scratch `tools/recipes/stage_d1_ring_p5s02a_scratch.py`, pred / licence
`tools/bench/plan_ring_p5s02a_pred.json` / `_licence.json`.

Question for prior art: has this project already built or measured (a) moving a SubVI into a frame of a newly created Case inside a While body, and
(b) a case in-tunnel whose only use is a pass wire to an out-tunnel in another frame, and what did those attempts leave behind?
