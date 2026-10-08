---
type: facts
status: current
date: 2026-10-08
card: 150-a1-1
---
# Card 150-a1-1 facts: s07 re-cut at the measured s06 load = ops 136..165 (30 actions, MAIN 678.8); the --rebase onto the real s06 graph is REFUSED (BINDING)
Offline only, no LabVIEW process (`prep_c150_a1_1_check_after.log` LV gate). No stage tool, hook, elrule or protected file changed (A 99/99 equal).
Status FAIL at the first unexpected result: the rebase refused. Returned there, as the card protocol says; not diagnosed, fallback not run.
## 1. Start and cut (`prep_c150_a1_1_mk.log`, 18/0, rc 0, 83 s)
- START 599.7 = `stage_prerun.x10_start(569ffbf5..)` = load_by_vi 593.8 (diag_c149_a3_2_graph.log:24) + op0_read_mb 5.9; the s05 re-cut rule
  (`prep_c146_a1_2_mk.py:52-53`, `stage_prerun.py:2061-2070`). Gate X0 in mk.log.
- Cut = op 165 (v18 ops 136..165, 30 actions `p4_rbA_re2`..`p4_rbE_sel`): MAIN 678.8 (margin 1.2 to 680, 16.2 to MEMSTOP 695), Executor 673.7.
  First op over 680 = 166 (MAIN 682.7); 40-action cap first passed at op 176; no 'of' split. Sensitivity: 594.7 -> op 167 (32 act, 679.1); 604.7 -> op 162 (27, 679.6).
  Next session at the same start would end at op 190 (= v18's last op; 25 ops left after s07).
- Compiled plan: N 30, R 6; kinds connect 21 / create 5 / delete_wire 4, all == v18; V18E end 22 rows == v18 #177, cdiff 0; NEG refused.
- In the cut: op 150 `p4_rbB_sel_t4168` (a #2626 row, mk.log FACT X11). X11 was NOT run (the prerun needs the rebased plan).
- SG census: 2 ControlTerminal rows from wired sources: `p4_rbA_re2` -> [23166,'Pos: Diffraction Pattern'] t9519 and
  `p4_rbD_sel_t25573` -> [23166,'autofocus reset count (1.2 to 1.1)'] t25573 (mk.log FACT SG-CENSUS). The recipes declare exactly ONE sink gate (PD355(b)).
## 2. Rebase (`prep_c150_a1_1_rebase.log`, rc 2, 1 s) - the failing step
- Command: `py tools/stage_prerun.py --rebase tools/bench/plan_ring_p4_s07v18.json --graph tools/bench/graph_ring_p4s06_20261008_192149.json`.
- CREATION-MAP `plan_ring_p4_s06v18_cfbd9823_20261008_175325.jsonl` (obj 4, diag 0, term 8).
- `REBASE REFUSED: BINDING: the created objects differ (name-free shape): ['BuildArray x0 simulated vs x1 real', 'LoopTunnel x2 simulated vs x3 real']`
  (raised at `tools/stage_prerun.py:3849`). Refused before carry_fs/simulation: no base_real_fsmap written, plan file not rewritten by the rebase.
- The refusal is about s06's created objects (sim end vs real s06 graph), not about s07's rows (inference, not measured: the PD364(c) fallback
  `--rebase` of the 14-action plan uses the same sim_of cfbd9823 + graph + map, so it would probably meet the same rebind; not run).
- Jev ladder: no JEV-LADDER line for `prep_c150_a1_1_rebase.log` in `tools/bench/jev_gate.log` (only JEV-PREFLIGHT :5343 for the maker).
## 3. Files now (pred and recipes NOT regenerated; dry/prerun/scratch-required NOT run)
| file | md5 | note |
|---|---|---|
| tools/bench/plan_ring_p4_s07v18.json | 10a4f59a0f1203abd08b6ae93139aa3c | 30 actions, PROVISIONAL base eeb22bba (not rebased) |
| tools/bench/plan_ring_p4_s07v18_in.json | 7b8900709509d2be892c6bc2aa0de44e | 30-action input |
| tools/bench/plan_ring_p4_s07v18_pred.json | e888ab67228f04ba98ed08d4e40055f6 | UNCHANGED = the 14-action 148 pred (stale vs the plan; recipe L0 refuses the pair) |
| tools/recipes/stage_d1_ring_p4_s07v18.py / _scratch.py | d6c8da7b / 273dc3de | unchanged |
| plan_ring_p4_s07v18_prov148.json / _in_prov148 / _pred_prov148 | aeae610e / 97e4e091 / e888ab67 | byte copies of the 148 files (mk gate P) |
| tools/bench/sim/ring_p4_s07v18/_prov148/*.json | 17 files | copies of the 148 sim step files; top-level step files now the 30-step sim |
| tools/bench/prep_c150_a1_1_session.json | a164722f10e2b46130a9728d4cd5299d | session table |
| scripts prep_c150_a1_1_mk / _check / _probe .py | 7a275061 / 9f33b780 / - | pred script not written |
## 4. Invariants (`prep_c150_a1_1_check_before.log` / `_after.log`, 99 files, A equal, PIN pass)
stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun dcd45aba, s06 VI 569ffbf5, s05 3f9ac26b, s04 95e408ff, bed 39511877,
memory_model 8eec443c, adopted_scratch 658fe5b9, graph a3ecb92b, s06 plan/in/pred/licence/recipes, sim/ring_p4_s06v18 tree, s06 creation map 99f9d253: unchanged.
OPEN: the real s06 file holds one BuildArray and one LoopTunnel more than s06's simulated end (rebind refusal :3849) - how is s07 to be bound to it?
