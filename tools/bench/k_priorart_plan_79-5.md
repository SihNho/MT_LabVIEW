Card 79-5 (cycle 79), stage K, docs/d1-loop12-17-split-plan.md Pre-decided 178(f) ROUTE (c).
Edit of tools/recipes/stage_d1_k.py since prior-art c79-k (archive/peer/2026-09-25-priorart-c79-k.md, released by FIXED at :308):
- the recipe no longer reads tools/bench/plan_k_rows.json; it executes and presents tools/bench/plan_k_split.json only
  (stagexec Executor, unchanged).
- K0 now checks the plan is a final stageplan/1; K1b now checks every plan action is compiled into exactly one real op
  (was: compiled ops == plan_k_rows decisions).
- IM takes each new tunnel's expected IndexMode from the plan's tunnel action `indexing` (178(a): originals measured 0 in
  k_contract_79) instead of plan_k_rows `tunnels`; P2 iterates the compiled ops instead of plan_k_rows decisions.
- IM, P2 (second pass by verify_term_uid, Is Broken? False), PB (178(c)), KN (31(a) name gate), ES recorded, save: unchanged.
Question: has this route or this recipe shape been built, refuted or settled elsewhere in the project files?
