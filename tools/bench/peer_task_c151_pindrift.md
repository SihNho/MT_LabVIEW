ATTACK this claim (refute it; do not confirm it).

Failure under review: `tools/bench/selftest_c147_b1_2_postmerge.log` (script `selftest_c147_b1_2.py`), first failing line 3:
`FAIL P0 pins before == card inputs ... {'memory_model.json': ['b4a6eec6','d42ccd46'], 'plan_ring_p4_s06v18_pred.json': ['c1bd6b3e','44e0a50e']}` - 19 pass / 1 fail.

Claim: this failure is NOT a regression from the chat-T6 merge (commit 9dbd384b, result gates D/TD/PB keyed by position). It is pin drift of a FROZEN cycle-147 self-test: the test pins the md5 of `tools/bench/memory_model.json` (88eeb037) and `tools/bench/plan_ring_p4_s06v18_pred.json` (c4a6a35a) as they were in cycle 147; cycles 149-150 legitimately changed both files (commit 1449ae07: memory_model.json +10 lines = new load_by_vi entries; pred.json +25 lines = V18E-R' rows). Every semantic check of the same script after P0 passes (R1, T0..T5, F1, F2, P1 all PASS, log lines 4-24), including T5 s03/s04/s05 against the stored run verdicts and T1/T1n D/TD/PB on the L5 fixture. Evidence: `tools/bench/cards/result_chat-T6v.json` facts; `git diff 4d762e7f 1449ae07 --stat`.

Alternative explanations to try: (1) T6's position-key change altered a result the test compares (so P0 is a symptom, not the cause); (2) the pin drift hides a real change in pred.json that is not V18E-R' rows; (3) the same drift would also hit the s08 build route (plan_ring_p4_s08v18*.json) and so is not safe to ignore.
What would falsify the claim, and the cheapest discriminating test (e.g. which md5 the test's pins match at 4d762e7f vs 1449ae07).
Read-only. Answer within 10 lines.
