---
card: 163-a1-2
status: current
date: 2026-10-10
---
# Brief 163-a1-2 (assignment 163-1) - OFFLINE: re-make the step-3 plan as group I alone (A41..A52) under the gate's own X10 start convention

`labview: none`; no tool edit (`stagekit`, `stagexec`, `stagesim`, `stage_prerun`, `stage_shared`), no `tools/hooks` edit, no launch. Read `tools/bench/diag_c163_a1_1_facts.md` (card 163-a1-1, PASS 22/0) and `docs/d1/ring-p5b.md` PD396(c).

## Why (assignment-session decision, written down; the closing report flags it)
Card 163-a1-1 computed MAIN(I+J) = 671.1 with START = `load_by_vi` f9ae7751 601.2, but the launch gate computes X10 with `stage_prerun.x10_start` = `load_by_vi[md5] + op0_read_mb` = 607.1
(`memory_model.json:119` `start_rule`), where MAIN(I+J) = 677.0 > 675 and MAIN(I) = 658.3. The step-2 calibration used that convention: 603.4 = x10_start(94ffff94), predicted MAIN 657.4, measured scratch peak 657.1
(`diag_c162_a1_2_facts.md`; PD396(a)(1) "X10 is the gate"). A plan the gate refuses cannot launch, and a 601.2 start would under-predict the real peak by 5.9 MB. PD396(c) says "otherwise group I alone": so the plan is
**A41..A52 (group I alone)**, group J becomes p5s02d in the next purpose. The limit 675 and every model key stay unchanged.

## Do
1. Keep the I+J plan: copy `tools/bench/plan_ring_p5s02c.json` (014c7d52) and `plan_ring_p5s02c_in.json` (caa0f639) aside as `plan_ring_p5s02c_ij.json` / `plan_ring_p5s02c_ij_in.json` (byte copies, md5 quoted) BEFORE anything is rebuilt.
2. Make `tools/bench/prep_c163_a1_2_mk.py` (<= 40 lines): it CALLS `prep_c163_a1_1_mk.py`'s flow with the group set = I only (A41..A52). If `prep_c163_a1_1_mk.py` has no parameter for the action range, make it parametrised in YOUR OWN copy (do not edit the 163-a1-1 file; it is history) - never retype a uid, never copy a stagekit function.
   Output `tools/bench/plan_ring_p5s02c.json` (written ONLY by `stagesim.simulate`, final True) and `plan_ring_p5s02c_in.json`.
3. Gates as in brief_163-a1-1 Part 2 point 4, quoted PASS/FAIL: ROWS, SB (REALSIM final True on 431cfd83, failed None, 12/12, 0 PROVISIONAL, 0 UNROUTABLE, every route row quoted), C compile (op list + checkpoints; every `delete_wire` a checkpoint), X8, X17, no-group-split, ids A41..A52.
4. X10: quote MAIN for group I with START = `stage_prerun.x10_start(f9ae7751)` (the gate's value, call the function; do not type 607.1) and the same on SX.checkpoint_ops; must be <= 675 (> 675 = FAIL, hand back). Also quote what the same function gives for I+J so the two numbers sit in one line.
5. Do NOT touch `memory_model.json`.

## FAIL conditions
Final False; UNROUTABLE; MAIN(I) > 675 under x10_start; mapped row differs from the input; a tool edit looks needed.

## Report `tools/bench/diag_c163_a1_2_facts.md` (<= 30 lines, facts only)
md5 of the kept I+J files and of the new plan/in; REALSIM line; action ids; route rows; compile ops + checkpoints; X10 numbers for I and I+J under x10_start (with the function's cite string); md5 UNCHANGED list; `OPEN:` lines with file:line.
