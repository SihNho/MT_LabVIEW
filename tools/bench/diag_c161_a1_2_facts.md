# diag_c161_a1_2 facts (card 161-a1-2, offline, labview none)

## 1. selftest_c157_innerface re-pin
- Measured md5: stagesim 95a162baec5324ff037a8d23bd7ef46d (pin was eb99c6ba -> re-pinned), addrcheck 207beb0d09102c78b1e06d1f076eec7e,
  plan_ring_p5s02a.json 4284c22a540f9e3f39c7092affe516af, sim/ring_p5s02a/step_15_tunnel.json b7da7fa71e7643f848ec5ff85fef4f5d (3 unchanged, not touched).
- Edited: docstring `selftest_c157_innerface.py:28` and `PINS` `:72` (stagesim only). Re-run 13/0 (was 12/1): `selftest_c157_innerface_c161_a1_2.log:33`.

## 2. selftest_stagexec_s4 -> shared rule
- Launch first REFUSED by guard_bash: "CARD 161-a1-2 ...: flags.labview is 'none' - tools/bench/selftest_stagexec_s4.py declares labview: read (scope header)".
  The script is offline (docstring line 1 "OFFLINE: no LabVIEW, no VI opened"; SimBackend only). Header at the file end set to
  `labview: none` + `evidence: tools/bench/selftest_stagexec_s4.log:69` (earlier offline run 24/0); guard_write accepted it.
- BEFORE (header-only change, logic as is): 23/1, FAIL B2 "CHECKPOINT: set [0, 1, 11, 21, 24] lacks ... [5, 15] (need [1, 5, 11, 15, 21, 24]); delete_wi..."
  `selftest_stagexec_s4_c161_a1_2_before.log:22,28` (BGRUN END rc=1) - the predicted B2 refusal.
- Edit `selftest_stagexec_s4.py:159-162`: hand-copied BIND|{0,last} replaced by `SX.checkpoint_ops(SX.compile_plan(...))`; B2 label and docstring :16 renamed.
- AFTER: 24/0, B2 PASS "partial reads 5, whole 6 -> 1, fallbacks 0" `selftest_stagexec_s4_c161_a1_2_after.log:22,28`.

## 3-4. Other re-runs
- selftest_c156_b2_2_invcheck: RESULT 20/0 `selftest_c156_b2_2_invcheck_c161_a1_2.log:183` (inner FAIL lines are its replayed drift cases).
- selftest_c161_delckpt: RESULT 11/0 `selftest_c161_delckpt_c161_a1_2.log:23`.

## 5. guard_peer
- No block seen: after the failing before-log, the after-run and delckpt launches were not refused.

## md5 UNCHANGED
- stagexec a4df7e15, stagesim 95a162ba, stagekit 0b5bb678, stage_prerun 7605116f. No tools/hooks file edited by this card
  (`git status` shows tools/hooks/material_marker.log modified - written by the bgrun --material marker, not by an edit).
- New md5: selftest_c157_innerface c6c5a2f9..., selftest_stagexec_s4 c153e5b8....

OPEN: other selftests that may still declare `labview: read` while offline (s4 was one) refuse under labview-none cards - not swept here.
