---
type: brief
status: current
date: 2026-10-08
---
# Brief 147-a1-1 — ADOPT the s05 work copy 3f9ac26b, no rerun (docs/d1/ring-p4b.md PD354(c), PD353(d), PD329(a))

Cycle 146's s05 scratch (card 146-a1-4) was a structural PASS (22/0, E1 real == sim at all 17 ops, peak 607.7 MB) and saved the work copy
`claudeDev\D1_ring_p4s05_20261008_002621.vi` md5 **3f9ac26b69179eb53c202d90407ce7ee** (319045 B, ExecState 0, saved by gui_save). It was held back only
by an Error List total (55 vs pred 57) that PD354(a) has since turned into a RECORDED cross-check. **Do not rerun the scratch.** Facts of that run:
`tools/bench/diag_c146_a1_4_facts.md`. Prepared scripts (read them first, run in this order): `tools/bench/diag_c146_a1_4_adopt.py`,
`_mkgraph.py`, `_graph.py`, `_t2626.py` (their md5 are in the card inputs).

## Steps
1. Verify before anything: md5 of the work copy == 3f9ac26b (any difference = RETURN); protect-check md5 of s04 `D1_ring_p4s04_20261007_215031.vi` 95e408ff,
   s03 `D1_ring_p4s03_20261007_202957.vi` 282301ca, bed `D1_ring_p3b2b_20261002_130007.vi` 39511877.
2. ADOPT through `stagexec.adopt_scratch` called BY IMPORT (the CLI form is refused, fp-39) via `diag_c146_a1_4_adopt.py` -> `claudeDev\D1_ring_p4s05_<stamp>.vi`
   (same bytes), `adopted_scratch.jsonl` entry, md5 recorded. Full final-role Error List read of that adopted file (`errorlist_check`, double-click each item) ->
   `tools/bench/errorlist_expected_D1_ring_p4s05_<stamp>.json`. Expected total 55 (item set == `errorlist_D1_ring_p4s05_20261008_002621_20261008_003324.json`
   06a59001, a record, not a gate).
3. In a FRESH LabVIEW instance: load the adopted file (measure the load MB with the same meter stage_prerun.x10_start uses) and read the whole graph ->
   `tools/bench/graph_ring_p4s05_<stamp>.json` + md5 (`_mkgraph.py` / `_graph.py`).
4. Build Array #2626 table from that graph (`_t2626.py`): every input terminal by uid, name, type, wired or not. This is the s06 licence evidence (PD352(d)).
5. `tools/bench/memory_model.json` `load_by_vi`: add ONE entry keyed by the adopted file's md5 (value = the measured load MB, vi, cite = file:line of the
   measurement). **Nothing else in that file changes** — X10 coefficients, MEM_STOP / MEMSTOP limits and every other entry stay byte-identical; check by diffing the
   old and new JSON key by key and report the single added key.
6. Handles before/after flat (+-100). LabVIEW closed and verified gone (`tasklist`). Protected md5 (step 1) unchanged after.

## Never
Rerun the s05 scratch or any other plan; open the bed / s03 / s04 for editing; edit stage tools; touch s06 files (`plan_ring_p4_s06v18*`, `prep_c14*_mk*`);
touch the camera or any motor.

## Return
`result/1`: adopted file + md5, final EL (total + per-class vs 06a59001), measured load MB, graph file + md5, the #2626 table, the single `load_by_vi` key added,
protected md5 before/after, handles before/after, `tasklist` after. Facts file `tools/bench/diag_c147_a1_1_facts.md`.
