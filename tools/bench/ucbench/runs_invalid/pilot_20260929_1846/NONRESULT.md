# NON-RESULT: card chat-B5 pilot attempt 1 (invalid, not to be scored or cited)

- run: `ucbench.py --tasks L1 --arms UC --reps 1 --par 1 --cap-min 60 --no-score --guard-usd 450 --tag pilot`
- started: BGRUN START 2026-09-29 18:46:53 (pilot_run.log, BGRUN PID 23968); lock re-verify 18:46:04 PASS (lock_pilot.log)
- interrupted: last write to cell.log / calls.jsonl 2026-09-29 19:03:05; no BGRUN END/TIMEOUT line, no RESULT line,
  no answer.md, no results_pilot.json. At that point the UC cell had 773 hook-logged calls, one Workflow task
  (wu36ig63h) at 3,746,873 cumulative tokens / 762 tool uses / 573 s.
- why invalid: interrupted mid-run (CLAUDE.md usage-limit rule 3: an interrupted benchmark cell is rerun from the
  beginning; partial numbers never enter a results table).
- moved here 2026-09-29 23:1x by the chat-B5 rerun (agent a7be57c7d08ef37a8); the stale worktree %TEMP%\ucb\L1 left
  by the attempt was removed (`git worktree remove --force`) before the rerun.
