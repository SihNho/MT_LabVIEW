The claim does not hold as written. The launch gate it specifies contradicts its own measured table, and the "22" is really 21 measured plus one leftover item that nobody has explained.

**1. Strongest reason it is wrong.** The joints gate says "the 7 PD230 nets unchanged" (`docs/d1-loop12-17-split-plan.md:2107`). But w25438 and w25461 are both PD230 nets and outer nets, and the measurement shows they change:
- w25438: loose joints 3→9, terminals 4→3 (`tools/bench/diag_c116d_decode.log:32`)
- w25461: loose joints 2→6, terminals 4→3 (`tools/bench/diag_c116d_decode.log:33`)

So a literal gate fails on the scratch's own evidence. A loose reading ("stays loose") would let almost any change through. The same double membership means "20 nets (13 outer + 7 PD230)" is really 18 distinct nets (`decode.log:18-38`).

The arithmetic is also weaker than it looks:
- The per-wire read gives 23 − 11 + 9 = **21** (`decode.log:42`). The claim's "24 − 11 + 9 = 22" starts from the Error List's 24, so it adds R1's leftover item without saying so.
- That leftover is unexplained. Only 536 of 1,945 R1 wires were read (`decode.log:3,47`; `docs/d1-loop12-17-split-plan.md:2104`), and the after state was read on 26 wires only (`decode.log:4,40`).
- "Unchanged by R2" is written as an open item, not measured (`tools/bench/cards/result_116-4.json:24`).

**2. Alternative explanation of the same evidence.** 22 = 22 may be a count coincidence rather than a match of the same items:
- The Error List reader does not attribute items to wire ids. It sorts by OCR text and reported "missing 2" and "not refined: [9, 27]" (`tools/bench/diag_c116b_scratch_el.log:85,88`).
- Its own allocation, 17 B3-licensed + 5 of 7 PD230 items (`diag_c116b_scratch_el.log:112-113`), does not follow the claimed −11 +9 path.
- R1 already showed that deleting a stub wire does not map one-to-one to loose-ends items: 11 stubs removed, 6 stub items gone (`docs/d1-loop12-17-split-plan.md:2068,2073`).
- R1's "7 dangling branches" were inferred, and a swap was never ruled out (`docs/d1-loop12-17-split-plan.md:2072`).

So R2 could remove the unexplained item (for example through a pass-through re-join on w25238 or w25225) and add a different loose segment somewhere in the ~1,900 wires nobody read. The count would still be 22.

**3. What would falsify the claim.** A whole-graph joints sweep of the R2 scratch that finds a set other than the 21 wires listed at `decode.log:42` plus the same R1 leftover wire. For example: 21 wires, with the leftover being something that is not a loose joint; or the leftover gone and a new wire loose.

**4. Cheapest discriminating test (no launch, offline copy).** Run the repaired `OpWireJoints_v1` sweep from `docs/d1-loop12-17-split-plan.md:2109-2112` twice, on R1 and on the scratch-after byte copy:
- **The claim holds if** R1 shows 24 loose wires including a named leftover, and the scratch shows 22 = those 21 + the same leftover.
- **My alternative holds if** the leftover is not the same wire or the totals differ.

Separately, rewrite the joints gate as an explicit expected table per net, with w25438 and w25461 expected to change.

Rule 1a is not the weak point. The deleted tunnels had no consumer (`docs/d1-loop12-17-split-plan.md:2108`), the 9 nets go from 3 terminals to 2 and keep their source (`decode.log:46`), and a loose segment feeds no node. What would change my mind on the count is a whole-graph sweep that names the leftover item and shows it survives R2.

DEFECT: major - the joints gate says the 7 PD230 nets stay unchanged, yet two of them (w25438, w25461) measurably change, and the 22 pin depends on an unexplained leftover item assumed to survive R2 without any whole-graph read after the change.