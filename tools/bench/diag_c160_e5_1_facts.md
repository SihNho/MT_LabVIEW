---
type: facts
status: current
date: 2026-10-10
card: 160-e5-1
---
# 160-e5-1: stagekit pin 1441bb4c -> 0b5bb678 in 5 suites + 5 pin-only helpers; 5 suites back to pre-edit counts
- Edits (old -> new, value only): basecase_frame.py:28,207 `stagekit 1441bb4c`/`"1441bb4c"` -> 0b5bb678 (7a26495e); b2_2_invcheck.py:96 GATE text `1441bb4ca75eb5a59afaa3555690db37` -> `0b5bb678169d659feed7408648a63354` (+ "; 160-e5-1 from 1441bb4c"), :106 -> 0b5bb678 (816c6268)
- passwire.py:34,164 -> 0b5bb678 (d652bdc0); delwire.py:17 appended "160-e5-1 re-pinned 1441bb4c -> 0b5bb678.", :51 -> 0b5bb678 (68383459); regface.py:43 -> 0b5bb678 (2e3f7cc6)
- Helpers: diag_c160_h1_1_check.py:24 (bb4549bf); diag_c160_g1_1.py:11,27 (1074419c); diag_c160_b2_1_md5.py:13 + comment (200abb12); prep_c160_b3_1_mk.py:46 + comment (c0d1d315); prep_c160_b1_1_mk.py:39 + comment (8acf4434)
- basecase_frame: pre 0,21,0 -> now 0,21,0 `selftest_c155_basecase_frame_c160_e5_1.log:25` RESULT pass 21 fail 0, BGRUN END rc=0
- b2_2_invcheck: pre 0,20,0 -> now 0,20,0 `selftest_c156_b2_2_invcheck_c160_e5_1.log:183` RESULT 20/0, rc=0
- passwire: pre 0,20,0 -> now 0,20,0 `selftest_c156_passwire_c160_e5_1.log:34` RESULT 20/0, rc=0 (532 s)
- delwire: pre 0,20,0 -> now 0,20,0 `selftest_c160_delwire_c160_e5_1.log:40` RESULT 20/0, rc=0
- regface: pre 0,12,0 -> now 0,12,0 `selftest_c160_regface_c160_e5_1.log:37` RESULT 12/0, rc=0 (its own artefact diag_c160_a2_1_plan_tmp.json 73971108)
- Final check: l0stem 14/0 `selftest_c160_l0stem_c160_e5_1.log:17` (ca61ea47 unchanged); stagemap 5/0 `selftest_c160_stagemap_c160_e5_1.log:9`
- UNCHANGED md5: stagekit 0b5bb678, stagesim 95a162ba, stagexec ddf23a31, stage_prerun 7605116f; no plan_ring_* / tools/hooks file newer than requires_160-e5-1.json except hooks/material_marker.log
- OPEN: live 1441bb4c pins remain only in prep_c160_c3_1_pred.py:39 and prep_c160_c3_1_md5.py:17 (+ docstring :7) - card 160-c3-2 owns them, not edited.
- OPEN: history/docstring mentions left as text: selftest_c160_l0stem_regress.py:13, delwire.py:17, and the "from 1441bb4c" comments added here.
