---
card: 150-a3-4
status: current
date: 2026-10-08
---
# Brief 150-a3-4 - RETRY of 150-a3-3 (parser device): refine the helper's heading rule; offline, ALONE

Everything in `tools/bench/cards/brief_150-a3-3.md` applies (hooks never edited; gate_fp entries fp-67..fp-70 are ALREADY logged - do NOT log them again). Read `tools/bench/diag_c150_a3_3_facts.md` (7b93f400) first.
150-a3-3 FAILED only on its own archive-output gate: with the plain LAST-heading rule, 10 archived files with TWO column-0 headings and no inline quote change output - 8 improve (pattern A: placeholder first, real second), 2 regress
(pattern B: `23c-r2.md:52,87`, `retrospective-cycle17.md:12,281`: real text under the first heading, placeholder under the last; the cycle17 answer then absorbs the first disposition text and `violations.py` counts a slug it did not count before). The plan word is "LAST line-anchored"; the facts show it is not enough alone.

## Change (the ONLY change; edits are on the 150-a3-3 outputs, which are in your write globs)
1. `tools/dispo.py`: the disposition heading = the LAST column-0 `## What was done with it` whose section body (placeholder `(Claude fills in)` stripped) is NON-EMPTY; if every heading's section is empty/placeholder, the LAST heading (so `retro_undisposed` and A4 still call it undisposed).
   `find_disposition` returns the answer = text before THAT heading. Document the rule in one comment line. An inline quote is still not a heading.
2. Sites unchanged (violations.py:177, cycle_runner.py retro_undisposed, audit_cycle.py A4 :619 and A9 :326) - re-point only if the function signature changes (it should not).
3. `tools/bench/selftest_c150_a3_3.py`: add cases for patterns A and B (copies of `23c-r2.md` and `retrospective-cycle17.md`, plus a synthetic pair) and an all-placeholder file with two headings. Show the OLD-code count (first-occurrence code from `tools/bench/prep_c150_a3_3_old_*.txt`) still fails at the 3 sites and the new passes; quote both.
4. Archive-output gate re-run over the 1119 files: expected outcome = pattern A 8 files fixed, pattern B 2 files UNCHANGED vs old output, inline-quote files as before (V cycle49/148/149, R cycle16/16b/26, A4 8 files). Any other difference is a RETURN with the file list.
5. Regression as brief 150-a3-3 step 4: `py tools/violations.py` 0 awaiting, retrospectives 148 and 149 listed, cycle17 tally back to its OLD value (quote both); old self-tests same counts as in the 150-a3-3 facts (cycle_runner_retro 9/0, audit_a9_witness 10/0, c116a_landed 14/4 rc1 pre-existing, stamp_window 15/0).
6. Invariants md5 as brief 150-a3-3 step 6, hooks tree md5 before = after (only `material_marker.log` may move).

## Return conditions
A hook edit needed; an output difference outside the expected list; old self-test counts moving; a gate refusing twice at the same place (gate_fp first).

## Report `tools/bench/diag_c150_a3_4_facts.md` (<= 30 lines)
New rule in one sentence, self-test old vs new counts, archive-output gate result (file counts per pattern), violations listing + cycle17 tally old/new, old self-test counts, files changed (md5 before/after), invariants, `OPEN:`. Facts only.
