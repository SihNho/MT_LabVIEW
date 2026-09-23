FAILED PREDICTION (connectivity-map plan step 5b, bench A5). Attack the CLAIM below; find the strongest reason it is wrong.

CONTEXT. `tools/jev_pairs.py` PAIR menu = a yes/no model question per candidate terminal pair ("does this source -> sink
realise the intent?"). Step 5 measured it on 49 labelled items (`tools/bench/jev_menu_pair_result.json`, 11 positives):
acc@0.5 0.898, Brier 0.075, and set the act threshold 0.70 = the smallest grid t whose yes-precision is 1.0 ON THE SAME 49
items. The plan's criterion (docs/connectivity-map-plan.md row 5b, A5): on a HELD-OUT half, PAIR must reach accuracy >= 0.85
with 0 dangerous-direction errors (a false "yes" at/above the threshold) to keep acting.

MEASUREMENT (`tools/bench/bench_map_20260923/a5_heldout.py`, log `tools/bench/bench_map_a5.log`, JSON
`tools/bench/bench_map_20260923/a5_heldout.json`): the 49 stored answers (no re-asking) split 50/50 by seed 20260923, item
level. Threshold from half 1 by the same rule = 0.65. Half 2: accuracy 0.92, Brier 0.040, recall 0.83, dangerous errors = 1:
the candidate for intent 1893 ("#3447 ControlReferenceConstant 'Focus Step (F1)' -> #48 SubVI 'Focus inc reference'") scored
p = 0.698 but is labelled FALSE. CHAIN: t 0.25, acc 0.931, 0 dangerous. RISK: t 0.95, acc 1.0, 0 dangerous. OP: t 0.95,
argmax acc 0.5, 1 acted row, 0 dangerous.

CLAIM: "PAIR does not meet the held-out criterion, so it must NOT act; every PAIR verdict goes to the LLM until the menu is
improved."

ALREADY RULED OUT: the split is not a code bug (the 0.698 item is the same false positive step 5 recorded, fp at
0.698/0.636); no answer was re-asked, so this is threshold over-fitting on a 24-item half, not sampling noise.

QUESTIONS: (1) Is the 1893 item's FALSE label itself correct? Read the labelled set and tools/bench/jev_menus_step5.py
`pair_set` (label = candidate keys == the S1 truth keys) and the S1 graph (docs/wiki/subvi/D1_s1_copy.json, wire 1893) -
could the "wrong" candidate be the same physical terminal under a renamed key? (2) Is an item-level split of 49 items with
11 positives a sound basis for "0 dangerous errors" at all - what would a grouped-by-intent split or a bootstrap say? (3)
What is the cheapest discriminating test between "PAIR is unsafe" and "the criterion is unmeasurable at n=25"?
