---
card: 163-a2-2
status: current
date: 2026-10-10
---
# Plan under review: RING P5-2 step 3 (card 163-a2-2) - the ONE scratch of plan_ring_p5s02c, offline-checked, not launched

Design: `docs/d1/ring-p5b.md` PD396 (:323-362), PD374(b) (record counter SR of loop 1.7). Base = the step-2 result
`claudeDev\D1_ring_p5s02b_20261010_105511.vi` f9ae7751 (graph `tools/bench/graph_ring_p5s02b_20261010_111905.json` 431cfd83).
Plan `tools/bench/plan_ring_p5s02c.json` 930699ec (group I alone, A41..A52, 8 ops, checkpoints [0,1,2,4,5,7,8]; PD396(c): I+J > 675 so J
becomes p5s02d), pred `plan_ring_p5s02c_pred.json` fc908036, licence c8fdf33a, predicted Error List
`errorlist_predicted_D1_ring_p5s02c_end.json` 373e0bf4 (53 standing, cleared 0, raised 0, UNPREDICTED A45 t_ci7 / A49 t_co7, upper 55).
Recipes `tools/recipes/stage_d1_ring_p5s02c.py` 6d1d5786 and `_scratch.py` a517557d (pair shape of the p5s02b pair, shared stagekit calls).
Offline gates passed (`tools/bench/diag_c163_a1_4_facts.md`): dry PASS-UNVERIFIED (CEN2 only) both recipes, prerun 16/0 (X10 658.3 <= 675),
`--scratch-required` rc 3 (CENSUS-UNPREDICTED); check_launch ALLOW (`tools/bench/diag_c163_a2_1_facts.md`).

## The 12 actions of group I (plan_ring_p5s02c.json:134-280)
- `sr_c7` add_shift_reg on While loop #23041 (body 23405) as CS7 - the 1.7 record counter (PD374(b)).
- `c_k07` create DigitalNumericConstant on diagram 686 by const_donor `claudeDev\DonorSRInit_v0.vi` uid 248 (as P5-1 c_k0); `w_k07` -> CS7L outer.
- `c_inc7` create Function Increment on case frame 31506 by donor `$work` uid 1978 (as P5-1 c_inc).
- `t_ci7` in-tunnel on case 31308 (frame 31506); `w_ci7_in` CS7L.inner -> TC7.outer; `w_ci7_inc` TC7.inner -> IN7.x;
  `w_c7_fi` TC7.inner (frame 31506) -> #376 'frame index' (term uid 5763).
- `t_co7` out-tunnel on case 31308; `w_inc7_co` IN7.x+1 -> TD7.inner; `w_co7_r` TD7.outer -> CS7R.inner;
  `w_c7_pass` TC7.inner -> TD7.inner in frame 31517 (pass-through where nothing was dequeued).
- Compiled ops: add_sr, create, connect, create, connect_term_uid (register_end_case_border, TC7), case_frame_wire, connect_term_uid (TD7),
  case_frame_wire. No delete_wire / delete_object in this step.

## What the gate measured (guard_cycle, card 163-a2-1, `tools/bench/diag_c163_a2_1_facts.md`)
- stage_prerun.proven_pattern(scratch recipe) = False: only `stage_d1_ring_p5s02a_scratch.py` ran this signature clean (needs >= 2);
  signature ops add_shift_reg / create / tunnel / wire, create classes DigitalNumericConstant / Function. priorart_diff.scope = None.

## Questions for prior art
(a) Has this project already built the same counter (add_shift_reg + const_donor init 0 + Increment by `$work` donor + in/out case tunnels
    + frame pass wire) - P5-1 (`stage_d1_ring_p5s01a/b`, `diag_c154_p5s01a_scratch.log`, `diag_c155_p5s01b_scratch.log`) or p5s02a - and did
    any of those runs leave a loose end, an auto-dropped tunnel or a renumbered register that this plan does not predict?
(b) Is a `$work` donor copy of Increment uid 1978 into a case frame of an inherited case (31308) recorded anywhere, and with what result?
(c) Has `register_end_case_border` onto a PLAN-MADE register whose tunnels are made in the same step been run (ring-p5b.md:142-143)?
(d) Does an existing shared function or adopted step already wire a node's 'frame index' (#376) from a counter, so this would duplicate it?
