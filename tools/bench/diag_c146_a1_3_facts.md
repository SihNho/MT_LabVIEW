---
type: facts
status: current
date: 2026-10-08
card: 146-a1-3
---
# Card 146-a1-3 facts: s05 re-cut at op 114 (21 actions); MAIN prerun X10 680.0 PASS (margin 0.0), scratch 674.9; both recipes dry PASS + prerun 16/0

Offline only. Nothing launched, no LabVIEW process (`prep_c146_a1_3_check_after.log:69`). No stage tool, v18, s04 file, recipe, gate or
memory_model.json edited (`prep_c146_a1_3_check_after.log:68`, A after == before for 63 files).

## 1. Cut (`prep_c146_a1_3_mk.log`, 18/0, rc 0; maker = copy of prep_c146_a1_2_mk.py, cut given as argv 114)
- s05 = v18 ops **98..114** = 21 actions `p4_t_slot`..`p4_ia_frameidx`; kinds tunnel 2, connect 7, create 6, branch 2; no 'of' group split.
- Start 611.3 (= x10_start(95e408ff) = 605.4 + 5.9), unchanged.
- Op 114 was the brief's first try and the gate passed it, so no shorter cut was tried.
- Projection printed by the maker (not a verdict): main = Executor + 2 x 2.53; op 114 680.0, op 113 676.1; **first op over 680 under the MAIN
  number: 115 (683.9)**. Executor-only: first op over 680 is 116 (680.2).
- Formula: the next session at the same start would end at op 138 (s06's real start is s05's unmeasured load).

## 2. Rebase (`prep_c146_a1_3_rebase.log`, rc 0)
- `:5` FALLBACK-COUNT 0; `:6` REBIND 13 nodes, 1 frame, 46 terminals by map; re-issued []; `:7-8` LABEL-DIFF #-69->#30098, #-68->#30102 (same as a1-2).
- `:49` 70 uids bound, base `sim/ring_p4_s05v18_base_real_fsmap.json` 58a844e8, completeness PASS, re-sim final=True. Plan -> **1fc9b486**.

## 3. Pred (`prep_c146_a1_3_pred.log`, 8/0) - `plan_ring_p4_s05v18_pred.json` 961f30c4
- X1 start 611.3 == prerun's own start. X10 Executor N 17, R 9, peak **674.9** (margin 5.1; MEMSTOP 695 margin 20.1).
- EL by `tools/elrule.py` (a5ee7d5c), base 58: **predicted 57** = 58 + new 2 [input -32 ('array','index'), local -30 ('FrameIdx')] - closed 3
  [local 30001, sr 29403, sr 29648]. Open at end: input -32, local -30, local 30016 ('Num'). Uncertain base [], uncertain subvi [].
  (a1-2 had 56: its op 115 wired local -30.)
- X17 PASS; census {} (21/21 UNPREDICTED); end rows 16, open pairs 11.

## 4. Dry / prerun (recipes unchanged: main 23c08932, scratch cd14eb47)
| run | log | result |
|---|---|---|
| main dry | `prep_c146_a1_3_dry.log:73` | DRY PASS |
| main prerun | `prep_c146_a1_3_prerun.log:98` | **16/0 PASS** |
| scratch dry | `prep_c146_a1_3_scr_dry.log:90` | DRY PASS |
| scratch prerun | `prep_c146_a1_3_scr_prerun.log:115` | 16/0 PASS |
- MAIN X10 (`prerun.log:92-94`): N 17, R 11 = Executor R 9 + source 2 [census_snapshot@30x2]; **PASS peak 680.0** (fail above 680.0); margin **0.0**,
  to MEMSTOP 695 **15.0**. The Executor 674.9 + 5.06 = 679.96 rounds to 680.0 (`stage_prerun.py:2593-2594`, `<=`).
- Scratch X10 (`scr_prerun.log:109-111`): R 9, source 0, PASS peak **674.9**; margin 5.1, to MEMSTOP 20.1. Scratch prints `MEM_STOP_MB 680.0; X10 from the md5-pinned pred 674.9` (`scr_dry.log:16`).
- WARN (main): X13 x3 (const, primitive, wire_sr: no replayer) `prerun.log:79-81`; X14 rows 21 > budget 15 (proven: no) `:95`.
- Recipe docstrings still say "v18 ops 98..124 (33 actions ...)" (`prerun.log:5`); text only, rows come from the plan file.

## 5. X11 / #2626
- X11 **PASS unlicensed** in both preruns (`prerun.log:76`, `scr_prerun.log:93`). No licence file written.
- Ops 118, 119, 132, 150 not in s05 (`mk.log` FACT X11). s06 starts at op 115; at the same-start formula s06 ends at op 138, so 118/119/132 in s06,
  150 in s07 (formula only; s06's start is unmeasured).

## 6. md5
Protected (unchanged, `prep_c146_a1_3_check_after.log`): s04 plan f349c39a / pred / _in, s04 + s05 recipes, v18 2ea6cafa, stage_prerun 61d6f590,
stagesim, stagexec, stagekit, vigraph, elrule a5ee7d5c, requiredness, licence, memory_model 559be4cf, s04 real base, s04 END step b5ae7f79,
s04 graph 094ba298, s04 EL file, s04 file 95e408ff, s03 file 282301ca, bed 39511877, *_prov2 0efd8737 / 81f2bd9f / a052145d, 36 files of sim/ring_p4_s05v18/_prov2.

| new / changed file | md5 |
|---|---|
| tools/bench/plan_ring_p4_s05v18.json (rebased) | 1fc9b486551b3f1fe42f25167375ba30 |
| tools/bench/plan_ring_p4_s05v18_in.json | 8fe54f0182c014848bd22c1a01d02593 |
| tools/bench/plan_ring_p4_s05v18_pred.json | 961f30c4cfa09dc47b2dca72ee3523cb |
| tools/bench/prep_c146_a1_3_session.json | a7fbdee11691606f12b5a4d910915861 |
| scripts prep_c146_a1_3_mk / _pred / _check .py | 8a0a8304 / 78334a87 / adeb0ea6 |

## 7. Jev ladder
No failed step in this card; no JEV-LADDER row owed.
