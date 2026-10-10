---
card: 164-a2-3
status: current
date: 2026-10-10
---
# Plan under review: RING P5-2 step 4 (card 164-a2-3) - recipe pair of plan_ring_p5s02d, offline-checked, NOT launched

Design: `docs/d1/ring-p5c.md` PD397(d), PD398; PD374(c)/(d), PD379(a)/(b) (1.7 stop on the published counter; SR for t3). Base = the step-3
result `claudeDev\D1_ring_p5s02c_20261010_125755.vi` 564d8cbe (graph `tools/bench/graph_ring_p5s02c_20261010_131658.json` 3d5196ab).
Plan `tools/bench/plan_ring_p5s02d.json` 872822f3 (groups J + K3, A53..A69, 17 actions, 13 ops, checkpoints [0,1,4,5,9,10,12,13], MAIN 642.5
<= 675; facts `tools/bench/diag_c164_a2_2_facts.md`). Pred `plan_ring_p5s02d_pred.json`, licence `plan_ring_p5s02d_licence.json` (0 renames),
predicted Error List `errorlist_predicted_D1_ring_p5s02d_end.json` (53 standing, cleared 0, raised 0, UNPREDICTED A64 / A67 reb groups and
A54 / A55 delete_object rows, upper 57). Recipes `tools/recipes/stage_d1_ring_p5s02d.py` and `_scratch.py` (pair shape of the p5s02c pair, shared
stagekit calls; the p5s02c pair ran clean: `tools/bench/diag_c163_a2_2_facts.md`).

## The 17 actions (plan_ring_p5s02d.json)
- J: `dw_cond` delete_wire #23489 (scaffold stop #23042 -> loop #23041 cond); `do_23042` delete_object (Comparison, the scaffold stop);
  `do_23501` delete_object (LoopTunnel, scaffold in-tunnel; the sim shows wires 23460 / 23519 on it before the delete).
- J: `c_lr7` create Local (read) of 'records final (1.2 to 1.7)' on body 23405; `c_eq7` create Equal? by `$work` donor uid 10019;
  `w_eq7_x` case out-tunnel #31735 outer -> EQ7.x (route cfw); `w_eq7_y` LR7 -> EQ7.y; `w_eq7_cond` EQ7 -> loop #23041 cond (route stop).
- K3: `sr_k3` add_shift_reg on #23041 (SK3); `c_k3i` const by `claudeDev\DonorSRInit_v0.vi` uid 248 -> SK3L outer (const_sr);
  `t_k3o` / `w_k3out` (#376 'file progress' term 5704) / `w_k3r` and `t_k3i` / `w_k3l` / `w_k3pass` (frame #31517): two connect_term_uid
  register_end_case_border groups on case #31308.
- Compiled ops: delete_wire, delete_object x2, create x2, connect x2, stop, add_sr, create, connect, connect_term_uid x2.

## Questions for prior art
(a) delete_wire + delete_object of scaffold objects inside a ring step: has a P4 / P5 stage already deleted a scaffold stop / in-tunnel by
    `delete_object` (and a wire by `delete_wire` as a checkpoint), and did LabVIEW leave loose-end / no-source items or auto-removed tunnels that
    this plan does not predict?
(b) Has a Local READ + Equal? into a While loop's cond terminal (route `stop`) been built before here (P4 1.x stops), and with what result?
(c) register_end_case_border onto a plan-made SR on an inherited case with a frame pass wire (step 3's TC7 / TD7 ran clean) - anything that
    differs for a SOURCE end on a base node terminal (#376 'file progress')?
(d) Does an existing shared function or adopted step already stop loop 1.7 on the record counter, so this would duplicate it?
