---
card: 160-f3-2
status: current
date: 2026-10-10
---
# Brief 160-f3-2 (assignment 160-2) - retry of 160-f3-1: passwire gate D vs the adopted t_go/t_ho compile change

`labview: none`, no tool edit, no `tools/hooks` edit, no plan/pred file edit. Card 160-f3-1 finished c134_1_dry 11/0 and invcheck 20/0 (do not touch those). Its remaining FAIL:
`selftest_c156_passwire.py` (321ef700, already re-pinned to stagesim 95a162ba / stagexec ddf23a31) is 19/1 where the last pass was 20/0: gate `D plan_ring_p5s02r_all.json compiles EQUAL to the
before-list (40 ops)` FAILS (`selftest_c156_passwire_c160_f3_1.log:27`). The before-list is `tools/bench/sim/ring_p5s02pw/compile_before.json` (7ca1c4c4), written before card 160-a2-1 changed
`stagexec` so that a base-RSR/LSR InnerTerminal dict end compiles to `connect_term_uid` `register_end_case_border` (`diag_c160_a2_1_facts.md` R3: only t_go / t_ho changed in the p5s02b input).

## Your job: MEASURE, then decide by the measured diff only
1. Compile `plan_ring_p5s02r_all.json` (15da9551) with the current tools and diff op by op against `compile_before.json` (40 ops). Print every differing op index with before / after (kind, rows, mode).
2. If the ONLY differences are the t_go / t_ho group ops (`tunnel` or equivalent before -> `connect_term_uid` `register_end_case_border` after, same rows, same sink faces) AND the op count and
   checkpoints are equal: this is the adopted change (not a regression). Then, in `selftest_c156_passwire.py` only: keep `compile_before.json` UNTOUCHED (history), write the new compile as
   `tools/bench/sim/ring_p5s02pw/compile_before_c160a2.json` by calling the same writer function the self-test already uses (find it; do not write a second serialiser), and make gate D compare
   against the new file, with the docstring (line ~31) naming both files and why. Run the self-test: target `RESULT 20/0`; log `selftest_c156_passwire_c160_f3_2.log`.
3. If ANY other op differs, or the count / checkpoints differ: do NOT re-baseline. Report the diff (index, before, after) as FAIL and stop - that is a possible regression of the compile.
Also quote the `D plan_ring_p5s02a.json` line (must stay PASS 17 ops) and confirm gate P pins PASS.

## Report `tools/bench/diag_c160_f3_2_facts.md` (<= 20 lines, facts only)
The op-by-op diff table; the decision (adopted / regression) with its evidence; RESULT line; md5 before/after of `selftest_c156_passwire.py`; md5 UNCHANGED: stagesim 95a162ba, stagexec ddf23a31,
stagekit 1441bb4c, stage_prerun 7605116f, compile_before.json 7ca1c4c4, plan_ring_p5s02r_all.json 15da9551, plan_ring_p5s02b*.json; `OPEN:` lines.
Note: card 160-c3-1 runs in parallel and reads (does not write) the tools and plan_ring_p5s02b.json; do not touch `tools/bench/prep_c160_c3_1*`, `tools/recipes/stage_d1_ring_p5s02b*`, `tools/bench/prerun_records.jsonl`.
