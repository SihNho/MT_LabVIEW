---
type: facts
status: current
date: 2026-10-02
---
# Card 140-P1 facts — P4 LabVIEW session 2, PROVISIONAL plan (offline only; LabVIEW never opened; nothing launched)
Maker `tools/bench/prep_c140_p1_s02.py` -> `prep_c140_p1_s02.log` rc 0, 10/0. Recipe dry -> `prep_c140_p1_dry.log` rc 1 (**FAIL**); prerun not run.
## 1. Provisional base (pass item 1)
- v14 ops 1..16 (16 actions `p4_dw_23310`..`p4_w_b_out`) simulated on graph_ring_p3b2b 50595c62: replays to end, 16 end rows all P3b-2b declared
  open pairs, 0 made by a session-1 action (`s02.log:4`). Same 16 ids as 140-2's `plan_ring_p4_s01.json` (md5 95f45bef at 20:13) (`s02.log:3`).
- Base `sim/ring_p4_v14_ops1_16/base_provisional.json` e3230e07 = that end state; plan base {path, md5, provisional: true,
  sim_of: `sim/ring_p4_v14_ops1_16/plan_ring_p4_v14_ops1_16_in.json` c51931f5} (my own ops-1..16 input, NOT plan_ring_p4_s01.json).
## 2. Cut (pass item 2) — table-A X10, start 606.1, limit 675 (`s02.log:5-6`)
- Session 2 = v14 ops **17..31** (`p4_x_i_rab1`..`p4_sel_mask`), 15 actions, N 15, R 12, peak **674.6**; op 32 would give 678.5.
  No `of` crosses s1|s2 or s2|s3 (17/18 and 19/20 RLE pairs both inside). Kinds: connect_term_uid 2, RLE 2, add_sr 2, create 7, connect 2.
- Compiled `plan_ring_p4_s02.json` at 606.1 reproduces 674.6 exactly; kinds == v14 ops 17..31 (`s02.log` gate X10).
## 3. Plan (pass item 3, partial)
- `plan_ring_p4_s02.json` 2d6725fb FINAL, open_rows_match, 11 open pairs (16 end rows, all step-0 bed-declared, 0 made by session 2);
  route_check off (provisional, as plan_ring_p3b_split_p3b2.py:219). Pred `plan_ring_p4_s02_pred.json` 2483212d: census {} (all 15 actions
  census-unpredicted), EL predicted 51 (alt 59 = +8 unwired created sinks), checked False; memory_pred start 606.1 (to be replaced, PD320(d)).
- Recipe `tools/recipes/stage_d1_ring_p4_s02.py` (95 lines) = stage_d1_ring_p4s1.py with names changed.
- **DRY FAIL** (`prep_c140_p1_dry.log:28-30`): L0, K1, L1 PASS; E1 ExecStop at the base compare (`stagexec.py:1906-1912`):
  "BASE: the scratch copy's graph differs from the plan's base graph: {'unbound': [-22, -20, -19, -18, -17, -15]}" = session 1's
  simulated objects in the provisional base. Same failure, same place on the P3b-2 provisional base: `stage_prerun_c132_1_p3b2_dry.log:21-26`
  (unbound [-116..-102]), after fp-21's provisional_dry_graph fix; P3b-2 then went through --rebase (card 132-6). Prerun not run.
## 4. Session-1 symbols session 2 takes (pass item 4)
- `p4_x_i_rab1`.dst `new:RAB1.index` and `p4_x_bufdiff`.dst `new:RAB1.new element/subarray` -> {"uid": -16, term} (RAB1 =
  `p4_ras_bufdiff`, v14 op 13). No other later v14 action names a session-1 symbol. Re-bound by `stage_prerun --rebase` (rename path,
  `stage_prerun.py:3584-3594`).
OPEN: is a dry/prerun PASS on a provisional base with session-N-created objects reachable at all (c132_1 says no), or is item 3 met only after --rebase?
