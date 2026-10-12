---
type: bench
status: current
date: 2026-10-12
tags: [bench, scripts, rules]
---
# Write-less rules A/B (docs/script-writing.md rules 10-15, from Ponytail) - cards chat-X13 + chat-X13b

Written by the chat from the cards' hand-backs. Raw: results.json, judge_results.json, judge_mapping.json (written
before judging), run_bench.py, cells_b1.log, cells_b2.log, judge_b.log (commits b6d87022, e1d07e9e).
3 real tasks x OLD/NEW doc x 2 = 12 claude -p cells (opus-5-5 high). X13: 5 cells lost to the bench's relative Write
rule after a `cd` (fixed with an absolute rule in X13b and re-run).

| | OLD (rules 1-9) | NEW (+ rules 10-15) |
|---|---|---|
| lines of code (12 cells) | 174 | 244 (+40 %) |
| assert self-checks (rule 14) | 0 | 21 |
| unasked options | 1 | 0 |
| shortcut notes (rule 13) | 0 | 2 |
| "skipped:" line (rule 10) | 0 | 1 of 6 |
| missing / empty input file (T2) | traceback / traceback (both cells) | RESULT line in 3 of 4 checks |
| blind judge "simpler without losing correctness" | 1 of 6 pairs | **5 of 6 pairs** |
| cost / time | $4.24 / 6.7 min | $4.94 / 7.9 min |

- Judges named missing/empty-file handling and the asserts as why NEW won T1/T2; they picked OLD in T3 r2 because the
  NEW script grew to ~100 lines with a fallback regex.
- Correctness vs a truth: T3 4/4 both arms. T1 and T2 truths were defined badly by the chat (T1 "class" read as
  checker/non-checker, which no script printed; T2 raw vs OCR-folded rows never fixed) - not a verdict on either arm.
- n = 2 per task and arm; run-to-run noise is as large as the arm effect on T1 grouping.

## Reading
The rules made scripts MORE ROBUST (edge handling, asserts) and judged simpler, but LONGER - rule 14's asserts add
lines, which is the opposite of Ponytail's "less code" aim. Rule 10 ("skipped:") barely took hold (1 of 6).
