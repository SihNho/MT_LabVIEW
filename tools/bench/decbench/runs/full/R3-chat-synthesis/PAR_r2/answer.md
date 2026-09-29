**The summary should not be sent as written.** Bullet 3 reverses the cost finding, and bullet 2 uses A/B numbers that no file records. I checked each analyst's main claims against the files, and all of them held.

**1. Strongest reason it is wrong (bullet 3).** "Fable costs about the same" compares totals over different numbers of runs.
- Fable low's $17.59 covers **5 runs**, one repeat per task (`tools/bench/matbench/report_v1.md:65`, `:77`).
- Opus high's $15.24 covers **10 runs** (`report_v1.md:17`).
- Per run that is about **$3.52 for Fable against $1.52 for Opus, roughly 2.3×**. Fable is also slower: 3.48 vs 2.56 mean minutes (`:77`, `:17`).
- The two sets were not scored the same way. The Fable runs are older v0 runs re-scored with the v1 scorer, n=1 (`:34`, `:65`). The Opus runs are v1 with n=2 (`:43`). So "5/5 vs 8/10" is not a like-for-like quality comparison either.
- The project's own record of the live Fable-low trial is "3x cost" (`CLAUDE.md:377`).

**2. Bullet 2's numbers have no source.**
- The recorded result is "high PASS 2.5 vs 2.0 per cycle, $33 vs $39, n=4/5, not decisive but never worse" (`CLAUDE.md:384-385`). The same figures appear in `tools/cycle_runner.py:252`, `tools/cycle_runner.py:1255` and `tools/bench/cards/brief_chat-N4.md:14`.
- A search for 2.17, 1.57, 37.18 and 38.24 finds none of them as A/B figures. 2.17 and 1.57 appear only as run times (`report_v1.md:8-9`); 2.17 also appears as an unrelated loss figure (`docs/violation-decisions.md:1659`).
- The recorded cost gap is about $6, not $1. "So high is also cheaper" also drops the n=4/5 sample size and the "not decisive" verdict.

**3. Bullet 1 is half right.**
- "Only T1 exceeded repeat noise" matches the report (`report_v1.md:34`).
- "Changed the score only on T1 and T3" is wrong. T2's mean score also moves with effort: low 0.5, medium 1, high 1, max 0.5 (`:27`). That movement is within repeat noise, but it is still a change.
- T3 sits exactly at the noise boundary: its within-repeat range is 1 and its between-condition range is 1.0 (`:28`).

**Alternative explanation of the same evidence.** The A/B figures may come from a wider window of cycles. The JUDGE-AB tags continue past cycle 97 to cycle 103, and cycles 102–103 were overridden by the escalation ladder (`tools/bench/cycle_runner.log:470-545`). In cycles 89–97 alone the arms are medium = 89, 91, 93, 95, 97 and high = 90, 92, 94, 96, which is the recorded n=4/5 (`cycle_runner.log:346-456`). For bullet 3, the writer most likely read "total usd" as a per-run figure.

**What would falsify these objections.**
- For bullet 3: a matbench record of Fable-low cost over 10 v1 runs that comes to within about 15 % of $1.52 per run.
- For bullet 2: a tally over cycles 89–97 that gives exactly 2.17 / 1.57 and $37.18 / $38.24.

**Cheapest test that separates the two readings.** Divide each condition's total cost by its run count (`report_v1.md:17`, `:77`): $17.59 / 5 against $15.24 / 10. Then recompute PASS and cost per cycle from the result cards for cycles 89–97 only, grouped by the arms at `cycle_runner.log:346-456`. That tally gives either 2.5/2.0 or 2.17/1.57, which settles bullet 2.

DEFECT: major - The summary calls Fable "about the same" cost by comparing a 5-run total with a 10-run total, when Fable costs about 2.3× as much per run, and its judgement A/B figures (2.17/1.57, $37.18/$38.24) contradict the recorded "2.5 vs 2.0, $33 vs $39, n=4/5, not decisive".