# Brief for card 124-3 — the two remaining P3a route gaps, offline (cycle 124 judgement, 2026-10-01)

Runs beside LabVIEW card 124-1 (which builds `gscript.case_inner_face` / `gscript.case_frame_wire`). NO LabVIEW. No gate files
(`tools/stage_prerun.py`, `tools/hooks/**`): a gate edit waits until no LabVIEW card is live.

## Facts (card 124-2, `tools/bench/cards/result_124-2.json`; `tools/bench/plan_ring_p3a_sim_v2.log:43-50`)
`plan_ring_p3a_in_v2.json` simulates all 25 actions, but FINALIZE refuses on the route check, 4 rows:
1. ROUTE 15 / 16 (tunnel groups `p3a_t_in` and `p3a_t_out`): `UNROUTABLE ADDRESS: node #10000032 / #10000029 not in Diagram[5]
   (#639).Nodes[]` — a cross-border wire into / out of a PLAN-MADE `case_wired` case frame. The LabVIEW side of exactly this was
   done in 123-9 with `connect_nested_v1` (`tools/bench/diag_c123_casetun.log:38,45`, `Is Broken?` False), so this is the route
   check's address resolution, not a missing LabVIEW capability.
2. ROUTE 17 `case_frame_wire`: CREATE-NO-VERB — expected until 124-1 lands its function. Not yours.
3. ROUTE 19 `p3a_w_qr_x`: `branch: tunnel #10000043 has no wired inner source` — `Quotient & Remainder`'s `x` takes the counter
   from the INPUT tunnel's inner face in the False frame (PD246(c) A5: `i = count mod 20` from the register's LEFT value, in
   the False frame), the same inner face that already feeds `Increment`. A case input tunnel has one inner face per frame, so
   "branch from the tunnel" is ambiguous.

## Work
- Fix (1) in stagexec's route check (and stagesim if its model is the cause): resolve a node created by the plan on a plan-made
  case frame's diagram; route it to the same `connect_nested_v1` path 123-9 used, with the frame diagram as the inner end.
- Fix (3) in the PLAN: re-address `p3a_w_qr_x` with `frame: "False"` from the input tunnel's inner face (the `frame` field of
  124-2), compiled as an in-frame wire; record in the plan row that it is the SECOND sink on that inner face (the scratch run of
  the launch card measures how LabVIEW makes it — a branch on the existing wire).
- Write `tools/bench/plan_ring_p3a_in_v3.json` (v2 stays). Simulate it: all 25 actions; the route check's ONLY remaining
  UNROUTABLE row may be ROUTE 17's CREATE-NO-VERB (none if 124-1's function already exists when you run).
- Self-tests: a new case for each fix in `tools/bench/selftest_case_frame_c124.py` (extend it) and the existing ones green
  (stagexec, stagesim, case_wired, launch_gate, c120_routes, census_predict — the numbers in result_124-2.json).
Related edits land together, self-tested, or not at all. Return at the first unexpected result.
