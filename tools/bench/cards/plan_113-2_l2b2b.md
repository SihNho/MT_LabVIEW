# Card 113-2 plan - L2-B2b launch (for the prior-art review)

**Stage:** L2-B2b (docs/d1-loop12-17-split-plan.md PD226(e); split page tools/bench/cards/split_plan_111_l2b2.md s2), rows B2-01..08 + B2-16 (9 wire rows).
**Input:** claudeDev\D1_l2_b2a_20260928_001426.vi (md5 107a3ef1..., the B2a bed, graph tools/bench/graph_l2b2a_20260928.json). **Output:** claudeDev\D1_l2_b2b_<ts>.vi (gui_save, broken by design, never run) + tools/bench/errorlist_expected_D1_l2_b2b_<ts>.json.

## What changed since card 113-1 (which stopped at P2 with 3 rows UNROUTABLE)
1. **T1 - route widening in `tools/stagexec.py` `connect_route`** (review archive/peer/2026-09-28-c113b-route.md s1/s4): a bare ControlTerminal -> a LoopTunnel OUTER sink now takes 'ctltun' (gate `OWNER_ROUTED` -> `FACE_ROUTED`), and a bare LoopTunnel OUTER source -> a ControlTerminal sink takes 'ctlsink' with the source addressed through its OWNER LOOP's class traverse + Terminals[] (new `src_cls`/`src_owner` in the route info, used by the Executor). Same existing op `OpCtlSinkWire_v1` (gscript.wire_ctlsink); no new op VI. Inner faces and constants stay refused. Self-test tools/bench/selftest_stagexec_c113a.log: 124 pass / 0 fail (119 before + 5 new T113a-e, incl. 3 negatives).
2. **T2 - live scratch check** (tools/bench/diag_c113c_scratch.py, byte copy of the bed, deleted): b2_04 and b2_07 wired, both read back with ONE source == planned source, b2_04 `Is Broken?` False on the ordered cfw second pass (wire_delta 0), Remove Bad Wires on a scratch-of-scratch deletes neither new wire.
3. **P2** - `plan_l2b2b_in.json` (unchanged, md5 d13c0de4) re-simulated: FINAL, 9/9 rows routed (nested, cfw, nested, ctltun, ctltun, cfw, ctlsink, cfw, ctltun) -> tools/bench/plan_l2b2b.json md5 58046f2f; D4 scope file plan_l2b2b_d4.json re-pinned to that plan md5, scope unchanged (20 nodes of namediff_l2b2b.json; 10 of them have no S1 row, so D4 grants nothing there - the recipe's L0b gate says so).
4. **Recipe** tools/recipes/stage_d1_l2b2b.py (120 lines) = cut of stage_d1_l2b2a.py: plan/D4 paths, L0b as above, L1 checks CT ends against the route check's CT-routed ends; RBW-PRE/PRE2 kept. Top-level dry PASS (tools/bench/stage_d1_l2b2b_dry2.log).

## Question for prior art
Has this CT <-> LoopTunnel outer-face routing, or the L2-B2b launch itself, already been built, refuted or decided elsewhere in this project (a different verb, an earlier decision that LoopTunnel faces must not take owner-addressed CT routes, a prior failure of OpCtlSinkWire_v1 on a loop owner)?
