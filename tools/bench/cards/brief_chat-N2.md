# Brief chat-N2 — material-model replay bench (detail for the card's pass items)

1. `tools/bench/matbench/matbench.py`: for each task x condition make a git worktree at the task's base commit (the
   PARENT of the commit that added the card) under `<scratchpad>/matbench/<task>_<cond>`; copy the replay card in with
   flags labview none / run_vi false / gui false / hardware none; write limited to the worktree.
2. One run = one `claude -p` cell, same spawn shape as `cycle_runner.py`'s material dispatch (model+effort per
   condition, env CYCLE_SESSION=1 BENCH_CELL=1, cwd = worktree, `--output-format json` for usd), prompt `CARD <card>`,
   hard timeout = truth max_minutes + 5 through bgrun. The cell's hooks see the WORKTREE's tools/.
3. T5 (authoring) and T6 (log-reader) are new task/1 cards written from truth_v0.json's sources; T6 uses the
   log-reader agent shape (read-only). Fill truth_v0.json with the exact sources chosen (paths, md5, reference rows).
4. `score.py`: parse each run's result/1 card (0 if none/invalid); apply expect (status, facts_all / facts_any hit
   groups, max_minutes); record minutes, usd, dispatch count; T1 workaround rule (designing around the missing verb
   instead of reporting it = 0). No model judges.
5. Run 6 tasks x 3 conditions = 18 cells, at most 3 in parallel, each under bgrun; timeout = score 0 and logged;
   nothing touches LabVIEW (tasklist checked before/after each batch, no LabVIEW.exe ever).
6. `report_v0.md`: per-task x condition score table, totals / minutes / usd per condition, a note per 0-score run
   (which expect group missed); `results_v0.json` with every cell's raw fields.
7. `selftest_matbench.py`: dry mode (claude stubbed) runs the pipeline on 1 task x 3 conditions and scores fixed fake
   result cards (hit / miss / workaround / timeout) -> 6/0.
8. Worktrees pruned after scoring; main checkout untouched outside tools/bench/matbench/** and the new cards.
