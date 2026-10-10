---
type: plan
status: current
date: 2026-10-10
card: 158-a3-2
---
# Prior-art plan: ONE retry scratch of ring P5-2 step 1 (cycle 158 round 3, PD386)

What is launched: `tools/recipes/stage_d1_ring_p5s02a_scratch.py` (64b4f18b) on a NEW byte copy of the adopted P5-1 file
`claudeDev\D1_ring_p5s01_20261009_124542.vi` (7f2582ae), plan `tools/bench/plan_ring_p5s02a.json` 4284c22a (17 ops, actions 1..23), unchanged since
the prior-art review `archive/peer/2026-10-09-priorart-priorart-c156-a1-1-p5s02a.md` (verdict `novel`).

Why a new review: card 158-a3-1 edited the scratch recipe after that review (71c3aed4 -> 64b4f18b). The changes (diag_c158_a3_1_facts.md:13-14):
- LOG / OUT_JSON / SUM_JSON renamed to `diag_c158_p5s02a_scratch.*` (lines 30, 33) so the retry has its own log (the old fixed c156 log was appended
  and `scratch_tail` read METER lines over the whole file).
- `OPS_CENSUS = (16, 17)` + `K.op_class_census_install` / `K.op_class_census_print` (lines 34, 42, 52): prints one per-op CLASS census line for ops 16/17
  from reads the run already takes (no extra LabVIEW read).
- the retry-card argument is printed (line 48, `K.retry_card_arg`). SCRATCH name, acts, the MAIN recipe body (b52b9ff5) and every op are unchanged.

Also changed by 158-a3-1 (not in the recipe): `tools/stagekit.py` 0d8f6d25 -> 07f9e35f, the result gates PB / D / TD judged per PD386
(`docs/d1/ring-p5.md` ~313-350): PB compares real vs the sim end re-keyed by the bound frame uid, D/TD compare (source, sink) pairs and RECORD a
sinkless stub (wire 24091), CEN2 compares the pred census = the c158-a2-2 measurement (`plan_ring_p5s02a_pred.json` ed84b5fd). Mutation re-score
4/0, no invariant row stopped blocking (`tools/bench/prep_c158_a3_1_rescore.log`).

The previous launch (card 158-a2-2, `tools/bench/diag_c158_a2_2_facts.md`) built the planned graph (E1 diff 0 at every checkpoint, ops 16/17 by
`gscript.connect_term_uid`) and stopped before save on the old PB / D / TD / CEN2 gates.

Pre-checks on these bytes (card 158-a3-2): dry MAIN + scratch PASS unverified 0; prerun 16/0 both, X10 planned MAIN 674.7 <= 675, scratch 669.6;
`--scratch-required` rc 3 CENSUS-UNPREDICTED; `check_launch` ALLOW with `--retry-card tools/bench/cards/task_158-a3-2.json`.

Question for the review: has this project already got something that makes this retry unnecessary or that it should reuse instead (a
per-op class census print, a per-run log, a PB/D/TD form keyed this way)?
