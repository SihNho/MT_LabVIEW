---
type: facts
status: current
date: 2026-10-08
card: 146-a1-2
---
# Card 146-a1-2 facts: s05 re-cut at op 115 (22 actions), X10 678.8 under the one start 611.3; main recipe prerun FAILS X10 at 683.9 (its 2 census reads are added); scratch prerun 16/0; no licence

Offline only. Nothing launched, no LabVIEW process (`prep_c146_a1_2_check_after.log` LV gate). No stage tool, v18, s04 file, recipe or gate edited.
Status FAIL: the main recipe's prerun has 1 FAIL (X10). Returned at that result as the card protocol says; not diagnosed or retried.

## 1. Load record (memory_model.json db163e03 -> 559be4cf)
- One key added to `load_by_vi`: `95e408ff14a406edd3f16b32ba7324f1` = 605.4, cite `tools/bench/diag_c145_2_graph.log:24` ("MEM after load: 605.4 MB private").
- Gate MM (`prep_c146_a1_2_check_after.log`): parsed json vs git HEAD, the only added key is this one; every other key equal; fail_above 680.0 and memstop 695.0 unchanged.

## 2. The one start
- `stage_prerun.x10_start(95e408ff..)` = 605.4 + op0_read_mb 5.9 = **611.3** (`stage_prerun.py:2043-2052`).
- Used by: the maker (`prep_c146_a1_2_mk.py`, gate X0), the pred (`prep_c146_a1_2_pred.py`, gate X1: `x10_plan_start(plan)` 611.3 == `x10_start` 611.3),
  and the prerun's own X10 (`stage_prerun.py:2584-2585`, `x10_plan_start` on the rebased base 58a844e8 whose `md5` = 95e408ff..).
- Other start sources (none used for s05 now): the old card-local literals `prep_c145_a2_6_mk.py:49` and `prep_c145_a2_6_pred.py:33` (605.4, load only);
  the model default `start_mb` 570.0 when no load is known (`stage_prerun.py:2101`); the read-only model's `start_mb` (`stage_prerun.py:2555`).
- **Same start, different R.** The main recipe's prerun X10 adds the recipe file's own whole-VI reads: `source 2 [census_snapshot@30x2]`
  (`prep_c146_a1_2_prerun.log:95`; recipe `stage_d1_ring_p4_s05v18.py:30` snap, called at :39 and :66), +2 x 2.53 MB (`stage_prerun.py:2590-2593`).
  The scratch recipe's source has 0 such reads (it imports the body), so its X10 = the Executor-only figure (`prep_c146_a1_2_scr_prerun.log:112`).
  145-a2-6 showed the same split (main R 12, scratch R 10; `diag_c145_a2_6_facts.md:37`).

## 3. Re-cut (`prep_c146_a1_2_mk.log`, 17/0, rc 0)
- s05 = v18 ops **98..115** = 22 actions `p4_t_slot`..`p4_w_arr_frameidx`; kinds tunnel 2, connect 8, create 6, branch 2; no 'of' group split.
- X10 (Executor model, R 10) at 611.3: **peak 678.8**; margin to 680 **+1.2**; to MEMSTOP 695 **+16.2**.
- First op over 680: **116** (680.2). Per-op peaks: 113 671.0, 114 674.9, 115 678.8, 116 680.2, 117 681.6, 118 683.0 (mk.log FACT X10-OP).
- Next session at the same start would end at op 139 (formula only; s06's real start is s05's unmeasured load).
- Old files kept: `plan_ring_p4_s05v18_prov2.json` 0efd8737, `_in_prov2` 81f2bd9f, `_pred_prov2` a052145d; 36 files of `sim/ring_p4_s05v18/` -> `sim/ring_p4_s05v18/_prov2/`
  (md5 list: mk.log FACT PROV2-SIM). The 145 `_prov` copies are untouched.
- Rebase `stage_prerun.py --rebase ... --graph graph_ring_p4s04_20261007_223245.json` PASS rc 0 (`prep_c146_a1_2_rebase.log:51`): CREATION-MAP
  `plan_ring_p4_s04v18_f349c39a_20261007_215246.jsonl`, FALLBACK-COUNT 0, REBIND 13 nodes + 1 frame + 46 terminals by map, re-issued [], LABEL-DIFF
  #-69->#30098 and #-68->#30102 (sim '' real 'min Num'); 70 uids bound; re-sim final=True. Plan 548d4c49 -> **1e29b4a1**; base 58a844e8 (unchanged bytes).

## 4. Pred (`prep_c146_a1_2_pred.log`, 8/0, rc 0) - `plan_ring_p4_s05v18_pred.json` dcfabeb3
- EL by `tools/elrule.py` (a5ee7d5c), base 58: **predicted 56** = 58 + new 1 [input -32 ('index')] - closed 3 [local 30001, sr 29403, sr 29648].
  Open at end: local 30016 ('Num'), input -32 ('index'). Uncertain base [], uncertain subvi [], subvis {}.
- Census {}: 22/22 UNPREDICTED. X17 PASS (3 primitives). End rows 16, open pairs 11.

## 5. Dry / prerun (recipes unchanged: main 23c08932, scratch cd14eb47)
| run | log | result |
|---|---|---|
| main dry | `prep_c146_a1_2_dry.log:75` | DRY PASS |
| main prerun | `prep_c146_a1_2_prerun.log:100` | **15/1 FAIL** |
| scratch dry | `prep_c146_a1_2_scr_dry.log:92` | DRY PASS |
| scratch prerun | `prep_c146_a1_2_scr_prerun.log:117` | 16/0 PASS (X10 678.8, :113) |
- The one FAIL (`prep_c146_a1_2_prerun.log:96`): `FAIL  X10 predicted LabVIEW private MB <= model fail_above_mb, from the compiled plan + checkpoint set (peak 683.9 MB)  {'peak_mb': 683.9, 'recorded': {'why': 'UNMEASURED: no recorded meter of stage_d1_ring_p4_s05v18.py covers ops 1..end (0 record(s))'}, 'model': 'tools/bench/memory_model.json'}`
  with `:94` `N 18 ops, BIND 8, R 12 reads, predicted peak 683.9` and `:95` `source 2 [census_snapshot@30x2]; ... Executor-only peak 678.8 MB, R 10`.
- Arithmetic only (not acted on): with the same +2 reads, op 114 gives 674.9 + 5.06 = 680.0 (rounded, margin 0.0) and op 113 gives 676.1.
- WARN (both): X13 x3 (const, primitive, wire_sr: no replayer), X14 rows 22 > budget 15 (proven: no).
- X11 **PASS unlicensed** in both preruns (`prerun.log:78`, `scr_prerun.log:95`).
- Scratch recipe prints `MEM_STOP_MB 680.0; X10 from the md5-pinned pred 678.8` (`scr_dry.log:16`).
- Recipe docstrings still say "v18 ops 98..124 (33 actions ...)" (`prep_c146_a1_2_dry.log:5`); text only, the rows come from the plan file.

## 6. X11 / #2626
- Ops 118 `p4_w_tp_row`, 119 `p4_w_rp_row`, 132 `p4_w_bd_row`, 150 `p4_rbB_sel_t4168` are all after op 115 (mk.log FACT X11). No licence file written.
- 118/119 fall in s06 (it starts at op 116). 132 and 150 fall in s06 if s06 reaches them; at the s05 start s06 would end at op 139, so 132 in s06,
  150 in s07 (formula estimate; s06's start is unmeasured).

## 7. md5 (`prep_c146_a1_2_check_before.log` / `_after.log`: A after == before for 24 files, PIN pass)
Unchanged: s04 plan f349c39a, s04 pred / _in, s04 + s05 recipes (23c08932 / cd14eb47), v18 2ea6cafa, stage_prerun 61d6f590 / stagesim / stagexec / stagekit /
vigraph, elrule a5ee7d5c, requiredness, licence `plan_l2b1_licence.json`, s04 real base, s04 END step b5ae7f79, s04 graph 094ba298, s04 EL file,
s04 file 95e408ff, s03 file 282301ca, bed 39511877 (full list: check_after.log MD5 lines).

| new / changed file | md5 |
|---|---|
| tools/bench/memory_model.json | 559be4cf4989e39c84fa584a01a2e503 |
| tools/bench/plan_ring_p4_s05v18.json (rebased) | 1e29b4a12faedee4889b650d15be25ab |
| tools/bench/plan_ring_p4_s05v18_in.json | ee64efa65758889d4f2369e6105e47af |
| tools/bench/plan_ring_p4_s05v18_pred.json | dcfabeb31a031273204f5db0388a62f5 |
| tools/bench/prep_c146_a1_2_session.json | f0dd1606aa774a45c5ed3e8e4b9b3353 |
| tools/bench/plan_ring_p4_s05v18_prov2.json / _in_prov2 / _pred_prov2 | 0efd8737 / 81f2bd9f / a052145d |
| tools/bench/op_hygiene/build_opwiringrules_v0_hygiene.json (copy; original kept) | 57e3bf4da3f590d2b06dc2a179c37acc |
| scripts prep_c146_a1_2_mk / _pred / _check / _hy .py | 11ce8eeb / 19270d62 / 907d06a1 / 60b7e18f |

## 8. Jev ladder
No `JEV-LADDER` line for `prep_c146_a1_2_prerun.log` in `tools/bench/jev_gate.log` when this card ended.
