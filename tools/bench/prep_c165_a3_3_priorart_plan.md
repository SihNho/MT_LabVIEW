---
card: 165-3-3
status: current
date: 2026-10-10
---
# Plan under review: RING P5-2 step 5 (card 165-3-3) - recipe pair of plan_ring_p5s02e, offline-checked, NOT launched

Design: `docs/d1/ring-p5c.md` PD400 (a)-(c), PD401 (a)-(b), PD402 (a)-(c) (lines 140-232); PD379(b) (K3f / K4 / K4f design rows). Base = the
step-4 result `claudeDev\D1_ring_p5s02d_20261010_152518.vi` 6dcd5c3d (graph `tools/bench/graph_ring_p5s02d_20261010_154830.json` 2a5fa0c4).
Plan `tools/bench/plan_ring_p5s02e.json` fd23974e (13 actions A72..A84, 9 ops, checkpoints [0,1,3,4,6,7,8,9], delete_wire ops [1,8], MAIN 665.0
<= 675; facts `tools/bench/diag_c165_a3_2_facts.md`). Pred `plan_ring_p5s02e_pred.json` (keys pd401b / pd402), licence
`plan_ring_p5s02e_licence.json` (0 renames, X11 CLEAN), predicted Error List `errorlist_predicted_D1_ring_p5s02e_end.json` (53 -> 49: cleared items
6 / 7 / 8 / 50 by A72 / A73 / A84 / A83; raised 0; UNPREDICTED reb groups A77 t_k4o / A80 t_k4i; upper 51). Recipes
`tools/recipes/stage_d1_ring_p5s02e.py` and `_scratch.py` (pair shape of the p5s02d pair, shared stagekit calls; the p5s02d pair ran 21/0:
`docs/d1/ring-p5c.md:145-149`).

## The tool change this plan relies on (card 165-3-1, `tools/bench/diag_c165_a3_1_facts.md`)
`tools/stagexec.py` 6ea6637f -> 1d5309f4: NEW `prime_deleted_face_skip` (`tools/stagexec.py:6384-6408`), called in the PRIME pass
(`:2630-2635`): PRIME skips proving at base an end that is a LoopTunnel InnerTerminal SINK whose base wire is the `wire_uid` of an EARLIER
checkpointed `delete_wire` op; logged `PRIME-SKIP`; every other end primes as before. Self-test `selftest_c165_prime.log` 38/0 (negatives n1-n4
still refuse). Before it (165-1-1): `stagexec.loop_inner_face_sink` (`tools/stagexec.py:6345`) routes a dst that is a While/For LoopTunnel inner
face with wire 0 by `gscript.connect_term_uid`.

## The 13 actions (plan_ring_p5s02e.json)
- K3f: `dw_10362` delete_wire (sink-only stub on LoopTunnel #5204's inner face t8776, no source; checkpoint); `w_k3f` OK3.outer (#31803, already
  wired: feeds w_k3r of step 4) -> t8776 (route connect_term_uid via loop_inner_face_sink, PRIME-SKIP #8776).
- K4: `sr_k4` add_shift_reg on loop #23041 (SK4); `c_k4i` const by `claudeDev\DonorSRInit_v0.vi` uid 248 -> SK4L outer (const_sr);
  `t_k4o` / `w_k4out` (#376 'file number to append out' term 5739) / `w_k4r` and `t_k4i` / `w_k4l` / `w_k4pass` (frame #31517): two
  connect_term_uid register_end_case_border groups on case #31308 (the same form as step 4's K3, which ran clean).
- K4f: `dw_25232` delete_wire (stub on LoopTunnel #10404's inner face t24342; checkpoint); `w_k4f` OK4.outer (made in this step, also feeds
  w_k4r) -> t24342 (compile kind branch; PRIME-SKIP #24342).
- Expectations per stub-delete + connect pair (PD401(b), pred `pd402`): face wire 0 after the delete; census after the connect in
  [{}, {'Wire': 1}]; face on OK3 / OK4.outer's net; Is Broken? False.

## Questions for prior art
(a) Has a stage here connected a sink onto the INNER face of a While/For LoopTunnel (after deleting what was on it), and did LabVIEW keep the
    tunnel's outer side, re-index it, or raise items this plan does not predict?
(b) PRIME-SKIP: has any earlier stage or tool deferred the base address proof of an end to its own step (or proved ends only after a delete), and
    did that hide a failure the base proof would have caught?
(c) A connect from an already-wired SelectorTunnel OUTER terminal (#31803 feeds w_k3r) onto a second sink - precedent
    `diag_c127_1_fsinner.log:81-102` (from a Flat Sequence inner face). Anything here that shows the SelectorTunnel outer case differs?
(d) Does an existing adopted step already wire 1.7's t3 / t4 registers to #5204 / #10404 (so this would duplicate it)?
