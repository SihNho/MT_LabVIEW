---
card: 149-a3-4
status: current
date: 2026-10-08
---
# Brief 149-a3-4 - s07: REBASE on the real s06 graph, then dry + prerun on current bytes; NOT launched (PD363(d))

Offline prep card, runs beside the census LabVIEW card 149-a3-3 (no LabVIEW, camera or motor). Read `tools/bench/diag_c148_a3_3_facts.md` and
`tools/bench/cards/brief_148-a3-3.md` first: they built the s07 plan, pred and recipes on a PROVISIONAL s06 base. The real s06 graph now exists:
`tools/bench/graph_ring_p4s06_20261008_192149.json` (a3ecb92b, 6062 rows, 25 loops, 23 FS, E5 PASS). s06 is adopted: claudeDev
`D1_ring_p4s06_20261008_174730.vi` (569ffbf5).

## Steps
1. **Inputs read:** the s07 plan `plan_ring_p4_s07v18.json` (aeae610e), pred (e888ab67), recipes `stage_d1_ring_p4_s07v18.py` (d6c8da7b) and
   `_scratch.py` (273dc3de), the makers `prep_c148_a3_3_mk.py` and `prep_c147_a1_3_mk.py`. Quote their current md5 and the plan's provisional marker.
2. **Rebase:** `py tools/stage_prerun.py --rebase tools/bench/plan_ring_p4_s07v18.json --graph tools/bench/graph_ring_p4s06_20261008_192149.json`
   (the form `diag_c148_a3_3` / the earlier `--rebase` logs used; find it by grep in `tools/bench/diag_c147_*` and quote the log line you copy). Quote the
   command output: base rule numbers before and after, rows, any gate line, the plan md5 before/after. If the CLI differs from the stage_prerun source,
   quote the source line (file:line) of the form actually accepted; no stage-tool edit.
3. **Dry + prerun on the CURRENT bytes** of the s07 pair and the plan (MAIN and scratch recipes), `--scratch-required` (expected exit 3 per the s06
   pattern): outputs quoted (PASS or the first failing gate and its file:line). Quote X10 for MAIN and scratch, the margins to 680 / 695, and the first
   op over 680 if any. A false-positive gate goes to `tools/bench/gate_fp_queue.jsonl` via `tools/gate_fp.py`, never by an env bypass.
4. **Not launched:** no `--launch`, no LabVIEW process. Recipes and plan changed only if the rebase tool rewrites the plan; every changed file listed by
   md5 before/after.
5. **Invariants:** stage tools, claudeDev files, memory_model 8eec443c, adopted_scratch.jsonl 658fe5b9, `sim/ring_p4_s06v18/**`,
   `graph_ring_p4s06_*` unchanged by this card.

## Return conditions
A rebase refusal (quote file:line and the refusal text, no workaround by editing a stage tool); a prerun gate failing twice at the same place; a protected
md5 that moved.

## Report (`tools/bench/diag_c149_a3_4_facts.md`, <= 35 lines)
Rebase output, plan md5 before/after, dry + prerun results with X10 numbers, exit codes, files changed, invariants, no LabVIEW. `OPEN:` line. Facts only.
