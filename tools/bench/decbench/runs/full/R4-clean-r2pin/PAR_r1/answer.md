**The claim does not hold as written.** The rule-1a part stands, but the pin of 22 is not fully accounted for by the measurements, and the joints gate contradicts its own table. All three analysts' main points check out against the files.

**1. Strongest reason it is wrong: the measured count is 21, and the pin is 22.**
- The reader found 23 wires with a loose joint in R1 and 21 in the scratch (`tools/bench/diag_c116d_decode.log:41-42`).
- All 11 deleted stubs are among the 23 (`:6-17,37`). Counted by wire, the result is 23 − 11 + 9 = **21**.
- The claim's "24 − 11 + 9" starts from the Error List's item count instead. That brings in R1's 24th item, which the plan itself calls "unexplained" (`docs/d1-loop12-17-split-plan.md:2104`). So one of the 22 is carried from R1, which PD231(d) says does not happen (`:2105`).
- The evidence cited for 22 (`decode.log:42-46`) actually shows 21.
- Coverage is also partial: 536 of 1,945 wires read before (`decode.log:3,47`), and only the 26 targeted wires after (`:40,47`).
- The pin was also set after the scratch had already shown 22, and the prediction made in advance (24) failed (`diag_c116b_scratch_el.log:114-116`). The `== 22` gate therefore only checks that the launch reproduces the scratch. It does not test the derivation.

**2. Second defect: the joints gate is written wrongly.**
- w25438 and w25461 belong both to the 13 outer nets and to the 7 PD230 nets (`plan:2070`; `decode.log:32-33`), so "20 nets" is really 18.
- The gate requires "the 7 PD230 nets unchanged" (`plan:2107`). But w25438 goes from L3/T4 to L9/T3, and w25461 from L2/T4 to L6/T3 (`decode.log:32-33`). A correct build would fail this gate as written.

**Alternative explanation of the same evidence: a swap.**
- R1's residual item could be removed by R2, and a different unread wire could become loose. That gives 22 items with a different set of wires.
- R1 already left a swap like this unresolved (`plan:2072`).
- The scratch's class tally does not follow the per-net story either. It uses only 5 of the 7 "PD230 dangling branch" licences (`scratch_el.log:113`), while the reader reports all 7 PD230 nets still loose. So the Error List matching works by class, not by wire.
- R1's own accounting did not treat stubs as one item each (11 stubs, 6 items, `plan:2068,2073`). That weakens "−11 items" as a rule, although R2's 11 stubs were each measured loose.

**What would falsify the claim.**
- A full sweep of R1 that puts the 24th item on a net R2 deletes or rewires, or
- a full sweep of the scratch finding a loose wire outside the 21 at `decode.log:42`, or two Error List items on the same wire.

**Rule 1a survives.** Only the outer nets lose a terminal (for example w24277 goes from T3 to T2, `decode.log:24`). B3 and R1 have equal properties (`plan:2097`), and the scratch's whole-graph terminal diff passed (`:2099`).

**Cheapest test that separates the claim from the swap:**
1. Run PD231(e) first: build `OpWireJoints_v1`, then sweep all 1,945 R1 wires and all 1,934 scratch wires, read-only (`plan:2109-2112`).
2. The claim holds only if the residual item sits on the same wire in both files, and the scratch's set of loose wires is exactly those 21 plus that one.
3. Before launch, rewrite the gate: 18 distinct nets, w25438 and w25461 matching their "after" rows, and the other 5 PD230 nets unchanged.

That sweep result is what would change my mind.

DEFECT: major - the pin of 22 is 21 measured loose wires plus R1's unexplained 24th item carried forward unmeasured, and the joints gate counts w25438/w25461 twice while requiring them "unchanged" when the J4 table shows they change.