---
card: 163-a1-4
date: 2026-10-10
---
# Adversary review: does the new PB "class 3" in tools/stagekit.py loosen the gate?

Context (read the files, do not trust this text): `tools/stagekit.py` PB gate `pb_check_bound` (:1979-2022) records a pred-extra PB row
instead of blocking it when `pb_inherited_row` returns a class. Classes 1 and 2 existed (card 161-a3-1). Card 163-a1-4 added class 3 to fix
gate-fp fp-86: at P5-2 step 3 (plan `tools/bench/plan_ring_p5s02c.json`) two #376 rows ('error in', 'total data array in') that the ADOPTED
step-2 plan (`tools/bench/plan_ring_p5s02b.json` actions w_g376 / w_h376, tunnels TG1/TG2/TH1/TH2 on case 31308) wired into both frames of
case 31308 are untouched by step 3 (base PB == end), yet were BLOCKED: class 1 wants each S1 source uid once and every tag on the node's
inherited frame [31506]; class 2 wants a connect action of THIS plan and base `after` == []. Measured: `tools/bench/diag_c163_a1_4_ctx.log`.

The change (all in tools/stagekit.py):
1. `pb_inherit_ctx` (:2033-) chain loop (:2078-2083): for every adopted plan in the chain (only records that passed the md5/json/bound checks),
   collect `chain_connects {(node, term): (plan path, action id)}` from its `wire` actions whose dst is a base terminal (newest plan first via
   setdefault) and `chain_tunnel_case {real tunnel uid (through THAT run's bindings): (plan path, case uid)}` from its `tunnel` actions.
2. `pb_inherited_row` (:2101-2150): when this plan has no connect onto the sink and `chain_connects` has one, class 2's checks run with
   (i) replaced by `R0[sink] == bound_end` (base PB row == end), (iii) using only the tunnels the SAME adopted plan created (tag tunnel must be
   in that plan's chain_tunnel_case, single case, every tag frame in `ctx["cases"][case]`), (ii) set of S1 source uids equal + every uid's
   multiplicity == 1 or the case's frame count when a tag sits off the node's inherited frame, (iv) only PD374D_PASSTHROUGH sinks may have
   other frames. Returns class 3. Class 1 and class 2 code paths are unchanged (for class 2 the added `tn in tcase` is implied by `case` being
   a single non-None value).
Self-test: `tools/bench/selftest_c163_pbchain.py` (positive on the real step-3 data + negatives N1-N6).

Questions — try to break it:
- Is there a row whose real end is WRONG (differs from what the original computation needs) that class 3 now RECORDS instead of blocking?
  Think of: a newer adopted plan that deleted / re-routed the sink's wire; a sink wired by an adopted plan but whose wire this plan's
  actions disturb upstream (source side) while R0 == bound_end still holds; tunnels whose uid was reused; an adopted record listed in
  `missing` (should add nothing); multiplicity coincidences.
- Does anything in class 1 / class 2 now pass that failed before?
- Is comparing R0 (base graph, plan step 0 via pred_end_graph) to bound_end (real end) on the frame-keyed PB rows sufficient to say "untouched"?
- Name the cheapest discriminating test for your strongest objection.
