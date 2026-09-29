**No, the pin isn't "measured per-net". It is 21 measured wires plus one carried, unidentified item, fitted to the scratch's 22.** The 9/2/2 split is measured (`tools/bench/diag_c116d_decode.log:43-46`). The 22nd item and the gate text are not.

**1. Strongest reason**
- After R2 the reader counted 21 loose wires, not 22 (`decode.log:42`). That after-pass read only the 26 target wires and swept none of the other 1,908 (`:40`).
- The 22nd item is R1's residual, which has been unexplained since B1 (`docs/d1-loop12-17-split-plan.md:1930,2104`). The card says R2 leaves it unchanged, but that was never read (`tools/bench/cards/result_116-4.json:24`). So the pin still carries a count licence, which 230(f) forbade (`split-plan.md:2078`).
- The model "one Error List item per loose wire" is tested only against that same total, because Error List items carry no uid (`archive/peer/2026-09-28-c116b-pin.md:29`). That is two unknowns and one equation.
- The sweep that must name the residual runs in STEP 0 (`split-plan.md:2112-2113`). The pin is fixed before it, and nothing says what a different result does to the pin.

**2. Alternative explanation**
Items may not be one per wire. LabVIEW's detail text says "This wire segment is not connected" (`tools/bench/diag_c116b_scratch_el.log:42`). Suppose:
- the residual is a second item on one retired stub, and
- one of w25438/w25461, whose loose joints grew 3→9 and 2→6 (`decode.log:32-33`), now gives two items.

Then 24 − 12 + 9 + 1 = 22: the same number from a different mechanism.

**3. What would falsify the claim**
Any one of these:
- a whole-graph sweep of R1 finds 23 loose wires, not 24;
- a sweep of R2 finds a count other than 22;
- the residual's uid differs between R1 and R2.

**Other defects in the gate text**
- "20 nets" are 18. w25438 and w25461 are in both sets (`decode.log:32-33`; `split-plan.md:2070`).
- "The 7 PD230 nets unchanged" is false for those two, which go T4→T3. Implemented literally, the gate fails a correct launch, and the cap is 2 launches (`split-plan.md:2004`).
- The 22 was read on the saved, reloaded scratch (`diag_c116b_scratch_el.log:3,7`). The 21 came from an unsaved rerun (`result_116-4.json:19`). No single file shows both.
- The rule-1a argument ignores start order: a node runs once all its inputs arrive (`archive/peer/2026-09-12-restructure-plan-4.6-attack.md:171`). It still holds, but only by luck:
  - 12 of the 13 sources are FlatSequence inner tunnels.
  - The 13th, w25911, comes from `Max Trans Pos.vi` in the loop's own frame (`tools/bench/graph_l2r1_saved_20260928.json:1`; `docs/frame-loop-wire-graph.md:274`), and that VI returns a constant (`docs/motor-limit-assurance-plan.md:62`).

**4. Cheapest discriminating test**
Run 231(e)'s v1 sweep on a byte copy of R1 before fixing the pin. It is read-only and needs no 660-second Error List read (`diag_c116b_scratch_el.log:88`).
- **24 loose wires, with the 24th touching none of the 24 retired-object wires:** the claim holds.
- **23 loose wires:** both the one-item-per-wire model and the pin fall.

Make the launch conditional on this result. A sweep that names an untouched 24th wire would change my mind.

DEFECT: major - the pin's 22nd item and its one-item-per-wire model were never measured, were fitted to the same scratch total, and were fixed before the sweep that could falsify them.