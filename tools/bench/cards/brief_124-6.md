# Brief for card 124-6 — P3a routes, FINAL plan and recipe, offline (cycle 124 judgement, 2026-10-01)

Decisions: `docs/d1-loop12-17-split-plan.md` Pre-decided **250** (read it), with 246(c)(d), 247, 249. The P3a design is fixed
there; do not re-design it. No LabVIEW. No LabVIEW card is live, so the one gate edit below is allowed.

## Measured facts to model (`tools/bench/cards/result_124-5.json`, `tools/bench/diag_c124_p3a_scratch.log`)
R1: register LEFT inner face (a terminal row, not a Nodes[] entry) → node in a case frame by `gscript.connect_term_uid` = ONE
SelectorTunnel on the case, one inner face per frame, +2 Wire, `Is Broken?` False. R2: node in a case frame → register RIGHT
inner face, the same. R3: `case_frame_wire` True-frame tunnel face → tunnel face = Wire +1. R4: `case_frame_wire` second sink on
an already-wired inner face = LabVIEW branches the existing wire, census {}. Census samples are in `tools/bench/census_samples.json`.

## Work
1. **Routes** (stagesim + stagexec): a wire whose outside end is a plan-made register inner face and whose other end lies in a
   plan-made case frame compiles to route `connect_term_uid` (stagesim model = R1/R2, so routes 15/16 of
   `tools/bench/sim/diag_p3a_route_124_3.log` become routable); a second sink on a used inner face compiles to `case_frame_wire`
   variant `branch` (R4, census {}), which closes route 19. `tools/stage_prerun.py` `SP_WIRING` (`:898`) gets `case_frame_wire`
   and `connect_term_uid` (it lacks them; stagexec's `REC_WIRING` has them). Self-tests: extend
   `tools/bench/selftest_case_frame_c124.py` with one case per route; the existing ones stay green.
2. **Plan**: `tools/bench/plan_ring_p3a_in_v3.json` from v2 (`p3a_w_qr_x` addressed by `frame: "False"` from the input tunnel's
   inner face); simulate: all actions, NO UNROUTABLE row. Then the FINAL plan `tools/bench/plan_ring_p3a.json` (≤ 25 rows) with
   census predictions (from the samples) and the predicted new Error List item count against
   `tools/bench/errorlist_expected_D1_ring_p2b_20261001_140658.json` (P2b: 54 items).
3. **Recipe** `tools/recipes/stage_d1_ring_p3a.py` (≤ 120 lines on stagekit; output `claudeDev\D1_ring_p3a_<ts>.vi` +
   `tools/bench/errorlist_expected_D1_ring_p3a_<ts>.json`), dry run, `stage_prerun.py --prerun` (X15 census PASS), the prior-art
   review (`prior_art_review.py` — required: `connect_term_uid` / `case_frame_wire` are new structure classes in a stage), and
   `stage_prerun.py --scratch-required` (record the exit code; 3 is expected).
Return at the first unexpected result. The scratch run and the ONE launch belong to the next cycle.
