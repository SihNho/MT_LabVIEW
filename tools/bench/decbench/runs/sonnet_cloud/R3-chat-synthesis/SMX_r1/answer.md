**1. Strongest reason it is wrong: bullet 3 compares totals over unequal n.**
- Fable/low is 5 cells, one repeat each, from a v0 batch that was re-scored (`report_v1.md:77,65`). Opus/high is 10 cells, n=2 per task (`report_v1.md:17,43`).
- Per cell that is $3.52 vs $1.52, about 2.3×, not "about the same". On the same five tasks it is $17.59 vs $7.62. Fable is also slower (3.48 vs 2.56 min).
- The repo's own record agrees: the Fable-low trial cost "3x" (`CLAUDE.md:380`).
- "5/5 vs 8/10" is not separable at this n. It also leans on the re-score: v0's scorer gave Fable-low T1 = 0 (`report_v0.md:7`), v1's gives 1 (`report_v1.md:69`).

**Other defects**
- **Bullet 2's window is mislabelled.**
  - The figures reproduce only over cycles 89–101 (7 medium, 6 high). PASS cards in `tools/bench/cards/result_*.json` give 11/7 = 1.57 and 13/6 = 2.17. CYCLE costs (`tools/bench/cycle_runner.log:356…525`) give $267.69/7 = $38.24 and $223.08/6 = $37.18.
  - The stated 89–97 gives 2.5 vs 2.0 PASS and $33 vs $39 at n=4/5, "not decisive" (`CLAUDE.md:384-385`, `brief_chat-N4.md:14`).
  - "High is also cheaper" rests on $1.06 (2.8%). Per-cycle cost spans $14.81–$58.53 in both arms (SD ≈ $14–19).
- **Bullet 1 omits T2.** Its means are 0.5/1/1/0.5 (`report_v1.md:27`), which supplies one of the two low→medium points. The report names only T5 and T6 as unchanged (`report_v1.md:34`).

**2. Alternative explanation.**
- Cycle cost and PASS count track the task and the material model, not judgement effort. Cycles 89–91 ran material on Fable low at ~3× cost (`CLAUDE.md:380`), costing $50–57 each (`cycle_runner.log:356,369,382`). The medium arm holds two of those three.
- Arms alternate by parity (`cycle_runner.log:346,359`), so each cycle's NEXT is set by the opposite arm.
- PASS counts cards, which depends on how many the judge cuts.
- Dropping cycle 99 (0 PASS) alone shrinks the PASS gap from 0.60 to 0.33.

**3. What would falsify it.**
- Fable-low per-cell cost within ~1.2× of Opus-high on matched tasks.
- For the A/B, the ordering flipping under a one-cycle change. Within-arm spread already gives t ≈ 1.1 on PASS and ≈ 0.1 on cost.

**4. Cheapest discriminating test.** Divide the `results_v1.json` totals by cell counts, which costs nothing. Then recompute the A/B on 89–97 from `cycle_runner.log` with SDs. If equal n is wanted, run Fable-low repeat 2 of the five tasks (~$18).

**What survives:** "only T1 exceeded repeat noise" (`report_v1.md:34`). I would change my mind on bullet 3 only if per-cell costs turned out equal.

DEFECT: major - "Fable costs about the same" compares $17.59 over 5 cells with $15.24 over 10, when per cell Fable low costs about 2.3× Opus high.