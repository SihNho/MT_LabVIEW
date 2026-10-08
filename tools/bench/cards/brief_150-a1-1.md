---
card: 150-a1-1
status: current
date: 2026-10-08
---
# Brief 150-a1-1 - P4 session 7 RE-MADE on the real s06 graph at the measured load (PD364(c)); offline, NOT launched

Plan of record: `docs/d1/ring-p4c.md` PD364(c). Read `tools/bench/diag_c148_a3_3_facts.md` (how the provisional s07 was made) and
`tools/bench/diag_c146_a1_2_facts.md` (how s05 was RE-CUT at a measured load with the same rule) first.

## Facts to start from (quote them, do not re-derive)
- s06 is adopted: `claudeDev\D1_ring_p4s06_20261008_174730.vi` 569ffbf5; its graph `tools/bench/graph_ring_p4s06_20261008_192149.json` a3ecb92b;
  `memory_model.json` `load_by_vi` s06 = 593.8 MB (memory_model 8eec443c). The prepared s07 (`plan_ring_p4_s07v18.json` aeae610e, 14 actions =
  v18 ops 136..149) is on a PROVISIONAL start 627.7 MB, so its dry/prerun fail by design (`stage_prerun.py:2593-2599`).
- Cut rule in force (PD320(e), PD352(b), limit 680 by PD328, MEMSTOP 695): start = the input file's measured load, plus the one op-0 read exactly as the
  s05 re-cut did it (`prep_c146_a1_2_mk.py`; quote the start formula and its source line); cut = the LONGEST prefix of v18 ops starting at op 136 with
  MAIN X10 <= 680, at most 40 actions, no `of` pair split.

## Steps
1. **Card-local copies, names only.** Copy `tools/bench/prep_c148_a3_3_mk.py` -> `tools/bench/prep_c150_a1_1_mk.py` and
   `prep_c148_a3_3_pred.py` -> `prep_c150_a1_1_pred.py`; change only: base = the REAL s06 graph (above) instead of the stagesim provisional end, START =
   measured 593.8 (+ op-0 read by the s05 re-cut rule), plan/recipe/pred names and the card id. Nothing else; no stage-tool edit.
2. **Cut.** Run the maker; quote the start, the cut op, MAIN X10 at the cut, the margin to 680 / 695, the first op over 680, the action count, the
   checkpoints. Print the sensitivity (start -5 / +5 MB) as the 148-a3-3 maker did.
3. **Regenerate** `tools/bench/plan_ring_p4_s07v18.json` (+ `_in`), `plan_ring_p4_s07v18_pred.json` (EL base = s06's MEASURED 51, `elrule.py` a5ee7d5c,
   no `provisional` flag) and the recipes `tools/recipes/stage_d1_ring_p4_s07v18.py` / `_scratch.py` from the s06 pair patterns exactly as 148-a3-3 did
   (SG sink-gate census row included if the cut still has a wired-source row into a ControlTerminal; quote it). If a longer cut needs a #2626 licence
   (a Build Array #2626 row) or any stage-tool edit: apply PD364(c)'s fallback - rebase the prepared 14-action s07 on the real s06 graph with
   `py tools/stage_prerun.py --rebase tools/bench/plan_ring_p4_s07v18.json --graph tools/bench/graph_ring_p4s06_20261008_192149.json` (form of
   `diag_c147_*` rebase logs; quote the source) and say so as the first line of the report. A licence needing new design = RETURN.
4. **Dry + prerun on the final bytes of MAIN and scratch recipes**, `--scratch-required` (expected exit 3 as for s06): all PASS (X10 line quoted for
   both, with margins). A false-positive gate goes to the queue via `py tools/gate_fp.py log ...`, never an env bypass; a real failing gate twice at the
   same place = RETURN with the line.
5. **Range + X10 evidence (pass item 0):** quote `range` (ops first..last) and the X10 values; confirm cut ops are v18 ops from 136 contiguous and
   `cdiff` vs v18 for the plan's end state, as in `diag_c148_a3_3_facts.md` sec. 1.
6. **Invariants** (before/after md5, 96-file form `prep_c148_a3_3_check*`): stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c,
   stage_prerun dcd45aba, s06 569ffbf5, s05 3f9ac26b, s04 95e408ff, bed 39511877, memory_model 8eec443c, adopted_scratch 658fe5b9, the s06 plan/recipes
   and `sim/ring_p4_s06v18` tree unchanged. No byte copy made, no LabVIEW process.

## Return conditions
A stage-tool edit would be needed (after the PD364(c) fallback is also impossible); a protected md5 moved; a prerun gate failing twice at the same
place; X10 not reproducible by the maker formula.

## Report (`tools/bench/diag_c150_a1_1_facts.md`, <= 40 lines)
Start formula + number, cut op / action count / X10 / margins, plan + pred + recipe md5, dry/prerun/scratch-required results, fallback used or not,
files changed, invariants. `OPEN:` line. Facts only; no LabVIEW was started.
