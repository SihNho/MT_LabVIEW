**Answer:** the two missing "loose ends" items most likely sit on nets 25438 and 25461, the two nets the pin counted as "already loose in R1". The pin assumed each would stay at one loose item after its tunnel sink was deleted. The numbers fit best if each went from 1 to 0 instead. I have not confirmed this.

**What the numbers show**
- The pin is 24 − 11 + 13 − 2 = 24 (`tools/bench/plan_l2r2_make.log:44`). The scratch VI read 22, while the other three classes matched exactly: no-source 1, not-connected 20, other 10, and the window's own count was 53 (`diag_c116b_scratch_el.log:27,114`). So this is not an OCR miscount; exactly two loose items are missing.
- The reader's licence table for the scratch VI shows where the drop fell. The B3 class stayed at 17 of 17, but the "PD230 dangling branches where a retired SR sink was cut" class fell from 7 in R1 to 5 (`diag_c116b_scratch_el.log:112-113`).
- R1's graph has exactly 7 shared nets whose shift-register sink was cut (PD230): w8590, w9051, w11253, w11389, w25438, w25461 and w29122 (`diag_c115d_graph.log:17-18,22-25,27`). Two of them, 25438 and 25461, carry the retired tunnels' outer terminals 5758 and 5583 as sinks (`diag_c115d_graph.log:24-25`, `plan_l2r2_make.log:37-38`). Those are exactly the two nets the pin special-cased.
- So the pin's own −2 correction is the part that failed. Deleting tunnels #5752 and #5569 apparently removed the dangling branch left by the cut shift-register sink on each net, so each net went from one loose item to none, not to "still one".
- Caveat: the licence table fills its classes by count, not by object ID. Pairing loose items between two Error Lists by screenshot has already failed once (`diag_c115d_sel.log:74`). The 7→5 drop is consistent with this explanation but does not prove it.

**The strongest competing explanation.** 25438 and 25461 stay loose as the pin assumed, and instead two of the 11 clean shared nets never gained a loose end when their tunnel was deleted. The best candidates are #2294 and #3644, the two tunnels with no inner stub (`plan_l2r2_make.log:26-27`). That also gives 24 − 11 + 11 = 22.

**Cheapest discriminating test.** Make one more byte copy of R1 and apply only two actions: delete stub wire 5746, then delete tunnel #5752 (net 25438). Then read the Error List's loose count (no LabVIEW run or save beyond the existing scratch-VI and Error List reader).
- The pin and the competing explanation both predict 23 (stub −1, net unchanged).
- My explanation predicts 22 (stub −1, and the net's existing loose item gone).

If it reads 23, repeat the test on tunnel #2294 alone (it has no stub). The pin predicts 25 there, and the competing explanation predicts 24.

ROOT CAUSE: The pin's "−2 for nets already loose in R1" rule is wrong: deleting tunnels #5752 and #5569 most likely also cleared the loose branch each of nets 25438 and 25461 already had, so each lost one loose item instead of staying the same, giving 22 instead of 24.
TEST: On a fresh byte copy of R1, delete only stub 5746 and tunnel #5752, then read the Error List: 22 loose items confirms this, 23 points to a clean shared net that gained no loose end.