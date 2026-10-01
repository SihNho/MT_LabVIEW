# Brief for card 123-5 — the two structure creators P3 needs + the census hook-in (cycle 123 judgement, 2026-10-01)

Decisions: `docs/d1-loop12-17-split-plan.md` Pre-decided **246(c)** (A1, A4, A5) and **247(c)(e)**. Previous card's
facts: `tools/bench/cards/result_123-3.json`, `tools/bench/diag_c123_routes.log`; census core: `result_123-4.json`,
`tools/census_predict.py`, `tools/bench/census_samples.json`.
Work only on BYTE COPIES of the bed `claudeDev\D1_ring_p2b_20261001_140658.vi` (md5 `652b1447ebbda761a7d5ba36455a0fa1`);
the bed is never saved over. Every script is a ≤ 120-line stagekit file.

## STEP 1 — case creator with a WIRED selector (LabVIEW, scratch)
`case_in` cannot be used: its selector is a panel control found by label (247(c)). Build a creator for a Case structure on
a given diagram (here While `#637`'s body `639`) whose selector is wired from a node output terminal: here `Equal?`
(`$work` donor, Comparison, output `x = y?`) with inputs BufNum (`#6810` `t6897`, wire `w3747`) and a constant. Read back:
the case's frames and their names (True/False), the selector terminal and its wire, the classes created. Deliver the
gscript verb, the stagexec plan route, the stagesim model, an opmodel record with created classes, a self-test, and a
`scratch_verify` record.

## STEP 2 — Flat Sequence creator (LabVIEW, same scratch run if convenient)
A Flat Sequence of N frames (here 3) on a given diagram — here the False frame of the STEP 1 case. Read back: frame count,
order, each frame's diagram uid, the classes created. Same deliverables as STEP 1. Any NEW op VI gets a hygiene record
(≥ 2,000 consecutive calls, 0 errors, handles flat ±100) — `gscript.op()` refuses it otherwise.

## STEP 3 — census hook-in (offline code, after the LabVIEW steps)
- `stage_prerun --prerun` runs `tools/census_predict.py` on the plan and its prediction file: a derived ≠ declared class
  count is a prerun FAIL (one line naming class, derived, declared); `CENSUS-UNPREDICTED` is an advisory line (prerun
  verdict unchanged) AND makes `stage_prerun --scratch-required <recipe>` exit 3.
- A way to record a scratch run's measured class census as a new sample in `census_samples.json` (a census_predict
  sub-command or a stagekit helper; the mechanism is yours), citing the log lines.
- stagekit: one census-gate helper that prints `UNVERIFIED-DRY` in dry mode (never PASS) and compares in a real run.
  Existing recipes are NOT edited.
- Record the classes STEP 1 and STEP 2 measured as samples.
- Self-tests: through the prerun path, the cycle-122 fixture (DigitalNumericConstant +1) → prerun FAIL; the corrected
  prediction → PASS; `plan_ring_p2a.json` / `plan_qrt_pool.json` → no FAIL, UNPREDICTED advisory; `--scratch-required`
  exits 3 for a recipe whose plan has an UNPREDICTED row. Existing self-tests stay green (at least
  `selftest_launch_gate`, the stagexec self-test, `selftest_census_predict`, `selftest_sr_init_c123`).

## Rules
- No stage recipe is run. GUI only if a step truly needs it (`lv_gui.ps1 -Exception Approved`, capture → locate → act →
  capture → confirm).
- Bed md5 unchanged at the end; scratch copies deleted or md5-recorded; LabVIEW closed and verified gone.
- Return at the first unexpected result (finish that step, LabVIEW closed, facts recorded).
- A failing log → the Jev ladder row; an owed hypothesis review is dispatched, never bypassed.
