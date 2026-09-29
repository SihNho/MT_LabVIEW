**The summary is wrong in two of its three bullets, and it should not be sent as written.**

**1. Strongest reason it is wrong: the Fable cost comparison sets a 5-cell total against a 10-cell total.**
- Fable low's $17.59 covers 5 cells, one repeat per task (`tools/bench/matbench/report_v1.md:65`, `:77`).
- Opus high's $15.24 covers 10 cells (`report_v1.md:17`).
- Per cell that is about $3.52 against about $1.52, so Fable costs roughly 2.3 times as much, not "about the same".
- The two results also come from different runs. The Fable cells are v0 runs re-scored with the v1 scorer (`report_v1.md:65`), and the Opus cells ran in the v1 batch (`report_v1.md:43-44`).

**2. The judgement A/B figures do not match what the repository records.**
- Every recorded source gives high PASS 2.5 against 2.0 per cycle, at $33 against $39, with n=4/5 (`CLAUDE.md:384`, `tools/cycle_runner.py:252`, `tools/cycle_runner.py:1255`).
- The summary's 2.17/1.57 and $37.18/$38.24 appear nowhere I searched.
- Even taken at face value, "high is also cheaper" would rest on a 3 % gap with n of about 5 per arm. CLAUDE.md calls the result "not decisive but never worse" (`CLAUDE.md:384`).

**3. Bullet one is also incomplete.** Effort changed T2's per-condition mean as well: low 0.5, medium 1, high 1, max 0.5 (`report_v1.md:27`). What is true is that only T1's spread between effort levels exceeds the spread between repeats (`report_v1.md:34`). T3's spread is 1.0 against a repeat spread of 1 (`report_v1.md:28`), so it does not exceed noise.

**Alternative explanation of the same evidence**
- 2.17 ≈ 13/6 and 1.57 ≈ 11/7. That suggests the summary averaged the A/B log through cycle 101, which gives 6 high and 7 medium cycles (`tools/bench/cycle_runner.log:346-513`), instead of the stated range 89-97.
- Cycles 102-103 were overridden by the escalation ladder (`tools/bench/cycle_runner.log:530`, `:545`), so the window someone chooses changes the result.
- If this is right, the "high is cheaper" sign depends on that window choice, not on the effort level.

**What would falsify the claim**
- For bullet 2: per-cycle PASS and cost for cycles 89-97 that reproduce 2.17/1.57 and $37.18/$38.24.
- For bullet 3: no per-cell comparison can make $3.52 against $1.52 "about the same". A Fable/low v1 rerun with 2 repeats (10 cells) that comes in near $15 would change the conclusion.

**Cheapest discriminating test**
- Read the `CYCLE n |` cost and PASS lines in `tools/bench/cycle_runner.log` for cycles 89-97, then for 89-101, and average them per arm.
- If 89-97 gives 2.5/2.0 at $33/$39 and 89-101 gives 2.17/1.57, the summary used the wrong window.
- Separately, divide each Fable and Opus total by its cell count. This is arithmetic on figures already in `report_v1.md:17` and `:77`.

DEFECT: major - The summary calls Fable low "about the same cost" by comparing a 5-cell total to a 10-cell total (about 2.3× per cell), and its A/B figures do not match the recorded 2.5 vs 2.0 PASS at $33 vs $39.