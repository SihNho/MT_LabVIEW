# Brief chat-N3 - matbench v1: fix v0 defects, then Opus 5.5 effort ladder (low / medium / high / max), n=2

Card chat-N2 built matbench v0 (`tools/bench/matbench/`, report_v0.md). The user (2026-09-26 10:2x) approved v1:

## v0 defects to fix first (all measured in report_v0.md "Validity notes")
1. T1 scoring: replace the facts_all wording group ['no LabVIEW run', ...] by the BEHAVIOUR: result card `cost.labview_runs == 0`
   (and no LabVIEW.exe seen by cell_guard). Keep the FlatSequence/frame-move group as required; make '9 of 11' a partial-only group.
   The workaround rule stays (designing around the missing verb = 0).
2. T4 environment: (a) restore worktree file mtimes from git commit times (git log -1 --format=%ct per file, or a
   checkout-time stamp of every tracked file to its last-commit time); (b) copy into the worktree the gate-release files
   that were committed WITH the card (recipe md5 1098a443, prior-art FIXED line, outcome review) - the card's own commit
   minus the card itself; verify with one Opus/medium dry cell that the pre-run is reachable (not BLOCKED by
   guard_cycle/guard_bash). If still BLOCKED after one fix attempt, DROP T4 from v1 and say so in the report.
3. T5 scoring: score = t5_struct 'equal to reference' (jaccard 1.0 = 1, else the jaccard), not the degenerate row metric.
4. Keep T2, T3, T6 as in v0.

## Conditions and repeats
- 4 conditions: claude-opus-5-5 at effort low / medium / high / max, agent shape = material (same spawn shape as v0's c0).
- n = 2 repeats per task x condition (repeat = same card, fresh worktree). 5-6 tasks x 4 x 2 = 40-48 cells, <= 3 in parallel.
- Cost guard: stop launching new cells if cumulative usd (from the cells' json) exceeds $120; report what ran.

## Report (report_v1.md)
- task x condition table with both repeats (score, minutes, usd), per-condition totals (mean score, mean minutes, total usd),
  variance between repeats per task (so a one-task difference can be called noise or not), notes per 0-score run.
- One paragraph, facts only: which effort level changes the SCORE, which only changes minutes/usd; the T3 uid group in
  particular (v0: Opus/medium missed 25240/25344/25382).
- Also re-score v0's fable/low and fable/medium cells with the v1 scorer (results_v0.json has the cards) so the two reports
  are comparable; put that as an extra table.
