---
type: brief
status: current
date: 2026-10-03
---
# Brief 143-3 — adopt s02, fix the EL predictor, rebase session 3 (OFFLINE; PD333, docs/d1/ring-p4b.md:171)

## Steps
1. **Adopt** `claudeDev\D1_ring_p4s02_20261003_110001.vi` (84cac48781c7c915c8f0d7e8fb079341) as P4 session 2's file with the
   PD329(a) mechanism (`tools/bench/adopted_scratch.jsonl` entry; whatever writer the PD329 card built — find it, do not
   hand-roll a second one). Write its expected Error List file from the full read
   `tools/bench/errorlist_D1_ring_p4s02_20261003_110001_20261003_110836.json` (53 items) in the same form as
   `tools/bench/errorlist_expected_D1_ring_p3b2b_20261002_130007.json`.
2. **Fix the EL predictor** (`tools/bench/prep_c142_5_pred.py:65-87`; same logic in `tools/bench/prep_c143_p1_pred.py:44-89`):
   CERTAIN items also for (i) a created node with an unwired OUTPUT terminal (e.g. a source-only Local) and (ii) a base
   loop whose conditional-terminal wire the plan deletes and does not re-wire in the same session; an item the plan
   CLOSES (a terminal open at the base that the session wires) is debited. Self-test: re-derive s02 → must give **53**
   (measured; `tools/bench/diag_c143_2_facts.md`); re-derive s01 → must give its measured 51. Both numbers in the log.
3. **Rebase session 3**: `py tools/stage_prerun.py --rebase tools/bench/plan_ring_p4_s03v18.json --graph
   tools/bench/graph_ring_p4s02_20261003_112505.json` (eda9db40). Then X10 at the MEASURED start 596.0 (if > 680 → re-cut by
   PD320(c) and report the new last op), pred via the fixed predictor (EL count + basis; expected: s02's 53 minus the two
   items s03's action 1 closes, plus s03's own), `--dry` and `--prerun` on BOTH s03v18 recipes, and `--prerun ...
   --scratch-required` exit code.
4. Report everything as facts; return at the first unexpected result.

## Never
edit stagexec / stagekit / stagesim / stage_prerun / gscript; touch LabVIEW; launch anything.
Facts → `tools/bench/prep_c143_3_facts.md`.
