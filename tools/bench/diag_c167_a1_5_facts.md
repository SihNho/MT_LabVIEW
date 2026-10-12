# Card 167-a1-5 facts (offline; no LabVIEW, no VI opened, no hook edited)
## Checks
- Hash before/after: diag_c167_a1_5_hash_before.log 8/0, _after.log 8/0 (8 card inputs equal except the 3 editable ones, 7 VIs equal to 75773b0d 7f2582ae eb1d0f31 94ffff94 f9ae7751 564d8cbe 6dcd5c3d).
- After: stagekit.py 22967183 (was b40155ed), selftest_c147_b1_2.py 6b634c81 (was 6bdde02b), errorlist_check.py bfa0a387 unchanged (_hash_after.log FACT lines).
- tasklist | grep -ci labview -> 0. `git diff --name-only -- tools/hooks` -> only tools/hooks/material_marker.log (the hook's own log, modified before this card started; no .py).
## Part A - shared helpers (note 2)
- Shared elcls ALREADY existed: stagekit.el_class (tools/stagekit.py:2840) + el_norm_ocr (:2831); no second one added.
- Moved into tools/stagekit.py (append-only, no existing line shifted): json_text_like :3205, json_newline_of :3216, rewrite_json :3221, json_changed_keys :3235, rewrite_json_selftest :3240.
- tools/bench/diag_c166_a1_1_lib.py now binds its four names to those stagekit functions (mm.py / census.py unchanged, they call the lib).
- diag_c166_a1_2_elexp.py had NO inline elcls/norm_ocr (its own docstring :10-13); not edited.
- Self-test diag_c167_a1_5_selftest.log 5/0: E2 'stagekit.el_class == old inline elcls per item: 47 equal, 0 differ' (old copy executed from diag_c165_a3_4_elexp.py:34,43,50 via ast).
- E3 class_counts(items) == stored diag_c166_a1_2_elexp.log:15 (looseends 23, anything 21, anvthing 1, buildarray-unwired 1, twotypes 1).
- E4 el_class counts = {input 1, other:...looseends 23, other:...anything 22, other:...twoterminals 1}: el_class folds OCR 'anvthing' into 'anything', so its classes are 4, not the brief's 5 (those are class_counts' plain-norm keys).
- J rewrite_json_selftest: 2 round-trips OK + rewrite in %TEMP%: written, backup byte-equal, changed keys == the one new key, 16 other keys equal, layout kept.
- Lib re-run diag_c167_a1_5_lib_selftest.log PASS 2/0; its SELFTEST lines md5 71c8db3e == stored diag_c166_a1_1_lib_selftest.log SELFTEST lines md5 71c8db3e.
- ruff: not run (`py -m ruff` needs an approval this session cannot give; guard_bash also refuses a command naming tools/stagekit.py, labview: build). lint.py / dupcheck.py take no file argument.
## Remaining old copies (closed scripts, not edited - record of what ran)
- elcls: diag_c150_a3_2_elexp.py:50, c151_a1_1:48, c152_b3_1:48, c154_a3_3:48, c155_a3_2:50, c158_a3_2b:49, c162_a1_2:50, c163_a2_2:50, c164_a3_5:50, c165_a3_4:50 (all *_elexp.py), diag_c149_a1_2_eladv.py:36.
- elcls: prep_c147_a1_3_pred.py:61, prep_c148_a3_3_pred.py:56, prep_c150_a2_5_pred.py:58, prep_c150_a3_1_pred.py:63, prep_c150_a3_6_pred.py:70, prep_c152_b2_1_pred.py:79, prep_c154_a3_2b_pred.py:61.
- elcls: tools/recipes/stage_d1_ring_p4_s06v18_scratch.py:95, s07v18:98, s08v18:98, s09v18:98, stage_d1_ring_p5s01a_scratch.py:98.
- JSON rewrite: prep_c164_a3_7_write.py:53 `dumps`.
## Part B - re-pins (note 6), each: ONE failing gate before, PASS after
- selftest_c165_innerface.py:250 stagekit dd57c1ca -> 22967183. Before: 'FAIL  P pins unchanged ... stagekit.py: 22967183' (24/1, _pin_innerface_before.log:31). After: 'PASS  P pins unchanged', RESULT PASS 25/0.
- selftest_c165_prime.py:117-118 stagekit dd57c1ca -> 22967183 (label + check). Before: 'GATE FAIL | P graph ..., stagekit dd57c1ca unchanged' (37/1, _pin_prime_before.log:118). After: PASS 38/0.
- selftest_c147_b1_2.py:29-30 P0 pins stagexec 1bab9cf9->1d5309f4, memory_model.json 88eeb037->d12bcd3b, plan_ring_p4_s06v18_pred.json c4a6a35a->c1bd6b3e. Before: P0 FAIL (19/1, _pin_c147_before.log:3). After: P0 PASS, P1 PASS, 20/0.
## Part C - STATUS relocation (note 7)
- Pre-edit copy tools/bench/diag_c167_a1_5_status_pre.md 3726898b (155 lines); moved = pre lines 76..87, 12 '- (history' bullets CYCLE 163 .. Cycle 158 round 3.
- archive/2026-10-12-status-cycle167-relocate.md 02f0ffb6 written by diag_c167_a1_5_relocate.py archive (bytes from the copy); STATUS edited with the Edit tool.
- diag_c167_a1_5_relocate_check.log 6/0: M 12 lines byte-equal contiguous in §1 (archive line 16); S whole-file byte compare == pre with 76..87 -> one pointer line; N 144 == 155-12+1; K current_bed_text -> D1_ring_p5_20261010_172913.vi; R 5 machine-key lines equal; H 12/12 about cycles < 164.
- Left in ## NEXT (not '- (history' bullets): STATUS.md:77 '- CARRY', :78 PARALLELISM RULE, :79 CYCLE 158 ROUND 2 (no history tag), :80-94 '(history ...' paragraphs for cycles 150-158 without '- '.
