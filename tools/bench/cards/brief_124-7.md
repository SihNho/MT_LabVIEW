# Brief for card 124-7 — ring P3a: scratch run, then ONE launch (cycle 124 judgement, 2026-10-01)

Plan items: `docs/d1-loop12-17-split-plan.md` Pre-decided **246(c)(d)**, **247(e)**, **250**. P3a is launch-ready
(`tools/bench/cards/result_124-6.json` PASS 5/0): `tools/recipes/stage_d1_ring_p3a.py` (md5 `3aa685de…`), FINAL plan
`tools/bench/plan_ring_p3a.json` (`3f325260…`), predictions `tools/bench/plan_ring_p3a_pred.json` (`152bd4d6…`): Error List 54 + 0
new (alternative 55), census Wire 11, DNC 4, Case 1, Diagram 2, Tunnel 1, SelectorTunnel 2, OuterTerminal 7, InnerTerminal 10;
the `add_shift_reg` face lines (+4/+4) are MODEL, not samples. `--scratch-required` rc=3.

## Judgement decisions on 124-6's two opens
1. **The scratch run re-measures the MODEL census lines.** The scratch's measured census is recorded as a sample in
   `tools/bench/census_samples.json` (PD247(e)); if — and only if — a line marked MODEL differs, that line of the pred file is
   corrected, citing the scratch log lines that show the owners (the PD245(b′) precedent). Any OTHER deviation (a non-MODEL
   census line, an object gate, a broken new wire, Error List ≠ 54 or 55 with the new item not explained by the plan's
   alternative) is the first unexpected result: finish the step, return.
2. **P3a stays ONE 25-row step** (X14 advisory WARN accepted): PD246(d) sized it at ≈ 24 rows with a full scratch run first, and
   its counter subgraph was already built and read back on a scratch by 124-5 (`tools/bench/diag_c124_p3a_scratch.log`).

## Steps
1. Scratch run of the recipe on a byte copy of `claudeDev\D1_ring_p2b_20261001_140658.vi` (the recipe's / stagekit's scratch
   mode as in 122-6/123-1): every object gate of the recipe passes, `Is Broken?` False on every new wire, Invoke +0. Scratch
   Error List read `--count-only --role scratch` → the pin (54 or 55). Census sample recorded; MODEL lines corrected per (1).
   Re-run dry + prerun if the launch gate keys on the pred file (offline). Scratch deleted.
2. ONE launch → `claudeDev\D1_ring_p3a_<ts>.vi`; the scratch's object gates hold; census == pred.
3. Final Error List full read (`--role final`) == the pin; `tools/bench/errorlist_expected_D1_ring_p3a_<ts>.json` reverdicts
   OK; references balanced; open→save handle growth inside the PD236(b) band. Broken-intermediate count becomes 2 of 6.
4. LabVIEW closed and verified gone (`tasklist`).

## Rules
- The bed is never saved over. GUI only through `lv_gui.ps1 -Exception Approved` with the broken-intermediate evidence; every
  GUI act is capture → locate → act → capture → confirm (`docs/cycle27-plan.md` Pre-decided 9).
- `stage_d1_ring_p3a.py` and `plan_ring_p3a.json` are NOT edited. A guard_peer hold → its Jev ladder row; an owed hypothesis
  review is dispatched (`-Agent claude -Role hypothesis`), never bypassed.
- Return at the first unexpected result. If the 60-minute backstop refuses a step, return with the state recorded.
