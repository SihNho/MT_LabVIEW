**I don't think the summary should be sent as written.** Its third bullet is wrong, the A/B numbers in the second bullet don't match anything in the repo, and the first bullet leaves out T2.

**1. Strongest reason it is wrong (bullet 3).** It compares two totals built from different numbers of runs.
- Fable low's $17.59 covers 5 runs, one per task, re-scored from v0 (`tools/bench/matbench/report_v1.md:65,77`).
- Opus high's $15.24 covers 10 runs, two per task (`report_v1.md:17,43`).
- Per run, Fable low costs about $3.52 and Opus high about $1.52, so Fable is roughly 2.3× dearer. It is also slower: 3.48 min against 2.56 min (`:17,77`).
- "About the same" reverses the finding. CLAUDE.md records the same bench as Fable low running "at half of max's minutes", which compares it with Opus max, not high (`CLAUDE.md:378,411`).

**Bullet 2: the numbers don't match the record.** The recorded A/B result is "high PASS 2.5 vs 2.0 per cycle, $33 vs $39, n=4/5" (`CLAUDE.md:384`). The figures 2.17, 1.57, $37.18 and $38.24 appear in no file in this checkout. The record also calls the result "not decisive but never worse" (`CLAUDE.md:384`), but the summary drops that caveat and n=4/5, and draws a cost conclusion ("also cheaper") from a $1 gap.

**Bullet 1: incomplete.**
- T2's mean score also differs by effort: low 0.5, medium 1, high 1, max 0.5 (`report_v1.md:27`). So effort did not change the score "only" on T1 and T3.
- T3's spread between effort levels (1.0) does not exceed its spread between repeats (1) (`:28`), so it can't be separated from noise. The report's own wording is that only T1 exceeds repeat noise (`:34`).

**2. Alternative explanation of the same evidence.**
- **Bullet 2:** 2.17 ≈ 13/6 and 1.57 = 11/7. That fits a wider window of 6 high and 7 medium cycles, i.e. cycles 89–101. The runner went on logging `JUDGE-AB` past cycle 97, to cycle 101 and beyond (`tools/bench/cycle_runner.log:485,513`). Cycles 102–103 were overridden by the escalation ladder (`:530,545`). So the summary probably used a different cycle window from the recorded 89–97 A/B, rather than adding new information. This is a guess from the arithmetic, not confirmed.
- **Bullet 3:** Fable's 5/5 is one repeat per task from a different run batch, v0 (`report_v1.md:65`). Opus high was 0 on T1 in both repeats (`:7`), and the Fable cells don't have that "missing verb" gap (`:69`). The difference could come from the batch rather than the model, and with n=1 it can't be separated from repeat noise (`:43`).

**3. What would falsify the claims.**
- **Bullet 3:** Fable low and Opus high cost the same per run when both get two repeats under the v1 scorer.
- **Bullet 2:** a runner-log tally for cycles 89–97 that gives 2.17 / 1.57 and $37.18 / $38.24. If it gives 2.5 / 2.0 and $33 / $39 instead, as `CLAUDE.md:384` says, the summary's numbers are wrong for that window.

**4. Cheapest discriminating test.**
- Sum the per-cycle `$` figures and the PASS-card counts from the `CYCLE <n> |` and `JUDGE-LADDER` lines in `tools/bench/cycle_runner.log`. Do it twice: once for cycles 89–97 and once for 89–101. Whichever window gives 2.17 / 1.57 is the one the summary used.
- For bullet 3, divide each total by its run count. That takes seconds and already refutes "about the same".

DEFECT: major - Bullet 3 compares a 5-run Fable total with a 10-run Opus total, so a roughly 2.3× higher cost per run is reported as "about the same", and bullet 2's A/B numbers don't match the recorded 2.5 vs 2.0 / $33 vs $39 (n=4/5) result.