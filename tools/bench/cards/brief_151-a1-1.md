---
card: 151-a1-1
status: current
date: 2026-10-09
---
# Brief 151-a1-1 - P4 session 8 SCRATCH + adopt (docs/d1/ring-p4c.md PD367(b)(c)(d), PD365(e), PD354(a)); the ONE LabVIEW card of this round

Everything in `tools/bench/cards/brief_150-a3-2.md` applies (and through it `brief_148-a2-4.md`, `brief_147-c3-3.md`, `brief_149-a3-1.md`, `brief_147-a1-8.md`, `brief_147-a1-4.md`:
launch, pass, adopt, `load_by_vi`, handles, LabVIEW-gone), with the s07 names replaced by s08 names (s06 -> s07 as the base) and these deltas.
Read `tools/bench/diag_c150_a3_6_facts.md` first: it is the offline prep this card launches.

## Inputs (md5 pinned in the task; a mismatch is a RETURN)
Plan `plan_ring_p4_s08v18.json` c328fdaf, pred cf2eccbf (EL predicted 48), licence 6b978d9e, MAIN recipe ca5a5478, scratch recipe 7cab5049, `stage_prerun.py` c739eb86,
real s07 graph `graph_ring_p4s07_20261008_224835.json` 71935a84, s07 VI `claudeDev\D1_ring_p4s07_20261008_222709.vi` b3f86b32 (never edited; the scratch runs on a NEW byte copy).

## Deltas
1. **Pre-launch**: re-run `--dry` and `--prerun` of the scratch recipe once on the final bytes (expected from `prep_c150_a3_6_scr_prerun.log`: PASS 16/0, X10 651.6; MAIN 656.7) and
   `--scratch-required` (expected rc 3, rows 1-19, `prep_c150_a3_6_scrreq.log`). A different count / X10 / rc is a RETURN with the facts, not a fix. Quote the numbers.
2. **Prior art**: s08 is a PROVEN pattern at 19 rows (X14 WARN `proven: no` in the facts). If the launch gate (`guard_cycle` / `stage_prerun --check-launch`) demands a prior-art review, run `py tools/prior_art_review.py`
   as a DIFF-ONLY review against the s07 scratch recipe (`stage_d1_ring_p4_s07v18_scratch.py`, review `archive/peer/2026-10-08-priorart-c150-s07-scratch.md`; changed lines only = names and action list).
   If it answers `novel`/`no-change`, go on. If the gate still refuses AFTER an ANSWERED review, that is a gate false positive: `py tools/gate_fp.py log`, no env bypass, RETURN with the refusal text. State which happened.
3. **Launch**: ONE scratch on a NEW byte copy of s07 b3f86b32, ops as the s08 plan (19 actions, ops 166..184). The sink-gate census is 0 `wire_indicators` rows (the recipes declare 0 gates; one ctlsink n18 `p4_rbR_out`).
   E1 real == sim EVERY op **including action 19 `p4_w_n2_arr`** (PD367(b): both its terminals already exist on frame #29869; the E1 measurement decides). D/TD/PB, licence (renames 4 entries, owners 9603/10465/23166/25545), X11 CLEAN, peak <= 680 / MEMSTOP 695.
   Record the METERED start MB against the pred start 595.3 and the peak against X10 (PD367(c)); no recalibration.
   RETURN at the first result differing from the prediction (if E1 fails at op 19: return with that fact, the next round cuts s08 to 18); no second launch inside this card (a retry is a new card).
4. **Adopt** (structural PASS only): `stagexec.adopt_scratch` called by import (PD354(a); the CLI form is refused), copy `diag_c150_a3_2_adopt.py` to `diag_c151_a1_1_adopt.py` with card id / names changed ONLY.
   Result `claudeDev\D1_ring_p4s08_<stamp>.vi`: quote path + md5. If the adopt refuses, RETURN with the refusal (file:line); do not edit a stage tool or the log.
5. **Final Error List expected file** of the adopted s08 bytes with the elrun wrapper (`py tools/bench/diag_c149_a1_2_elrun.py` form; the per-command wrapper puts the LocalCache site-packages on `sys.path[0]` - a read of 0 items is an environment fault, not an answer).
   Copy `diag_c150_a3_2_elexp.py` -> `diag_c151_a1_1_elexp.py`. Quote the total, the per-class diff vs s07's 50 AND vs the pred's 48. The Error List is a recorded cross-check, not a gate (PD354); another count is REPORTED, the file written from what was read.
6. **Fresh-instance load + graph read**: copies of `diag_c150_a3_2_mkgraph.py` / `_graph.py` -> `tools/bench/graph_ring_p4s08_<stamp>.json` + md5 and the load MB. **Quote FS #29721's frame and border rows found in this graph** (frame #29869 and its borders/tunnels:
   owner, index, class, name) - the next step's ops 185..190 are built on them (PD367(d)); also say whether the graph read records FS frames/borders at all.
7. **`memory_model.json`**: ONLY one `load_by_vi` entry for the adopted s08 md5 (copy `diag_c150_a3_2_memload.py` / `diag_c149_a1_2_memload.py` form). Key-by-key diff quoted (before = md5 pinned in the task); no limit, coefficient, MEMSTOP or X10 value changes.
8. **Invariants** md5 before = after: stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun c739eb86, vigraph 13be0847, stagesim 748bbf30, s07 b3f86b32, s06 569ffbf5, bed 39511877, graph 71935a84, the s08 plan/pred/licence/recipes.
   Handle counts before/after recorded; no byte copy / `_elc_*` left; `tasklist` LabVIEW count 0 at the end (closed and VERIFIED gone).
9. **Concurrent cards**: none. No tool or hook edit (no tool edit beside a LabVIEW card). Touch only the write globs.

## Report (`tools/bench/diag_c151_a1_1_facts.md`, <= 45 lines)
Pre-launch dry/prerun/scratch-required numbers; prior-art outcome; gate outcomes per op class (E1 incl. op 19, prim, D/TD/PB, licence, X11, peak MB, metered start vs 595.3); adopted file + md5 + load MB; EL total + per-class diff vs 50 and 48;
graph json + md5 + FS #29721 frame/border rows; `load_by_vi` key-by-key diff; invariants; handles; LabVIEW gone. `OPEN:` line. Facts only. Dispatch a hypothesis peer only if a gate FAILS (failed-prediction rule).
