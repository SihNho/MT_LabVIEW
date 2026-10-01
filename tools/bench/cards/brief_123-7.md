# Brief for card 123-7 — make the wired-selector case creator plan-usable, then hook in the census check (cycle 123, 2026-10-01)

Decisions: `docs/d1-loop12-17-split-plan.md` Pre-decided **248(a)(b)(d)** and **247(e)**. Previous card:
`tools/bench/cards/result_123-5.json`, `tools/bench/diag_c123_struct.log`, review
`archive/peer/2026-10-01-c123-5-s1a-branch.md` ("What was done with it"). Census core: `tools/census_predict.py`,
`tools/bench/census_samples.json`, `tools/bench/selftest_census_predict.py`.
Work only on BYTE COPIES of the bed `claudeDev\D1_ring_p2b_20261001_140658.vi` (md5 `652b1447ebbda761a7d5ba36455a0fa1`).

## STEP 1 — `case_wired` (LabVIEW, one scratch run)
Predictions, stated before the run:
- `Equal?` (`$work` donor, on `#639`) with `x` wired from `#6810` `current image number` (already on w3747): `x`'s wire uid
  == 3747, the count of terminals on w3747 rises by exactly 1, `Is Broken?` False on w3747. (A branch adds a sink to the
  existing Wire object; a wire COUNT is not the gate.)
- `case_wired` on `#639` with the selector from `Equal?`'s `x = y?`: frames False/True, selector wire == the source wire,
  and NO `Invoke` left behind (the purge added in this card); census after the purge recorded per class.
- `tidx` (`tools/bench/diag_c123_struct.py:35` and wherever the same helper lives) raises on an unknown terminal name
  instead of returning index 0.
Then deliver for `case_wired`: the stagexec plan route, the stagesim model, the measured class census as a sample in
`tools/bench/census_samples.json` (cite the log lines), and a self-test. No new op VI is expected; if one is needed, it
gets a hygiene record (≥ 2,000 calls, 0 errors, handles flat ±100).

## STEP 2 — census hook-in (offline code, after STEP 1)
Exactly `tools/bench/cards/brief_123-5.md` STEP 3: prerun FAIL on derived ≠ declared; `CENSUS-UNPREDICTED` advisory +
`--scratch-required` exit 3; recording a scratch run's census as a sample; stagekit's dry census helper printing
`UNVERIFIED-DRY`; existing recipes untouched; self-tests (cycle-122 fixture FAIL, corrected PASS, P2a/pool no FAIL,
exit 3 on UNPREDICTED) and the existing ones green (`selftest_launch_gate`, the stagexec self-test,
`selftest_census_predict`, `selftest_sr_init_c123`).

## Rules
- No stage recipe is run. Bed md5 unchanged; scratch deleted or md5-recorded; LabVIEW closed and verified gone.
- Return at the first unexpected result (finish the step, LabVIEW closed, facts recorded).
- A failing log → the Jev ladder row; an owed hypothesis review is dispatched, never bypassed.
- Keep every bgrun start inside the first 60 minutes after binding (the card backstop).
