ATTACK this claim (card 151-a3-1, failed-prediction gate on tools/bench/diag_c151_a1_1_el.log, script tools/bench/diag_c149_a1_2_elrun.py).

CLAIM: diag_c151_a1_1_el.log ended `BGRUN END rc=1` with `ERRORLIST-VERDICT: MISMATCH` (items 46 == window N 46, extra 0, missing 4,
line 82) only because the elrun wrapper compares the NEW session-8 file's read against the PREVIOUS session's expected file
(`tools/bench/errorlist_expected_D1_ring_p4s07_20261008_222709.json`, total 50). The session-8 plan (`tools/bench/plan_ring_p4_s08v18.json`,
19 actions, ops 166..184) closes Error List items: its pred (`tools/bench/plan_ring_p4_s08v18_pred.json`, errorlist block) predicted 48
(base 50, closed local #30016 and shift register #9603). The read is 46: 2 below the pred, inside the PD354(a) tolerance |total diff| <= 3
(`tools/recipes/stage_d1_ring_p4_s08v18_scratch.py:88,109-126`). The Error List is a RECORDED cross-check, not a gate (PD354; brief
`tools/bench/cards/brief_151-a1-1.md:28-29`): the card should write the s08 expected file from what was read and continue.
Same pattern as the s07 card: `tools/bench/diag_c150_a3_2_el.log` rc 1 MISMATCH vs the s06 file (extra 1, missing 2), recorded
(`tools/bench/diag_c150_a3_2_facts.md:27-31`).

Context that is measured: the scratch that made this file passed 22/0 (E1 real == sim for all 19 ops, D new 11 == sim 11, lost 5 == 5,
TD/PB PASS) - `tools/bench/diag_c150_p4s08v18_scratch.log:264-274`; the read bed md5 f99e8414 == scratch saved file, byte copy identical;
`refine_rows: not refined [18, 29]` (el.log ~line 78); the wrapper's own line 81 says "BY-DESIGN check: STOP - Error List items MISSING
['None','None','None'] - never by design".

Already ruled out: environment fault (OCR engine rapidocr loaded, 46 items read == the window's own count 46); a different file (md5 match).

Questions: what is the strongest reason the claim is wrong (e.g. the 2 items below the pred mean an action closed something the plan did
not intend, or OCR lost rows)? Which 4 items are missing relative to the s07 expected file, and which 2 relative to the pred? What
cheapest offline test separates "pred over-counted" from "read lost rows" from "the build closed an unplanned error"?
