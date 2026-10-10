---
type: facts
status: current
date: 2026-10-10
card: 159-f1-1
---
# Suite re-pins to the final tool bytes + the two labview-read suites (PD388(f), PD389(e)) - re-pins green, c134_1_dry FAIL 9/2
## Re-pins (old -> new)
- selftest_c158_runcheck.py:152 `"tools/stage_prerun.py": "9decb20f"` -> `"7605116f"` (docstring :24 same). No stagekit pin (only a FACT print :156).
- selftest_c158_wire0face.py:260 `"tools/stage_prerun.py": "9decb20f"` -> `"7605116f"` (docstring :29 same). No stagekit pin (FACT print :265).
- selftest_c134_2_gates.py:91-93 `records(2)` / "D2 dry_rule 2 -> allowed" -> `records(3)` / "D2 dry_rule 3 -> allowed" (docstring :11 same); stage_prerun.py:3434 DRY_RULE = 3.
## Re-pinned suites (final bytes) - all green
- runcheck 10/0 (diag_c159_f1_1_c158_runcheck_final.log), wire0face 24/0 (..._c158_wire0face_final.log), c134_2_gates 11/0 (..._c134_2_gates_final.log).
## labview-read suites: `py tools/bgrun.py --material --max-min 20 --log <log> -- py -u tools/bench/<suite>.py`
- selftest_stagekit -> selftest_stagekit_c159_f1_1.log:79 `51 pass / 0 fail` vs last pass diag_c147_c3_1_selftest_stagekit.json:4-5 (2026-10-08) 51/0: EQUAL. (log ends "(NO RESULT LINE)", :80, as before.)
- selftest_c134_1_dry -> selftest_c134_1_dry_c159_f1_1.log 9 pass / 2 fail (BGRUN END rc=1 144 s) vs last pass selftest_c134_1_dry_c136_p2_measure.log:5 (2026-10-02) 11/0: NOT EQUAL.
  - T2a (log:5): recipe tools/recipes/stage_d1_ring_p3b2a.py md5 now 0d1f0c15, pin bb5ba064 (selftest_c134_1_dry.py:82). Recipe last changed by git e86181ad 2026-10-04 (chat-E3 scope header appended).
  - T2 (log:6): bb5ba064 -> "=== DRY FAIL: first_fail=GATE PB frame-keyed cdiff(S1, real end) == the bed's 16 rows and the plan's 11 open (node, term) pairs (FATAL, before save)", coverage 63/81, unverified 1.
  - No c134_1_dry run exists between 2026-10-02 and today, so whether T2 fails from today's stagekit edit, the 10-04 header or another tool change is NOT measured. Not diagnosed (card rule).
## Other self-tests on stale pins (LISTED, not re-pinned)
- No self-test pins stagekit 9cd8822e (only selftest_c159_cen2_ends.py:37, which pins its kept copy file, and prep_c159_c1_1_mk.py:55, a prep script).
- Pin stage_prerun 9decb20f (+ stagekit 07f9e35f): selftest_c156_passwire.py:161, selftest_c155_basecase_frame.py:206, selftest_c156_b2_2_invcheck.py:101 - not run.
## md5 after / unchanged
- stagekit ac3a8f57, stage_prerun 7605116f, stagesim eb99c6ba, stagexec 7a712ccb (unchanged by this card). Self-tests now: runcheck 0c638d34, wire0face 02f3cc46, c134_2_gates a2965b7e.
- VIs (bytes, via selftest_c159_cen2_ends V0/V1, diag_c159_f1_1_vipins.log): 94ffff94, s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae unchanged.
- `git status --short tools/hooks` -> only `M tools/hooks/material_marker.log` (written by bgrun --material). No LabVIEW process before or after (tasklist).
## OPEN
- selftest_c134_1_dry T2a/T2 (selftest_c134_1_dry.py:82-84): re-pin to the header-carrying recipe md5 and re-judge T2, or bisect T2 (10-04 header vs 10-10 stagekit) first? No JEV-LADDER row yet for selftest_c134_1_dry_c159_f1_1.log.
