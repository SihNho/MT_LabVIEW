**1. Strongest reason it is wrong: "per-net, not carried from R1" overstates it.** 21 of the 22 items are named by the reader. The 22nd is R1's unnamed residual, carried over.
- The reader gives 23 → 21 loose wires (`tools/bench/diag_c116d_decode.log:41-42`).
- 22 appears only by starting from the Error List's 24, whose 24th item is unnamed (`docs/d1-loop12-17-split-plan.md:2104`; `tools/bench/cards/result_116-4.json:18`).
- The after-state was never swept (`decode.log:40`, `sweep_read 0`).
- That is the carried count licence that `archive/peer/2026-09-28-c115e-sel.md:117-120` rejected. `c116b-pin.md:95` warned against it too: "matching a count without knowing which wires make it up".
- The pin moved 24→22 only after the scratch read 22 (`result_116-2.json:2`), so "equals the scratch Error List" is a fit. The independent evidence is the −2 delta, which the Error List and the joints agree on, plus the 9 named nets.

**The gate text is also wrong.**
- "20 nets (13 outer + 7 PD230)" double-counts w25438/w25461 (`diag_c116d_nets.json:3`; `plan_l2r2_pred.json:102,107`). That is 18 distinct nets.
- "7 PD230 nets unchanged" is false for those two: their J4 rows change (`decode.log:32-33,46`). A literal check would fail a correct build.
- No recipe contains a joints gate (no `wire_joints` under `tools/recipes`).
- J4's "after" was read in memory, before Remove Bad Wires, with `SAVE=False` (`diag_c116d_j3.py:3,6`). The 22 comes from a saved, reloaded file (`diag_c116b_scratch_el.log:3,7`). The launch's read point is unspecified.

**2. Alternative explanation.** 22 = 21 named + a different unread wire after than before (a compensating pair). Or "any 0x100 joint ⇒ one item" matches the Error List only by a constant +1. That rule was calibrated on two toy wires (`diag_c116d_decode.py:2-5`). On the real graph the flag marks only some joints (`decode.log:24`). Counts cannot separate these.

**3. Falsifiers.**
- The v1 sweep names R1's 24th wire on a touched net.
- An after-state sweep names a different 22nd.
- The launch Error List ≠ 22.
- Joints on the saved file ≠ in-memory J4.

**4. Cheapest test (no stage launch).**
- Run the planned `OpWireJoints_v1` sweep (`split-plan.md:2109-2112`) on R1 and on the in-memory after-state.
- Diff the loose-wire uid *sets*, not the counts. Expect R1's 24 minus 11 stubs plus the 9 nets, with the same residual uid on both sides.
- Also diff v1's reads on the 37 target nets against `diag_c116d_j3_raw.json`.

**Verdict.** 22 will probably reproduce, because the scratch measured it with the same recipe (`result_116-2.json:19`). Rule 1a rests on the ENDS and TD gates (`tools/recipes/stage_d1_l2r2.py:76,81`), not on this pin. I would change my mind on the pin only if one of the §3 observations appears.

DEFECT: minor - the pin is presented as per-net derived though one of its 22 items is an unnamed carried residual, and the "20 nets" joints gate is miscounted (18 distinct) and contradicts J4 for w25438/w25461.