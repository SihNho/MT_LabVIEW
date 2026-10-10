---
card: 163-a1-4
status: current
date: 2026-10-10
---
# Brief 163-a1-4 (assignment 163-1) - TOOL FIX for gate-fp fp-86 (stagekit PB), then re-dry and the remaining offline gates of step 3 (p5s02c). `labview: none`

Card 163-a1-3 (`tools/bench/diag_c163_a1_3_facts.md` c5539bc2, log `prep_c163_a1_3_dry.log:54`) stopped at the first gate: `DRY FAIL PB`. Facts it measured (re-read them, do not trust this paragraph):
`eq_diff []` (real == sim re-keyed); the two blocked PB rows are node #376 `error in` and `total data array in`: S1 source uids [3934,4965] / [1842,3954] vs the end's x2 on frames 31506 + 31517,
inherited frames of the node = [31506] only. Both rows were wired by STEP 2 (`w_g376` / `w_h376`, adopted p5s02b) into case 31308 f0 + f1, and at step 2 they passed as PB class 2 (diag_c162_a1_2_scr_dry.log RECORD PB lines).
At step 3 they are untouched rows of the BASE graph 431cfd83 whose wiring an ADOPTED earlier step made, and `stagekit.pb_inherited_row` (class 1 = base row == end; class 2 = wired by THIS plan) has no class for that.
The step-3 plan does not touch them (eq_diff [], base == end True). Logged as `fp-86` in `tools/bench/gate_fp_queue.jsonl`.

## Why a tool edit is in scope (assignment-session decision, flagged in the closing report)
Purpose item 3 requires dry PASS; the deliverable's own gate refuses it on a row the deliverable does not touch. CLAUDE.md "deliverable first ... unless that very gate refuses the deliverable's launch" and the 2026-09-24
tool permission (the cycle needs it, and the same class would refuse every later P5 step: P5-3 .. P5-6 all start from a base that carries step-2 wiring). `tools/hooks/**` is NOT touched. Rule 1a: this is a gate about
the simulator vs the real read-back; it changes no computation.

## Part 1 - read, then decide the smallest change (measurement first)
1. Read `stagekit.pb_inherit_ctx` (:2033-), `pb_inherited_row` (:2085-2132), `pb_check_bound`, and `tools/bench/selftest_c161_pbinherit.py`. Quote what `ctx["frames"]`, `["cases"]`, `["connects"]`, `["R0"]`, `["after0"]`, `["missing"]`
   hold for node #376 and for the step-3 plan (call `pb_inherit_ctx` on `plan_ring_p5s02c.json`, print those keys for the two blocked sinks). Say WHICH of the existing conditions fails and why (class 1: `frames` lacks 31517? or `R0 != bound_end`?).
2. The class to add is: the base row was wired by an ADOPTED earlier plan (the chain in `tools/bench/adopted_scratch.jsonl` is already walked by `pb_inherit_ctx`) into a case that plan created, base (R0) == end, S1 source uid set
   == end's, multiplicity == that case's frame count. Evidence must come from the adopted plan's files (its wire action onto that sink + its case's frames), not from a literal. If the existing machinery can be extended with ONE
   small change (e.g. also collecting `frames` per node for the sinks an adopted plan wired, or relaxing class 1's `inh` only by those frames), do that; do not add a parallel checker.
3. NO loosening: class 1 and class 2 must still refuse everything they refused. A row with a tag on a frame NOT created or wired by the chain still fails. Add to `selftest_c161_pbinherit.py` (you may add NEW files `selftest_c163_pbchain.py`;
   edit an existing self-test only by adding cases) at least: the #376 positive case from the real step-3 data, a negative where the frame is not in the chain, a negative where the S1 source uid set differs, a negative with wrong multiplicity.
4. Edit ONLY `tools/stagekit.py` (+ self-test files). `stagexec`, `stagesim`, `stage_prerun`, `stage_shared`, hooks: no edit. Record old -> new md5 of `stagekit.py` (9b8f82c1 -> ?). Run the existing self-tests that import stagekit
   (`selftest_c161_pbinherit`, `selftest_c158_gates386`, `selftest_c159_cen2_ends`, `selftest_c157_*` that touch PB; find them with `grep -l stagekit tools/bench/selftest_*.py` and run all under bgrun, offline) - all must stay as before.
5. Peer: one `-Agent claude -Role hypothesis` adversary review of the diff (does it loosen a gate? is there a row class where the new rule says PASS and the real end would be wrong?), asked to REFUTE; archive; record the disposition.
   Prior-art: run `py tools/prior_art_review.py` only if the launch/check gate says it is owed for this edit; quote the verdict.

## Part 2 - re-run the step-3 offline gates on the new stagekit bytes (the 163-a1-3 outputs are the inputs, unchanged)
Run exactly the command forms in `prep_c163_a1_3_dry.log` (read the head of that log; reuse the same makers, do not rewrite them): dry on `stage_d1_ring_p5s02c.py` and `stage_d1_ring_p5s02c_scratch.py`
(target PASS or PASS-UNVERIFIED with only CEN2 unverified), prerun (X10 MAIN <= 675, X14, X17, X8), `py tools/stage_prerun.py --scratch-required tools/recipes/stage_d1_ring_p5s02c.py` (quote the exit code and reason line).
Do NOT run `--check-launch` (the scratch launch card does; it names `DRY-UNVERIFIED-OK: CEN2 new-object census`). Do NOT run `--launch`. Pred / licence / EL files from 163-a1-3 are reused as they are; if the stagekit change makes a
pin in them stale (md5 of stagekit inside the pred), regenerate with the 163-a1-3 makers and report old -> new md5.
Return at the FIRST unexpected result with the line (a second PB/other FAIL: facts only, no second tool edit).

## Report `tools/bench/diag_c163_a1_4_facts.md` (<= 40 lines)
Part 1 measurements (the ctx values; which condition failed), the diff in words + `git diff --stat`, old -> new md5, self-test counts before/after, peer file + disposition, dry / prerun / scratch-required lines quoted (rc),
md5 UNCHANGED list (stagexec a4df7e15, stagesim 95a162ba, stage_prerun 7605116f, stage_shared b688edd4, memory_model def9e640, plan 930699ec, graph 431cfd83, EL 60e02787, VIs f9ae7751 / 94ffff94 / 7f2582ae / eb1d0f31), `OPEN:` lines.
