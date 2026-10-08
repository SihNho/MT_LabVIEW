---
card: 150-a3-1
status: current
date: 2026-10-08
---
# Brief 150-a3-1 - s07 prepared: pred with V18E-R' (PD366(c)), recipes with BOTH sink gates (PD366(e)), X10, licence, dry + prerun; offline, NOT launched

Plan of record `docs/d1/ring-p4c.md` PD366 (lines 314-354) and PD365(d). This REPLACES `brief_150-a2-6.md` decision 1 (name normalisation on both sides is void, PD366(c));
its decision 2 (two sink gates) stands. Read `tools/bench/diag_c150_a2_5_facts.md` (rebase done, V18E-R miss), `brief_150-a2-3.md` steps 2-7 (form), and
`tools/bench/sim/ring_p4_v18/ring_p4_v3/summary.json:188-243` (the v18 rows). Offline: no LabVIEW, camera or motor.

## State (do NOT redo)
Plan `plan_ring_p4_s07v18.json` is **08c2ad4d** (rebased, final, completeness PASS, `prep_c150_a2_5_rebase.log:80`). Do NOT run `--rebase` again unless the plan md5 differs.
`stage_prerun.py` stays c739eb86 (no edit). Copy `prep_c150_a2_5_pred.py` (85196a77) to `prep_c150_a3_1_pred.py` and `prep_c150_a2_5_check.py` (9a99d7a8) to `prep_c150_a3_1_check.py` (same pin).

## Steps
1. **V18E-R' in your own pred script** (replaces the old key-set compare at the former `prep_c150_a2_5_pred.py:103-106`; no stage-tool edit). PASS iff all three hold, each printed:
   (1) only-s07 rows (rebased s07 end cdiff vs v18 sim after #177 `p4_rbE_sel`) is EMPTY;
   (2) every only-v18 row has `before: null` in v18's `cdiff_detail` at the compared step AND its node (owner uid) owns a RENAMED-OLD entry read from the rebase output
       (`prep_c150_a2_5_rebase.log` / `info['renamed_old']`; never typed);
   (3) on each such node, the multiset of sink-terminal names in the real s06 graph `graph_ring_p4s06_20261008_192149.json` (a3ecb92b) equals S1's, S1 read with `stagesim.load_s1` (never typed).
   Print the three checks and the excluded keys. Anything else FAILs: RETURN with both row lists and the `before/after` columns. Pred written with EL base 51 (as the old script).
2. **X10 after the rebase** (rebased plan, start from the measured load). MAIN <= 680 -> go on. Over 680 -> the longest group-respecting prefix <= 680 (PD320(e)), re-made and re-rebased by the
   same tools (`stage_prerun.py --rebase` on the cut plan), V18E-R' on it; quote range, count, X10, margins, first op over 680. Not a return.
3. **Recipes**: regenerate MAIN `tools/recipes/stage_d1_ring_p4_s07v18.py` and `_scratch.py` for the final action list: base/start/cut/pred only, copy the s06 pair's form
   (`stage_d1_ring_p4_s06v18.py`, `_scratch.py`); no new op kind. Each declares a SINK GATE for EVERY s07 census row that goes through `wire_indicators`, read from the census by script
   (`prep_c150_a1_1_session.json:395-420`: n1 `p4_rbA_re2` -> [23166,'Pos: Diffraction Pattern'], n28 `p4_rbD_sel_t25573` -> [23166,'autofocus reset count (1.2 to 1.1)']; expect 2 - the file is
   the source, do not type the pairs); each with PD355(b)'s pass rule as in the s06 recipe. Quote the s06 declaration form, the s07 lines, and why the count is what it is. Run X11
   (`--buildarray-check`, row `p4_rbB_sel_t4168` on #2626, op 150) and quote it.
4. **Licence by script**: write `tools/bench/plan_ring_p4_s07v18_licence.json` (pb-licence/1, s06 form `plan_ring_p4_s06v18_licence.json` 7f70bbf9) FROM the rebased plan:
   `rename_by_uid` #2626 if X11 flags op 150; `renames` = every BASE sink terminal (uid, owner) that an s07 connect row wires, `from`/`to` unset (= any name, `tools/stagekit.py:1412-1421`).
   State the entry count and owners.
5. **Dry + prerun** on the FINAL bytes of both recipes and the plan; `--scratch-required` exit code quoted (expected 3 per the s06 pattern). X10 lines for MAIN and scratch and margins to 680 / 695.
   A false-positive gate goes to `py tools/gate_fp.py log` (never an env bypass); no `tools/hooks/**` edit. PROVEN-PATTERN or a diff-only prior-art line - say which.
6. **Invariants** (md5 before = after): stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun c739eb86, vigraph 13be0847, stagesim 748bbf30, s06 VI 569ffbf5,
   s05 3f9ac26b, bed 39511877, memory_model, adopted_scratch, graph a3ecb92b, `sim/ring_p4_s06v18/**`, the s06 plan/pred/licence/recipes. List every changed file by md5 before/after.

## Return conditions
A stage-tool fault (file:line + refusal, no edit); V18E-R' check (1), (2) or (3) failing (row lists); a prerun gate failing twice at the same place; a protected md5 moved;
a hook false positive that blocks the deliverable (log with gate_fp.py first).

## Report `tools/bench/diag_c150_a3_1_facts.md` (<= 35 lines)
Plan md5, V18E-R' three checks with excluded keys, X10 numbers, X11, sink-gate lines, licence summary, dry/prerun/scratch-required with exit codes, files changed (md5 before/after), invariants, `OPEN:`. Facts only.
