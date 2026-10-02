**Strongest reason the claim is wrong: 22 is the scratch result relabelled as a derivation. The derivation needs an unexplained +1 and rests on a partial census.**

1. **The arithmetic only reaches 22 by carrying R1's unexplained residual.**
   - The measured wire-level result is "23 wires with a loose joint" in R1 and "21" after. That is 23 − 11 removed + 9 added (`tools/bench/diag_c116d_decode.log:41-42`).
   - The claim says 24 − 11 + 9 = 22. The extra item is B1's "1 unexplained residual" (`archive/peer/2026-09-28-c116b-pin.md:54`).
   - The log says R1 read 23 wires against 24 listed. The plan admits that residual is "unexplained" (`docs/d1-loop12-17-split-plan.md:2104`).
   - The claim assumes that item sits on a net R2 does not touch. Nothing shows this. If it sits on a deleted stub or an outer net, the true expectation is 21 or 23.
   - The plan's own planned acceptance test, `OpWireJoints_v1` naming the 24th item (`:2109-2112`), has not run yet. Pin 22 therefore depends on a fact that is still open.

2. **The "before" census is partial.**
   - The v0 reader returned clean reads only for wires 0-535. From read 536 on, 1409 of 1945 reads failed with error 1055 (`diag_c116d_decode.log:3`, final `VALID` line).
   - The 23-wire set comes from 37 targets plus 536 swept wires. A loose wire among the other ~1400 would be invisible in both "before" and "after".
   - "24 loose-end items in R1" therefore comes from the Error List, not from the per-net evidence the claim cites.

3. **The 22 is a post-hoc fit, not a prediction.**
   - The pre-launch pin was 24, and the scratch Error List gave 22 (`diag_c116b_scratch_el.log:114-116`, PIN gate FAIL).
   - The pin was then re-set to the observed value. The J4 table was read from that same scratch build.
   - So the launch gates check "R2 reproduces the scratch". They do not test the rule-1a statement that each outer net keeps its source and 1-3 sinks.
   - The terminal diff in 230(f) carries that statement, not these gates.

4. **Counting unit.** The unit is one item per wire. A single stub wire has L15 loose joints (`diag_c116d_decode.log:15`). R1 showed 11 stubs removed but only 6 stub items gone (`split-plan.md:2072`), so item counts do not map one-to-one to wires. The NI page the earlier review fetched does not say whether an item is per wire or per segment (`c115e-sel.md:129-130`). A joint change inside one wire could shift the count by ±1 with no rule-1a effect.

5. **The gate depends on the repaired reader.** The 20-net joints gate uses the repaired reader (`OpWireJoints_v1`, `split-plan.md:2109`), which is not yet built or tested. Its predecessor leaks references.

**Alternative explanation of the same evidence:** the residual item sits on one of the 9 newly-loose or 2 re-joining nets, and the sum 22 is a coincidence of offsetting miscounts. The scratch count would be unchanged, but a launch could still differ.

**What falsifies the claim:** the 24th R1 item is located on a touched net, or v1's whole-graph sweep of all 1,945 R1 wires finds loose wires outside the 23.

**Cheapest discriminating test:** run `OpWireJoints_v1` over all 1,945 R1 wires. This is already planned as 231(e). It must show 24 loose items, name the 24th item's net, and show that net is not among the 11 stubs or 20 target nets. If the 24th is on an untouched net, 22 holds. If it is on a touched net, the pin must be re-derived.

I could not shake points 1-2. The 22 may well be right, but it is not independently established. Launch should wait on 231(e).

DEFECT: major - the 24 − 11 + 9 = 22 derivation absorbs an unlocated residual item, and the 23-wire "before" census covers only 536 of 1945 wires, so the pin is the scratch count refitted rather than an independent prediction.