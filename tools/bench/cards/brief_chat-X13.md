# Card chat-X13 - does docs/script-writing.md rules 10-15 ("Write less", from Ponytail) change how scripts are written?

User 2026-10-12: "추가하고 테스트". Rules 10-15 were added to docs/script-writing.md (this commit). Measure, offline, an
A/B on the same small scripting tasks: arm OLD = the file before rules 10-15 (`git show HEAD~0:docs/script-writing.md`
as of the commit BEFORE this one - find it with `git log -2 -- docs/script-writing.md`), arm NEW = the current file.
No LabVIEW, no hardware. Read docs/script-writing.md yourself first; new scripts carry the header at the TOP.

## Cells
- 3 tasks x 2 arms x 2 repeats = 12 `claude -p` cells: model claude-opus-5-5, effort high (the material default),
  env with BENCH_CELL=1, each bounded (<= 10 min) under bgrun; `--allowedTools Read Glob Grep Write Edit Bash` and the
  task's output path only. Each cell's prompt: the task text + "The script rules you must follow are in <arm file path>
  (a copy in your scratch folder); read it first. Do not read docs/script-writing.md." Put each arm's copy and each
  cell's output under tools/bench/xs_write_less/<arm>_<task>_r<n>/ (the cell writes ONLY there).
- Tasks (real recurring needs, real input files, read-only on them):
  T1 "Write count_gate_fp.py that reads tools/bench/gate_fp_queue.jsonl and prints the number of OPEN entries per gate
     class, then a RESULT line."
  T2 "Write el_diff.py that takes two Error List JSON files (use tools/bench/errorlist_*.json pairs) and prints the
     items in one but not the other, then a RESULT line."
  T3 "Write cycle_costs.py that reads tools/bench/cycle_runner.log and prints, per cycle, its cost and whether its
     assignment rounds ended PURPOSE_MET or HANDBACK, then a RESULT line."

## Measure per cell (mechanical first)
correct output on the real input (the cell's own run + your independent check), lines of code (non-blank, non-comment),
number of CLI options/flags not asked for, new imports beyond stdlib, presence of an assert self-check (rule 14), a
"skipped:" fact or line (rule 10), shortcut comments (rule 13), cost USD, minutes. Then ONE blind judge (fresh claude -p,
opus-5-5 high, read-only, A/B mapping recorded before judging) per task pair: which script is simpler without losing
correctness or edge handling (empty file, missing file), with reasons.

Return the report as TEXT (table per task x arm x repeat, totals per arm, what n=2 cannot show). Commit the bench
folder. The chat writes the report file.
