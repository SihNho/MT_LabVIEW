---
card: 148-a3-1
status: current
date: 2026-10-08
---
# Brief 148-a3-1 - retry of 148-a2-3: 4 suites NOW vs pre-fix, stale worktrees, unmask test (PD360(b)(c))

Offline, `labview: read`, ALONE. The previous attempt (`tools/bench/diag_c148_a2_3_suites.py`) crashed at :81 because `git worktree add` at :79 ran with rc/stderr discarded; no suite ran (`diag_c148_a2_3_facts.md:17`). Review `archive/peer/2026-10-08-c148-a2-3-t3regress-prefix.md` is ANSWERED and accepted; t3_regress 7/3 is accepted as pre-existing (PD360(a)) - do NOT run it again and do not re-run the stagekit plain run or the 7 x10 tests.

## Step 0 - before anything
`tasklist` (timeout 20 s): quote the LabVIEW process count (must be 0). `git worktree list`: quote. md5 of stagekit, stagexec, gscript, elrule.

## Step 1 - stale worktrees
Remove `Temp/e3head_r96iqm4t`, `Temp/f2head_1n3cihvt` (git worktree remove --force, then `git worktree prune`) and delete the empty `Temp/c148a23head_*` dirs (Python shutil.rmtree is fine; they are under %TEMP%, created by earlier cycle-148 runs). Do not touch the main tree or `V6_bench\*`. Quote `git worktree list` after.

## Step 2 - the fixed wrapper `tools/bench/diag_c148_a3_1_suites.py` (new file, based on the a2-3 wrapper)
Every `subprocess.run` is checked (rc, stderr printed) and the script stops at the first failed step. Pre-fix tree = HEAD 07202624 exported into %TEMP% (`git worktree add --detach` with the rc/stderr checked, or `git archive HEAD | tar -x`; you choose). Quote the md5 of every edited module in that tree (stage_prerun.py, guard_cycle.py, guard_write.py, guard_assign.py and the edited self-tests) against `git show HEAD:<path>`. Run `selftest_c134_1_a4.py`, `selftest_c134_2_regress.py`, `selftest_c_e3_suite.py`, `selftest_f2_suite.py` NOW and on the pre-fix tree (`--root <tree>` or the equivalent each script takes - check its argv first), timeout >= 15 min each, under `py tools/bgrun.py --material --max-min N --log <log> -- py -u <script>`. Serialize any two that write a file another reads. A suite that leaves a worktree behind: remove it in `finally` and check the rc.
Green = rc 0, or the same failing children as pre-fix. A NEW difference on an edited module is a RETURN (facts only, no fix, no retry).

## Step 3 - the unmask test `tools/bench/diag_c148_a2_3_unmask.py` (review 2(b))
Copies of `plan_ring_p3b2.json` and `plan_ring_p4_s03v18.json` into %TEMP% with their provisional base restored (`finalized.plan_in`, e.g. `plan_ring_p4_s03v18.json:335-337`); run `SP.rebase` on the copies with the HEAD `stage_prerun` (pre-fix tree) and with the disk `stage_prerun`; same for the c106e recipe with X17 skipped. Output = per-gate comparison. Equal -> closes 2(b); any difference -> RETURN. The originals of the plans are read only.

## Never
Edit anything outside the write globs. Start LabVIEW. Retry after a first unexpected result.

## Report (`tools/bench/diag_c148_a3_1_facts.md`, <= 40 lines)
Table suite -> tree, rc, counts, seconds; PRE md5s; failing children; CMP lines; unmask per-gate table; worktree list before/after; invariants md5; LabVIEW process count before/after; `OPEN:` line.
