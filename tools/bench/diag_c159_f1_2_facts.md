---
type: facts
status: current
date: 2026-10-10
card: 159-f1-2
---
# Why selftest_c134_1_dry reads 9/2 (T2a, T2) - measured; no tool, recipe, hook or self-test edited
## 1 T2a: header-only
- Pin bb5ba064 = `git show 0b72718d:tools/recipes/stage_d1_ring_p3b2a.py` (2026-10-02 10:10). Current 0d1f0c15 = e86181ad (2026-10-04 chat-E3).
- `git diff 0b72718d -- tools/recipes/stage_d1_ring_p3b2a.py`: 1 file, 4 insertions, 0 deletions; the 4 lines are `# ---` / `# labview: build` / `# hardware: none` / `# ---` appended after line 98. No non-comment line changed.
## 2 T2 with stagekit 9cd8822e: still FAIL
- How: tools/bench/diag_c159_f1_2_t2.py runs `stage_prerun --dry <recipe> --no-record` in a child whose sys.meta_path finder serves the swapped module bytes with __file__ = the real tools/<name>.py (BENCH/ROOT unchanged); nothing on disk replaced, no temp copies (bytes in memory).
- C0 current bytes: DRY FAIL GATE PB, unverified 1 (diag_c159_f1_2_t2.log:13,16) = reproduces selftest_c134_1_dry_c159_f1_1.log:6.
- C1 stagekit 9cd8822e: same DRY FAIL GATE PB, unverified 1 (log:25,28). Today's stagekit edit is NOT the cause.
## 3 Single swaps (with stagekit 9cd8822e unless noted): none of them restores PASS
- C2 + stage_prerun 9decb20f (HEAD, pre-PD387(e)): FAIL PB, unverified 0 (log:37,40). C5 stage_prerun 9decb20f alone: FAIL PB, unverified 0 (log:73,76).
- C3 + addrcheck 951efd0e (first rev, 10-03; ed216d5b): FAIL PB (log:49,52). C4 + addrcheck 589685c8 (ee6e63b7): FAIL PB (log:61,64). addrcheck did not exist at the last pass (born 951efd0e 2026-10-03).
- Bracket: C6 every tools/*.py at 421d6108 (commit of the last 11/0 log, 2026-10-02): T2 PASS, PB PASS, `DRY PASS ... coverage 72/81, unverified 0` (log:85-86).
  C7 every tools/*.py at HEAD a9d0da22 (2026-10-09 22:51; stagekit ab9773cc, stage_prerun 9decb20f): FAIL PB (log:95,98). Same data files on disk in C6 and C7.
- So the PB cause is a COMMITTED tool change between 421d6108 and a9d0da22, not stagekit 9cd8822e->ac3a8f57, not PD387(e), not addrcheck. Not bisected (outside the card's swaps); vigraph 3f2fe63c->a7eb58c7, stagexec d3051577->69b1a301, stagekit b1f77050->ab9773cc, jev_candidates e167fa4d->eefe4976 all changed in that range (11 commits on vigraph/stagexec/jev_candidates).
## 4 What T2 asserts vs gets
- T2 (selftest_c134_1_dry.py:83-84) asserts only: last line starts `=== DRY PASS:`, rc 0, `unverified 0`. The numbers live in the recipe's PB gate (stage_d1_ring_p3b2a.py:73-74): cdiff rows == plan_ring_p3b2a_pred.json `cdiff_rows` (16) and the (node, term) set == plan_ring_p3b2a.json `open_rows` (11).
- Obtained (C0/C1/C7): extra [], missing ['2626|Terminal|array|0'..'|3'] -> 12 of 16 rows (log:13); FR, D (10==10, 2==2), TD PASS; CEN2 UNVERIFIED-DRY in every config.
- The 16/11 are properties of the plan/pred files (bed), not of the stub dry: C6 meets them with today's files. Separately, current stage_prerun counts the CEN2 UNVERIFIED-DRY line (unverified 1, C0/C1/C3/C4), so T2's `unverified 0` fails with stage_prerun 7605116f even if PB passed (C2/C5/C7 with 9decb20f print unverified 0).
## md5 / unchanged
- After: stagekit ac3a8f57, stage_prerun 7605116f, stagesim eb99c6ba, stagexec 7a712ccb, addrcheck 207beb0d, recipe 0d1f0c15, selftest_c134_1_dry 10178208 (log:99 UNCHANGED).
- VIs 94ffff94 / s09 eb1d0f31 / P5-1a 2482fe7b / P5-1 7f2582ae unchanged (diag_c159_f1_2_vipins.log V0/V1, selftest_c159_cen2_ends). `git status --short tools/hooks` -> only material_marker.log (bgrun). No LabVIEW process (tasklist).
- git-by-md5 lookup is inline in selftest_c134_1_dry.py:32, selftest_x10_c130_1.py:28, matbench/matbench.py:86 (no shared function; not extracted, outside write globs).
OPEN: which of the 11 commits 421d6108..a9d0da22 (vigraph/stagexec/stagekit/jev_candidates) drops the 4 rows 2626|Terminal|array|0-3 from PB (stage_d1_ring_p3b2a.py:71-74) - bisect, or re-pin pred?
OPEN: T2 requires `unverified 0` (selftest_c134_1_dry.py:84) but PD387(e) counts the recipe's CEN2 UNVERIFIED-DRY line (stage_prerun.py:1074-1075) - T2 cannot PASS on stage_prerun 7605116f as written.
