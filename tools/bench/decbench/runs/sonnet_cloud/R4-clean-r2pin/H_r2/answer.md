**Verdict: the claim does not hold as written. The number 22 is a measured 21 plus one item nobody has explained.**

**1. Strongest reason it is wrong.** The joints reader never reached 22.
- Before the change it found 23 loose wires against R1's 24 Error List items (`tools/bench/diag_c116d_decode.log:41`). After it found 21 against the scratch build's 22 (`:42`).
- The per-net arithmetic on the reader's own numbers is 23 − 11 + 9 = 21. The card says so: "read after-set sum 21 = 23-11+9" (`tools/bench/cards/result_116-4.json:22`).
- 22 only appears when you start from R1's 24, which includes the 24th item. That item is still unexplained: "residual 1 lies in the 1409 unread wires or is not a loose joint" (`result_116-4.json:18`; `docs/d1-loop12-17-split-plan.md:2104`).
- So the pin carries one item from R1 as a bare count. Plan 230(f) forbade exactly that ("NO count licence carries into L2-R2", `docs/d1-loop12-17-split-plan.md:2078`).
- The statement that R2 leaves the residual alone is asserted, not read. After the change the sweep read 0 of the 1,908 other wires (`tools/bench/diag_c116d_decode.log:40`). Only 26 target wires were read.

**Second defect: the joints gate contradicts its own table.**
- w25438 and w25461 are on both lists: the 13 outer nets and PD230(d)'s 7 (`docs/d1-loop12-17-split-plan.md:2070`). The "20 nets" are really 18.
- Both nets change in J4: w25438 goes from L3/T4 to L9/T3, and w25461 from L2/T4 to L6/T3 (`tools/bench/diag_c116d_decode.log:31-32`).
- A gate requiring "the 7 PD230 nets unchanged" (`docs/d1-loop12-17-split-plan.md:2107`) therefore fails on a correct R2. Or it gets satisfied by a loose reading that checks nothing.
- The scratch build's licence match also attributed only 5 of the 7 PD230-class items (`tools/bench/diag_c116b_scratch_el.log:113`). That attribution is by count only, so it cannot confirm the per-net story.

**2. Alternative explanation.** The scratch build's 22 = 21 wires measured as loose + 1 item that was never measured. That item could be:
- a second Error List item on one wire, or
- an item on an unread wire that R2 removes, while R2 also creates a new item elsewhere.

Either way the totals match by coincidence, not because the 24th item survived unchanged.

**3. What would falsify the claim.** The repaired whole-graph sweep (231(e), `docs/d1-loop12-17-split-plan.md:2111-2112`) names R1's 24th item, and it is:
- on a wire that R2 deletes or touches, or
- not a wire with a loose joint at all.

In either case the "24 − 11 + 9" bookkeeping is wrong even though the total is right.

**4. Cheapest test that separates the two.** Before launching, run `OpWireJoints_v1` across all 1,945 wires on R1 and the same sweep on the scratch copy (no new LabVIEW stage is needed). Then check that:
- the set of loose wires goes 23 → 21 with exactly the 9 + 2 + 11 changes listed, and
- the same named residual wire appears in both, with its Error List item still present.

If that holds, the pin becomes 21 named wires + 1 named item. That is a real per-net pin. Separately, rewrite the gate so the overlapping nets are checked against J4, not as "unchanged".

**What would change my mind:** the v1 sweep shows the residual item on one wire, untouched by R2, in both files. In that case 22 is right and only the gate wording needs fixing.

On rule 1a there is no objection. Terminal counts on the outer nets drop by exactly the deleted tunnel terminal, and the source flags stay (`tools/bench/diag_c116d_decode.log:21-34`).

DEFECT: major - the 22 pin includes R1's unexplained 24th item as an unmeasured carried count (the reader measured 23→21), and the joints gate wrongly requires w25438 and w25461 "unchanged", although J4 shows both change.