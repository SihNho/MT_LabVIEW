**The claim is wrong in two places.** Only 21 of the 22 loose-end items were measured wire by wire; the 22nd is carried over from R1. And the joints gate contradicts the reads it cites.

**1. Strongest reason.** The wire-by-wire sums are 23 in R1 and 21 after R2 (`tools/bench/diag_c116d_decode.log:41-42`). The claim starts from R1's Error List count of 24, so the unlocated 24th item comes along with it (`tools/bench/cards/result_116-4.json:18,24`). That is the same unexplained +1 the counts have had since B1 (`docs/d1-loop12-17-split-plan.md:1930,2104`).
- Only 536 of R1's 1,945 wires were read (`decode.log:3,47`).
- Decision (e) makes naming that 24th item the acceptance test for the full-graph read (`split-plan:2112`). But (d) fixes 22 before that read runs, and says nothing about what happens if the read puts the item on a wire R2 touches (`:2113`).
- The 21 come from an unsaved rerun held in memory (`result_116-4.json:19`). The 22 comes from 116-2's saved scratch (`tools/bench/cards/plan_116-2_l2r2.md:38-39`; `tools/bench/diag_c116b_scratch_el.log:114`). No single file was read both ways.
- "One Error List item per wire" is an assumption written into the decoder (`tools/bench/diag_c116d_decode.py:5`). The J1 test measured joint flags, not Error List items (`result_116-4.json:14`).

**The gate itself is wrong.** w25438 and w25461 are in both groups (`decode.log:32-33`), so "20 nets" is really 18. Both also change: terminals 4→3, loose joints 3→9 and 2→6.
- If "unchanged" is taken literally, the gate fails a correct launch, and only 2 launches are allowed (`split-plan:1981`).
- If it means "still loose", the gate cannot see the only two nets that may now carry two dangling branches. That is exactly where counting per wire and counting per branch give different answers.
- No joints check covers the 5 other loose nets or the unlocated item.

**2. Alternative explanation.** The 24th item may be a leftover Error List entry that sits on no loose wire; the items carry no uid (`archive/peer/2026-09-28-c116b-pin.md:29`). Then the real loose-wire count goes 23→21, and 22 matches only because the same entry shows up again. That is the count-matching `c116b-pin.md:95` warned against.

**3. What would falsify the claim.** The full read of R1 finds a number of wires with a loose joint (flag 0x100) other than 24, or finds the 24th on a stub or on one of the 13 outer nets.

**Rule 1a gap.** The argument covers only the values on the wires (`split-plan:2040,2108`). Deleting 13 input tunnels also removes 13 inputs that loop 1.1 (`#637`, `split-plan:1931`) waits for before it starts. Nothing shows anyone checked whether those source nodes have side effects.

**4. Cheapest test.** The full-graph read in (e) is already step 0, so tie the pin to its result:
- If R1 has 24 loose wires and the 24th is on a wire R2 never touches, 22 stands. Otherwise, work the number out again.
- Write the joints gate as the per-net after-values stored in `diag_c116d_decode.json`, not as "unchanged".
- At launch, read the joints and the Error List on the same saved file.

I would accept 22 if the full read puts the 24th item on an untouched wire and the launch file shows 22 both ways.

DEFECT: major - the joints gate calls the 7 PD230 nets "unchanged" although the reads show w25438/w25461 losing a terminal and gaining loose joints, and the 22nd item is an unlocated R1 leftover pinned before the read meant to find it.