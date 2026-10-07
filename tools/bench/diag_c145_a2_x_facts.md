---
type: facts
status: current
date: 2026-10-07
card: 145-a2-X
---
# 145-a2-X — X11 facts on Build Array #2626 (offline, read-only; no re-cut proposed)

Measured by `tools/bench/diag_c145_a2_x_facts.py` -> `tools/bench/diag_c145_a2_x_facts.log` (BGRUN END rc=0, 4/0). Op numbers =
`stagexec.compile_plan(v18)` 1-based (the numbering of `prep_c145_p1_mk.py:73-75`); v18 = 202 actions / 190 ops (log:4).

## 1. Where v18 closes (2626, array)
- #2626 terminals in the v18 base `graph_ring_p3b2b_20261002_133824.json` (line 1): output t2813 `appended array` (unwired);
  inputs t2832, t4160, t4165 `array` UNWIRED, t4168 `array` wired (w25283). The three unwired inputs are already named `array`.
- No v18 action consumes the #2626 output (no action with src uid 2626, log:19). At v18's simulated end
  (`sim/ring_p4_v18/ring_p4_v3/step_202_wire_remove_loose_ends.json` line 1) t2813 is still `wire_uid 0`; the #2626 -> #376
  crossing is itself an open QRT row (v18:13-16).
- v18 wires all four `array` inputs (log:15-18): op 118 `p4_w_tp_row` t4160 (v18:1646-1655), op 119 `p4_w_rp_row` t4165
  (v18:1656-1665), op 132 `p4_w_bd_row` t2832 (v18:1859-1868), op 150 `p4_rbB_sel_t4168` t4168 (v18:2087-2096). At step_202 all
  four inputs carry sim wires (-214/-192/-193/-229).
- Sessions: s04 = ops 79..97 (log:5); s05 = ops 98..124 = the 33 actions of `plan_ring_p4_s05v18.json` (log:6, plan :7). Ops 118/119
  fall in s05; ops 132 and 150 fall after s05 (not yet cut; 66 of 190 ops left after s05, `prep_c145_p1_mk.log:10`).
- v18 never drops the row: its finalized `open_rows` still lists (2626, `array`) (v18:2634-2637), with (2626, `element`)
  (v18:2638-2641); v18 `final: false` (v18:2574). Declared reason: "carried from R2: licensed rename (plan_l2b1_licence.json)"
  (v18:23-27).

## 2. Ops 118 / 119 on #2626
- op 118 = action #126 `p4_w_tp_row`, kind connect: src `new:IAVT1.element` -> dst {uid 2626, term_uid 4160}; why "#2626 element|1
  t4160 <- Trans Pos" (v18:1646-1655; log:10,15).
- op 119 = action #127 `p4_w_rp_row`, kind connect: src `new:IAVR1.element` -> dst {uid 2626, term_uid 4165}; why "#2626 element|2
  t4165 <- Rot pos" (v18:1656-1665; log:11,16). Same rows in s05 (`plan_ring_p4_s05v18.json:410-426`).
- s05 simulated end (`sim/ring_p4_s05v18/step_33_wire.json` line 1): t4160 -104, t4165 -105 wired; t2832 and t2813 unwired; t4168 w25283.

## 3. What plan_l2b1_licence.json licenses
- Plan: `tools/bench/plan_l2b1.json` only (licence:4). Decided by brief_110-4 item 1: "the rename is LICENSED, keyed by terminal uid;
  no other row is licensed" (licence:5).
- One entry (licence:8-14): node 2626, term_uids [2832, 4160, 4165]; require "all listed uids are UNWIRED inputs of the node in the
  real end read, else the licence is void" (licence:12); why: wiring #5058 onto t4168 (row `rw_5124_4168`) renames these three
  unwired inputs `element` -> `array` (licence:13).
- In plan_l2b1.json `array` arises from `rw_5124_4168` #5058 t5124 -> #2626 t4168 (plan_l2b1.json:331-343); #2626 is moved by
  `mv_2626` (:97-102). plan_l2b1's own open row is (2626, `element`) (:361-365), NOT (2626, `array`); its end rows list only
  `2626|Terminal|element|0..2` (:513-515).

## 4. Does the licence cover (2626, array) as used by ops 118/119 — NO
- Machine: `pb_licences` keeps a licence only when its `plan` path equals the plan checked (stage_prerun.py:1272-1275);
  pb_licences(v18) = {} and pb_licences(s05) = {} (log:33,39); only pb_licences(plan_l2b1.json) = {2626: licence} (log:43).
- Content: the licence covers the RENAME of t2832/t4160/t4165 while they stay UNWIRED (licence:12); ops 118/119 WIRE t4160/t4165,
  i.e. two of the three listed uids stop meeting its `require`. It names no v18/s05 row.
- X11 result: v18 4 flags / 4 unlicensed (log:34-38: tp_row, rp_row, bd_row, rbB_sel_t4168); s05 2 / 2 (log:40-42); l2b1 1 flag,
  licensed (log:44-45).

## 5. The refusing gate
- `tools/stage_prerun.py:2905-2911` (gate X11, defined :82-84; check `buildarray_open_sibling` :1282-1308); replay
  `--buildarray-check` :4880, :4917-4968. Recorded refusal, `tools/bench/prep_c145_p1_prerun.log:31` (same at
  `prep_c145_p1_scr_prerun.log:45`):
  `FAIL  X11 no row wires one Build Array input while a sibling input is an open row (unless pb-licence/1)  [{'row': 'p4_w_tp_row', 'node': 2626, 'wired': 'array', 'open': ['array'], 'licensed': None, ...}, {'row': 'p4_w_rp_row', ...}]`

No plan, pred, recipe or tool edited; the four card inputs hash unchanged after the run (log:3, :46).
