---
card: 155-a4-1
status: current
date: 2026-10-09
---
# Plan under review: RING P5-2 step 1 (card 155-a4-1) - offline plan, not launched

Design: `docs/d1/ring-p5.md` PD374(b)(c)(d), PD376(d), PD378(c). P5-1 is adopted (`claudeDev\D1_ring_p5s01_20261009_124542.vi` 7f2582ae, real
graph `tools/bench/graph_ring_p5s01_20261009_125622.json` 6716c499). P5-2 = the loop 1.7 side of the results queue. Maker
`tools/bench/prep_c155_a4_1_mk.py` (log `tools/bench/prep_c155_a4_1_mk.log`) wrote the whole P5-2 input plan (`tools/bench/plan_ring_p5s02_all.json`,
62 actions, groups A..J) after a route census, and cut it by X10 (<= 680) and 40 actions: step 1 = actions 1..29 / ops 1..19 (MAIN 680.0 at start
603.4); step 2 = actions 30..62 (later card).

Step 1 content (`tools/bench/plan_ring_p5s02.json`):
- A: a NEW shift register on loop 1.7 #23041 (body #23405, parent 686) fed by a 2nd branch of Obtain Queue #31258 'queue out'; Dequeue Element
  (DonorQueue_v0 #45, `primitive` route) on L.inner, its 'queue out' -> R.inner (wire_sr LeftIn / RightIn); Release Queue (#46) on 686 fed by R.outer.
- B: an I32 100 constant on Dequeue 'timeout in ms (-1)' (const_on_term).
- C: a NEW Case on Dequeue 'timed out?' (case_wired, frames False/True; False = an element was dequeued).
- D: `move_in` of #376 (save trace SubVI), #3052 (its refnum constant) and #3453 ('file progress' indicator) into the Case's False frame, then
  the two same-frame wires #3052 -> #376 'saved file refnum' and #376 'file progress' -> #3453 (connect / ctlsink).
- E: Dequeue 'element' -> case input tunnel -> #376 'current frame data array in'.
- F1-F3: the loop in-tunnels #24357 / #24361 / #25223 (their INNER faces, base) -> case input tunnels -> #376 'cal cluster path' / 'file size' /
  'selected path'.
- G (first half): LSR #24133 inner (base) -> case input tunnel -> #376 'error in'.

NEW here (no earlier launch): `move_in` into a frame of a case this plan creates (earlier move_in rows only targeted loop bodies, e.g.
`tools/bench/plan_l7_split.json` action 1 moved #376 into #23405); a case tunnel group whose OUTSIDE source is a BASE loop tunnel's inner face or a
BASE left shift register's inner face (compile kind `tunnel`, executor route `cfw`); Dequeue / Release Queue created by the `primitive` route
(DonorQueue_v0, X17 entries `tools/stage_prerun.py:2809-2813`). Offline: pass A + REALSIM 0 PROVISIONAL, route check PASS, X8 / X17 clean, X11
CLEAN. Files: plan `tools/bench/plan_ring_p5s02.json`, pred `_pred.json`, licence `_licence.json`, recipes
`tools/recipes/stage_d1_ring_p5s02.py` + `_scratch.py` (the stagekit.RingSession template shape). The next card runs the scratch recipe once on a
byte copy of the P5-1 file.
