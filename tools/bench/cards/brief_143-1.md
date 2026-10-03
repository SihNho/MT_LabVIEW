---
type: brief
status: current
date: 2026-10-03
---
# Brief 143-1 — P4 session 2: prior-art review → ONE scratch → adopt (PD332(d), docs/d1/ring-p4b.md:156-170)

## Steps
1. **Prior-art review** of `tools/recipes/stage_d1_ring_p4_s02v18.py` (and `_scratch.py`) with `tools/prior_art_review.py`
   (cycle card `gates_due`: guard_cycle refuses the recipe until a newer review exists). Verdict `novel` → go on. Any other
   verdict: release only by a `REFUTED:` / `FIXED:` line with a citation under `## What was done with it` (CLAUDE.md §5,
   fourth layer); if no citation releases it → RETURN (judgement decides).
2. **ONE scratch run** of `tools/bench/plan_ring_p4_s02v18.json` (e941ebbf, 34 actions = v18 ops 25..58) on a BYTE COPY of
   `claudeDev\D1_ring_p4s01_20261002_232547.vi` (md5 starts dc61e193) with `tools/recipes/stage_d1_ring_p4_s02v18_scratch.py`.
   The `--scratch-required` check runs in the accepted `--prerun ... --scratch-required` form (the plain form is gate-fp
   fp-37, already queued).
3. **Predictions (a miss is a RETURN with the facts, LabVIEW closed, files saved):**
   - every op real == simulated; prim gate PASS on every created node; D / TD identity gates PASS (key (uid, owner, name));
   - peak ≤ 680 MB (X10 678.5 at 596.5); MEMSTOP 695 not hit;
   - Error List **51**, or **52** only if the extra item is base node #23166 newly unwired (term ''); any third value = return;
   - census: unpredicted by design (derived {}) — the MEASURED census is written into `plan_ring_p4_s02v18_pred.json` by a
     script that cites the log line (PD264(c) form).
4. **All PASS ⇒ ADOPT** the scratch file as `claudeDev\D1_ring_p4s02_<stamp>.vi` (PD329(a): `adopted_scratch.jsonl` entry,
   no second run on the s01 file), md5 recorded; full Error List read `--role final` + expected file; then in a FRESH
   LabVIEW instance: load (MB measured) + whole graph read → `tools/bench/graph_ring_p4s02_<stamp>.json` with md5.
5. Bed (`D1_ring_p3b2b_20261002_130007.vi` 395118775a52bc90073f4449b99f899d) and s01 md5 checked unchanged before and after.
   Handles flat. LabVIEW closed and verified gone.

## Never
- open the bed or the s01 file for editing; launch `plan_ring_p4_s02.json` (v17) or `plan_ring_p4_rasrest.json` (SUPERSEDED,
  PD332(b)); run a second scratch inside this card; diagnose-and-retry after a miss.

## Return
`result/1` with: review verdict + file, scratch gate table, peak, EL count (+ item 52's node if any), census written,
adopted file + md5, final EL, load MB, graph file + md5, and a JEV-LADDER row for any failing log.
Facts file: `tools/bench/diag_c143_1_facts.md`.
