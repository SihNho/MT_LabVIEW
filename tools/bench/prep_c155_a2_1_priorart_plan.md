---
card: 155-a2-1
status: current
date: 2026-10-09
---
# Plan under review: RING P5-1b (card 155-a2-1) - offline plan, not launched

Design: `docs/d1/ring-p5.md` PD374(e), PD378(b) (form S). P5-1 (32 actions / 22 ops, `tools/bench/plan_ring_p5s01.json`) was cut at X10 by card
154-a3-2b: P5-1a = actions 1..20 (built and adopted, `claudeDev\D1_ring_p5s01a_20261009_101219.vi` 2482fe7b, real graph
`tools/bench/graph_ring_p5s01a_20261009_103621.json` bd67a511). P5-1b = the remainder, actions 21..32 = P5-1 ops 15..22, planned on the REAL
P5-1a graph (`tools/bench/prep_c155_a2_1_mk.py`, log `tools/bench/prep_c155_a2_1_mk.log`).

P5-1b content (rows copied field for field from `tools/bench/plan_ring_p5s01_in.json` 21..32; P5-1a symbols mapped to the real uids of the
P5-1a graph through the P5-1a sim end + the scratch log's STEPX bindings):
- w_false_pass: count pass-through in the False frame of the base Case #30726 (case tunnel #31175 inner -> #31186 inner), case_frame_wire;
- c_lw / w_final: `records final (1.2 to 1.7)` local write on frame 686, fed by the count SR R #30996 outer;
- sr_q / w_obt_srq: a refnum shift register on loop #10170 fed by Obtain Queue #31258 'queue out';
- t_qi / t_qo groups: L.inner -> case input tunnel -> Enqueue #30756 'queue'; 'queue out' -> case output tunnel -> R.inner
  (connect_term_uid, register_end_case_border on the base case);
- w_q_false: refnum pass-through in the False frame, case_frame_wire.

NEW here (not proven by an earlier launch): the Case is a BASE-graph case, not one this plan created, so its frames are addressed by diagram uid
(`frame: "#30914"`, measured order [30914, 30922] = LabVIEW Frames[k], card 155-a1-1 `tools/bench/diag_c155_a1_1_facts.md`; tools stagexec
53e17623 / stagesim eb99c6ba). Compile: 8 ops = case_frame_wire, create, connect, add_sr, connect, connect_term_uid x2, case_frame_wire (same kinds
as P5-1 ops 15..22). Offline: pass A + REALSIM 0 PROVISIONAL, X10 MAIN 657.2 <= 680 (start 608.5). Files: plan
`tools/bench/plan_ring_p5s01b.json`, pred `_pred.json`, licence `_licence.json`, recipes `tools/recipes/stage_d1_ring_p5s01b.py` + `_scratch.py`
(the stagekit.RingSession template shape, `tools/recipes/stage_template_ring.py`). The next card runs the scratch recipe once on a byte copy of
the P5-1a file.
