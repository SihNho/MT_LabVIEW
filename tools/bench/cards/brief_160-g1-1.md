---
card: 160-g1-1
status: current
date: 2026-10-10
---
# Brief 160-g1-1 (assignment 160-1) - OFFLINE FACTS TABLE: split A41..A80 into steps by whole groups (PD390(d))

`labview: none`: no LabVIEW process, no tool/recipe/plan/`tools/hooks` edit. You write `tools/bench/diag_c160_g1_1_facts.md` and, if you need one, a throwaway
`tools/bench/diag_c160_g1_1*.py`. `docs/script-writing.md` binds you: call the shared readers and the `prep_c159_c1_1_lib.py` helpers; do not paste blocks.
Take every number from files, never from memory. No step-3 plan file is written: a facts table only.

## Inputs (read)
- `docs/d1/ring-p5b.md` PD390(d) and PD388(h) (cut rule: whole groups, new LabVIEW instance per step, START_ASSUMED 603.4, MAIN <= 675 per step).
- `tools/bench/diag_c159_c1_1_facts.md` and `tools/bench/prep_c159_c1_1_mk.log` (groups, per-op MAIN, GAP/BLOCKED status), `tools/bench/memory_model.json` (5b87de43).
- `tools/bench/plan_ring_p5s02b_in.json` and `tools/bench/graph_ring_p5s02a_20261010_032547.json` (94ffff94) for the A41..A80 rows.

## Do
1. List the groups of A41..A80 (I A41-52, J A53-60, K3 A61-69, K3f A70, K4 A71-79, K4f A80) with action count, status (OK / GAP / BLOCKED, from the log) and, for the OK groups,
   the per-group MAIN cost as it would be in a FRESH instance (START_ASSUMED 603.4 + that group's ops through the memory model; reuse `prep_c159_c1_1_lib`/stagexec compile
   as the earlier card did; quote which function you called).
2. Apply the rule: greedy prefix of whole groups with MAIN <= 675 per step; a step ends where the next whole group would exceed 675 or where a GAP/BLOCKED group begins
   (a GAP/BLOCKED group has no compile, so it cannot be assigned a MAIN: say so). Name each step (p5s02c, p5s02d, ...) with action range, groups, MAIN, and the in-between
   file name pattern it would save (follow the naming of `D1_ring_p5s02a_20261010_023239.vi`; do not invent a timestamp).
3. State which verbs/steps a GAP or BLOCKED group is missing (quote the log line), as facts.

## Report `tools/bench/diag_c160_g1_1_facts.md` (<= 40 lines, facts only)
The table (step, actions, groups, ops, MAIN, start file, saved file pattern), the rule applied, GAP/BLOCKED rows with their log lines, `OPEN:` lines. No step-3 plan.
md5 unchanged (before/after): stagekit 1441bb4c, stagesim a3261b56, stagexec c4a6e0b6, stage_prerun 7605116f, plan input 56bfddd3, graph 7ac24924; `tools/hooks` untouched.
