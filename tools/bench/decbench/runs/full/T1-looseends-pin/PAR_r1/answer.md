The build was correct and the pinned prediction was wrong. The "−2 already loose in R1" term was inferred, not measured. The data fit four of the 13 shared nets already having a loose-end item in R1, not two.

**What holds up against the files**
- **The build did exactly what the plan said.**
  - The class count dropped by LoopTunnel −13 and Wire −11, with nothing else changed (`diag_c116b_scratch.log:283`).
  - All 13 shared nets kept their source and their kept sinks, and no terminal was added (`:284-285`).
  - Remove Bad Wires found 40 bad wires on the R1 copy and 29 on the new one. The difference is exactly the 11 deleted stubs, and no live shared net was hit (`:316-320`).
- **The error-list reader counted correctly.** The total of 53 is the window's own count, and every item was read (`diag_c116b_scratch_el.log:83,88`). The no-source, not-connected and other classes match the pin exactly, so the whole −2 is in loose ends (`:114`).
- **The −2 term rests on an inferred location.** The pin (`plan_l2r2_make.log:44`) takes nets 25438 and 25461 from R1's PD230 list, whose own citation says "LOCATION IS INFERRED, not measured (no Selection List reader…)" (`errorlist_expected_D1_l2_r1_20260928_055441.json:75`). The other 17 R1 loose items were never located either (`:7`). So any of the 13 nets could already have been loose.
- **The 13 nets are all different wires** (`diag_c116b_scratch.log:284`). So two tunnels sharing one net cannot explain the gap.
- **The −11 term is not the problem.** A stub that had no loose item in R1 would push the result above 24, not below.

**What does not hold up**
- Analyst 2 read "PD230 … 7 used 5" (`diag_c116b_scratch_el.log:113`) as locating the 2 missing items. It does not. The reader has no item locations, so it fills the R1 classes in order: 17 go to the first class, 5 are left for PD230. That line says nothing about where the shortfall is.
- Analyst 1's per-item highlight screenshots do not appear in this log, and the raw JSON (`:86`) is not in this checkout. The "offline screenshot comparison" test cannot be run from here.

**Most plausible alternative:** the R1 set really is {25438, 25461}, but two of the tunnel deletions left no dangling segment. The likeliest pair is #2294 (net 25238) and #3644 (net 25225), the only two tunnels with no inner stub (`plan_l2r2_make.log:26-27`). Explanations A (four nets already loose) and B (two deletions left nothing) both give 22. They differ only in how many of the 13 nets already had a loose-end item in R1.

**Cheapest discriminating test:** no build and no scratch deletion. Re-run the existing Error List reader, which already double-clicks every item (`diag_c116b_scratch_el.log:97`), on a byte copy of R1. After each "Wire has loose ends" double-click, read the block diagram's Selection List over VI Server to get the highlighted wire's uid. Then count how many of the 13 shared-net uids appear:
- **4:** A is confirmed. Re-pin from the measured locations.
- **2:** B is indicated. Repeat the same read on the scratch copy to find the two nets that gained no item.

A second scratch deletion cannot separate A from B: "already loose" and "left no segment" both give +0.

ROOT CAUSE: The pin subtracted only the two nets (25438, 25461) that it inferred, without measuring, to be already loose in R1; four of the 13 shared nets evidently already carried a loose-end item, so the tunnel deletions added 9 items instead of 11 (24 − 11 + 9 = 22) while the build itself was correct.
TEST: Re-run the Error List reader on a byte copy of R1 with a Selection List read after each "Wire has loose ends" double-click, and count how many of the 13 shared-net uids appear: 4 confirms the stale attribution, 2 points to two deletions that left no dangling segment.