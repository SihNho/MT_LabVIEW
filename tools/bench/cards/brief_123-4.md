# Brief for card 123-4 — the census device's core, OFFLINE, new files only (cycle 123 judgement, 2026-10-01)

Decision being implemented: `docs/violation-decisions.md`, block "inference-over-measurement — 2026-10-01 13:56".
Why: cycle 122's P2b class-count prediction was typed by hand (`tools/bench/plan_ring_p2b_make.py:82`), and the recipe's
census gate passes in dry mode (`DRY or dc == exp`, `tools/recipes/stage_d1_ring_p2b.py:98`), so a wrong number first
showed up inside LabVIEW. The fix: the census prediction is COMPUTED from measured samples.

This card runs beside card 123-3 (LabVIEW). It writes NEW files only and edits no gate or build code. The hook-in to
`stage_prerun --prerun` and stagekit is a later card's job (123-5), not this one.

## Deliver
1. `tools/bench/census_samples.json` — per op and variant (e.g. `OpConstInd_v0` with an array value vs a scalar value),
   the MEASURED class-count change of one call, each sample citing the log lines that measured it. First sample:
   `OpConstInd_v0`, from `tools/bench/stage_d1_ring_p2b_scratch_pin.log:60,78,96,114,132` and `tools/bench/stage_d1_ring_p2b.log`
   (an array value adds its ArrayConstant AND the element DigitalNumericConstant inside it; a scalar adds one
   DigitalNumericConstant; plus the indicator). Add samples for the other ops the P2b, P2a and pool plans use only where a
   log measured them; never invent one.
2. `tools/census_predict.py` — standalone (imports none of stagesim / stagekit / stagexec / gscript). Input: a stage
   plan JSON and its census prediction file. Output per class: derived change, declared change, and a verdict:
   `PASS`, `FAIL` (class, derived, declared), or `CENSUS-UNPREDICTED` (a create row whose op/variant has no sample) —
   never PASS for an unpredicted row. Ends with one `RESULT {...}` line (result-line/1).
3. `tools/bench/selftest_census_predict.py` — cases: (a) `plan_ring_p2b.json` with cycle 122's prediction (DNC +1; rebuild
   it as a fixture from the current file, md5 `98ca9b30…`, with that one line set back to +1) → FAIL naming
   DigitalNumericConstant, derived +5; (b) the current corrected prediction → PASS; (c) `plan_ring_p2a.json` and
   `plan_qrt_pool.json` with their own prediction files → no FAIL (UNPREDICTED rows listed, which is honest); (d) a
   fabricated plan row with an op that has no sample → CENSUS-UNPREDICTED.

## Rules
- No LabVIEW, GUI or hardware. No edits to `tools/stage_prerun.py`, `tools/stagekit.py`, `tools/stagexec.py`,
  `tools/stagesim.py`, `tools/gscript.py`, `tools/hooks/**`, or any existing opmodel file.
- A sample is only what a log measured (cite file:line). If the plan or prediction format cannot be read as described,
  record what the files actually contain and return.
- Return at the first unexpected result.
