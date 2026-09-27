# Card 113-4 plan - L2-B2b launch 2 (for the prior-art review)

**Stage:** L2-B2b (docs/d1-loop12-17-split-plan.md PD226(e); split page tools/bench/cards/split_plan_111_l2b2.md s2), now 8 wire rows: B2-01, 02, 04..08, B2-16.
**Input:** claudeDev\D1_l2_b2a_20260928_001426.vi (md5 107a3ef1..., the B2a bed, graph tools/bench/graph_l2b2a_20260928.json). **Output:** claudeDev\D1_l2_b2b_<ts>.vi (gui_save, broken by design, never run) + tools/bench/errorlist_expected_D1_l2_b2b_<ts>.json.

## What changed since card 113-2 (reviewed: archive/peer/2026-09-28-priorart-c113c-l2b2b.md, verdict novel, recipe sha 5c6f0e7f)
1. **Launch 1 (card 113-2)** passed every gate except PB: cdiff(S1, real end) had a NEW pair (#11261 BuildArray, 'array') after row b2_03 (#11363 t11369 -> #11261 t11270): the real end read t11270 as 'element' (tools/bench/stage_d1_l2b2b.log:187-189, :214). Nothing saved. Hypothesis review archive/peer/2026-09-28-c113d-pb.md: leading alternative = BuildArray #11261 re-evaluates its input names because t11273 (the #11608 open row, QRT D5) is unwired since L2-B1.
2. **Judgement PD227(d):** b2_03 moves to the stage that wires t11273. Card 113-4 applies exactly that and nothing else.
3. **Plan:** tools/bench/plan_l2b2b_in.json = the 113-2 input minus action b2_03, plus the declared open row (#11261, 'array'); re-simulated by tools/bench/diag_c113f_plan.py: FINAL, open_rows_match (16 declared == 16 simulated end pairs), route check PASS 8/8 (nested, cfw, ctltun, ctltun, cfw, ctlsink, cfw, ctltun) -> tools/bench/plan_l2b2b.json md5 7a530b0c. D4 scope file re-pinned to that md5, scope unchanged (20 nodes). History copies plan_l2b2b_in_9row.json / plan_l2b2b_9row.json kept.
4. **Recipe tools/recipes/stage_d1_l2b2b.py:** docstring (row set 8, open rows 16, launch command with --retry-card task_113-4.json) and the Stage task label only; no gate, route or D4 logic changed; 120 lines. Top-level dry PASS (tools/bench/stage_d1_l2b2b_dry3.log), prerun 10/0 (tools/bench/stage_d1_l2b2b_prerun2.log).

## Question for prior art
Has leaving (#11261,'array') open until the stage that wires t11273, or launching L2-B2b without b2_03, already been decided against, refuted or tried elsewhere in this project (an earlier stage that removed a row and then failed PB/E1 for the dropped pair, or a decision that BuildArray rows must be wired in input order)?
