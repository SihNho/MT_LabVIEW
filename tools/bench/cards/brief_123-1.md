# Brief for card 123-1 — finish ring P2b (cycle 123 judgement, 2026-10-01)

Plan items: `docs/d1-loop12-17-split-plan.md` Pre-decided 240–245, especially **245(b′)**.

## Why the cycle-122 scratch failed, and what is already measured
The P2b scratch run (`tools/bench/stage_d1_ring_p2b_scratch_pin.log`) passed every object gate and failed only CEN2:
DigitalNumericConstant +5 against a hand-typed prediction of +1. The owners are already in that log:
- `:60` DNC `#25535` owned by ArrayConstant `#25465`
- `:78` DNC `#25774` owned by ArrayConstant `#25632`
- `:96` DNC `#26122` owned by ArrayConstant `#25898`
- `:114` DNC `#26401` owned by ArrayConstant `#26244`
- `:132` DNC `#26495` (the `Latest` constant) owned by Diagram `#4866`

So the prediction was wrong, not the build: each new ArrayConstant carries its element DigitalNumericConstant.

## Steps
1. Correct `tools/bench/plan_ring_p2b_pred.json`: the DigitalNumericConstant line becomes +5, citing the five log lines above.
   Change no other prediction line. Do NOT edit `tools/recipes/stage_d1_ring_p2b.py` or `plan_ring_p2b.json`.
2. If the launch gate keys its dry/prerun records on the prediction file, re-run dry + prerun (offline, seconds). Both PASS.
3. Check the kept scratch `claudeDev\scratch_c122_p2b_20261001_132703.vi` has md5 starting `a18b92d5`. Run
   `tools/bench/stage_d1_ring_p2b_el.py` on it: the Error List pin must show 0 new items, total 54 (PD240(d)). It deletes
   the scratch afterwards. Scratch Error List read = `--count-only --role scratch`.
4. ONE launch of `tools/recipes/stage_d1_ring_p2b.py` → `claudeDev\D1_ring_p2b_<ts>.vi`. Every object gate of the scratch
   must hold: 5 labels exact (`Num`, `TransPos`, `RotPos`, `FrameIdx`, `Latest`), `read_term_type` == the F-types,
   `read_const_value` == PD240(b) values, all on `#4866`, none inside a loop, 5 new wires, none lost, cdiff == 16 rows,
   CEN2 == the corrected prediction.
5. Final Error List full read (`--role final`) == the pin. Write `tools/bench/errorlist_expected_D1_ring_p2b_<ts>.json`;
   it must reverdict OK. References balanced; open→save handle growth inside the PD236(b) band.
6. Read-only, on the SAVED `D1_ring_p2b_<ts>.vi`, no save: for `IMAQ Create #20436`, for `'Cam'` `IMAQ Create #13938`, and
   for every `IMAQ Create` inside For `#23093`, record the source of the **Image Type** input (uid and class, or
   "unwired") and its value via `read_const_value`. Write `tools/bench/facts_c123_imgtype.json`. If a reader cannot read
   a class (e.g. an enum constant), record the class and mark the value OPEN. Do not build a reader for it.
7. LabVIEW closed and verified gone (`tasklist`).

## Rules
- Bed never saved over. GUI only through `lv_gui.ps1 -Exception Approved` with the broken-intermediate evidence; every GUI
  act is capture → locate → act → capture → confirm (`docs/cycle27-plan.md` Pre-decided 9).
- If `guard_peer` holds the launch on `stage_d1_ring_p2b_scratch_pin.log`, apply the Jev ladder row; an owed hypothesis
  review is dispatched (`-Agent claude -Role hypothesis`), never bypassed.
- Return at the first unexpected result (finish the step, LabVIEW closed, facts recorded). If the 60-minute backstop
  refuses a step, return with the state recorded.
