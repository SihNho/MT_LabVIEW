---
type: facts
status: current
date: 2026-10-07
card: 145-a2-6
---
# Card 145-a2-6 facts: s05 (v18 ops 98..124) re-made on s04 f349c39a's end and REBASED on the real s04 graph (PASS); EL 55 by the fixed rule; X10 685.4 > 680 at 605.4; dry PASS x2; prerun 15/1 x2 = X11 only (expected, not cleared); scratch-required exit 3

OFFLINE only. Nothing launched, no LabVIEW process (`prep_c145_a2_6_check_after.log` LV gate). No plan edited by hand, no licence, gate,
stage tool, recipe, v18 or s04 file edited.

## Step 1 - provisional copies + re-make + rebase
- Provisional kept: `plan_ring_p4_s05v18_prov.json` b7d27e24, `_in_prov.json` 7fbdaa62, `_pred_prov.json` 6666a718; the 36 files of
  `sim/ring_p4_s05v18/` copied byte-identical to `sim/ring_p4_s05v18/_prov/` (inside the card's write glob; md5 list `prep_c145_a2_6_mk.log` FACT PROV-SIM).
  The older provisional dirs `sim/ring_p4_s05v18_s04end/`, `sim/ring_p4_s05v18a/` were not touched.
- Maker `prep_c145_a2_6_mk.py` (f7497bb2) = copy of `prep_c145_p1_mk.py` (c7fdf263). Changes: pins S04 9ff46b0e -> f349c39a and END4F
  3c4d8f8c -> b5ae7f79 (s04 re-simulated by prep_c145_2_fix.py); START 605.4; cut FIXED at 124 by the card (gate: splits no 'of' group),
  X10 reported not gated; new paths inside the write glob (base `sim/ring_p4_s05v18/s04end/base_provisional.json` e23f5dca, pass A
  `sim/ring_p4_s05v18/_passA/`). `prep_c145_a2_6_mk.log` 16/0, rc 0.
- Same content as the provisional: 33 actions `p4_t_slot`..`p4_w_fd_in`, 27 ops (tunnel 3, connect 13, create 6, branch 3, move_in 2);
  R3 W1 #16483, W1.body #29699, SL1R #29403, SD1L #29655, SD1R #29648; 14 cross refs; TIE 19 end rows; 14 open pairs.
- Rebase `stage_prerun.py --rebase ... --graph graph_ring_p4s04_20261007_223245.json` PASS rc 0 (`prep_c145_a2_6_rebase.log`):
  CREATION-MAP `plan_ring_p4_s04v18_f349c39a_20261007_215246.jsonl`, 13 nodes + 1 frame + 46 terminals MAP-BOUND, FALLBACK-COUNT 0,
  re-issued []; LABEL-DIFF LoopTunnel #-69->#30098, #-68->#30102 (sim '' real 'min Num'); 70 uids bound; re-sim final=True failed=None.
  Plan **5fb19dce -> 0efd8737**; base -> `sim/ring_p4_s05v18_base_real_fsmap.json` 58a844e8 (written by the tool, path outside the card glob).

## Step 2 - pred (`prep_c145_a2_6_pred.py` 97c2506f, log `prep_c145_a2_6_pred.log` 6/1, rc 1 = the X10 gate only, non-fatal by design)
- `plan_ring_p4_s05v18_pred.json` **a052145d**, keyed to plan 0efd8737; graph 58a844e8; bed 95e408ff.
- EL by tools/elrule.py (a5ee7d5c) WITH subvis, base = s04 MEASURED 58 (`errorlist_expected_D1_ring_p4s04_20261007_215031.json` 1a28fe86):
  **predicted 55** = 58 + new 0 - closed 3 [local 30001, sr 29403, sr 29648]. Open at start [local 30001, local 30016, sr 29403, sr 29648];
  open at end [local 30016 ('Num')]. Uncertain base [[29240, ['y']]] (move_in, not counted); uncertain subvi []; subvis {} (s05 drops no SubVI).
- Census {}: 33/33 actions UNPREDICTED. X17 PASS (3 primitives).

## Step 3 - X10 at the measured s04 load 605.4 (memory_model.json db163e03)
- Compiled plan N 27, R 10: **peak 685.4 MB vs fail_above 680.0 (margin -5.4) and MEMSTOP 695.0 (margin 9.6)** (pred.log FACT X10).
- Per-op formula: ops 98..124 685.4; next op 125 689.3; **first op over 680 = 121; longest cut <= 680 = op 120 (679.8)** (mk.log FACT X10-FORMULA).
- Prerun's own X10 (its own start, not 605.4): main 655.1 (R 12), scratch 650.0 (R 10), both PASS, 'UNMEASURED' meter (prerun.log:117-119).
- Scratch recipe prints `MEM_STOP_MB 680.0; X10 from the md5-pinned pred 685.4` (scr_dry.log:16): the scratch stop is below the predicted peak.

## Step 4 - dry / prerun / scratch-required (recipes unchanged: main 23c08932, scratch cd14eb47)
- Main dry **PASS** (`prep_c145_a2_6_dry.log:97`), scratch dry **PASS** (`prep_c145_a2_6_scr_dry.log:114`); graph = the rebased base.
  STALE-ADDRESS fresh read + one retry on ops 21, 22, 25, 26 (dry.log:67,70,77,80), all retried to pass.
- Main prerun **15/1** (`prep_c145_a2_6_prerun.log:123`), scratch prerun **15/1** (`prep_c145_a2_6_scr_prerun.log:140`). The ONE fail, both:
  `FAIL  X11 no row wires one Build Array input while a sibling input is an open row (unless pb-licence/1)  [{'row': 'p4_w_tp_row', 'node': 2626,
  'wired': 'array', 'open': ['array'], 'licensed': None, 'plan': 'tools/bench/plan_ring_p4_s05v18.json'}, {'row': 'p4_w_rp_row', 'node': 2626,
  'wired': 'array', 'open': ['array'], 'licensed': None, ...}]` (prerun.log:100, scr_prerun.log:117). As predicted by the card; NOT cleared.
  No other refusal. WARN X13 x4 (const, primitive, move_in, wire_sr: no replayer), X14 rows 33 > budget 15 (proven: no).
- `--prerun stage_d1_ring_p4_s05v18.py --scratch-required ...`: exit **3** `SCRATCH-REQUIRED | CENSUS-UNPREDICTED rows 1..33`
  (`prep_c145_a2_6_scrreq.log`).

## Step 5 - unchanged (`prep_c145_a2_6_check_before.log` / `_after.log`: A after == before for 23 files, LV no process)
s04 plan f349c39a, s04 pred / _in, s04 + s05 recipes, v18 2ea6cafa, stage_prerun / stagesim / stagexec / stagekit / vigraph, elrule a5ee7d5c,
requiredness 13b0d75f, memory_model db163e03, licence `plan_l2b1_licence.json`, s04 real base a63f5929, s04 END step b5ae7f79, s04 graph 094ba298,
s04 file 95e408ff, s03 file 282301ca, bed `D1_ring_p3b2b_20261002_130007.vi` 39511877 (full md5 list: check_after.log MD5 lines).

## New files
| file | md5 |
|---|---|
| tools/bench/plan_ring_p4_s05v18.json (rebased) | 0efd8737f8202f48242dc1ed21e4c641 |
| tools/bench/plan_ring_p4_s05v18_in.json | 81f2bd9ff8d691d862f8a6ca495d9829 |
| tools/bench/plan_ring_p4_s05v18_pred.json | a052145d5fe2402c14510ee43fb433f2 |
| tools/bench/sim/ring_p4_s05v18_base_real_fsmap.json | 58a844e8302ab4a90865549d78298acb |
| tools/bench/sim/ring_p4_s05v18/s04end/base_provisional.json | e23f5dcaf57af908c6db4ce1e3e69e8f |
| tools/bench/prep_c145_a2_6_session.json | 0216b3ee42c7d87be5e44627882331ef |
| tools/bench/plan_ring_p4_s05v18_prov.json / _in_prov / _pred_prov | b7d27e24 / 7fbdaa62 / 6666a718 |
