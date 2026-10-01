# Brief 131-5 — name the extra loose end, owed review, then ONE launch of P3b-1 (LabVIEW), PD273

Decision: `docs/d1/ring-p3b.md` PD272 + PD273 (read both). Previous: `tools/bench/cards/result_131-4.json`.

## Steps
0. **Offline measurement (≤ 10 min):** diff the `wire has loose ends` items of
   `tools/bench/errorlist_expected_D1_ring_p3a_20261001_180540.json` (55) against
   `tools/bench/errorlist_scratch_c129_ring_p3b1_20261002_052136_20261002_053812.json` (53) by every identifying field
   the files carry (location text, object/wire uid, owner, position). Report which item(s) are gone and, for each, the
   wire/net uid if recorded, and whether a `wire_remove_loose_ends` row of `plan_ring_p3b1.json` targets that net (cite
   the plan line). Unknown stays unknown. This result does NOT gate steps 1–4.
1. **Owed hypothesis review** for `stage_d1_ring_p3b1_el_scratch.log` (failed prediction 54 → 53): `-Agent claude -Role
   hypothesis` single arm via `-ReviewCard`, with PD273(a) and step 0's facts as the claim to attack. Wait for ANSWERED;
   report its verdict line. It discharges the gate; it does not gate the launch beyond that.
2. **S4:** measured census from `pin4.log:455` into `plan_ring_p3b1_pred.json` (`diag_c131_4_census.py`), expected Error
   List = 53 (class `wire has loose ends` 22), `fail_above` 690.0; name the lines. Recipe `--dry` 31/31 + `--prerun` 15/0.
3. **ONE launch** of `tools/recipes/stage_d1_ring_p3b1.py` on the bed (P3a 4dfa44aa) → `claudeDev\D1_ring_p3b1_*.vi`,
   waited in-turn to `BGRUN END` (`.claude/agents/material.md:92-98`). Predictions: all gates PASS through op 31 incl.
   tunnel names (`Image Out`, `current image number`) and per-frame counts; census == pred; peak ≤ 690 MB; saved file +
   md5; bed md5 unchanged.
4. **Final full Error List** (`--role final`) of the saved file: prediction 53; write the expected file; list the
   `wire has loose ends` items that differ from P3a's 55 (the same diff as step 0, on the real file). LabVIEW verified gone.

Return at the first result that differs from its prediction (step finished, LabVIEW closed). Do NOT edit STATUS.md or move
`current-bed:`. result/1 in `tools/bench/cards/result_131-5.json`.
