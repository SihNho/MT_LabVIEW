---
card: 148-a3-2
date: 2026-10-08
status: PASS - unmask 5/0 EQUAL, worktrees cleaned, 4/4 suites GREEN (NOW failing set is a subset of PRE)
---
## Step 0 (before)
- LabVIEW processes: 0 (`tasklist /FI "IMAGENAME eq LabVIEW.exe"` -> "no tasks match").
- git worktree list: main 07202624 [master]; Temp/e3head_r96iqm4t, Temp/f2head_1n3cihvt (detached 07202624); V6_bench/A, A13, A13K, A_run1_20261006_2113, B.
- Invariants: stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c; stage_prerun dcd45aba; unmask efb5f66b; suites 014319cd.

## Step 1 PREDICTION (written before the run)
- diag_c148_a2_3_unmask.py (revised): p3b2_A, p3b2_B, s03_A, s03_B EQUAL HEAD vs disk; c106e_noX17 both sides X5 PASS (ops 7), 0 FAIL, 0 differing lines -> RESULT 5/0.

## Step 1 RESULT - diag_c148_a2_3_unmask_r2.log (d2f3fd70), BGRUN END rc=0 after 259 s, RESULT PASS 5/0
| case | HEAD | DISK | verdict |
|---|---|---|---|
| p3b2_A | ok, 116 uids bound, re-sim final=True | same | EQUAL 89/89 |
| p3b2_B | ok, 116 uids, final=True | same | EQUAL 89/89 |
| s03_A | ok, 20 uids (not re-simulated) | same | EQUAL 4/4 |
| s03_B | ok, 20 uids | same | EQUAL 4/4 |
| c106e_noX17 | rc 0, 25 PASS / 0 FAIL / 6 WARN, child RESULT PASS 15/0, DRY PASS coverage 58/70, graph_dispA_step33.json | same | EQUAL 58/58, 0 diff lines |
- 4 children each got a fresh PRERUN_LOG_DIR (log :16,:18,:20,:22 "fresh True"). The log prints gate counts, not the X5 line itself, so "ops 7" is not quoted; X5 is among the 25 PASS (0 FAIL).
- tools/bench/sim/disp/graph_dispA_step33.json mtime 2026-09-27 03:06 (not rewritten by the run).

## Step 2 - diag_c148_a3_1_suites.log (ffbe085d), BGRUN END rc=0 after 3122 s, RESULT PASS 4/0
- Cleanup: worktree remove --force e3head_r96iqm4t rc=0, f2head_1n3cihvt rc=0, prune rc=0 (log :14-16); no c148a23head_* dir existed. PRE tree c148a31_s5hspi_b (HEAD 07202624) removed rc=0 at the end (:174). Final list (:177-182): main + V6_bench/A, A13, A13K, A_run1_20261006_2113, B.
- PRE md5s (tree = HEAD blob CRLF, != disk, all "pre-fix"): stage_prerun 87aa6bbf/disk dcd45aba; guard_cycle 67cc1f38/2df2f11c; guard_write 4195b4fb/f61bec73; guard_assign e9879c20/bbaa2325; selftest_assign_flow 9da0d231/47906beb; c147_b1_2 39deebd5/1dd09f3d; chat_p1 8250b3ef/8753ee8a; chat_p2 b8d2925f/69460108; guard_cycle_offline 559ce71c/9f170fee; guard_cycle_rerun 1999831b/5dde9eea; guard_session 6956b1c4/d4f63b2f; guard_session_pairing edf76181/45592a58.
| suite | NOW rc / result / s | PRE rc / result / s | NEW | verdict |
|---|---|---|---|---|
| c134_1_a4 | 1 / FAIL 9/3 / 824 | 1 / FAIL 4/8 / 249 | [] | GREEN (:162) |
| c134_2_regress | 1 / FAIL 13/4 / 1008 | 1 / FAIL 8/9 / 243 | [] | GREEN (:163) |
| c_e3_suite | 0 / FAIL 56/11 / 435 | 0 / PASS 67/0 (24 pre-existing) / 673 | [] | GREEN (:164) |
| f2_suite | 0 / PASS 73/0 (13 pre-existing) / 795 | 0 / PASS 73/0 (27 pre-existing) / 752 | [] | GREEN (:165) |
- NOW failing children: c134_1: c133_6_fr (KeyError 'fs_frames'), stage_prerun_c106e (E1), c125_1_offline_measure (c134_1_dry). c134_2: same + c134_1_dry. All also fail PRE.
- c_e3 NOW's 11 are tagged "FAIL (new test) ... HEAD: absent at HEAD" (:61-71) although e.g. selftest_chat_p1.py IS in HEAD (its blob is shown at the PRE md5 step); f2 NOW lists the same 11 as PRE-EXISTING with identical text at HEAD (:74-86). So 0 real new failures; the e3 suite's HEAD lookup misreported.
- Deviation from the wrapper's docstring prediction ("c134 failing sets NOW == PRE"): PRE fails 5 MORE children (dry_c130_5, c103, c106c, c128b, stageplan; pre-only, :162). Cause seen: the %TEMP% HEAD worktree lacks untracked data files (FileNotFoundError .../c148a31_s5hspi_b/tools/bench/sim/ring_p3b2a/step_21_wire_remove_loose_ends.json, :102). NOW subset of PRE in all 4 suites.

## Step 3 (after)
- LabVIEW processes 0 (tasklist after; wrapper :4 and :184). Invariants unchanged: stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun dcd45aba. No tool/hook/plan/recipe/self-test edited; written: this file, diag_c148_a2_3_unmask_r2.log, diag_c148_a3_1_suites.log.

OPEN: the PRE baseline (a HEAD worktree) misses untracked data, so 5 children fail there only; accept "NOW subset of PRE" as green, or require a baseline that carries the untracked sim files?
