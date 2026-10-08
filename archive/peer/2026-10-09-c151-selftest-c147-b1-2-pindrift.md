# c151-selftest-c147-b1-2-pindrift

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $0.8405  in 12 / out 4949 / cache-create 82340 / cache-read 413521  (57s, 10 turn(s))
- **date:** 2026-10-09 02:56:53
- **outcome:** ANSWERED (61s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim (refute it; do not confirm it).

Failure under review: `tools/bench/selftest_c147_b1_2_postmerge.log` (script `selftest_c147_b1_2.py`), first failing line 3:
`FAIL P0 pins before == card inputs ... {'memory_model.json': ['b4a6eec6','d42ccd46'], 'plan_ring_p4_s06v18_pred.json': ['c1bd6b3e','44e0a50e']}` - 19 pass / 1 fail.

Claim: this failure is NOT a regression from the chat-T6 merge (commit 9dbd384b, result gates D/TD/PB keyed by position). It is pin drift of a FROZEN cycle-147 self-test: the test pins the md5 of `tools/bench/memory_model.json` (88eeb037) and `tools/bench/plan_ring_p4_s06v18_pred.json` (c4a6a35a) as they were in cycle 147; cycles 149-150 legitimately changed both files (commit 1449ae07: memory_model.json +10 lines = new load_by_vi entries; pred.json +25 lines = V18E-R' rows). Every semantic check of the same script after P0 passes (R1, T0..T5, F1, F2, P1 all PASS, log lines 4-24), including T5 s03/s04/s05 against the stored run verdicts and T1/T1n D/TD/PB on the L5 fixture. Evidence: `tools/bench/cards/result_chat-T6v.json` facts; `git diff 4d762e7f 1449ae07 --stat`.

Alternative explanations to try: (1) T6's position-key change altered a result the test compares (so P0 is a symptom, not the cause); (2) the pin drift hides a real change in pred.json that is not V18E-R' rows; (3) the same drift would also hit the s08 build route (plan_ring_p4_s08v18*.json) and so is not safe to ignore.
What would falsify the claim, and the cheapest discriminating test (e.g. which md5 the test's pins match at 4d762e7f vs 1449ae07).
Read-only. Answer within 10 lines.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Still checking whether the claim survives. So far it holds only in part: what it says changed in `pred.json` doesn't match the file, and one of its "semantic passes" grades itself against the drifted file.

1. **Strongest reason the claim is wrong:** two of its key statements don't hold up.
   - The current `tools/bench/plan_ring_p4_s06v18_pred.json` has no "V18E" anywhere. What it does have is a census block: `census`, `census_unpredicted` with exactly 25 names, `"census_overall": "MEASURED-SCRATCH"` at lines 15-51, and `census_source` card 148-a2-4 at lines 296-308. The 25 lines look like the census block, not V18E-R' rows.
   - "Every semantic check passes" is circular for PB. T1/T1n PB compares its result to `PRED["cdiff_rows"]`, which is read from the drifted file (`selftest_c147_b1_2.py:100,122`). PB passing only shows agreement with the new answer key, not with the cycle-147 one.
2. **Alternative explanation:** commit 1449ae07 also changed `cdiff_rows` (`pred.json:75-94`), and the T6 position-key PB output moved the same way. A regression would then pass PB unseen, and P0 would be its only visible symptom. The log can't tell this apart from the claim.
3. **What would falsify the claim:** any hunk of `git diff 4d762e7f 1449ae07 -- tools/bench/plan_ring_p4_s06v18_pred.json` that falls inside `cdiff_rows` (lines 75-94). Or: T1 PB fails when `PRED` is loaded from `git show 4d762e7f:tools/bench/plan_ring_p4_s06v18_pred.json`.
4. **Alternative 3 (the s08 route) fails for `memory_model.json`.** No gate in the script uses it; it appears only in `PINS` at line 29. `plan_ring_p4_s08v18_pred.json:231-232` already pins b4a6eec6, the new md5, so the s08 route matches the new file. The leftover is that `s06v18_pred.json:288-289` still cites 88eeb037. That only matters if s06 is ever launched again.
5. **Cheapest discriminating test:** run that one-file `git diff` and see where the hunks fall. Also check that the md5 of the 4d762e7f blob starts with c4a6a35a and the `memory_model` blob with 88eeb037. I couldn't run git or md5 myself because this role has no shell.

**Verdict:** "not a regression from the T6 merge" is plausible. The drift comes from 1449ae07, which landed before the merge 9dbd384b. But the evidence offered for it misdescribes the `pred.json` change, and the claim isn't settled until that diff shows `cdiff_rows` unchanged.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
