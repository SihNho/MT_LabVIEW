---
card: 148-a2-3
status: current
date: 2026-10-08
---
# Brief 148-a2-3 - retry of 148-a1-2: discharge the t3_regress failing log by review, then the remaining runs (offline, `labview: read`) (PD359(d))

`retry_of_card` = 148-a1-2, which was BLOCKED: its pre-fix t3_regress run left a log with `RESULT 7/3` (bgrun marks rc=1 on any failing RESULT line, `tools/bgrun.py:296`), `guard_peer` then refused every further run (JEV-LADDER new-problem p=0.782, hypothesis review owed). Facts so far: `tools/bench/diag_c148_a1_2_facts.md` (stagekit plain 51/0, 7 x10 self-tests all rc 0 - NOT re-run here). No tool, hook, plan, licence, recipe or self-test is edited; only `tools/bench/diag_c148_a2_3*` and `archive/peer/**` are written.

## Step 1 - the hypothesis review (this card carries peer `hypothesis`)
Dispatch ONE `peer.ps1 -Agent claude -Role hypothesis` review (adversarial; the dispatcher appends the refutation instructions; `-TimeoutSec >= 780`, via `powershell -Command "& 'tools/peer.ps1' ... -TaskFile <f>"`). The claim to ATTACK, stated with its evidence: "the 3 failing children of `selftest_t3_regress.py` (c133_1_fsroutes R1/R2, rebase_uidreuse_c143_4 U1/U2, stage_prerun_c106e E1/X17) are PRE-EXISTING, caused by stale premises in those self-tests, and are not caused by the cycle-148 edits (stage_prerun.py, guard_cycle.py, guard_write.py, guard_assign.py and their self-tests); `diag_c148_a1_1_facts.md:24` shows the same failures on the pre-fix blobs, run individually". Attach `diag_c148_a1_2_before_t3_regress.log` and `diag_c148_a1_1_facts.md`. Archive as usual; ANSWERED required. Ask the reviewer for the cheapest discriminating test too.

## Step 2 - measurements the review does not forbid (only after the review is archived ANSWERED)
All under `py tools/bgrun.py --material --max-min N --log <log> -- py -u <script>`:
1. Plain `selftest_t3_regress.py`, `--max-min 15` (earlier run: ~150-165 s). Quote the RESULT line and the failing children.
2. The four suites that timed out at 240 s in 148-a1-1: `selftest_c134_1_a4.py`, `selftest_c134_2_regress.py`, `selftest_c_e3_suite.py`, `selftest_f2_suite.py`, each `--max-min 15`. They do not touch LabVIEW; you may run them concurrently only if none writes a file another reads (check; else serialize). Quote rc + counts, and the wall-clock of each.
3. For every non-zero result in 1 or 2: the SAME script against the pre-fix blobs (`git show HEAD:<path>` copies of each edited module the script loads, as `tools/bench/diag_c148_a1_1_before.py` did; remember the children load current disk files, so wrap each child's module, not only the parent) or a cited statement that no edited module is loaded by it. Compare counts and failing case ids.
4. A NEW difference from pre-fix on an edited module is a RETURN (facts only), not a fix.

## Never
Edit anything outside the write globs. Start LabVIEW. Re-run the stagekit plain run or the 7 x10 tests. Retry a suite after a first unexpected result.

## Report (`tools/bench/diag_c148_a2_3_facts.md`, <= 35 lines)
Review path + md5 + disposition; table script -> rc, counts, seconds; pre-fix comparison per non-zero; invariants md5 (stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c); LabVIEW process count before/after; `OPEN:` line.
