# card 138-3: the two red self-tests are already red at HEAD (offline, no LabVIEW)

The isolation could not be a `git worktree`: the permission layer refused `git worktree add` and `git archive`. Instead,
`tools/bench/wt_c138_3/<combo>/tools/` held copies of the top-level tools/*.py, directory junctions to the tools/ subdirectories
(their fixtures are clean against HEAD), and the three modules for each combination (the HEAD bytes taken from `git show`).
The main tree was never checked out or stashed. The trees were removed afterwards: 28 junctions unlinked, wt_c138_3 gone
(prep_c138_3_clean.log). Script: prep_c138_3_combos.py. Log: prep_c138_3_combos.log.

| combo | stagesim / stagexec / stage_prerun md5 | c133_1_fsroutes | c133_6_fr |
|---|---|---|---|
| head    | 46be02a7 / d3051577 / 74818fbc | FAIL R1 'base is not provisional', then IndexError at :62 | KeyError 'fs_frames' at :44 |
| simexec | 345ad14b / 8e57b67b / 74818fbc | the same | the same |
| prerun  | 46be02a7 / d3051577 / 878d530d | the same | the same |
| new     | 345ad14b / 8e57b67b / 878d530d | the same | the same |
(prep_c138_3_combos.log:8-35)

Cause: both are stale fixtures. The tests read live plan files, and later stages rebased those plans in place.
- c133_1: the test copies the live tools/bench/plan_ring_p3b2.json (selftest_c133_1_fsroutes.py:37). It was written against
  md5 98992a59 with a provisional base (selftest_c133_1_fsroutes.log:3, 6/0). At HEAD 0b72718d (cycle 133) the plan is already
  rebased: md5 03ec58c2, base sim/ring_p3b2_base_real_fsmap.json. So stage_prerun.py:3567-3568 refuses ('base is not
  provisional'), and that refusal is correct. 98992a59 never reached a commit; the previous commit, 53737825, holds 7bcf4ffa
  with a provisional base (prep_c138_3_hist.log:3-4).
- c133_6 b: the test reads the live plan_ring_p3b2b.json and its base (selftest_c133_6_fr.py:41-44). Commit 23cd9f3e
  (cycle 134) rebased it onto graph_ring_p3b2a_fs_20261002_102553.json, which has no 'fs_frames' key (it has fs_measured).
  At 0b72718d its base was sim/ring_p3b2b_base_provisional.json, which has fs_frames, and the test passed 9/0
  (prep_c138_3_hist.log:8-9; selftest_c133_6_fr.log:10,14).
- Last commit at which each fixture still matched its test: c133_6 at 0b72718d; c133_1 at 53737825 (only the provisional
  shape; that exact md5 was never committed).
- Neither failure is caused by the 138-1 or 138-2 edits. No tool was edited and no gate_fp entry was logged: these are
  self-test fixture failures, not gate refusals.
