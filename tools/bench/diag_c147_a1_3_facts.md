---
type: facts
status: current
date: 2026-10-08
card: 147-a1-3
---
# Card 147-a1-3 facts: s06 re-made on the real adopted-s05 graph

s06 is v18 ops 115..135 (25 actions). The start is 612.6, MAIN X10 is 679.3, the rebase used no fallback, and cdiff against v18 is 0.
The #2626 licence is written. The predicted Error List is 55. The recipe pair passes dry and prerun (16/0 each).

Everything ran offline and alone. No LabVIEW process was present before or after (`prep_c147_a1_3_check_before.log`, `_after.log`, 0 processes).
No stage tool, elrule, v18 file, s05 file or memory_model.json was edited (A after == before for 159 files).

## 1. Start rule, cut, X10 (`prep_c147_a1_3_mk.log`, RESULT 17/0, `BGRUN END rc=0 after 58s`)
- **START 612.6** = `x10_start(3f9ac26b)` = load_by_vi 606.7 (`diag_c147_a1_1_graph.log:24`) + op0_read_mb 5.9. The pred and the prerun use
  the same number: pred X1 says prerun `x10_plan_start(plan)` 612.6 == pred 612.6 (`prep_c147_a1_3_pred.log`, X1).
- **Cut = ops 115..135**, 25 actions from `p4_w_arr_frameidx` to `p4_rbA_re1`. No group is split. The first op over 680 is 136 (MAIN 680.6).
  55 of 190 ops are left. At the same start, the formula's next session would end at op 158.
- MAIN X10 is 679.3, leaving 0.7 to 680 and 15.7 to MEMSTOP 695. The Executor peak is 674.2 (5.8 / 20.8).
- **The prerun's own lines decide:**
  - main recipe: `X10 ... predicted peak 679.3 MB (fail above 680.0)` PASS (`prep_c147_a1_3_prerun.log:109-111`).
  - scratch recipe: 674.2 PASS (`prep_c147_a1_3_scr_prerun.log:131-133`, 0 source reads).
- Sensitivity:

  | start | cut op | MAIN | actions |
  |---|---|---|---|
  | 607.6 | 137 | 677.0 | 27 |
  | 612.6 | 135 | 679.3 | 25 |
  | 617.6 | 131 | 678.7 | 21 |

- Kind gate:
  - ops 116 and 131 (`p4_w_idx_frameidx`, `p4_w_idx_bufdiff`) are both branch -> connect. Both are ALLOWED because the source is
    new:TS1, made by v18 op 98, which is in an earlier session.
  - the other 19 ops have the same kind in v18 and s06.
  - the negative control is REFUSED.
- Compiled kinds: connect 14, move_in 2, tunnel 2, create 2, delete_wire 1 (N 21, R 6).

## 2. Rebase onto cbeeadf5 and end comparison
- `prep_c147_a1_3_rebase.log`: RESULT 1/0, rc=0, 42 s.
  - The CREATION-MAP is `plan_ring_p4_s05v18_1fc9b486_20261008_002835.jsonl`, with 8 nodes and 16 terminals bound by the map.
  - **FALLBACK-COUNT 0.** 30 uids are bound. Completeness PASS. The re-simulation is final.
  - The new base is `tools/bench/sim/ring_p4_s06v18_base_real_fsmap.json` (a4f9e39d). The tool writes this path itself, and it is not
    one of this card's write globs.
- Maker V18E (on the provisional base): s06 end 18 rows == v18 sim after #147 18 rows, cdiff 0.
- After the rebase, pred V18E-R compares the rebased end 18 rows with v18 #147: only s06 [], only v18 [], **cdiff 0** (`prep_c147_a1_3_pred.log`).

## 3. #2626 licence
- **Licence written** because ops 118 and 119 are in the cut, and so is 132 (`p4_w_bd_row`, t2832; `prep_c147_a1_3_mk.log` FACT X11):
  - file `tools/bench/plan_ring_p4_s06v18_licence.json`, md5 7dce79aa
  - form copied from `plan_l2b1_licence.json`, as read by `stage_prerun.pb_licences` (`stage_prerun.py:1261-1278`)
  - node 2626, term_uids [2832, 4160, 4165] (`diag_c147_a1_1_t2626.log:8-10`), with the `require` text of PD352(d)
    (`docs/d1/ring-p4b.md:292-299`)
- No other node is licensed. The plan rows wire the inputs by term uid: tp_row -> 4160, rp_row -> 4165, bd_row -> 2832.
- The main prerun's X11 line is a PASS. Its 3 rows are licensed by this file, and the open sibling is (2626, 'array')
  (`prep_c147_a1_3_prerun.log:92`).
- Op 150 (`p4_rbB_sel_t4168`) is not in s06.

## 4. Predicted Error List (elrule a5ee7d5c, unchanged)
`prep_c147_a1_3_pred.log`: RESULT 10/0. Pred file `plan_ring_p4_s06v18_pred.json` c4a6a35a.
- Base 55 (expected file 6f2ca28a). Rule new [sr 23508], closed [local 30239] -> **predicted 55**.
- `uncertain_base_newly_unwired_inputs` [[10757, ['array']]]: a base node with a newly unwired input that the rule does not count.
- Per class. Classes come from `elcls`: elrule.item_class -> local/cond/sr, the unwired/required-input text -> input, anything else
  -> other:<norm_ocr(raw)>.
  - start read b654430d: input 6, local 2, loop-tunnel undirected 3, no-source 1, not-connected 20, loose-ends 20, output-tunnel->RAS 1,
    output-tunnel->SubVI 1, two-types 1
  - predicted: the same, except local 1 and a new sr 1, total 55
  - written to `errorlist.per_class`

## 5. Recipes
- `stage_d1_ring_p4_s06v18.py` (41ad9d35) is a copy of the s05 main recipe (23c08932). It differs only in labels and names:
  - header moved to the top
  - docstring :5-19
  - PLAN/PRED :25,27
  - L0 label :41-42
  - CEN2 label :72
  - ES label :78
  - R key :93,95
  - Stage name/out json/task :99
- `stage_d1_ring_p4_s06v18_scratch.py` (8554bdd6) against the s05 scratch (cd14eb47), as `diff` hunks (old -> new line numbers):
  - `1,7c1,13` header + docstring
  - `9,14c15,25` docstring names + the advisory paragraph
  - `18c29,30` import R s06 + `import elrule`
  - `20,22c32,34` PLAN / PREDF / LOG names
  - **`68a81,155` the ADVISORY EL block added**:
    - `norm_ocr`, `elcls` (the same copy as the pred), `el_advisory`
    - rc 1 only on an unseen class or |total diff| > 3; rc 2 if the pred is unkeyed or has no per_class
    - `el_advisory_print` prints `EL-ADVISORY ...`
    - `el_selftest`
  - `70,72c157,165` the `--el-advisory-selftest` / `--el-advisory <read json>` branches, which exit before K.Stage, plus the Stage
    name/work/out/task
  - `79,81c172,174`, `88c181`, `90c183`: the result key, print label, card id and sum json name
  - `93,96d185` the tail header removed
- Every structural gate is unchanged: E1, D, PB, PRIM, TD, FR, NG, HB, PS, MEM, MEML, IN, GONE. They come from the imported main body or
  from unchanged lines.
- The EL step was a separate `errorlist_check.py` run in the s05 scratch too. The advisory is run after that read:
  `--el-advisory <read json>`.

## 6. Dry / prerun / scratch-required
- main dry: `=== DRY PASS: first_fail=None coverage 72/78 lines ...` RESULT 1/0 (`prep_c147_a1_3_dry.log`)
- main prerun: `RESULT ... "gates":{"pass":16,"fail":0}` (`prep_c147_a1_3_prerun.log:116`). WARN X14 rows 25 > budget 15 (proven: no),
  advisory.
- scratch dry: `=== DRY PASS: first_fail=None coverage 57/132 lines` RESULT 1/0 (`prep_c147_a1_3_scr_dry.log`)
- scratch prerun: RESULT 16/0 (`prep_c147_a1_3_scr_prerun.log:138`). WARNs: X13 (no replayer for const/primitive/move_in/wire_sr) and
  X14 rows 25.
- `--scratch-required` main: `SCRATCH-REQUIRED | stage_d1_ring_p4_s06v18.py | CENSUS-UNPREDICTED ... rows [1..25]`, then
  `BGRUN END rc=3` (`prep_c147_a1_3_scrreq.log`).

## 7. Advisory EL test (`prep_c147_a1_3_elselftest.log`, offline, RESULT 5/0)
The synthetic classes round-trip through elcls (10 classes, 55 items).

| case | read | diff | rc |
|---|---|---|---|
| A | +1 item of an unseen class 'Feedback Node: Initializer terminal is not wired' | 56 vs 55 | 1 (RETURN) |
| B | +4 items of a known class | +4 | 1 |
| C | +2 items of a known class | +2 | 0 (RECORDED) |
| D | the prediction itself | 0 | 0 |

**Side effect (gate FP logged as fp-52):** bgrun recorded this offline run in `tools/bench/stage_runs.jsonl` as a stage run of
`stage_d1_ring_p4_s06v18_scratch.py`, cycle 147, cap 2. It therefore uses one of the scratch's RETRY_CAP slots for this cycle
(`stage_prerun.py:3396-3406`). One slot is left for the real scratch.

Also, the launch gate refused the selftest until dry and prerun had been recorded. Running the selftest after the prerun cleared it.

## 8. Files (new / written)
| file | md5 |
|---|---|
| tools/bench/plan_ring_p4_s06v18.json (rebased) | cfbd9823d3b47be39de94f2125ad6b66 |
| tools/bench/plan_ring_p4_s06v18_in.json | db72d8af5b1f6da643e4c84b1260a61a |
| tools/bench/plan_ring_p4_s06v18_pred.json | c4a6a35aff6f71d508ea2c43c24ec510 |
| tools/bench/plan_ring_p4_s06v18_licence.json | 7dce79aaa168e30e7b4af11968e18e19 |
| tools/bench/sim/ring_p4_s06v18_base_real_fsmap.json (rebase output) | a4f9e39da768284e96f0b5d26606fb6f |
| tools/bench/prep_c147_a1_3_session.json | 860dbcf13ec4acdba085f384ef203d9c |
| tools/recipes/stage_d1_ring_p4_s06v18.py | 41ad9d3584a0999d741c4a3a7df6a4d1 |
| tools/recipes/stage_d1_ring_p4_s06v18_scratch.py | 8554bdd67d1e98e6be91b491f55a3859 |
| tools/bench/prep_c147_a1_3_mk.py / _pred.py / _check.py / _probe.py | 8900e0df / 7fd5654c / 7d657135 / 67c4ad35 |

Protected md5s are identical before and after (`prep_c147_a1_3_check_after.log`, A 159/159):

| file | md5 |
|---|---|
| stagexec | 1bab9cf9 |
| stagekit | 9a3fceaf |
| stagesim | 748bbf30 |
| stage_prerun | 61d6f590 |
| elrule | a5ee7d5c |
| v18 | 2ea6cafa |
| s05 plan | 1fc9b486 (whole sim/ring_p4_s05v18 tree unchanged) |
| s05 vi | 3f9ac26b |
| s04 | 95e408ff |
| s03 | 282301ca |
| bed | 39511877 |
| memory_model.json | 88eeb037 |
| graph | cbeeadf5 |

## 9. Jev ladder
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| all card logs | no JEV-LADDER row (no failed prediction; JEV-PREFLIGHT advisories only, `jev_gate.log`) | - | - | all PASS; scrreq rc=3 as predicted |
