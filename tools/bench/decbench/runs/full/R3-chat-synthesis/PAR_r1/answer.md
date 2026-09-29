**The summary is wrong. Its third line gets the cost the wrong way round, and its second line quotes A/B numbers that no file in this checkout contains.** Each point the analysts made held up when I checked it against the files.

**1. Strongest reason: line 3 compares a 5-run total with a 10-run total.**
- Fable low's $17.59 covers 5 runs. These are older v0 runs, one repeat per task, re-scored with the v1 scorer (`tools/bench/matbench/report_v1.md:65`, `:77`).
- Opus high's $15.24 covers 10 runs (`report_v1.md:17`).
- Per run, Fable low costs about $3.52 and Opus high about $1.52. Fable is roughly 2.3 times as expensive, not "about the same".
- Fable is also slower: 3.48 min against 2.56 min per run (`:77`, `:17`).
- Its cheapest single run cost $2.57, already above Opus high's average (`:69-73`).
- "5/5 vs 8/10" also sets one repeat against two.

**2. Line 2's numbers do not match the record.**
- 2.17, 1.57, $37.18 and $38.24 appear in no file outside `archive/`. The only "2.17" is an unrelated dollar loss (`docs/violation-decisions.md:1659`).
- Every recorded source says high 2.5 vs medium 2.0 PASS per cycle, at $33 vs $39, with n=4/5, "not decisive but never worse" (`CLAUDE.md:384-385`, `tools/cycle_runner.py:252`, `:1255`).
- The summary leaves out the "not decisive" caveat. A cost gap of about $1 over about 5 cycles per effort level cannot support "high is also cheaper".

**3. Line 1 is half right.**
- T2's average score also changes with effort: low 0.5, medium 1, high 1, max 0.5 (`report_v1.md:27`). So "only on T1 and T3" is false.
- "Only T1 exceeded repeat noise" is correct (`:34`). T3's spread between effort levels (1.0) only equals its spread between repeats (1), so it is not separable from noise (`:28`, `:43`).

**Alternative explanation for line 2.** The numbers may have been averaged over the wrong set of cycles. The medium/high alternation kept running past cycle 97, through cycle 103. Cycles 102 and 103 were "OVERRIDDEN" by the escalation rule, so they were not run at the effort level their parity assigned (`tools/bench/cycle_runner.log:470-545`). Averaging over 89-103 would give different figures from the recorded 89-97 ones. Otherwise the numbers are invented. I did not test either possibility.

**What would prove the summary right:**
- For line 3: Fable low costing about $1.5 per run when run twice per task in the same batch as the Opus runs. The report's $2.57–$5.03 per Fable run rules this out.
- For line 2: a result file for cycles 89-97 that actually gives 2.17 / 1.57 / $37.18 / $38.24.

**Cheapest test that separates the two.**
- Divide each total by its run count: 17.59/5 against 15.24/10. That settles line 3 in seconds.
- Then recompute PASS and cost per cycle from the cycle cards in `tools/bench/cycle_runner.log`, once for cycles 89-97 and once for 89-103.
  - If only 89-103 reproduces 2.17 / 1.57, the summary used the wrong range.
  - If neither range does, the numbers were made up.

The only parts that hold are "T1 is the only task above noise" and "high was not worse than medium". The summary should not be sent as written.

DEFECT: blocker - Line 3 compares Fable low's 5-run total with Opus high's 10-run total and calls the cost "about the same", when per run Fable costs about 2.3 times as much ($3.52 vs $1.52, report_v1.md:17,77); line 2's A/B figures also contradict the recorded 2.5 vs 2.0 PASS at $33 vs $39.