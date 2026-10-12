---
type: bench
status: current
date: 2026-10-12
tags: [bench, models, subscription]
---
# X10 - GPT vs Claude on the same replayed material cards (matbench T1, T2, T3, T5, T6)

Card chat-X10e (result_chat-X10e.json, commit 6b8ffef7), after X10-X10d (blocked on GPT-cell guarding) and the
Claude-GPT agreed hook fix scope-cwd-fix-20261012 (card chat-X11, c4efa1ec). Written by the chat from the card's
hand-back (sub-agents cannot write report files). Raw data: tools/bench/matbench/x10/ (runs/<task>_c2_r<n> = Claude,
runs/<task>_c9_r<n> = GPT; results_x10.json; blind_mapping.json written before scoring, seed 61012).

## Setup
Claude arm: opus-5-5 / high, matbench condition 2, base-commit hooks + cell_guard. GPT arm: gpt-6.1-sol / high via
`codex exec --profile matbench -s danger-full-access` in the fixed cell ..\V6_bench\gpt_cell (hook trusted by the user:
codex_cell_hook.py = cell_guard + adapt_codex/guardcore), same bench-cell markers (matbench.CELL_MARKERS), AGENTS.md =
the base commit's CLAUDE.md + material.md. Step 0 live 7/7 (x10/x10e_step0_regate.log:18-25). Blind mechanical scoring.

| task | Claude r1 | Claude r2 | GPT r1 | GPT r2 |
|---|---|---|---|---|
| T1 | 0 / 1.68 min / $1.50 | 0 / 2.12 / $1.28 | 0 / 4.28 / 5h 23->28 % | 0 / 4.70 / 3->8 % |
| T2 | 1 / 2.21 / $1.41 | 1 / 2.36 / $1.49 | 1 / 3.56 / 28->33 % | 0 / 3.45 / 8->12 % (fact 490 chars) |
| T3 | 1 / 2.89 / $1.63 | 1 / 2.24 / $1.49 | 0 / 5.54 / 33->38 % (fact 265 chars) | 1 / 4.19 / 12->17 % |
| T5 | 1 / 4.37 / $1.88 | 1 / 12.68 / $2.28 | 1 / 7.07 / 38->1 % (window reset) | 1 / 5.63 / 17->22 % |
| T6 | 1 / 0.95 / $0.81 | 1 / 0.67 / $0.70 | 0 / 1.27 / 1->3 % (no valid card) | 0 / 2.89 / 22->24 % (extra fields) |

| | Claude opus-5-5 high | GPT gpt-6.1-sol high |
|---|---|---|
| score | **8/10** (same as matbench v1 high) | **4/10** |
| wall time | 32.2 min (3.2 / cell) | 42.6 min (4.3 / cell) |
| tokens | 17.8M cache read, 0.85M cache write, 96.7k out | 10.6M in (9.79M cached), 76k out, 13.6k reasoning |
| cost / plan use | $14.47 (list); Claude Max 20x weekly 0 -> 2 % over the WHOLE day's work (bench + other cards + discussions) | ChatGPT Plus: 5-hour window ~38 points, weekly 4 -> 11 % (step 0 included) |

## What the numbers do not show (read before deciding)
- **GPT was handicapped by tooling, not only by skill.** (1) The GPT cell runs the main tree's CURRENT hooks; their
  scope-header rule refused September base-commit scripts that carry no header (tools/protocol.py, stagesim.py, task
  scripts): 8 refusals in 7 cells. GPT could not run `py tools/protocol.py validate`; Claude validated its card in all 10
  cells. Three of GPT's six zeros are card-FORMAT failures (fact > 200 chars, BOM + missing gates, extra fields) that
  the validator would have caught. (2) A bug in codex_cell_hook.py (fail-closed UnicodeEncodeError on Korean text)
  denied 2 GPT calls (T3 r1, T6 r1). (3) 4 relative-path refusals (the agreed scope-cwd rule) cost GPT re-runs.
- n = 2 per task and arm, one setting each; September tasks; mechanical scorer; the logs name their model (blinding
  covers bookkeeping only). Claude T5 r2's token count covers its last turn only.
- Plan-use units differ: Claude's weekly % includes everything done that day; GPT's is measured per cell on Plus.
