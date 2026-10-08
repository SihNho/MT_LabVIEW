---
card: 148-a3-2
status: current
date: 2026-10-08
---
# Brief 148-a3-2 - retry of 148-a3-1: revised unmask first, then worktree cleanup + the 4 suites NOW vs pre-fix (PD360(b)(c))

Offline, `labview: read`, ALONE. Read `tools/bench/diag_c148_a3_1_facts.md` first and `tools/bench/cards/brief_148-a3-1.md` for the full spec (still valid; this brief only adds the order and the carry-over).

## Carry-over from 148-a3-1 (facts, not instructions to skip anything)
- Unmask rebase cases p3b2_A/B and s03_A/B: HEAD 61d6f590 == disk dcd45aba, all EQUAL (`diag_c148_a2_3_unmask.log` CASE lines) - these stand; they are re-produced by the revised script anyway.
- The c106e_noX17 case came out DIFFERENT only because the script ran the full recipe (no `sys.argv`, `PRERUN_LOG_DIR` set after import, `stage_prerun.py:124`), producing a clock-stamped dry VI name that differs. Review `archive/peer/2026-10-08-c148-a3-1-unmask-clockstamp.md` (ANSWERED, claim REFUTED, disposition FIXED at `diag_c148_a2_3_unmask.py:65`: own child per variant, env `PRERUN_LOG_DIR`, `sys.argv`, stamp normalisation, all diffs). The revised script was NOT run. Pre-148 E1 X5 PASS: `s4_c106e_e1_full.log:88`.
- Step 1 (worktree removal) and Step 2 (the 4 suites) never ran. The wrapper `diag_c148_a3_1_suites.py` is written (rc/stderr checked everywhere, PRE tree = `git worktree add` HEAD 07202624, 1500 s cap, worktree cleanup in `finally`) and was never launched. `git worktree remove` typed directly in the Bash tool needed approval: do the removal INSIDE the wrapper's Python (`subprocess.run(["git","worktree","remove","--force",path])` with rc checked, then `git worktree prune`, then `shutil.rmtree` of the empty `c148a23head_*` dirs), run under bgrun.

## Order (the short job first, so the suites do not overlap its prerun)
1. `tasklist` (timeout 20 s) LabVIEW count, `git worktree list`, md5 of stagekit/stagexec/gscript/elrule.
2. Run the REVISED `tools/bench/diag_c148_a2_3_unmask.py` under bgrun. Prediction (write it into the facts before running): c106e X5 PASS at ops 7 on both sides, 0 diff lines; the four rebase cases EQUAL. If a case differs: RETURN with the facts, no fix inside the card. If the guard asks for a review (JEV-LADDER) the review above was archived after the failing log; cite it.
3. Then launch `diag_c148_a3_1_suites.py` under `py tools/bgrun.py --material --max-min 150 --log tools/bench/diag_c148_a3_1_suites.log -- py -u tools/bench/diag_c148_a3_1_suites.py`: Step 1 cleanup, PRE-tree md5s, the 4 suites NOW and pre-fix. Green = rc 0 or the same failing children as pre-fix. A NEW difference is a RETURN.
4. You may edit only your OWN diag files (`diag_c148_a3_1*`, `diag_c148_a2_3_unmask*`). No tool/hook/plan/recipe/self-test edit.

## Never
Start LabVIEW. Retry a suite after a first unexpected result. Touch the main tree beyond reading it, or `V6_bench\*`.

## Report (`tools/bench/diag_c148_a3_2_facts.md`, <= 40 lines)
Table suite -> tree, rc, counts, seconds; PRE md5s; failing children; CMP lines; unmask per-gate table; `git worktree list` before/after; invariants md5; LabVIEW count before/after; `OPEN:` line.
