---
type: facts
status: current
date: 2026-10-09
card: 154-a4-1
---
# 154-a4-1 facts - FAIL at compile: actions 21 / 32 (`frame` wires) are refused on the base case #30726; no plan written; offline, LabVIEW 0
## Run (`prep_c154_a4_1_mk.py` e65b41d3, log `prep_c154_a4_1_mk.log` RESULT 5/1, BGRUN END rc=1 after 14 s)
- Run 1 (`prep_c154_a4_1_mk_r1.log`) died on MY gate MAP: Case #30726 owns no terminal rows (same as diag_c154_a3_3_nodes.log:49); gate now also accepts an objs entry.
- M0 pins PASS (graph bd67a511, _in fabc4b9c, plan ed6ceb9e, P5-1a plan ed62e8d6, session a50bf0a5, memory_model 386a4cf4, tools 78b8d5a1/1bab9cf9/9decb20f/a7eb58c7) (log:3).
- R: actions 21..32 == the 12 named in the brief (k = 20 from prep_c154_a3_2b_session.json cut.k_actions) (log:5-6).
## Symbol -> real uid (log:7-15, sym from sim/ring_p5s01a/step_20_wire.json c9c3a0b8, bound from diag_c154_p5s01a_scratch.log STEPX lines; MAP PASS)
- CQ1 -17 -> #30726 (CaseStructure obj, no rows); CQ1.f1 -19 -> diagram #30922 (owners: CaseStructure 30726); EQ1 -24 -> #30756 ('queue' t30935, 'queue out' t30980).
- QO1 -3 -> #31258 ('queue out' t31335, unwired); SN1R -38 -> #30996 (outer t31016 unwired, inner t31007 w31171).
- TC1 -50 -> #31175 (False-frame 30914 inner t31177 open); TC2 -56 -> #31186 (False-frame 30914 inner t31191 open).
- Rows changed only in the mapped fields (log:16-27); `side`/`frame`/`why` kept as written.
## The refusal (log:30-31)
- compile_plan: "action 1 (w_false_pass): `frame` on 31175 - only a tunnel or selector of a case an EARLIER create of this plan made has frame names" (stagexec.py:613-615).
- pass A: same action, stagesim.resolve_addr: "#31175 has no inner face on a frame named 'False' (frames []; only a case this plan created carries frame names)" (stagesim.py:790,797-800).
- Action 32 (w_q_false) uses the same `frame` addressing on tunnels of #30726, so the same refusal applies to it (case_frame_op needs `loop` == a plan-made case, stagexec.py:606).
## PROBE, fact only, not a plan (log:28-29; sim/ring_p5s01b/_probe)
- Without the 2 frame wires the 10 actions compile to 6 ops: create, connect, add_sr, connect, tunnel [5,6,7], tunnel [8,9,10]; pass A failed null, 11 steps, 0 PROVISIONAL.
- In the whole P5-1 compile the same groups were ops 20/21 = connect_term_uid (register_end_case_border) and ops 15/22 = case_frame_wire (prep_c154_a3_2b_mk.log:23-30).
  On the base case they compile to plain `tunnel` (stagexec.py:781 needs created[loop] == "case").
## Not done (return condition "a refusal"): cut / X10, REALSIM, pred, licence, recipes, dry / prerun, X17/X14, --scratch-required, --check-launch, prior-art. No plan_ring_p5s01b* written.
## Invariants: `prep_c154_a4_1_inv_before.log` / `_after.log`: 170 files, before == after (only tools/hooks/material_marker.log, hook-written). LabVIEW processes 0.
OPEN: frame addressing on a BASE case's tunnels (actions 21, 32) - give the stage tools that support (tooling card), or re-address by term_uid (route changes from case_frame_wire), or another split?
