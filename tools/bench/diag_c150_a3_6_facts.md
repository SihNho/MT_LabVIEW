---
type: facts
status: current
date: 2026-10-08
card: 150-a3-6
---
# Card 150-a3-6 facts: s08 MADE (not run), capped before action 20 - 19 actions, ops 166..184, MAIN X10 656.7; rebase / pred / licence / dry / prerun PASS; NOT launched
Offline only. No LabVIEW before or after (`prep_c150_a3_6_check_before.log` / `_after.log`, LV PASS). No stage-tool, hook or elrule edit, no `--launch`.
## 1. Maker (`prep_c150_a3_6_mk.py` = copy of `prep_c150_a3_5_mk.py` b6448a4c; log `prep_c150_a3_6_mk.log` RESULT 20/0, rc 0)
- The cap is one line, `prep_c150_a3_6_mk.py:64` `MAXACT = 19` (it was 40 at `prep_c150_a3_5_mk.py:57`). Gate CAP PASS: `p4_x_n2_order` (op 185) is the first action NOT included.
- Gate P: 150-a3-5 left 26 files (`sim/ring_p4_s08v18/s07end` + `_passA`). They were byte-copied first into `prep_c150_a3_6_prev_s08.zip` a349eb84 (read-back == originals).
- START 595.3 = x10_start(b3f86b32) = 589.4 + op-0 5.9 (X0). Cut op 184: 19 actions `p4_rbE_t`..`p4_w_n2_arr`. MAIN 656.7 / Executor 651.6. Margin 23.3 to 680, 38.3 to 695.
- Sensitivity: +13.6 MB start -> still op 184, MAIN 670.3 (mk.log). No 'of' group crosses the cut (`groups_split_at` [185, 187, 189] are above it).
- Tail = ops 185..190 (6 ops): 185 `p4_x_n2_order`, 186 `p4_rle_x_n2_order`, 187 `p4_x_slot_fs`, 188 `p4_rle_x_slot_fs`, 189 `p4_x_n2_out`, 190 `p4_rle_x_n2_out`.
  - They need either a measurement of FS #29721's diagram or a later stage. That is not decided here; stagesim.py is untouched.
- BOUNDARY (read from the plan and sims): the tail refs are IAZ1.array, TS1.outer, IAN1.index, IAN1.element and SQ1.n2. All five were made in s01..s07; none was made in s08.
  - s08 sim end: 21 rows; none is on #29869 or #29721. 150-a3-5 pass A stopped at n20 `p4_x_n2_order` (read from the zip copy).
- SA / TIE / SB / NEG / X10s / V18E gates all PASS. KIND: no kind differences. R: 3 real symbols (SQ1 29724, LRN5 30016, IAN1 29879). C2: 9 cross refs.
## 2. Rebase (`prep_c150_a3_6_rebase.log` rc 0)
- Plan 37d2cead -> **c328fdaf**. REBIND: 5 nodes, terminals 20 by map. Lines 'RENAMED-OLD' 0 and 'FLIPPED-OLD' 0. Completeness PASS; re-simulated final=True.
- Base `sim/ring_p4_s08v18_base_real_fsmap.json` a9d35eee.
## 3. Pred (`prep_c150_a3_6_pred.py`; log RESULT 13/0)
- Written `plan_ring_p4_s08v18_pred.json` cf2eccbf.
- V18E-R' (1): only-s08 rows [] PASS.
- V18E-R' (2): the 3 only-v18 rows `2626|Terminal|array|1..3` have before null and node 2626 owns RENAMED-OLD. PASS.
  - The RENAMED-OLD entries were read from the s07 rebase log `prep_c150_a2_5_rebase.log` 28341ad1. The s08 rebase log has none.
  - Added check (2b) PASS: all 3 rows were already only-v18 at s08 step 0, so they are inherited.
- V18E-R' (3): #2626 real s07 graph {'array':1,'element':3} == S1 PASS.
- X1: start 595.3. X10: Executor 651.6, margin 28.4 to 680. X17 PASS.
- EL: base 50, closed local#30016 and sr#9603, predicted 48. Per-class total 48 == rule.
## 4. X11, sink gates, licence
- X11: `--buildarray-check` gives CLEAN, rc 0 (`prep_c150_a3_6_x11.log`).
- Sink-gate census (`prep_c150_a3_6_session.json`): 1 ControlTerminal sink, n18 `p4_rbR_out` -> [23166, 'autofocus reseed flag (1.2 to 1.1)'], route ctlsink.
  - 0 rows need a gate, so both recipes declare 0 gates. The dry SG gate says "0 rows" (`prep_c150_a3_6_dry.log:28`).
- Licence `plan_ring_p4_s08v18_licence.json` 6b978d9e (log RESULT 5/0): rename_by_uid [] (X11 clean).
  - renames: 4 entries, owners 9603[22281], 10465[10469], 23166[25557], 25545[25596]; read back (None, None).
## 5. Recipes / dry / prerun (final bytes: MAIN ca5a5478, scratch 7cab5049, plan c328fdaf, pred cf2eccbf, licence 6b978d9e)
- MAIN dry PASS (`_dry.log:85`). MAIN prerun PASS 16/0; X10 MAIN 656.7, R 7 (`_prerun.log:104-106`).
- Scratch dry PASS (`_scr_dry.log:109`). Scratch prerun PASS 16/0; X10 651.6 (`_scr_prerun.log:128-130`).
- `--scratch-required` MAIN: rc **3** (CENSUS-UNPREDICTED rows 1-19). `--check-launch` scratch: ALLOW rc 0. X14 WARN "rows 19, budget 15 (proven: no)"; no PROVEN-PATTERN line. No prior-art review run.
- Dry PARITY touched diagrams [23166, **29869**] (`_dry.log:31`). Action 19 `p4_w_n2_arr` wires #30016 -> #29879, and both terminals sit on frame #29869 (base fsmap). The sim and E1 passed it.
## 6. Invariants (`prep_c150_a3_6_check_after.log`: B 154/154, PIN PASS, A after == before 154 files, LV none)
- Unchanged: stagekit, stagexec, gscript, elrule, stage_prerun, vigraph, stagesim, dispo; the VIs s07/s06/s05/bed; memory_model; adopted_scratch; graphs s07/s06; every s07 file and tree; every diag/prep_c150_a3_5 file; tools/hooks/**.
- One exception: `material_marker.log` a8d79a98 -> 892d6c24. The hook appends to it on every --material command.
- Changed: prerun_records.jsonl ee224215 -> 981c2dbb. The sim/ring_p4_s08v18 tree (150-a3-5's partial tree) was superseded and its copy is in the zip.
OPEN: the capped s08 still has action 19 (`p4_w_n2_arr`) inside frame #29869 (same-frame wire, simulated fine). Is "before action 20" the intended cap, or must s08 end at 18?
