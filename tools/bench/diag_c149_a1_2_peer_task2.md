ATTACK this claim (card 149-a1-2, failing log tools/bench/diag_c149_a1_2_eladv.log, script tools/bench/diag_c149_a1_2_eladv.py).

CLAIM: diag_c149_a1_2_eladv.log:3 (EL-ADVISORY total read 51 pred 55 diff -4, unseen [], rc 1 RETURN) is a faithful evaluation of
the recipe's own EL-ADVISORY rule on the s06 Error List read tools/bench/errorlist_D1_ring_p4s06_20261008_174730_20261008_181243.json,
and it is the SAME failure already reviewed in archive/peer/2026-10-08-c149-a1-2-el51.md (the 51-vs-55 read of diag_c149_a1_2_el.log),
not a new one. diag_c149_a1_2_eladv.py copies tools/recipes/stage_d1_ring_p4_s06v18_scratch.py:84-129 (OCR_ALIASES, EL_TOTAL_TOL 3,
norm_ocr, elcls via tools/elrule.py item_class, el_advisory) because guard_bash's launch gate refused the recipe's own offline
`--el-advisory` mode citing an old failed segment of the appended scratch log (logged as gate FP fp-62). The only intentional change is
the pred's plan-md5 key check, which uses a plain md5 of tools/bench/plan_ring_p4_s06v18.json instead of stagekit.md5.

Give: the strongest reason the copy is NOT equivalent to the recipe's rule (a line that differs in effect), whether rc 1 could be an
artefact of the copy, what would falsify "same failure as el51", and the cheapest read-only check. No LabVIEW.
