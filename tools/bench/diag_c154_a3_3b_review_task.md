ATTACK this claim (card 154-a3-3b, failed-prediction gate on tools/bench/diag_c154_a3_3_el.log, script tools/bench/diag_c149_a1_2_elrun.py).

CLAIM: diag_c154_a3_3_el.log ended `BGRUN END rc=1` with `ERRORLIST-VERDICT: MISMATCH` (items 47 == window N 47, extra 2, missing 0,
log lines 77-83) only because the elrun wrapper compares the NEW P5-1a file's read against the PREVIOUS step's expected file
(`tools/bench/errorlist_expected_D1_ring_p4s09_20261009_060515.json`, total 45). The P5-1a plan (`tools/bench/plan_ring_p5s01a.json`, 20 actions,
14 ops: creates Obtain Queue, Enqueue Element, a Case, a count shift register, Increment, tunnels) ADDS Error List items. Its pred
(`tools/bench/plan_ring_p5s01a_pred.json` errorlist block, lines 182-376) predicted 48 = base 45 + 3 new `input` items (#-56 TC2 the
count-out case tunnel in the False frame, #-24 Enqueue, #-3 Obtain). The read (`tools/bench/errorlist_D1_ring_p5s01a_20261009_101219_20261009_102108.json`)
has 47: the two extra items are 'Tunnel: Missing assignment to tunnel' (= TC2, which the pred classed as `input`) and
'Enqueue Element: Contains unwired or bad terminal' (= #-24); no item names Obtain Queue (#-3). Obtain's only required input
'element data type' is wired by plan action w_qk_obt (op 3), so an Obtain error is not expected; the pred's #-3 item is the pred's error.
Per class read: input 2 (base Build Array + Enqueue), tunnel 1, not-connected 22, loose-ends 21, two-types 1 (pred: input 4, 22, 21, 1).
The Error List is a RECORDED cross-check, not a gate (PD354, PD370(a); brief `tools/bench/cards/brief_154-a3-3.md:20`): the card writes the
P5-1a expected file from what was read and continues.
Same pattern as cards 151-a3-1 / 152-b3-1: `tools/bench/diag_c152_b3_1_el.log` rc 1 MISMATCH vs the s08 file, recorded (`tools/bench/diag_c152_b3_1_facts.md:27-33`).

Context that is measured: the scratch that made this file passed 23/0 (E1 real == sim for all 14 ops, D new 10 == sim 10, lost 1 == 1,
TD/PB PASS, PRIM PASS for Obtain/Enqueue/Increment) - `tools/bench/diag_c154_p5s01a_scratch.log:235-277`; the read bed md5 2482fe7b == scratch saved
file; bed md5 unchanged True (el.log:83).

Already ruled out: environment fault (OCR loaded, 47 items read == the window's own count 47); a different file (md5 match).

Questions: what is the strongest reason the claim is wrong (e.g. the missing Obtain item means op 3's wire did not land, or the Tunnel item is not TC2);
an alternative explanation; what would falsify the claim; the cheapest discriminating test (offline, from the graph read the card does next).
