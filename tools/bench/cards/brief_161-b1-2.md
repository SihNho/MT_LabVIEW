---
card: 161-b1-2
status: current
date: 2026-10-10
---
# Brief 161-b1-2 (assignment 161-1) - OFFLINE MEASUREMENT: where do the 31 PB rows on #376 come from, when the pred has 26 and the plan 24 open pairs?

`labview: none`, no `--launch`, no tool/hook/recipe/plan/pred edit. Read `tools/bench/diag_c161_b1_1_facts.md` (all), `tools/bench/prep_c161_b1_1_dry.log` lines 40-60 (the PB FAIL record, `eq_diff`, `blocked`, `pairs_extra_left`), `docs/d1/ring-p5b.md` PD393.

## Known
- Card 161-b1-1: with checkpoint set (0,1,2,3,4,5,7,8,9,10) the dry runs all 10 ops (STEPX diff 0 each) and then gate PB fails: real end vs sim end `eq_diff []`, both 31 rows; the pred (`plan_ring_p5s02b_pred.json` 18729409, made by `prep_c160_c3_1_pred.py`) has 26 rows (26 slots) and the plan 24 open (node, term) pairs; `pairs_extra_left` = 5 on node 376 (cal cluster path, error in, file size, selected path, total data array in); blocked whys: frame tags 'not the plan's frame(s) []' (3 sinks) and 'source terminal uids doubled vs S1' (error in, total data array in).
- Before this, the dry never got past ops 5/9 (c160), so PB was never evaluated on p5s02b. The pred's 26 rows were computed by the pred maker without a real dry end.

## Measure (facts only; do NOT decide what to change)
1. Read the PB gate code (`tools/stagekit.py`, search the PB message text) and quote the exact definition of the three numbers: sim-end rows, "pred's N rows (slots)", "plan's open (node, term) pairs": which function computes each and from which input.
2. Rerun nothing in LabVIEW. Using the saved dry artefacts (graph json, step files under `tools/bench/sim/ring_p5s02b/**`, the pred file), list the 31 rows and the 26 pred rows keyed the same way and print the symmetric difference (rows only in the 31, rows only in the 26), each row with its owner/term and the plan action id that creates or changes it (if derivable).
3. For the 5 `pairs_extra_left` pairs on #376: say which plan actions (ids from `plan_ring_p5s02b.json`) touch them, and whether the pairs appear in S1 (the base graph `94ffff94` json) already; whether the "doubled source uid" rows (3934, 4965) come from a wire that op 1/4/8 (delete_wire) deleted and re-created, i.e. whether a delete_wire action leaves the OLD wire's row in the real-end graph beside the new one.
4. Does the 26-row pred differ from the 31-row sim end by exactly the 5 extra pairs? Yes/no with the row lists.
5. Is `eq_diff []` (sim end == real end) true for the same reason at the old checkpoint set (0,2,3,5,7,9,10)? If a measurement answers it cheaply from saved graphs, quote; if it needs a rerun of the dry (offline only, ~66 s, `py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c161_b1_2_dry_old.log -- ...`, same form as `prep_c161_b1_1_dry.log`), run it ONLY on a COPY of the recipe in `tools/bench/` with the old set, never edit the real recipe; otherwise say 'not measured'.

## Report `tools/bench/diag_c161_b1_2_facts.md` (<= 40 lines, facts only)
PB definitions (file:line); the two row lists' symmetric difference; the 5 pairs with action ids; doubled-uid explanation as measured; `OPEN:` lines. md5 UNCHANGED: stagesim 95a162ba, stagexec a4df7e15, stagekit 0b5bb678, stage_prerun 7605116f, plan f4520b10, pred 18729409. Hook false positive: `py tools/gate_fp.py log ...`, report, no bypass.
