---
card: 151-a3-2
status: current
date: 2026-10-09
---
# Brief 151-a3-2 - P4 session 9 MADE (not run): the tail ops 185..202 on the REAL s08 graph; OFFLINE (docs/d1/ring-p4c.md PD367(d), PD367(h), PD365(d), PD366)

Same pattern as `tools/bench/cards/brief_150-a3-6.md` (and through it `brief_150-a3-5.md`): copy the maker `prep_c150_a3_6_mk.py` (f3e6d12c), the pred `prep_c150_a3_6_pred.py` (7996f5b1), the licence
`prep_c150_a3_6_licence.py` (efe26399) and the check `prep_c150_a3_6_check.py` (4455f2cc) to `prep_c151_a3_2_*` with ONLY the s07->s08 / s08->s09 names, pins, paths and the cap changed (say which lines).
Read first: `tools/bench/diag_c150_a3_6_facts.md`, `tools/bench/diag_c151_a1_1_facts.md` (the s08 result: adopted `claudeDev\D1_ring_p4s08_20261009_031503.vi` f99e8414, graph
`graph_ring_p4s08_20261009_033522.json` 44858dbf, load_by_vi 589.1, EL 46 expected `errorlist_expected_D1_ring_p4s08_20261009_031503.json` c19cde96).

## Measurement
1. **Base:** s08 = f99e8414 (never edited), graph 44858dbf. Remaining v18 ops = 185..202 (18 actions; the s08 sim end is the rebase source, as s07's was). START = `stage_prerun.x10_start(f99e8414)` = load_by_vi 589.1 + op-0 read (expect 595.0 = 589.1 + 5.9; quote the real number).
2. **Cut:** remove the 19-action cap (`MAXACT`) from the maker's cut rule; the cut is the longest group-respecting prefix with MAIN X10 <= 680 (PD320(e)). Whole remainder (ops 185..202) if it fits; otherwise the longest fitting prefix = s09 (and the rest named as s10). Quote the X10 margin at the cut,
   and ALSO the sensitivity at start + 21.4 MB (s08's metered start over its pred, `diag_c151_a1_1_facts.md:22`) and + 13.6 (s07) - as numbers only: NO recalibration of the start term (PD367(c)), and the cut stays decided by the unshifted rule.
3. **Rebase onto the real s08 graph** with `stage_prerun --rebase` (the s07 form: `prep_c150_a3_6_rebase.log`), plan -> `tools/bench/plan_ring_p4_s09v18.json`. The simulator could not run ops 185..190 from the s07 graph (`stagesim.py:1805-1807`, PD289(f): frame #29869 of FS #29721). The s08 graph now records them
   (FS #29721 frame [29869]; 7 rows on it; 0 border tunnels, `diag_c151_a1_1_fs.log`). **If the simulator STILL refuses an op of 185..190 on the real s08 graph: RETURN at once** with the refusal verbatim (file:line), the op, the FS #29721 rows, and which later ops (191..202) do not depend on it (from the plan's refs). No `stagesim.py` / stagekit / stagexec edit, no patch of the graph.
4. **Pred with V18E-R'** (PD366(c), the s08 pred form `prep_c150_a3_6_pred.py`): three checks, EL base = s08's **46** (the expected file, not 50). Also take the OPEN of card 151-a3-1: the review `archive/peer/2026-10-09-c151-a3-1-el46.md` says the pred missed two closures (Select #4538, IndexArray #29879) because
   `elrule.predict` got no `carry`. MEASURE (offline, no elrule edit): run `elrule.predict` for the s08 plan with the carry set the review names ({4538, 29843, 29879, 30002, 2626}) and say whether it gives 46; if so pass the same carry in the s09 pred, else pass none and quote both totals. The EL count is a recorded cross-check, not a gate (PD354).
5. **Recipes** `tools/recipes/stage_d1_ring_p4_s09v18.py` + `_scratch.py` (copies of the s08 pair, names/pins only), a sink gate per `wire_indicators` census row read by script (zero allowed; PD366(e)), **licence by script** (PD365(d)), X11 `--buildarray-check`, dry + prerun on FINAL bytes of plan + both recipes, `--scratch-required` rc, `--check-launch` of the scratch recipe. NOT launched (no `--launch`).
6. **Invariants** md5 before = after: stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun c739eb86, vigraph 13be0847, stagesim 748bbf30, errorlist_check 2b466a89, s08 f99e8414, s07 b3f86b32, graphs 44858dbf / 71935a84, s08 plan/pred/licence/recipes
   (c328fdaf, cf2eccbf, 6b978d9e, ca5a5478, 7cab5049), memory_model a28b6dd7. No LabVIEW process before or after (tasklist count 0). No file under tools/hooks edited. If a gate refuses your OWN prep script's command text (as `--el-advisory` was refused), do not route around it: `py tools/gate_fp.py log` if accepted, else name it in OPEN.

## Report `tools/bench/diag_c151_a3_2_facts.md` (<= 45 lines)
Cut (action count, op range, first op not included, X10 MAIN/Executor margins + the two sensitivities); rebase rc + lines; simulator outcome on ops 185..190 (the FS #29721 question answered); pred checks + EL base/predicted + the carry measurement; licence entries; sink-gate census; X11; dry/prerun/scratch-required/check-launch numbers; invariants; `OPEN:` line. Facts only; a result-dependent action is not yours to take (RETURN with the facts).
