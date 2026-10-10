---
type: facts
status: current
date: 2026-10-10
card: 160-e4-1
---
# 160-e4-1: gate_l0 accepts <stem>_in[N] (fp-82). Predicate + self-test PASS; regression FAIL 10/5, every new FAIL a stagekit md5 pin
- OLD `stagekit.py:2410`: `... and os.path.splitext(fz["plan_in"]["path"])[0].endswith(st + "_in")`
- NEW `stagekit.py:2410`: `... and plan_in_matches_stem(fz["plan_in"]["path"], st)`; label :2409 `{0}_in[N]`; docstring :2405-2406 (same 2 lines).
- Predicate `stagekit.py:2872-2880` `plan_in_matches_stem(path, stem)`: basename w/o ext startswith `<stem>_in`, tail all ASCII digits (empty ok).
  No `import re`; added after `bound_from_cmap`, so no earlier line moved. Also stricter: a prefix (`xplan_..._in`) is now refused (old endswith allowed it).
- Self-test `selftest_c160_l0stem.py` (ca61ea47): `RESULT ... "gates":{"pass":14,"fail":0}` (`selftest_c160_l0stem_c160_e4_1.log`); accepts _in/_in2/_in12,
  refuses _inx/_in_2/_in2b/p5s02a stem/no suffix/_out/prefix; finalized.plan_in of p5s01a, p5s01b, p5s02a (_in) and p5s02b (_in2) all match their stem.
- md5 stagekit 1441bb4c -> 0b5bb678. UNCHANGED: stagesim 95a162ba, stagexec ddf23a31, stage_prerun 7605116f; no plan_ring_* and no tools/hooks file
  newer than the bind (only the hook's own `tools/hooks/material_marker.log`).
- Regression `selftest_c160_l0stem_regress.py` (calls prep_c156_a1_2_lib.run_suite, 15 c15x/c16x suites importing stagekit), before = fresh pre-edit run:
  before `diag_c160_e4_1_before.log` RESULT 1/0; after `diag_c160_e4_1_after.log` RESULT pass 10 / fail 5.
- EQUAL (rc,PASS,FAIL): compdiff_poskey 0,8,0; poskey_convert 0,10,0; gatefp73 1,8,2 (pre-existing); innerface 1,12,1 (pre-existing); gates386 0,16,0;
  runcheck 0,10,0; wire0face 0,24,0; a4_1 1,12,1 (pre-existing); cen2_ends 0,8,0; stagemap 0,5,0 (== last log selftest_c160_stagemap_c160a2.log:9, 5/0).
- DIFFER, only on stagekit md5 pins: basecase_frame 0,21,0 -> 1,20,1 (P1 pins); b2_2_invcheck 0,20,0 -> 1,18,2 (pin + exact GATE text with md5);
  passwire 0,20,0 -> 1,19,1 (P pins); delwire 0,20,0 -> 1,18,2 (P0 + V1 tool pins); regface 0,12,0 -> 1,10,2 (P0 + V1 tool pins).
- OPEN: pins of 1441bb4c (outside globs, not edited): selftest_c155_basecase_frame.py:207, selftest_c156_b2_2_invcheck.py:96,106,
  selftest_c156_passwire.py:164, selftest_c160_delwire.py:51, selftest_c160_regface.py:43; prep_c160_b3_1_mk.py:46, prep_c160_b1_1_mk.py:39,
  prep_c160_c3_1_md5.py:17, prep_c160_c3_1_pred.py:39, diag_c160_h1_1_check.py:24, diag_c160_g1_1.py:27, diag_c160_b2_1_md5.py:13.
- OPEN: card rule "a count that differs is a FAIL, not a re-pin" vs pass item 4 (pins listed as OPEN): the 5 pin-only diffs need a re-pin card.
