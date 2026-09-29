**Verdict: 22 is a pin fitted to the scratch result, not an independent derivation. The per-net evidence does not reproduce it.**

**1. Strongest reason the claim is wrong: the arithmetic mixes Error List items with wires.**
- The reader counted 23 loose wires in R1 against 24 Error List items, and 21 after against 22 items (`tools/bench/diag_c116d_decode.log:41-42`).
- The measured per-net sum is therefore 23 − 11 + 9 = 21. The result card says so itself: "read after-set sum 21 = 23-11+9" (`tools/bench/cards/result_116-4.json:22`).
- 22 is reached only by starting from the Error List's 24, which includes one item no read explains (`docs/d1-loop12-17-split-plan.md:2104`). Only 536 of 1,945 wires were read before, and 26 after (`diag_c116d_decode.log:47`).
- Wires and items are demonstrably not one-to-one: in R1, deleting 11 stub wires removed only 6 loose-ends items (`docs/d1-loop12-17-split-plan.md:2073`). The claim assumes 11 stubs = 11 items here.
- The "equal to the scratch" agreement is circular: the pin was 24, the scratch read 22 and failed, then the pin was reset to 22 (`tools/bench/diag_c116b_scratch_el.log:114-116`).

**2. Alternative explanation.** The 22 is a different composition that happens to sum the same.
- The Error List may count items per loose segment group rather than per wire. The stubs carry 2 to 15 loose joints each (`diag_c116d_decode.log:6-17,37`).
- w25438 and w25461 are called "already loose", but they changed: loose joints 3→9 and 2→6, with new flags (`diag_c116d_decode.log:32-33`).
- The scratch's licence table used only 5 of the 7 PD230 dangling-branch items (`diag_c116b_scratch_el.log:113`), yet the gate expects the 7 PD230 nets unchanged (`docs/d1-loop12-17-split-plan.md:2107`). Two items moved class or vanished, unexplained.
- So the unexplained 24th item could disappear while an extra item appears elsewhere, and the count gate would still pass.

**3. Falsifying observations.**
- A full sweep of R1 finds the 24th item on one of the 11 stubs or 13 outer nets, or finds it is not a loose joint at all.
- The scratch Error List's 22 items, double-clicked to location, do not map onto exactly the 21 named wires plus that one residual.

**4. Cheapest discriminating test.** Do this after the reader repair already ordered in (e) (`docs/d1-loop12-17-split-plan.md:2109-2112`), and before launch:
- Run the repaired reader over all wires of an R1 byte copy and of the scratch.
- Compare the loose-wire uid sets with the Error List items one to one, in both files.
- Pin the uid set, not the integer 22.

The joints gate on 20 nets is the sound part of the decision. On rule 1a the structural argument holds: terminals drop by exactly one on each of the 13 outer nets (`diag_c116d_decode.log:46`). It remains structural only, never run.

I do not believe the claim holds as worded. A full-graph read that names the 24th item and shows a one-to-one item-to-wire map would change my mind.

DEFECT: major - the pin of 22 adds an unexplained Error List item to a per-wire count that itself sums to 21, so the count gate can pass on a different set of loose wires than the one derived.