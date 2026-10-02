# c135-2-launch-compare

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** 
- **date:** 2026-10-02 12:46:43
- **outcome:** TIMEOUT (180s)
- **verdict-card:** NO-VERDICT: outcome TIMEOUT
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id hyp-c135-2-launch-compare, role hypothesis) ---
CLAIM: launch_p3b2_c135.log failed (compare DIFFERENT -> finalize F3 FAIL) by our-script-bug only: compare used STORED borders and ref 102553 predates the 134-6 'status' annotation (stagesim.py:386); re-annotated, the a-file graph equals the ref on every field, so plan b ae6b6111 applies unchanged.
PREDICTED: C EQUAL (LabVIEW uid allocation deterministic, PD290(d)) -> plan b ae6b6111 as is -> session b
OBSERVED: C DIFFERENT on 'borders' only (launch_p3b2_c135.log:43): 7 nested-FS borders carry status UNMEASURED in 123012, not in 102553; F3 10363 != 10334 (+29 a-created rows). Re-annotated compare offline: EQUAL, ref changes = 7 x status added (diag_c135_2_compare.log); self-test 9/0.
ALREADY RULED OUT: a real border difference: the re-annotation diff on the reference is ONLY an added 'status' key, no removed/changed field (diag_c135_2_compare.json reannotation_changes)
ALREADY RULED OUT: a terminal/wire/frame difference: graph_key fields node_classes, terminals (full rows), wires, fs_frames EQUAL in both the old and the new compare (launch_p3b2_c135.log:43, diag_c135_2_compare.log)
ALREADY RULED OUT: F3 as a computation difference: PD290(b) accepted +29 object rows as representation (no simulated Wire/Terminal object rows); F3's reference is 04204133's end, not the a-file
ATTACHMENT: tools/bench/launch_p3b2_c135.log (md5 baabf65168b18bbe5c61f03ce89fb016)
ATTACHMENT: tools/bench/launch_p3b2_c135_f.log (md5 None)
ATTACHMENT: tools/bench/launch_p3b2_c135.py (md5 16e941a61d3cf0695d58f6a921fc767f)
ATTACHMENT: tools/bench/launch_p3b2_resume_c135_compare.py (md5 None)
ATTACHMENT: tools/bench/selftest_c135_2_compare.log (md5 None)
ATTACHMENT: tools/bench/diag_c135_2_compare.log (md5 None)
ATTACHMENT: tools/bench/diag_c135_2_compare.json (md5 None)
ATTACHMENT: docs/d1/ring-p3b.md (md5 None)
--- END REVIEW CARD ---

Refute the claim in the attached review/1 card (launch_p3b2_c135.log failure = our-script-bug in compare C; plan b applies unchanged to the a-file). Read the attached logs and scripts.

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"hyp-c135-2-launch-compare","verdict":"<one of: refuted | supported | unverified>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

(no answer within 180s — job stopped)

## Sources

(extract from answer)

## What was done with it

TIMEOUT (180 s default) - told nothing. Re-dispatched with -TimeoutSec 900 as `2026-10-02-c135-2-launch-compare-r2.md` (ANSWERED).
