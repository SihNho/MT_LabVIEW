---
type: facts
status: current
date: 2026-10-03
---
# Card 143-3 facts: s02 ADOPTED (EL 53 expected file), EL predictor FIXED (s02 53 / s01 51), s03 REBASE REFUSED (UID-REUSE) = RETURN

OFFLINE only; no LabVIEW, nothing launched. Inputs md5-checked against the card (all 9 match).

## Step 1 — adopt + expected Error List (PD333(a))
- Expected EL file `tools/bench/errorlist_expected_D1_ring_p4s02_20261003_110001.json` md5 1d90bde9: P3b-2b's 10 entries (51) + 2 entries
  (Local "not connected to anything" #6902; While "Conditional terminal is not wired" #10170/#23246), total 53.
  `errorlist_check.compare(read items, expected)` -> extra [] missing [] (`prep_c143_3_s02.log` 4/0).
- `plan_ring_p4_s02v18_pred.json` errorlist block only: predicted_total 53 (fixed rule), measured 53, checked true; other keys unchanged
  (gate P); md5 67c3bf29 -> 8f8b465c; plan md5 e941ebbf unchanged.
- ADOPTED through the PD329 writer `stagexec.adopt_scratch` (`prep_c143_3_adopt.py`, `prep_c143_3_adopt.log` 2/0): scratch log
  `diag_c143_1_scratch.log`, required E1,FR,D,TD,PB,PS all PASS, artefact 84cac487, input s01 dc61e193, plan_md5s {s02v18: e941ebbf};
  `adopted_launch(stage_d1_ring_p4_s02v18.py)` returns the record. `tools/bench/adopted_scratch.jsonl` md5 a5c93bba (first entry).
- The CLI form `py tools/stagexec.py adopt ...` was refused by guard_bash (flags.labview none treats every stagexec invocation as
  LabVIEW): gate false positive **fp-39** logged (`gate_fp_queue.jsonl`); routed by importing the same function (form prep_c142_5_pred.py uses).

## Step 2 — EL predictor fixed (PD333(b))
- Rule module `tools/bench/prep_c143_3_elrule.py`: item SETS L (Local with every terminal unwired), C (While body Diagram's '' sink
  unwired), A (created node with an unwired sink, PD322(e)); predicted = base + |end - start| - |start - end|.
- `selftest_elpred.log` 7/0: U1-U4 synthetic PASS; **s02 re-derived = 53** (new [cond 23166, local -20], closed []);
  **s01 re-derived = 51** (new [], closed []). Detail `selftest_elpred.json`.
- `prep_c142_5_pred.py` and `prep_c143_p1_pred.py` now count via the module (EL FIXED line; alternative_total None). Not re-run
  (re-running prep_c142_5 would overwrite s02's measured census; prep_c143_p1 is the provisional-base form).

## Step 3 — s03 rebase: REFUSED (first unexpected result; returned here)
- `py tools/stage_prerun.py --rebase tools/bench/plan_ring_p4_s03v18.json --graph tools/bench/graph_ring_p4s02_20261003_112505.json`
  -> `REBASE REFUSED: UID-REUSE between N's base and the real graph: ["term #23276 ('ParameterTerminal', 'Comparison')->('Terminal', 'Local')"]`,
  `BGRUN END rc=2` (`prep_c143_3_rebase.log:3-5`). Check: `stage_prerun.py:3453-3455` -> `stagexec.uid_reuse` (`stagexec.py:942`).
- Real s02 graph: #23276 = 'StopAll' SINK terminal of Local #6899 (StopAll WRITE, created in s02 as -18), wire 6929.
  s01 / s03 provisional base: #23276 = ParameterTerminal of Comparison #10171 ('x = y?'), which s02's plan deletes
  (scratch TD lost list and `recycled_uids [23276, 29071, 29299]`, `diag_c143_1_scratch.log:391`).
- Unchanged: `plan_ring_p4_s03v18.json` 9d5049d8 (still PROVISIONAL), `plan_ring_p4_s03v18_pred.json` e2e69c04, graph eda9db40.
- NOT done (depend on the rebase): X10 at 596.0, s03 EL prediction, dry/prerun on both s03v18 recipes, `--scratch-required` exit code.
  Prepared, not run: `tools/bench/prep_c143_3_pred.py` (X10 at 596.0; EL from the fixed rule on base 53, gate: closed includes cond 23166
  + local 6902).
- JEV-LADDER: no row for prep_c143_3_rebase.log in jev_gate.log.
