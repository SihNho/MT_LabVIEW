**1. Strongest reason the claim is wrong: bullet 3 compares totals over unequal cell counts.** Fable low's $17.59 covers 5 cells (report_v1.md:77). Opus high's $15.24 covers 10 (report_v1.md:17). Per cell that is $3.52 vs $1.52, about 2.3×.
- Fable low costs more on every task ($2.57–5.03 at :69-73, vs $0.72–2.31 at :7-11) and is slower (3.48 vs 2.56 min).
- The repo itself records "3x cost" for the Fable-low trial (CLAUDE.md:380).
- The 5/5 vs 8/10 gap is one T1 cell. It scored 0 under the v0 scorer (report_v0.md:7,35) and 1 only after the scorer was rewritten (report_v1.md:40,69).

**Bullet 2 is mis-sourced.** For cycles 89-97 the repo records high 2.5 vs medium 2.0 PASS and $33 vs $39 (CLAUDE.md:384; brief_chat-N4.md:14), which matches the log (cycle_runner.log:356-467).
- The summary's 2.17 / 1.57 / $37.18 / $38.24 reproduce only from cycles 89-101 (6 high, 7 medium). That uses cycle_runner.log:356-525 plus result-card PASS counts.
- Widening the window cut the "saving" from about $6 to $1.06.
- Per-cycle costs span $14.8–58.5. My hand arithmetic puts the standard error of the cost gap at about $9.6. For PASS, the gap is 0.6 with SE about 0.55.
- So "cheaper" is a 2.8 % gap inside noise. CLAUDE.md:385 itself says "not decisive".

**Bullet 1 is selective.** T2 also varied (0.5 / 1 / 1 / 0.5, report_v1.md:27), and only T5 and T6 are listed as unchanged (:34). By the report's own rule (:22,28), T3 is no more separable from noise than T2. "Only T1 exceeded noise" is correct (:34), but it rests on the max condition alone (:26).

**2. Alternative explanation.** Cycle cost is the whole-session `total_cost_usd` (cycle_runner.py:1515-1516). It tracks the work NEXT assigned: cycles 93, 94 and 96 cost about $15–16, while cycle 100 cost $58.5 (log :411,425,452,510). Odd/even alternation (cycle_runner.py:266-272) is not randomisation. PASS per cycle counts material-card outcomes, not judgement quality. Fable's "same cost" is a denominator artefact.

**3. Falsifier.** Fable low's per-cell cost is at or below Opus high's. Or high is cheaper than medium by more than about 2 SE over at least 10 cycles each.

**4. Cheapest discriminating test.** Divide the totals by cell count, which is free. Then run a permutation test on the 13 per-cycle costs and PASS counts already logged. For causation, replay one frozen cycle card at both efforts, twice each.

Only bullet 1's second clause survives. I would revisit bullet 3 only if the 5-vs-10 cell counts were wrong.

DEFECT: major - Bullet 3 compares a 5-cell total with a 10-cell total, so "about the same" is really about 2.3× per cell (report_v1.md:17,77), and bullet 2's "cheaper" is a $1.06 gap inside about $9.6 of noise, drawn from a window other than the one stated.