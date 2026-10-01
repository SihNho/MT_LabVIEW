# Brief for card 123-9 — case-tunnel faces in the non-body frame (cycle 123 judgement, 2026-10-01)

Decision: `docs/d1-loop12-17-split-plan.md` Pre-decided **249(c)(d)**. Facts from `tools/bench/cards/result_123-8.json`:
stagesim keeps only the body frame's inner face of a plan-made case tunnel (`tools/stagesim.py:358-362`); stagexec sends a
wire from a created tunnel to kind `branch` (`tools/stagexec.py:473-474`); case data-tunnel creation is unmeasured in
stagesim (`_case_tunnel` docstring, `tools/stagesim.py:812-820`). The plan that needs it: `tools/bench/plan_ring_p3a_in.json`
action 20 `p3a_w_true_pass` (`tools/bench/plan_ring_p3a_sim.log:21`). Case creator: `gscript.case_wired` (123-7).

## HARD TIME LIMIT
Return by **16:35** local time. Do not START a LabVIEW run or a multi-file code change after **16:25** — return with the
state recorded instead. The session that dispatched you is killed at 16:48. Never leave stagesim / stagexec / the plan
schema half-changed: make the related edits together and self-test them before returning, or make none.

## STEP 1 — measure (LabVIEW, one scratch run on a byte copy of `claudeDev\D1_ring_p2b_20261001_140658.vi`)
A ≤ 120-line stagekit script. On body `639`: a fresh `Equal?` and a `case_wired` case with its selector. An I32 value from
outside the case enters through an INPUT tunnel; the False frame wires it through `Increment` to an OUTPUT tunnel; the
True frame wires the input tunnel's inner face straight to the output tunnel's inner face; the output tunnel's outer face
feeds a new sink outside the case. Read back per frame: tunnel uids, each frame's inner-face uids, wires, `Is Broken?`
False, and the classes created (a census sample with log lines). Bed md5 `652b1447…` unchanged; scratch deleted;
LabVIEW verified gone.

## STEP 2 — code (only after STEP 1 passes)
- The plan format (stageplan/1) gets a `frame` field on case-tunnel face addresses (src and dst).
- stagesim resolves the inner face per frame, modelled on STEP 1's measured facts.
- stagexec compiles a wire between inner faces in a named frame, on the route STEP 1 used.
- Self-tests: a plan with the True-frame pass-through simulates and compiles; `plan_ring_p3a_in.json` action 20 passes
  stagesim; the existing self-tests stay green (stagexec 124/0, case_wired 14/0, census hook-in 12/0, launch_gate 29/0,
  c120_routes 29/0, census_predict 14/0).

## Rules
- No stage recipe is run. Return at the first unexpected result (finish the step, LabVIEW closed, facts recorded).
- A failing log → the Jev ladder row; an owed hypothesis review is dispatched, never bypassed — unless the time limit
  forbids it, in which case return and say so.
