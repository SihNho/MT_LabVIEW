**No. The 22 does not come from a per-net count. The reader measured 21, and the 22nd item is an unexplained leftover from earlier builds, carried forward without being measured.**

**1. Strongest reason it is wrong.**
- **The sum mixes two different counts.** The reader counts *wires with a loose joint*: 23 in R1 and 21 after R2 (`tools/bench/diag_c116d_decode.log:41-42`). In "24 − 11 + 9", the 24 is the Error List item count, while the 11 and the 9 are wire counts. Using wires throughout gives 23 − 11 + 9 = 21.
- **The extra item has never been explained.** It has been there since B1 (`docs/d1-loop12-17-split-plan.md:1930`) and is still unexplained in 231(c) (`:2104`).
- **Nobody measured whether it survives R2.** 116-4 only states that it does (`tools/bench/cards/result_116-4.json:24`). The after-R2 read covered 26 of 1,934 wires (`decode.log:40,47`).
- **So this is a count licence carried from R1**, which 230(f) forbids (`split-plan.md:2078`). The reviewer warned against exactly this: "Matching a count without knowing which wires make it up" (`archive/peer/2026-09-28-c116b-pin.md:95`).
- **22 is a fitted number, not a prediction.** It is simply the observed value after the plan's own prediction of 24 failed (`diag_c116b_scratch_el.log:114-116`).

**The joints gate also contradicts itself.**
- "20 nets" is really 18: w25438 and w25461 are in both lists (`decode.log:32-33`).
- "7 PD230 nets unchanged" is false for those two. They go from 3 loose joints / 4 terminals to 9 / 3 (w25438) and from 2 / 4 to 6 / 3 (w25461), and their flags change too.
- A gate written literally fails the only launch. A gate relaxed to "still loose" no longer checks joints.

**2. Another explanation for the same evidence.** The count of 22 could be 21 per-wire items, minus a leftover item that does not survive R2, plus one wire now counted twice. For example, w25438 now has 9 loose joints and could produce two items, as in the per-segment alternative recorded before the scratch build (`c116b-pin.md:21`).
- The leftover sits among the 1,409 unread wires (`decode.log:3`) or is not a wire at all.
- Error List items carry no uid (`c116b-pin.md:29`), so a count gate cannot tell these cases apart.
- The two numbers also come from two different builds. The 22 is from the saved scratch file (116-2, 43/0). The joints are from an unsaved rerun (116-4 J3, 42/0; `result_116-4.json:19`).

**3. What would falsify the claim.** Any one of these:
- A whole-graph sweep of R1 finds only 23 wires with a loose joint, so the leftover is not a loose-joint wire.
- The sweep finds the leftover on something R2 deletes or changes.
- The set of loose wires after R2 is not R1's set minus the 11 stubs plus the 9 nets.

**4. Cheapest test that separates the two.** The work is mostly already paid for. 231(e)'s repaired reader (`OpWireJoints_v1`) must "name R1's residual" (`split-plan.md:2112`), and that is STEP 0 of cycle 117 (`:2113`).
- Add one more sweep of the same kind on the scratch build after R2 (unsaved rerun).
- Keep the pin at 22 only if the after-R2 set equals R1's set minus the 11 stubs plus the 9 nets, with the leftover wire unchanged.
- This costs no extra launch. The pin would depend on the sweep instead of being decided before it.

**What would change my mind:** the repaired reader's sweep puts the leftover on a wire R2 does not touch, and the after-R2 set matches as above. Then 22 holds, backed by a measured item.

I don't dispute the rule 1a part. The whole-graph terminal-list diff and the kept sources and sinks (P2) cover it. This is a flaw in the count gate, not in the computation.

DEFECT: major - The pin of 22 includes one Error List item from R1 that was never explained or re-measured (the measured count is 21), and the joints gate says the 7 PD230 nets stay unchanged when two of them visibly change.