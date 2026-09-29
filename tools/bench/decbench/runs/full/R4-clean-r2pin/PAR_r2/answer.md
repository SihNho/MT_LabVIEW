**No, the claim doesn't hold as written.** All three analysts' main points survived when I checked them against the files. I dropped one side point: Analyst 3 read the scratch log's "missing 2" as evidence about loose wires. That line belongs to the Error List reader's bookkeeping (its row refinement lists 2 rows as "not refined: [9, 27]"), not to which wires are loose (`diag_c116b_scratch_el.log:85,88`).

**1. Strongest reason: the reader measured 21, not 22.**
- The reader found 23 wires with a loose joint in R1, where R1's Error List has 24 loose-ends items. It found 21 after the build, where the scratch Error List has 22 (`tools/bench/diag_c116d_decode.log:41-42`).
- So 23 − 11 + 9 = 21. The claim's "24 − 11 + 9 = 22" starts from the Error List count, which includes R1's 24th item. The plan itself calls that item unexplained (`docs/d1-loop12-17-split-plan.md:2104`).
- Coverage was partial on both sides. Only 536 of 1,945 R1 wires were read. After the build only the 26 target wires were read, and the whole-graph sweep read 0 (`decode.log:3,40,47`).
- The 22 was seen on the scratch build first (`plan:2099`) and explained afterwards (`plan:2103`). So the scratch count agreeing with 22 is not an independent check.
- Carrying that one unexplained item forward is the kind of count licence 230(f) forbids (`plan:2078`).

**Second defect: the joints gate contradicts its own table.**
- w25438 and w25461 are among the 7 PD230 nets (`plan:2070`) and also among the 13 outer nets.
- In the 116-4 table, both change: w25438 goes L3→L9 and T4→T3, and w25461 goes L2→L6 and T4→T3 (`decode.log:32-33`).
- So "the 7 PD230 nets unchanged" (`plan:2107`) fails on a correct build, or gets quietly read loosely.
- The "20 nets" are 18 distinct nets.

**2. Alternative explanation of the same evidence.**
- The Error List classes don't attribute items to particular wires. The 17-item "B3 licences" class stays fully used while the PD230 class drops to "7 used 5" (`scratch_el.log:112-113`). That looks like a fill order, not a per-wire match.
- So an equal total can hide a different set of wires. For example, R1's residual item could sit on a segment that R2 removes, while some wire among the ~1,900 unread ones goes loose.
- Or the residual could be a second segment on a wire already counted, such as w25438, whose loose joints rise from 3 to 9.
- Either way the count is 22, but the per-net story and the rule-1a reasoning would be about the wrong wires.

**3. What would falsify the claim.** A full sweep of the scratch copy (or the L2-R2 output) whose loose-wire set is not exactly the decode's 21 plus the same residual wire uid found in R1. It is also falsified if that residual belongs to an object L2-R2 retires.

**4. Cheapest test that separates the two.**
- Step 231(e) already owes the repaired reader, `OpWireJoints_v1`, with a full sweep of R1 (`plan:2109-2112`). Run the same sweep on the existing scratch copy as well, and compare the two sets by uid.
- The claim predicts: R1 = the decode's 23 + X, and scratch = the decode's 21 + the same X.
- In the same step, restate the joints gate as 18 distinct nets:
  - the 9 newly loose nets (loose after);
  - w25238 and w25225 not loose;
  - the 5 PD230-only nets unchanged;
  - w25438 at L9/T3 and w25461 at L6/T3.

The rule-1a part holds at the structural level. Every outer net keeps its source, with 2–4 terminals after the build (`decode.log:24-36`, `:46`). The file has never been run. I would withdraw the objection to 22 if the v1 sweep names the same residual uid in both files.

DEFECT: major - The pin of 22 is 21 measured wires plus R1's unexplained 24th item carried over as a count, and the joints gate calls w25438 and w25461 "unchanged" although the 116-4 table shows both changing (L3→L9, L2→L6).