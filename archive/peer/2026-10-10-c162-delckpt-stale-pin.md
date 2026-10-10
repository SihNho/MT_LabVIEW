# c162-delckpt-stale-pin

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $0.9640  in 10 / out 6749 / cache-create 94792 / cache-read 353298  (72s, 12 turn(s))
- **date:** 2026-10-10 10:35:54
- **outcome:** ANSWERED (76s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim. Strongest reason it is wrong, an alternative explanation, what would falsify it, the cheapest discriminating test.

Failing log: tools/bench/prep_c161_a3_1_suite_after.log (script prep_c161_a3_1_suite.py), first_fail "not green: selftest_c161_delckpt" (line 8: rc=1, gates pass 9 / fail 2).

CLAIM: the two selftest_c161_delckpt fails are STALE PIN failures, not a defect in the delete_wire checkpoint rule. The suite ran at 09:45 while the p5s02b pred md5 was still 18729409; card 161-a3-2 then re-pinned it to a1fd43fb (comment in tools/bench/selftest_c161_delckpt.py:138), so the "P pins unchanged" gate (line 140) and one more pin-based gate compared against the new value only after the file had changed. On the current bytes the self-test is expected to pass. Computation (rule 1a) is not touched: the test checks stagexec's checkpoint validator, not any VI.

Read: tools/bench/prep_c161_a3_1_suite_after.log, tools/bench/selftest_c161_delckpt.py, tools/bench/cards/assign_result_161_3.json, tools/bench/diag_c161_b2_1_facts.md.
Do not run LabVIEW. Name the log or script (prep_c161_a3_1_suite_after.log / prep_c161_a3_1_suite.py) in your answer.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The conclusion holds, but the explanation doesn't.** The two `selftest_c161_delckpt` fails in `prep_c161_a3_1_suite_after.log:8` were not caused by a pin going stale after the run. Both fails were already there before the run, and one of them is not a pin check at all. The checkpoint rule itself is fine, but the evidence for that is the gates that passed, not the pin story.

## 1. Strongest reason the claim is wrong
- **The order of events is backwards.** The same 9 pass / 2 fail result appears in the *before* sweep (`prep_c161_a3_1_before_selftest_c161_delckpt.out:3,19`), before card 161-a3-1 edited anything. At 09:45 the test still pinned the pred to **48b50b29**, while the file was already 18729409 (161-b1-1 had re-made it). The re-pin to a1fd43fb by 161-a3-2 (test file `:138`) came later and fixed the failure; it could not have caused a fail at 09:45. 161-a3-1 recorded exactly this: `diag_c161_a3_1_facts.md:29-30,47` says "both fails PRE-EXISTING … P pins pred 48b50b29".
- **D2 is not a pin check.** At 09:45 its assertion was "stored pred set == the old set (0,2,3,5,7,9,10)" (`after_…delckpt.out:3`; `diag_c161_a3_1_facts.md:29`). The stored set was already the new one (0,1,2,3,4,5,7,8,9,10). 161-a3-2 then rewrote D2 to compare against the stored sets and a new x10 record (`selftest_c161_delckpt.py:97-99`; `diag_c161_a3_2_facts.md:29`). The test went green because its expectation was rewritten, not because a pin caught up with a file.

## 2. Alternative explanation of the same evidence
The test was out of date in two places since 161-b1-1 re-made the pred:
- D2 still expected the old stored set.
- P still pinned 48b50b29.

161-a3-2 rewrote both. That is a legitimate update, since the rule is supposed to change the stored set. But the rewritten D2 is partly circular:
- The x10 record was made by `stagexec.checkpoint_ops` (`diag_c161_a3_2_facts.md:12`). "x10 record == cp" therefore compares `checkpoint_ops` with itself.
- If the stored pred sets were produced the same way, "stored == cp" is circular too.
- The only independent part of D2 is the hard-coded `sorted(OLD | DW) == cp`.

## 3. What would falsify the claim
Any of these:
- The before sweep at 11/0 → it isn't. Falsifies "the pins went stale after the run".
- The checkpoint list printed in D2's detail differing from (0,1,2,3,4,5,7,8,9,10) → it doesn't.
- Any of V1–V5 failing → none did.
- On the current bytes, D2's line `:99` failing, or V2–V5 failing.

What actually rules out a defect in the delete_wire rule:
- In the failing run itself, D1 and V1–V5 all passed. Sets missing op 1, 4 or 8 were refused with `delete_wire op(s) not in the set: [..]` and 0 backend calls (`after_…delckpt.out:2,5-9`).
- D2's own detail shows `'delete_wire': [1, 4, 8]`.

## 4. Cheapest test that separates the two explanations
Two offline reads, no LabVIEW:
1. Compare the before and after `.out` files: 9/2 in both, same two labels, so the failure came before the card and was not caused by it. Already done above.
2. Re-run `selftest_c161_delckpt.py` on the current bytes (about 30 s). It already gave 11/0 at 10:07 (`selftest_c161_delckpt_c161_a3_2.log:23`, test file 9bd4889a, pred a1fd43fb). This is still valid only if neither file's md5 has moved since then. `diag_c161_b2_1_facts.md:34` shows the pred unchanged after 161-b2-1.

To make D2 a real check, add one gate that does not go through `checkpoint_ops`. For example, compute the required set by hand from the op kinds in D1's detail: binding ops {2,3,5,7,9}, plus delete_wire ops {1,4,8}, plus ops 0 and 10.

## Side findings
- **Suite harness hides fail lines.** `prep_c161_a3_1_suite.py:30` catches only lines starting with `FAIL` or containing `GATE FAIL`. delckpt prints `  FAIL  …` with two leading spaces, so the suite log shows `fails=[]` next to `fail: 2` (`prep_c161_a3_1_suite_after.log:8`). That is why the cause had to be reconstructed after the fact.
- **The stored p5s02a set is refused.** The executor rejects it for lacking op 12, a move_in run-closing op, not a delete_wire one (`after_…delckpt.out:17-18`). The S gate passes anyway because it only checks for delete_wire reasons. This doesn't bear on the claim, but replaying that stored set would be refused.
- Rule 1a is not affected: this is offline Python that checks checkpoint sets, not a VI's computation.
- I did no web search, because every claim here is about this project's own Python and logs, with no external API involved. I ran nothing and edited nothing.

**What would change my verdict:** a current-bytes run in which V2–V5 or the independent part of D2 fails.

## Sources

(extract from answer)

## What was done with it

Card 162-a2-1 (2026-10-10 11:3x, brief_162-a2-1.md step 4). The CONCLUSION held (the delete_wire checkpoint rule is not
defective) and the review's CORRECTION of the explanation is ADOPTED: the 09:45 fails pre-dated the re-pin (pred pinned
48b50b29 while the file was 18729409) and D2 was an outdated expectation that 161-a3-2 rewrote; "stale pin after the run"
is not claimed. Current-bytes run `tools/bench/selftest_c161_delckpt_c162_a2_1.log` (test 9bd4889a): 10 pass / 1 fail -
D1, D2, V1-V5 and the three S gates PASS (:4-19); the one FAIL is `P pins unchanged` (:21), plan_ring_p5s02b_pred.json
a1fd43fb (pin, selftest_c161_delckpt.py:138) vs 4cef0a8c on disk since card 162-a1-2's census write
(diag_c162_a1_2_facts.md:39). That pin is not one the brief names, so it was NOT edited and fp-84 was NOT drained; returned
to judgement. The review's circularity point on D2 (x10 record and stored sets both from checkpoint_ops) and its side
findings (suite harness misses "  FAIL" lines, stored p5s02a set refused for op 12) are recorded, not acted on here.
