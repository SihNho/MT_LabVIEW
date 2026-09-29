Done checking both sources. The summary is wrong in two places: bullet 3 makes Fable look about 2.3× cheaper per cell than it is, and bullet 2's numbers come from a different range of cycles than the one it cites.

**1. Strongest reason: bullet 3 compares totals over different numbers of cells.** Fable low's $17.59 covers 5 cells, one repeat each (tools/bench/matbench/report_v1.md:65, :77). Opus high's $15.24 covers 10 cells (report_v1.md:17). Per cell that is $3.52 vs $1.52, about 2.3×, or about 1.85× per point scored. Fable low actually costs about what Opus **max** costs per cell ($3.31, report_v1.md:18). For "about the same" to hold, the per-cell costs would need to be within roughly 10 % of each other.

**Bullet 2 uses cycles 89–101, not 89–97.** Its figures come out exactly when high = cycles 90…100 and medium = cycles 89…101:
- High: 13 PASS results / 6 cycles = 2.17; $223.08 / 6 = $37.18.
- Medium: 11 / 7 = 1.57; $267.69 / 7 = $38.24.

The costs come from the CYCLE lines (tools/bench/cycle_runner.log:356–525). The PASS counts come from the HEARTBEAT lists (log:393, :479, :494, :523), which count only `status == "PASS"` results (tools/cycle_runner.py:1166). Over the cited cycles 89–97, the same lines give 2.5 vs 2.0 PASS per cycle and $33.42 vs $39.41, which is what CLAUDE.md:384 records.

**Bullet 1 leaves out T2.** T2's mean scores vary with effort (0.5 / 1 / 1 / 0.5, report_v1.md:27), and the report lists only T5 and T6 as unchanged (:34). "Only T1 exceeded repeat noise" is correct (:34), at n = 2 (:43).

**2. Alternative explanation.** Fable's "same cost" comes only from it having half as many runs. The high/medium gap can come from which cycles landed on which side, not from effort:
- Cycles go to high or medium by odd/even cycle number, not at random (log:346).
- Cycles 89–91 were the trial that ran material (worker) sessions on Fable low, at "3x cost" (CLAUDE.md:380), and two of those three cycles were medium.
- PASS per cycle counts result files, not work done: result 94-2 counts although it lists 0 artefacts (log:423).

**3. Observation that falsifies the claim.** Take cycles 89–91 out of the summary's own range: medium averages $32.07 (93–101) and high $33.68 (92–100). "High is also cheaper" reverses. The $1.06 gap is also small next to the spread of single-cycle costs, from $14.81 (log:452) to $58.53 (log:510).

**4. Cheapest discriminating test.** Arithmetic on lines already cited:
- Divide each total in report_v1.md:17 and :77 by its cell count. That settles bullet 3.
- Recompute the high and medium means from the CYCLE lines with and without cycles 89–91. If the direction of the cost gap changes (it does), "cheaper" reflects which cycles each side got, not effort.

DEFECT: major - Bullet 3 sets Fable low's 5-cell total ($17.59) against Opus high's 10-cell total ($15.24), which hides that Fable low costs about 2.3× as much per cell.