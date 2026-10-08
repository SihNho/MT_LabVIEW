---
card: 152-b3-1
status: current
date: 2026-10-09
---
# Brief 152-b3-1 - P4 session 9 SCRATCH + adopt (docs/d1/ring-p4d.md PD368(e), PD369, PD365(e), PD354(a)); the ONE LabVIEW card of this step; broken file 5 of 6

This is `tools/bench/cards/brief_151-a1-1.md` again (read it first; through it brief_150-a3-2 / 148-a2-4 / 147-c3-3 / 149-a3-1 / 147-a1-8 / 147-a1-4: launch, pass, adopt, `load_by_vi`, handles, LabVIEW-gone),
with the s08 -> s09 names (s07 -> s08 as the base) and these deltas. Read `tools/bench/diag_c152_b2_1_facts.md` first: it is the offline prep this card launches. The s08 round's scripts `diag_c151_a1_1_{adopt,elexp,mkgraph,graph,memload,fs,inv}.py` are the copy sources (-> `diag_c152_b3_1_*`; names, ids, pins, paths ONLY; say which lines changed).

## Inputs (md5 pinned in the task; a mismatch is a RETURN)
Plan `plan_ring_p4_s09v18.json` 9d622c95, pred 85dbb0ba (EL predicted 46, no carry), licence 6d003b8d, MAIN recipe 4be3ff28, scratch recipe b1f6a87c, `stage_prerun.py` c739eb86, stagesim 128bacfb,
real s08 graph `graph_ring_p4s08_20261009_033522.json` 44858dbf (derived e26b4d90 is the REALSIM base only), s08 VI `claudeDev\D1_ring_p4s08_20261009_031503.vi` f99e8414 (never edited; the scratch runs on a NEW byte copy), memory_model a28b6dd7.

## Deltas against brief_151-a1-1.md
1. **Pre-launch:** re-run `--dry`, `--prerun` of the scratch recipe once on the final bytes (expected `prep_c152_b2_1_dry.log` / `_prerun.log`: dry 1/0, prerun 16/0, X10 633.3 Executor / MAIN 638.4) and `--scratch-required` (expected rc 3, census rows 1..6, `prep_c152_b2_1_scrreq.log:3`) and `--check-launch` (ALLOW). A different count / X10 / rc is a RETURN with the facts, not a fix.
2. **Prior art:** s09 is a PROVEN pattern (X14 `proven: no` in the facts: 6 rows). If the launch gate demands a prior-art review run `py tools/prior_art_review.py` DIFF-ONLY against the s08 scratch recipe (changed lines only = names, the action list, the two s09-shape gate adaptations FR `(on or NC == 0)` and licence R "zero allowed").
   An ANSWERED `novel`/`no-change` => go on. If the gate still refuses after an ANSWERED review: `py tools/gate_fp.py log`, no env bypass, RETURN with the refusal text. State which happened.
3. **Launch:** ONE scratch on a NEW byte copy of s08 f99e8414, ops 185..190 (6 actions). E1 real == sim EVERY op, **ops 187 `p4_x_slot_fs` and 189 `p4_x_n2_out` included** (op 187's new FS border tunnel is named 'min slot' on both faces, `fs_tunnel_naming_table.json` row 135 / `diag_c152_b1_2_cross.log:93`; a different real name is a RETURN fact), D/TD/PB by position key (T6), licence, X11 CLEAN, peak <= 680 / MEMSTOP 695.
   Record the METERED start MB against pred start 595.0 and the peak against X10 (PD367(c)); no recalibration. RETURN at the first result differing from the prediction; no second launch in this card.
4. **Adopt** (structural PASS only): `stagexec.adopt_scratch` by import (PD354(a)); copy `diag_c151_a1_1_adopt.py` -> `diag_c152_b3_1_adopt.py`. Result `claudeDev\D1_ring_p4s09_<stamp>.vi`: quote path + md5. A refusal => RETURN with it (file:line); no tool/log edit.
5. **Final Error List expected file** of the adopted s09 bytes with the elrun wrapper (as brief_151-a1-1 step 5; 0 items read = environment fault, not an answer): `tools/bench/errorlist_expected_D1_ring_p4s09_<stamp>.json`. Quote the TOTAL and the PER-CLASS diff vs s08's 46 AND vs the pred's 46 (the carry-45 alternative also quoted). A recorded cross-check, not a gate (PD354); another count is REPORTED and the file written from what was read.
6. **Fresh-instance load + graph read:** `tools/bench/graph_ring_p4s09_<stamp>.json` + md5 + load MB. Quote FS #29721's frame/border rows in this graph (frame #29869 + borders/tunnels: owner, index, class, name) - the tunnel for op 187 must be among them.
7. **`memory_model.json`:** ONLY one `load_by_vi` entry for the adopted s09 md5 (form of `diag_c151_a1_1_memload.py`). Key-by-key diff quoted (before = a28b6dd7); no limit, coefficient, MEMSTOP or X10 value changes.
8. **Invariants** md5 before = after: stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun c739eb86, vigraph 13be0847, stagesim 128bacfb, fs_tunnel_naming_table 769ae8d0, s08 VI f99e8414, graph 44858dbf, derived e26b4d90, the s09 plan/pred/licence/recipes (step Inputs), ring-p4d.md cf2ffa4a.
   Handle counts before/after recorded; no byte copy / `_elc_*` left; `tasklist` LabVIEW count 0 at the end (closed AND verified gone).
9. **Concurrent cards:** none. No tool or hook edit. Touch only the write globs. A gate refusing your OWN command text is a false positive: `py tools/gate_fp.py log`.

## Report (`tools/bench/diag_c152_b3_1_facts.md`, <= 45 lines)
Pre-launch numbers; prior-art outcome; gate outcomes per op class (E1 incl. ops 187/189, prim, D/TD/PB, licence, X11, peak, metered start vs 595.0); adopted file + md5 + load MB; EL total + per-class diff vs 46 / pred; graph json + md5 + FS rows; `load_by_vi` diff; invariants; handles; LabVIEW gone. `OPEN:` line. Facts only. Dispatch a hypothesis peer only if a gate FAILS.
