---
type: brief
status: current
date: 2026-10-07
---
# Brief 144-1 — OFFLINE: regenerate the s03 prediction by the PD349 rule; dry + prerun both recipes on their CURRENT bytes

Cycle 144 pass item 1. Plan of record `docs/d1/ring-p4b.md` PD336(a); rule change `docs/d1/INDEX.md:231` (PD349, chat-T3/T4/T5).

## Why
`plan_ring_p4_s03v18_pred.json` (7fab8cf0) still says Error List **56** (old predictor). Since then the Error List rule was replaced
(PD349: arm A13K's SR class + A narrowed by terminal class; `tools/bench/prep_c143_3_elrule.py`, `selftest_elpred.py` 15/0 re-derives
s01/s02/s03 = 51/53/55). The s03 scratch recipe's bytes also changed (573b8537 -> fa6423ab) and the main recipe is now 61b0faf5 (was
d420f951), so the dry + prerun records of cycle 143 are stale (a failed or changed tool invalidates earlier pre-run records).

## Steps (measurement only)
1. Run `tools/bench/selftest_elpred.py` as the rule's own check; report the count.
2. Regenerate the Error List block of `tools/bench/plan_ring_p4_s03v18_pred.json` for plan `plan_ring_p4_s03v18.json` (da66a030, **not edited**)
   on the real s02 graph `graph_ring_p4s02_20261003_112505.json` (eda9db40) with the PD349 rule, by the same pred script that wrote 7fab8cf0
   (`tools/bench/prep_c143_5_pred.py`, copy it to `prep_c144_1_pred.py` if it needs a change; keep its RB/RB2 and negative-uid gates).
   Report: predicted EL count (the purpose expects **55**), the certain/uncertain item list with the basis, X10 at the measured 596.0
   MB (must stay <= 680), the census derivation. If the rule gives a number other than 55: write it, report it, stop — do not adjust the rule.
3. `--dry` and `--prerun` (the accepted `--prerun ... --scratch-required` form) on BOTH `tools/recipes/stage_d1_ring_p4_s03v18.py` and
   `..._scratch.py` at their current bytes; report counts (the cycle-143 result was dry PASS, prerun 16/0 each), the exit code of
   `--scratch-required`, and whether `new:LRB1.value` / `new:LWB1.value` still resolve in the dry (chat-T5 added a measured terminal-class table).
4. Record md5s of: plan, pred (new), both recipes, `termclass_table.json`, `prep_c143_3_elrule.py`, in the facts file.

## Never
- edit stagexec / stagekit / stagesim / stage_prerun / gscript / the plan / the recipes (a prep or LabVIEW card may start right after);
- launch anything; touch LabVIEW.

## Return
`result/1` with: EL count + basis, X10, dry/prerun counts for both recipes, `--scratch-required` exit code, new pred md5, recipe md5s, any
stop with step and line. Facts file: `tools/bench/prep_c144_1_facts.md`.
