# Brief 131-4 — finish the P3b-1 scratch (S3/S4), then ONE launch of P3b-1 (LabVIEW), PD272

Decision: `docs/d1/ring-p3b.md` PD272 (read it). Result of the scratch: `tools/bench/cards/result_131-3.json`.

## Steps — return at the first result that differs from its prediction
1. **S3**: `tools/bench/stage_d1_ring_p3b1_el.py` scratch mode on the scratch VI already on disk
   (`claudeDev\scratch_c129_ring_p3b1_20261002_052136.vi`, via `stage_d1_ring_p3b1_scratch_pin.json`), Error List
   `--count-only --role scratch`. Prediction: per-class counts == the expected written by pin4 (54 = 55 − 1 + 0,
   `pin4.log:590`). The script deletes the scratch; LabVIEW verified gone after.
2. **S4**: the MEASURED census from `pin4.log` into `plan_ring_p3b1_pred.json` by a script citing the log line (PD264(c));
   in the same edit set the launch memory stop `fail_above` to **690.0** (PD272(b)) and say which line. Then recipe
   `--dry` 31/31 + `--prerun` 15/0 again; report `--scratch-required` exit.
3. **ONE launch** of `tools/recipes/stage_d1_ring_p3b1.py` on the bed (P3a, md5 4dfa44aa) → `claudeDev\D1_ring_p3b1_*.vi`,
   waited in-turn to `BGRUN END` (`.claude/agents/material.md:92-98`). Predictions: every gate PASS through op 31 incl.
   tunnel names and per-frame counts; census == pred; peak ≤ 690 MB (pin4 measured 680.8); saved file exists with its md5;
   bed md5 unchanged.
4. **Final full Error List read** (`--role final`) of the saved file; prediction 54 items == pin4's expected; write
   `tools/bench/errorlist_expected_D1_ring_p3b1_<stamp>.json`. LabVIEW verified gone.

Do NOT edit STATUS.md and do NOT move `current-bed:` — judgement accepts the bed. Broken-file count would become 3 of 6.
result/1 in `tools/bench/cards/result_131-4.json` with saved path + md5, peak, gate counts, Error List count.
