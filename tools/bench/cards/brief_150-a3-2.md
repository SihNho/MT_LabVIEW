---
card: 150-a3-2
status: current
date: 2026-10-08
---
# Brief 150-a3-2 - P4 session 7 SCRATCH + adopt (docs/d1/ring-p4c.md PD366, PD365(d)(e), PD354(a)); the ONE LabVIEW card of round 3

Everything in `tools/bench/cards/brief_148-a2-4.md` applies (and through it `brief_147-c3-3.md`, `brief_147-a1-8.md`, `brief_147-a1-4.md`: launch, pass, adopt, `load_by_vi`, handles, LabVIEW-gone),
with the s06 names replaced by s07 names and these deltas. The route AFTER the structural PASS is `brief_149-a3-1.md` steps 1-5 (adopt by import, final Error List expected file, graph, `load_by_vi`).
Read `tools/bench/diag_c150_a3_1_facts.md` (f1c382c0) first: it is the offline prep this card launches.

## Inputs (md5 pinned in the task; a mismatch is a RETURN)
Plan `plan_ring_p4_s07v18.json` 08c2ad4d, pred 6f46fc3c (EL predicted 52), licence aedbe1f1, MAIN recipe e0f1152f, scratch recipe 80dbdb41, `stage_prerun.py` c739eb86,
real s06 graph `graph_ring_p4s06_20261008_192149.json` a3ecb92b, s06 VI `claudeDev\D1_ring_p4s06_20261008_174730.vi` 569ffbf5 (never edited; the scratch runs on a NEW byte copy).

## Deltas
1. **Pre-launch**: re-run `--dry` and `--prerun` of the scratch recipe once on the final bytes (expected: scratch dry PASS, prerun PASS 16/0, X10 673.7, margin 6.3 / 21.3 - `prep_c150_a3_1_scr_prerun.log:153-155`).
   A different count or X10 is a RETURN with the facts, not a fix.
2. **Prior art**: X14 said `proven: no` (30 rows > 15), and no prior-art review exists for the s07 scratch recipe. If the launch gate (`guard_cycle` / `stage_prerun --check-launch`) demands one, run `py tools/prior_art_review.py`
   as a DIFF-ONLY review against the s06 scratch recipe (`stage_d1_ring_p4_s06v18_scratch.py`, reviewed `novel` in `archive/peer/2026-10-08-priorart-c148-s06-scratch.md`; changed lines only = the sink-gate spec lines and names), exactly as cycle 147 card did.
   If it answers `novel`/`no-change`, go on. If the gate still refuses AFTER an ANSWERED review, that is a gate false positive: `py tools/gate_fp.py log`, no env bypass, RETURN with the refusal text. Say in the facts which happened.
3. **Launch**: ONE scratch, a NEW byte copy of s06 569ffbf5, ops as the s07 plan (30 rows). Both SINK GATES (n1 `p4_rbA_re2`, n28 `p4_rbD_sel_t25573`) must PASS with readback; E1 real == sim every op; D/TD/PB, licence, X11 (op 150 licensed by rename_by_uid #2626); peak <= 680 / MEMSTOP 695.
   RETURN at the first result differing from the prediction; no second launch inside this card (a retry is a new card).
4. **Adopt** (structural PASS only): `stagexec.adopt_scratch` called by import (PD354(a); the CLI form is refused - fp-39), copy `diag_c149_a3_1_adopt.py` to `diag_c150_a3_2_adopt.py` with card id/names changed ONLY. Result `claudeDev\D1_ring_p4s07_<stamp>.vi`: quote path + md5.
   If the adopt refuses, RETURN with the refusal (file:line); do not edit a stage tool or the log.
5. **Final Error List expected file** of the adopted s07 bytes with the elrun wrapper: `py tools/bench/diag_c149_a1_2_elrun.py` form (per-command wrapper puts the LocalCache site-packages on `sys.path[0]` in-process - the runner process lacks comtypes/rapidocr; a read of 0 items is an environment fault, not an answer).
   Copies `diag_c150_a3_2_elexp.py` from `diag_c149_a3_1_elexp.py`. Quote the total, the per-class diff vs s06's 51 AND vs the pred's 52, and whether item 6 "source void -> sink I32" is present or gone. The Error List is a recorded cross-check, not a gate (PD354); another count is REPORTED, the file written from what was read.
6. **Fresh-instance load + graph read**: `diag_c149_a3_1_mkgraph.py` / `_graph.py` copies -> `tools/bench/graph_ring_p4s07_<stamp>.json` + md5 (the real s07 graph that s08 is made from) and the load MB.
7. **`memory_model.json`**: ONLY one `load_by_vi` entry for the adopted s07 md5 (copy `diag_c148_a2_4_memload.py` / `diag_c149_a1_2_memload.py` form). Key-by-key diff quoted (before 8eec443c); no limit, coefficient, MEMSTOP or X10 value changes.
8. **Invariants** md5 before = after: stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun c739eb86, vigraph 13be0847, stagesim 748bbf30, s06 569ffbf5, s05 3f9ac26b, bed 39511877, graph a3ecb92b, s07 plan/pred/licence/recipes.
   Handle counts before/after recorded; no byte copy / `_elc_*` left; `tasklist` LabVIEW count 0 at the end (closed and VERIFIED gone).
9. **Concurrent cards**: none. No tool or hook edit (no tool edit beside a LabVIEW card). Touch only the write globs.

## Report (`tools/bench/diag_c150_a3_2_facts.md`, <= 45 lines)
Pre-launch dry/prerun counts + X10; prior-art outcome; gate outcomes per op class (SG with readback for both gates, E1, prim, D/TD/PB, licence, X11, peak MB); adopted file + md5 + load MB; EL total + per-class diff + item 6;
graph json + md5; `load_by_vi` key-by-key diff; invariants; handles; LabVIEW gone. `OPEN:` line. Facts only. Dispatch a hypothesis peer only if a gate FAILS (failed-prediction rule).
