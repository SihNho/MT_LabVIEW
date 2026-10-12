# diag_c171_a2_1 facts (card 171-a2-1, assignment 171-2, 2026-10-13) - offline, no LabVIEW (tasklist 0 before/after)
## Step 0 re-hash (`diag_c171_a2_1_hash.log`, 20/0 PASS): all 19 rows OK, no drift
D1_ring_p6_20261012_212645.vi c2d9c13c | D1_ring_p5_20261010_172913.vi 75773b0d | graph_ring_p6_20261012_212645.json fbc7b7ee
D1_s1_copy.vi 3e3d23ce | D1_s1_replay_20260925_075422.vi 126f8497 | replay_imaqdx_get_image_buf.vi a89dafc1 (label swapped per PD413(d))
replay_get_image_cal.vi afce0d04 | replay_get_buff_image.vi 842ecad9 (label swapped) | replay_imaqdx_get_image_buf_paced60.vi e40ec867
replay_get_buff_image_paced60.vi 59ec66b6 | p6_replay_frames_manifest.txt 9055d98a | m8b_replay_compare.py 82443af9
plan_replay_swap_170.json 01c21526 | stage_replay_swap.py fa94e80c | stage_prerun.py db81a1d3 | plan_replay_swap_78.json cdc14e32
plan_replay_swap_95.json ea7cf810 | plan_replay_swap_110.json 6b5ef7e5 | diag_c171_a1_2_patch.diff f8f1fd95 (row added)
7f2582ae -> claudeDev\D1_ring_p5s01b_20261009_123319.vi and D1_ring_p5s01_20261009_124542.vi (`_hash.log:21`)
Script edit: diag_c171_a1_1_hash.py (two labels swapped, one row added) -> md5 bca9f5c7.
## Step 1 - selftest_dry_c130_5.py ONCE on UNPATCHED stage_prerun (`diag_c171_a2_1_c130_5_unpatched.log`, 115 s)
stage_prerun.py md5 db81a1d3 before AND after; `git diff --stat tools/stage_prerun.py` empty before and after.
T1 `:4` FACT T1 SKIPPED: plan_ring_p3b.json is no longer the stale 4003eaa5 fixture (re-finalized, PD268(c))
T2 `:6` PASS  T2 injected stop at op 5 ... EXECUTOR-STOP executed 4 of 21 ops
T3 `:8` FAIL  T3 full run stage_d1_ring_p3a.py: ... === DRY FAIL: first_fail=GATE PB frame-keyed cdiff(S1, real end) == the P2b bed's
   16 rows and the plan's 11 open (node, term) pairs (FATAL, before save) coverage 61/79 lines, first mutation Stage._op create,
   unverified 1, graph tools/bench/graph_ring_p2b_20261001_154542.json   (`:7` executors: planned 21, executed 21, completed)
T4 `:9` PASS executor_stops unit
Totals `:10` RESULT status FAIL gates pass 2 fail 1, first_fail "T3 full run stage_d1_ring_p3a.py ..."
## Class: A - T3 FAILs at GATE PB with the same text as `diag_c171_a1_2_c130_5.log:8` (lines 3-9 of both logs are
   textually identical; totals 2/1 in both; only card id and runtime 115 s vs 116 s differ). I.e. the FAIL is present on the unpatched checker db81a1d3 too. Decision not taken.
Record stays 3/0 (`selftest_dry_c130_5_c134_2.log:10`). No Jev ladder row for this log in jev_gate.log.
