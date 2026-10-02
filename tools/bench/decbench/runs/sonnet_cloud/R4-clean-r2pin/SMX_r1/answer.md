**1. Strongest reason it is wrong: not the number, the gate built on it.** As worded, the joints gate fails a correct launch.
- "20 nets (13 outer + 7 PD230)" is 18. w25438 and w25461 sit in both lists (`tools/bench/plan_l2r2_pred.json:38-52`, `diag_c116d_nets.json:3`).
- "The 7 PD230 nets unchanged" is false for those two. Each goes L→L+6/+4 and T4→T3 (`tools/bench/diag_c116d_decode.log:32-33`). Five are unchanged (`:18,19,21,22,38`).
- The recipe has no joints read (120 lines, 0 matches, `tools/recipes/stage_d1_l2r2.py`). The gate is unbuilt, and adding it changes the md5 that plan `:2113` pins, so a re-dry is owed.
- "The launch gates are therefore…" drops 231(d)'s "gates are 230(f)'s, plus:" (plan `:2105`). Rule 1a rests on ENDS/TD/PB (`stage_d1_l2r2.py:76,81,93`), which neither new gate replaces.

**2. Alternative reading: "measured per-net" is thinner than stated.**
- Reads cover 536 of 1,945 wires before and 26 of 1,934 after. They give 23→21, not 24→22 (`decode.log:40-42,47`).
- The 24th item is unnamed. "Unchanged by R2" is asserted (`tools/bench/cards/result_116-4.json:24`), and it may "not be a loose joint" (`:18`). (d)/(f) fix 22 unconditionally, though STEP 0's sweep is meant to name it (plan `:2112-2113`).
- Error List items carry no uid (`archive/peer/2026-09-28-c116b-plan.md:75`), so item-to-wire matching is aggregate only. Both tables fall by 2.
- The pin was set after the scratch returned 22 (`diag_c116b_scratch_el.log:114`). It checks launch == scratch, not rule 1a.
- J4's "after" column is an in-memory pre-save read (`diag_c116d_j3.py:3,7`). The 22 comes from a saved, reopened file (`diag_c116b_scratch_el.log:7`). No joints read of a saved R2 file exists.

**3. Falsifiers.**
- (a) Launch loose ≠ 22 with the other classes at 1/20/10.
- (b) The v1 sweep places the 24th on a touched net, or finds ≠ 24 loose wires in R1.
- (c) Saved-file joints differ from J4 on any net.

**4. Cheapest discriminating test.**
- Offline, seconds: union the two net lists and diff w25438/w25461 in `tools/bench/diag_c116d_decode.json`. This settles §1.
- For §2: run the scheduled v1 sweep on R1, then the same sweep on the saved `D1_l2_r2`. Require a loose-wire count equal to Error List 22, with the 24th named.

**Verdict.** I still believe 22 as a regression pin for this recipe on this bed. The 13 nets are accounted for (9 + 2 + 2). One-item-per-wire counting is corroborated: w25438/w25461 gained 6 and 4 loose joints (`decode.log:32-33`), yet 22 fits only if they added no items. (b) or (c) would change my mind.

DEFECT: minor - the joints gate double-counts w25438/w25461 (20 vs 18 nets) and calls the 7 PD230 nets "unchanged" though two change per the J4 table, so a literal implementation falsely fails a correct launch.