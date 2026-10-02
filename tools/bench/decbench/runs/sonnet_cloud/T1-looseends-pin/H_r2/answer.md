The failure is in the prediction, not the build: the pin of 24 loose ends assumed one effect per wire that nobody had measured, and the one measured result (22) contradicts it.

**What the pin assumed.** The pin was 24 − 11 + 13 − 2 = 24 (`tools/bench/plan_l2r2_make.log:31`). It rests on two unmeasured beliefs:
1. Each of the 13 nets that loses a tunnel sink gains exactly one "Wire has loose ends" item.
2. Exactly two of those nets, 25438 and 25461, already had one in R1.

The second belief comes from the R1 licence for the 7 "PD230 dangling branch" items. That licence lists w25438 and w25461 and says outright "LOCATION IS INFERRED, not measured (no Selection List reader; … Q2 swap alternative OPEN)" (`tools/bench/errorlist_expected_D1_l2_r1_20260928_055441.json:75`). Without that subtraction the planner's own model gave 26 (`plan_l2r2_make.log:20`), and the observed count is lower still.

**What the scratch build shows.**
- The build itself matched the simulation exactly. Only the 11 stubs and 13 tunnels went, no wire was added, and all 13 shared nets kept their source and their kept sinks (`diag_c116b_scratch.log:280-286`, `:43 pass / 0 fail`). So the build is not the problem; the count of error-list items per net is.
- The other three classes matched the pin exactly: no-source 1, not-connected 20, other 10 (`diag_c116b_scratch_el.log:112`). The whole −2 is in loose ends.
- In the licence table, the 17-item loose-ends pool is fully used (17/17), while the PD230 dangling-branch row drops from 7 to 5 (`diag_c116b_scratch_el.log:110-111`). Those two rows are filled by count, not by location, so this only hints at where the two missing items are.
- Remove Bad Wires gives no per-net information. Its difference between the bed and the scratch is exactly the 11 stubs (`diag_c116b_scratch.log:320`), and it only reports whole wires it deletes, not loose ends it trims.

**Two competing explanations.**
- **(A) Most likely, given the PD230 row going 7 → 5:** deleting tunnels #5752 and #5569 removed the loose-ends item that 25438 and 25461 already had in R1. The pin assumed that item would stay.
- **(B) The alternative:** 25438 and 25461 behaved as predicted, and two of the other 11 nets did not gain an item. Either LabVIEW cleaned up the branch on delete, or those nets were already loose in R1 under the unmeasured location assignment.

Both give 22, and nothing in the current logs separates them.

**Cheapest test that separates them.** Take a fresh byte copy of the R1 bed. Delete only the 4 rows for those two nets: stubs w5746 and w5979, then tunnels #5752 and #5569. Read the loose-ends count with the existing error-list reader (`diag_c116b_scratch_el.py`).
- The pin's model predicts 24 − 2 + 0 = 22.
- (A) predicts 20.
- (B) predicts 22, and the deficit sits in the other 11 nets.

This needs no new reader and reuses the scratch-build harness.

ROOT CAUSE: The pinned 24 assumed one loose-ends item per affected net, with 25438 and 25461 already loose in R1, but that per-net assignment was inferred, never measured (`errorlist_expected_D1_l2_r1_20260928_055441.json:75`); in the real Error List two of the 13 nets don't end up with the item the arithmetic expects (most likely 25438 and 25461, whose PD230 dangling-branch row fell from 7 to 5).
TEST: On a fresh byte copy of R1, delete only stubs w5746 and w5979 and tunnels #5752 and #5569, then read the Error List's loose-ends count: 20 confirms that deleting those two tunnels cleared the two pre-existing items, and 22 puts the deficit on the other 11 nets.