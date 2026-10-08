---
type: brief
status: current
date: 2026-10-08
---
# Brief 147-a1-4 — P4 session 6: ONE s06 scratch on a byte copy of the adopted s05 -> adopt on structural PASS (docs/d1/ring-p4b.md PD329(a), PD352, PD354(a))

Same shape as brief 146-a1-4 (`tools/bench/cards/brief_146-a1-4.md`, the s05 scratch it describes passed 22/0 and was adopted by card 147-a1-1) and brief
145-a1-1 (`brief_145-a1-1.md`). s06 = v18 ops 115..135 (25 actions), made by card 147-a1-3 on the REAL adopted-s05 graph (facts `tools/bench/diag_c147_a1_3_facts.md`).
Prerun: MAIN X10 679.3, SCRATCH X10 674.2, both 16/0; X11 PASS LICENSED (ops 118/119 and 132 in s06, `plan_ring_p4_s06v18_licence.json`). Start 612.6 = 606.7 + 5.9.
Pred EL 55 by `tools/elrule.py` (a5ee7d5c), base 55 = the adopted-s05 read.

## Steps
1. **Inputs unchanged before launch (md5; any difference = RETURN):** plan `tools/bench/plan_ring_p4_s06v18.json` cfbd9823, `_in.json` db72d8af, `_pred.json` c4a6a35a,
   `_licence.json` 7dce79aa, recipes `tools/recipes/stage_d1_ring_p4_s06v18.py` 41ad9d35 / `_scratch.py` 8554bdd6, `memory_model.json` 88eeb037, `tools/elrule.py` a5ee7d5c;
   adopted s05 `claudeDev\D1_ring_p4s05_20261008_002621.vi` **3f9ac26b** (same bytes), s04 `D1_ring_p4s04_20261007_215031.vi` 95e408ff, s03
   `D1_ring_p4s03_20261007_202957.vi` 282301ca, bed `D1_ring_p3b2b_20261002_130007.vi` 395118775a52bc90073f4449b99f899d. Re-run `--dry` + `--prerun ... --scratch-required`
   on the current bytes first (expected exit 3). A gate demanding prior-art or a review: the pattern is PROVEN (s04 and s05 passed the same shape) -> `PROVEN-PATTERN`;
   a false refusal goes to `tools/gate_fp.py`, never an env bypass. `stage_runs.jsonl` shows one s06 scratch slot already used by an OFFLINE selftest (gate-fp fp-52); one
   real scratch run is within RETRY_CAP.
2. **ONE scratch run** of `plan_ring_p4_s06v18.json` with `stage_d1_ring_p4_s06v18_scratch.py` on a BYTE COPY of 3f9ac26b (the original is never opened for editing). Record the
   METERED start (fresh load + op-0 read; prerun assumed 612.6) and the PEAK in MB.
3. **Structural predictions (a miss = RETURN with facts, LabVIEW closed, files saved; no diagnose-and-retry):** every op real == simulated (E1); prim gate PASS on every
   created node; D / TD identity gates PASS (keyed by uid, owner, name); PB open pairs as predicted; the #2626 licence used exactly as licensed (uids 2832/4160/4165, no
   other node); peak <= 680 MB (`MEM_STOP_MB` 680; a stop there = RETURN, the judgement session decides); MEMSTOP 695 not hit. **The Error List is ADVISORY (PD354(a)):**
   the scratch recipe prints `EL-ADVISORY` (total + per-class vs pred 55 and vs the start read b654430d); it fails the run only on a class in neither the start read nor the
   pred, or |total diff| > 3. Census is unpredicted by design -> write the MEASURED census into `plan_ring_p4_s06v18_pred.json` by a script citing the log line.
4. **All structural gates PASS => ADOPT** by `stagexec.adopt_scratch` called BY IMPORT from a script (the CLI form is refused, fp-39; `adopted_scratch.jsonl` entry) as
   `claudeDev\D1_ring_p4s06_<stamp>.vi`; md5 recorded; full Error List read (`--role final`) -> `tools/bench/errorlist_expected_D1_ring_p4s06_<stamp>.json`; per-class
   difference vs the elrule pred (55) and vs the s05 read, with ONE line explaining each non-zero class. Then in a FRESH LabVIEW instance: load (MB measured with the same
   meter as `x10_start`) + whole-graph read -> `tools/bench/graph_ring_p4s06_<stamp>.json` with md5. Handles before/after flat (+-100). Adapt the card-147-a1-1 scripts
   (`diag_c147_a1_1_adopt.py`, `_mkgraph.py`, `_graph.py`) to the new file names.
5. `memory_model.json`: add ONE `load_by_vi` entry keyed by the adopted s06 md5 (value = measured load MB, vi, cite); nothing else changes (key-by-key diff reported).
   Only if the scratch is adopted. Report the metered start vs the 612.6 assumption and the peak vs the X10 prediction (calibration data), without changing any coefficient.
6. 3f9ac26b, 95e408ff, 282301ca, bed 39511877 md5 unchanged before and after. LabVIEW closed and verified gone (`tasklist`).

## Never
Open the bed, s03, s04 or the adopted s05 for editing; launch any other plan; run a second scratch inside this card; edit stage tools (stagexec / stagekit / stagesim /
stage_prerun / gscript / elrule) — a tool fault is a RETURN plus a gate-fp entry; save a broken intermediate other than through the adopt path; touch the camera or any motor;
write any `memory_model.json` field but the one `load_by_vi` entry.

## Return
`result/1` with: gate table, metered start and peak MB, EL-ADVISORY lines and per-class diff with explanations, census written, adopted file + md5, final EL, load MB, graph
file + md5, the single `load_by_vi` key, protected md5 before/after, handles before/after, `tasklist` after. Facts file `tools/bench/diag_c147_a1_4_facts.md`.
