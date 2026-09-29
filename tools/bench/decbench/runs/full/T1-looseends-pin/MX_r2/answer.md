The build looks correct. What failed is the pinned prediction: its "−2 already loose in R1" correction rests on an unmeasured guess about which wires carry R1's loose-end errors, and 4 of the 13 shared nets (not 2) were already loose.

**Why the build looks correct**
- Every graph check passed: the lost wires are exactly the 11 stubs, LoopTunnel −13 and Wire −11, all 13 shared nets keep their source and kept sinks, the terminal diff is exact, and the computation diff equals R1's 16 rows (`diag_c116b_scratch.log:279-285,303`). Remove Bad Wires deleted nothing it shouldn't have (`:320`).
- 53 is LabVIEW's own count (`diag_c116b_scratch_el.log:27`). Only the loose-ends class moved; the other classes match the prediction (`:114`) and no item falls outside R1's licensed classes (`:115`).

**Why the prediction is wrong**
- It counts one loose-ends item per wire, so a net that is already loose adds nothing (`plan_l2r2_make.log:44`). R1's accounting used the same model (`archive/peer/2026-09-28-c115e-sel.md:107`).
- Deleting a stub removes one item, as R1's 6 stub deletions did (`errorlist_expected_D1_l2_r1_20260928_055441.json:69`). So 22 = 24 − 11 + 9: only 9 nets gained an item, which means exactly 4 were already loose.
- The "2" comes only from the PD230 list:
  - Its location is marked "INFERRED, not measured" (`…json:75`), and R1's other 17 loose items are unlocated too (`:7`).
  - No tool maps an Error List item to a wire, and the wire terminal list cannot see loose segments (`c115e-sel.md:53,93`).
  - The test that would have settled this was never run (`docs/d1-loop12-17-split-plan.md:2072`).
- The correction was added between two runs of the plan script, changing 26 to 24 (`plan_l2r2_make.log:20,42`). Counting one item per loose segment instead would predict at least 26, which fits even worse.

**Most plausible alternative:** the PD230 location is right (only w25438 and w25461 were loose), but 2 of the 13 tunnel deletions left no dangling outer segment. That also gives +9.

**Cheapest discriminating test:** no rebuild is needed. The R2 scratch copy is already deleted (`diag_c116b_scratch_el.log:118`), so start from a byte copy of R1 and clear only the 13 shared nets, by either:
- running "Remove Loose Ends" on each net, as review c115e-sel proposed (`:126`); or
- using the existing `delete_wire` on those 13 whole nets (its replayer exists, `split-plan:2066`).

Then read the Error List once (about 11 min, `diag_c116b_scratch_el.log:88`) and check only the loose-ends class. The root cause predicts 20 and the alternative predicts 22. The files alone cannot tell them apart.

ROOT CAUSE: The pinned prediction assumed only 2 of the 13 shared nets (w25438/w25461, from the unmeasured PD230 location guess) already had a loose end in R1, but LabVIEW lists one loose-ends error per wire and 4 were already loose, so the tunnel deletions added 9 errors, not 11, and 22 is the correct count.
TEST: On a byte copy of R1, clear the loose ends of only the 13 shared nets (Remove Loose Ends, or `delete_wire` of those whole nets) and read the Error List once: 20 loose-end errors confirms the root cause, while 22 means two tunnel deletions left no dangling segment.