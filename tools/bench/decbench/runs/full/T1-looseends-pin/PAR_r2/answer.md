The build did what the plan said. The prediction was wrong: it assumed only 2 of the 13 shared nets already had a loose-ends item in R1, and that assumption was never measured. The most likely truth is 4, and one small scratch run can tell that apart from the main alternative.

**Checked and holds up**
- **The 22 is real.** The Error List window reports its own count of 53 (`diag_c116b_scratch_el.log:27`). Only the loose-ends count differs; the other three classes match the pin (`:114`). Nothing falls outside R1's error classes (`:115`).
- **The build matched the plan.** It removed exactly the 11 planned stub wires and the 13 tunnels, and added nothing (`diag_c116b_scratch.log:279,281,283`). All 13 shared nets kept their ID, source and kept sinks (`:284`). The before/after Remove Bad Wires difference is exactly the 11 stubs (`:320`).
- **The "−2 already loose" term was added later and is a guess.** The first run of the plan maker predicted 26 (`plan_l2r2_make.log:20`); the rerun predicted 24 (`:42-44`). The term's only source is the R1 licence file, which says **"LOCATION IS INFERRED, not measured … Q2 swap alternative OPEN"** (`errorlist_expected_D1_l2_r1_20260928_055441.json:75`). R1's other 17 loose-ends items have no net attached at all (`diag_c116b_scratch_el.log:112`).
- **This exact risk was raised before and left open.** The hypothesis review warned that a shared net might already carry a loose end, and that carrying the count forward into L2-R2 could hide it (`archive/peer/2026-09-28-c115e-sel.md:106-107,115,157-163`). Four already-loose nets gives 24 − 11 + 13 − 4 = 22.

**Refuted or weakened**
- **Analyst 2's evidence.** "7 licensed, 5 used" for that licence group (`diag_c116b_scratch_el.log:113`) is just what is left after the first group takes 17 (`:112`) out of 22. It says nothing about where the missing items are. Their mechanism is also weak: deleting a sink node elsewhere leaves a dangling branch, which is why the pin counts +1 per net. It is hard to see why the same deletion would clean up an older branch on these two nets.
- **Analyst 1's test.** It relies on a `Wire.Is Broken?` read that does not exist as a standalone read-only function; it is only built into the connect functions (CLAUDE.md, "When a diagnosis is GUESSED twice"). A new tool would be needed.
- **Analyst 3's offline test.** The per-item screenshots are not in this checkout (a search of `tools/bench/errorlist_shots/` finds nothing). Also, the raw read file for the scratch VI (the path at `diag_c116b_scratch_el.log:86`) is not in this checkout either, so the test's inputs cannot be confirmed from here.

**Cheapest test that separates them**
Make a byte copy of R1 and delete only stub w5746 and tunnel #5752 (net 25438). Then read the Error List with the existing reader (about 11 minutes, `diag_c116b_scratch_el.log:120`).
- **23** means net 25438 stays loose, as the pin assumed, so the missing 2 are other nets that were already loose.
- **22** means deleting the tunnel removed the old dangling branch too.
- **24 or more** rules out both.

This needs no new tool. It does not identify which two other nets were already loose; that still needs a per-net read before the pin is recomputed.

ROOT CAUSE: The pin subtracted only the two nets [25438, 25461] that R1's licence guessed were already loose, a location it says was never measured, while most likely four of the 13 shared nets already had a loose-ends item in R1 (24 − 11 + 13 − 4 = 22), the case review c115e-sel Q2 left open.
TEST: On a byte copy of R1, delete only stub w5746 and tunnel #5752 and read the Error List: loose-ends 23 confirms net 25438 stays loose and other shared nets were already loose, while 22 means deleting the tunnel removed its dangling branch.