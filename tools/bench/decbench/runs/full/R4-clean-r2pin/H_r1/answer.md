**The claim is wrong as stated.** The match to 22 is a fitted coincidence, not a derivation. The joints gate also contradicts its own measurement.

**1. Strongest reason: the arithmetic mixes Error List items with wire counts, and the leftover 1 is assumed, not measured.**
- 24 is R1's Error List item count. But the reader found only **23** wires with a loose joint in R1 (`tools/bench/diag_c116d_decode.log:41`).
- The per-wire version of the same sum is 23 − 11 + 9 = **21** wires (`:42`), not 22.
- The formula reaches 22 only by assuming R1's unexplained 24th item carries into R2 unchanged. The plan itself says that item is unexplained (`docs/d1-loop12-17-split-plan.md:2104`).
- The "after" state was not swept either: 26 wires read, `sweep_read: 0` (`decode.log:40,47`). No other wire in the scratch build was checked for loose ends.

**2. Alternative explanation of the same evidence.**
- The Error List does not count one item per wire. The 22 could come from the R1 residual disappearing, while one newly loose net gives two items. w24333 goes from 0 to 8 loose joints (`decode.log:25`) and could split into two dangling segments.
- The licence tally already disagrees with the per-net story. The PD230 dangling-branch class reads "7 used 5" in the scratch build (`diag_c116b_scratch_el.log:113`). Yet the reader shows all 7 PD230 nets still loose after (`decode.log:18-38`).
- So the classifier fills licence classes by message count. It cannot tie Error List items to nets, and the NC "no extra" pass (`:115`) proves nothing about which wires are loose.

**3. The joints gate as written would fail, or is ambiguous.**
- "20 nets (13 outer + 7 PD230)" counts w25438 and w25461 twice. They are in both sets (`decode.log:32-33`), so there are 18 distinct nets.
- The gate also says "7 PD230 nets unchanged", but those two nets change: L3/T4 → L9/T3 and L2/T4 → L6/T3.
- Read literally, the gate fails on a correct build. Read loosely ("still loose"), it would pass a wrong one.

**4. Observation that would falsify the claim.**
The repaired whole-graph sweep (Pre-decided 231(e), `:2109-2112`) names R1's 24th item on a wire that R2 changes or deletes, or on none of them. The claim also fails if an R2 sweep finds a loose-wire set other than the 21 named wires plus that residual.

**Cheapest discriminating test.**
- Run the `OpWireJoints_v1` sweep that 231(e) already requires, first on R1 and then on the R2 scratch byte copy. No launch is needed.
- The claim holds only if the set of loose wires in R2 equals the 21 named wires plus the one residual wire from R1, and that residual wire's joints are the same in both files.
- Then change the gate from a count to that named set of 22 wires. Use 18 distinct nets, with separate before and after expectations for w25438 and w25461.

**What survives:** the rule-1a part does not depend on the count. Each outer net keeps its source and live sinks, and a loose joint feeds no node. If the sweep puts the residual on an untouched wire, I would accept pin 22.

DEFECT: major - The pin 22 matches the scratch Error List only by assuming R1's unexplained 24th item carries over (the per-wire sum gives 21), and the joints gate counts two nets twice and calls "unchanged" two nets that do change.