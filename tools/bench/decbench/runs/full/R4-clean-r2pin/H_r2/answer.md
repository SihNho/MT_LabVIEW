**The claim does not hold as written.** The reader's own measurement gives 21 loose wires, not 22, and the joints gate contradicts the J4 table it cites.

**1. Strongest reason it is wrong: 22 is not measured per net; it is 21 plus an unexplained item carried over from R1.**
- The reader counts wires that have a loose joint: 23 before and 21 after (`tools/bench/diag_c116d_decode.log:41-42`).
- The claim's arithmetic starts from the Error List's 24, not the reader's 23. The per-net sum is actually 23 − 11 + 9 = 21.
- The missing item is R1's residual: "23 read vs 24 listed" is "unexplained", and "only 536 wires were read" (`docs/d1-loop12-17-split-plan.md:2104`; the log shows 536 of 1945 read at `diag_c116d_decode.log:47`).
- After the deletion, the sweep read 0 wires outside the 26 targets (`:40`). Nothing measured says the 24th item survives R2 unchanged.
- The pin was also set after the scratch build showed 22 against the old pin of 24 (`:2099`). Calling 22 "equal to the scratch Error List" is a fit to that result, not an independent prediction.

**Gate defect: "the 7 PD230 nets unchanged" contradicts the J4 table.**
- w25438 and w25461 are both outer and PD230 nets (`:32-33`).
- In the table they change: L3/T4 → L9/T3 and L2/T4 → L6/T3.
- Only 5 of the 7 PD230 nets are unchanged (`:18-22`, `:38`).
- "20 nets (13+7)" is really 18 distinct nets.
- Applied literally, the gate fails a correct launch. Applied loosely, nobody knows what it checks.

**2. Alternative explanation of the same evidence.** Two changes could cancel out, so the Error List shows 22 by coincidence:
- The residual item sits on a wire R2 touches, or in the 1,409 unread wires, and it disappears.
- A new loose item appears elsewhere, also unread after the deletion.

Nothing separates this from "the residual persists". The same situation was already left open for R1 ("a swap is not excluded", `:2072`). Whether w25238/w25225 truly "re-join" is also inferred: the table shows only J −1 and pass-through 1 → 0, with L staying 0 (`:26`, `:28`).

**3. What would falsify the claim.** A full sweep, on R1 and on the scratch, that finds either:
- the 24th/22nd item on a different wire in each file, or
- after-state loose wires other than the 21 listed.

Either result makes the 22 match a coincidence.

**4. Cheapest test that separates the two.** Run 231(e)'s repaired `OpWireJoints_v1` sweep over all wires of R1 and of the scratch copy, which needs no new launch. It passes only if:
- the same named residual wire appears in both files, and
- the after-state set equals the 21 listed plus that one wire.

Then rewrite the joints gate as: 9 nets newly loose, w25238/w25225 still not loose, the 5 PD230-only nets unchanged, and w25438/w25461 matching their J4 "after" rows.

What would change my mind: 231(e)'s own acceptance, where the sweep names R1's 24th item, showing the same wire loose in the scratch. Rule 1a is not in dispute here: the terminal diff and "loose joints feed no node" are separate from this counting defect.

DEFECT: major - the pin of 22 includes one Error List item no reader has identified (the per-net sum is 21), and the gate "7 PD230 nets unchanged" contradicts J4's own rows for w25438/w25461.