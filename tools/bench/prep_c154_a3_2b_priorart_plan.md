---
card: 154-a3-2b
status: current
date: 2026-10-09
---
# Plan under review: RING P5-1a (card 154-a3-2b) - offline plan, not launched

Design: `docs/d1/ring-p5.md` PD374(a)(c)(e), PD375(a), PD376(a) (form S). Full fragment P5-1 (32 actions / 22 ops) was planned by card
154-a3-2 (`tools/bench/plan_ring_p5s01.json`) and refused by X10 (MAIN 701.0 > 680, `tools/bench/diag_c154_a3_2_facts.md`). PD374(e) lets the
plan maker cut: P5-1a = the longest op prefix with X10 MAIN <= 680 = ops 1..14 = actions 1..20 (MAIN 677.3), `tools/bench/prep_c154_a3_2b_mk.log`.

P5-1a content (rows copied unchanged from `tools/bench/plan_ring_p5s01_in.json`, census `tools/bench/p5_route_census.md` rows S1-S3, 4-15):
- on frame 686: a 1-D DBL array constant (DonorQueue_v0 #52) + Obtain Queue (DonorQueue_v0 #108) by the `primitive` route (gscript.create_primitive_nested); const -> 'element data type';
- `records final (1.2 to 1.7)` I32 indicator + a -1 constant on FS frame #4866;
- a NEW Case structure in loop 1.2's body (#23166) selected by RingSeqCheck #29724 'valid'; Enqueue Element (#44 donor) in its True frame; `#2626` 'appended array' -> case tunnel -> 'element';
- a NEW enqueue-count shift register on loop #10170 (init 0 constant), L.inner -> case tunnel -> Increment -> case tunnel -> R.inner (connect_term_uid route).
Left for P5-1b (actions 21..32, not planned now): False-frame pass-through of the count, the local write of the final count after 1.2, the refnum
shift register into 1.2 and its two case tunnels, the refnum False pass-through.

New structure class here: queue primitives created by the `primitive` route from a donor, a Case on 'valid' inside loop 1.2, a shift register
threaded through case tunnels. Files: plan `tools/bench/plan_ring_p5s01a.json`, pred `tools/bench/plan_ring_p5s01a_pred.json`, licence
`tools/bench/plan_ring_p5s01a_licence.json`, recipes `tools/recipes/stage_d1_ring_p5s01a.py` (+ `_scratch.py`, copies of the s09 pair
`tools/recipes/stage_d1_ring_p4_s09v18.py`), maker `tools/bench/prep_c154_a3_2b_mk.py`. Offline only: stagesim pass A + REALSIM 0 PROVISIONAL,
dry + prerun PASS. The next card launches the scratch recipe once on a byte copy of `claudeDev\D1_ring_p4s09_20261009_060515.vi`.
