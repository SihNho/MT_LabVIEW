---
card: 150-a1-3
status: current
date: 2026-10-08
---
# Brief 150-a1-3 - MEASURE why `--rebase` of s07 onto the real s06 graph is refused (BINDING); offline, no tool edit

Retry of card 150-a1-1 (FAIL). Read `tools/bench/diag_c150_a1_1_facts.md` first (sec. 2 is the refusal). This card MEASURES; it does not choose a fix.

## What is known
`py tools/stage_prerun.py --rebase tools/bench/plan_ring_p4_s07v18.json --graph tools/bench/graph_ring_p4s06_20261008_192149.json` ->
`REBASE REFUSED: BINDING: the created objects differ (name-free shape): ['BuildArray x0 simulated vs x1 real', 'LoopTunnel x2 simulated vs x3 real']`
raised at `tools/stage_prerun.py:3849`. The shape comparison is at :3830-3849: `sim_new` = terminals of the plan's provisional end that are not in the
base (`prov`), `real_new` = terminal rows of the real graph whose identity (term uid, owner uid, name) is not in N's base (`before`).
Creation map used: `tools/bench/creation_map/plan_ring_p4_s06v18_cfbd9823_20261008_175325.jsonl` (md5 99f9d253, obj 4, diag 0, term 8).

## Steps (measurement only; no edit of any stage tool, hook, elrule, or protected file)
1. **Read** `tools/stage_prerun.py` around the `--rebase` function (the lines before :3849, from where `prov`, `before`, `real` are built) to see exactly
   where `before` and `prov` come from for a plan on a given `sim_of`. State in one line each: what `before` is, what `prov` is, what `real` is.
2. **Identify the unmatched objects.** With a card-local script `tools/bench/diag_c150_a1_3_probe.py` (labview none; imports `stage_prerun`/`stagekit`
   read-only, no write outside `diag_c150_a1_3*`), reproduce `sim_new` and `real_new` for the s07 plan and print, per node: node class, owner/parent
   structure, term uids, the `shape()` key. Name the ONE BuildArray and the TWO extra LoopTunnels that exist in `real_new` but not in `sim_new` (uids,
   which structure the tunnels sit on, which terminal the BuildArray feeds) and say which s06 plan row created or touched them (grep the s06 plan
   `plan_ring_p4_s06v18.json`, `_licence.json`, creation map; the s06 licence renames and the reused wire uid 23807 are hypotheses, not facts).
3. **Why the earlier rebases passed.** Find the s05 -> s06 rebase log (`diag_c147_*` rebase logs, `prep_c147_*rebase*`) and state whether its `before`/`prov`
   came from the same kind of `sim_of` (stagesim end of the previous stage) and what differed. One short paragraph with file:line.
4. **Fallback.** Copy `tools/bench/plan_ring_p4_s07v18_prov148.json` to `tools/bench/plan_ring_p4_s07v18_fb150.json` (a COPY; the 30-action
   `plan_ring_p4_s07v18.json` md5 10a4f59a must stay byte-identical) and run `py tools/stage_prerun.py --rebase tools/bench/plan_ring_p4_s07v18_fb150.json
   --graph tools/bench/graph_ring_p4s06_20261008_192149.json` under bgrun if the hook asks for it (offline, short). Quote rc and the last 3 lines. If it
   PASSES quote the new plan md5 and base; if refused quote the refusal verbatim and whether it is the same BINDING list.
5. If step 2 shows a cause that is a fault of the input data (not of the stage tool), state it. If a fix needs a stage-tool edit (`stage_prerun.py`,
   `stagekit.py`) or a design choice, say so with file:line and RETURN; do not edit.
6. Invariants (md5 before/after): stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun dcd45aba, s06 569ffbf5, s05 3f9ac26b,
   s04 95e408ff, bed 39511877, memory_model 8eec443c, adopted_scratch 658fe5b9, graph a3ecb92b, the s06 plan/pred/licence/recipes, `sim/ring_p4_s06v18`
   tree, plan_ring_p4_s07v18.json 10a4f59a, `_in` 7b890070. No byte copy of a VI, no LabVIEW process.

## Return conditions
A protected md5 moved; the probe needs a write outside `diag_c150_a1_3*` / `plan_ring_p4_s07v18_fb150*`; a stage-tool edit is needed (that is a RETURN
with file:line, not a failure to hide).

## Report (`tools/bench/diag_c150_a1_3_facts.md`, <= 35 lines)
Sec. 1 what before/prov/real are (file:line). Sec. 2 the unmatched BuildArray + LoopTunnels (uids, owners, creating s06 row). Sec. 3 why s05->s06 passed.
Sec. 4 fallback result verbatim. Sec. 5 invariants. `OPEN:` line. Facts only; no fix is chosen here.
