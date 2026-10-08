---
card: 150-a3-5
status: current
date: 2026-10-08
---
# Brief 150-a3-5 - s08 MADE (not run) on the REAL s07 graph at the measured s07 load (docs/d1/ring-p4c.md PD365(g), PD364(c), PD366(c)(e)); offline

Offline: no LabVIEW, camera or motor; NO `--launch`; no stage-tool, hook or elrule edit. This is the s07 preparation again, one session later. The routes already exist - copy them, change names/bases only:
`tools/bench/cards/brief_150-a1-1.md` + `prep_c150_a1_1_mk.py` (7a275061: the cut maker, start rule, MAXACT 40), `brief_150-a2-3.md` (rebase, X10, pred, recipes, licence, dry + prerun), `brief_150-a3-1.md` with
`prep_c150_a3_1_pred.py` (2644bdd4: V18E-R'), `prep_c150_a3_1_check.py` (1b935cd2), `prep_c150_a3_1_licence.py` (da47cb38), and `diag_c150_a3_1_facts.md` / `diag_c150_a3_2_facts.md` (what s07 measured: start, peak, load, renames).

## Facts this card starts from (do not re-measure)
Adopted s07 = `claudeDev\D1_ring_p4s07_20261008_222709.vi` md5 b3f86b32 (never opened/edited); real s07 graph `tools/bench/graph_ring_p4s07_20261008_224835.json` 71935a84; `load_by_vi` s07 = 589.4 MB (memory_model b4a6eec6);
metered scratch start was 613.3 vs predicted 599.7 and the peak 661.7 stayed under X10's 673.7 (`diag_c150_a3_2_facts.md`). 67 v18 ops remained after s06 and s07 took ops 136..165, so v18 ops 166..190 (25 ops) remain: s08 may be P4's last session.

## Steps
1. **Maker (copy of `prep_c150_a1_1_mk.py` -> `prep_c150_a3_5_mk.py`)**: START = `stage_prerun.x10_start(<s07 md5 b3f86b32..>)` = load_by_vi 589.4 + op-0 read (the s06 rule; quote it); input = s07's SIMULATED end (`sim/ring_p4_s07v18/step_30_create.json` or the plan's real end - read which the s06->s07 route used);
   v18 ops from 166; longest prefix with MAIN X10 <= 680 (PD320(e)), <= 40 actions, no `of` pair split; PD366(f): over 680 -> the cut, not a hand-back. If the whole of 166..190 fits, say so. Plan `tools/bench/plan_ring_p4_s08v18.json` (+ `_in`), sim in `tools/bench/sim/ring_p4_s08v18/`.
   Byte-copy any pre-existing s08 files first (there should be none; say so). Do NOT overwrite any s07 file (plan/pred/licence/recipes/sim).
2. **Rebase** onto the REAL s07 graph: `py tools/stage_prerun.py --rebase tools/bench/plan_ring_p4_s08v18.json --graph tools/bench/graph_ring_p4s07_20261008_224835.json` (bgrun if the hook asks). Quote rc, REBIND / RENAMED-OLD / FLIPPED-OLD lines, md5 before/after.
   The name-free rebind (c739eb86) is meant to bind renamed old terminals. If it is refused, quote the refusal with file:line and RETURN (no tool edit).
3. **X10 after the rebase** at the measured start; <= 680 else the longest group-respecting prefix (re-make + re-rebase by the same tools). Quote range, count, X10, margins to 680 / 695, first op over 680. Note the +13.6 MB start deviation seen at s07 (an OPEN of 150-a3-2) as a fact; do not change any coefficient.
4. **Pred** (copy `prep_c150_a3_1_pred.py` -> `prep_c150_a3_5_pred.py`, same pin/check pattern): V18E-R' (PD366(c)) - three checks printed, excluded keys, RENAMED-OLD read from the rebase output, #2626/other nodes' sink-name multiset from the real s07 graph vs S1 (`stagesim.load_s1`); EL base = s07's measured 50. If a check FAILS: RETURN with both row lists and before/after columns.
   If the cut contains no #2626-type rename the check (2)/(3) may be empty - say so; do not invent rows.
5. **Recipes** `tools/recipes/stage_d1_ring_p4_s08v18.py` + `_scratch.py` from the s07 pair (`e0f1152f`, `80dbdb41`): base/start/cut/pred only, no new op kind; a SINK GATE for EVERY s08 census row that goes through `wire_indicators`, read from the census by script (state the count and rows; zero is a valid answer if stated). X11 (`--buildarray-check`) quoted.
6. **Licence** `tools/bench/plan_ring_p4_s08v18_licence.json` (pb-licence/1, s07 form `plan_ring_p4_s07v18_licence.json` aedbe1f1) FROM the rebased plan by script (copy `prep_c150_a3_1_licence.py`): `rename_by_uid` where X11 flags a row; `renames` = every BASE sink terminal (uid, owner) an s08 connect row wires, `from`/`to` unset. Entry count and owners.
7. **Dry + prerun PASS** on the final bytes of both recipes and the plan; `--scratch-required` rc quoted (expected 3 per the pattern); X10 lines for MAIN and scratch; PROVEN-PATTERN or the prior-art situation stated (do NOT run a prior-art review: the launch is a later cycle's card). A false-positive gate -> `py tools/gate_fp.py log` (no env bypass).
8. **Invariants** md5 before = after: stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun c739eb86, vigraph 13be0847, stagesim 748bbf30, s06 569ffbf5, s05 3f9ac26b, s07 b3f86b32, bed 39511877, memory_model b4a6eec6, adopted_scratch 450c894c, graph s07 71935a84 and s06 a3ecb92b,
   every s07 plan/pred/licence/recipe/sim file, `tools/hooks/**`, `dispo.py` 4b456b18. List every changed file by md5 before/after. No LabVIEW process at the end.

## Return conditions
A rebase/prerun refusal (verbatim + file:line); a V18E-R' check failing; a prerun gate failing twice at the same place; a protected md5 moved; MAIN > 680 even for the shortest meaningful prefix; a hook false positive that blocks the deliverable (gate_fp first).

## Report `tools/bench/diag_c150_a3_5_facts.md` (<= 40 lines)
Cut range + count + start + X10 numbers, rebase output, V18E-R' checks, X11, sink-gate rows, licence summary, dry/prerun/scratch-required with exit codes, files changed, invariants. `OPEN:` line. Facts only.
