---
type: facts
status: current
date: 2026-10-08
card: 146-a1-5
---
# Card 146-a1-5 facts: s06 made provisionally (ops 115..129, 19 actions, MAIN X10 679.3 at 623.5). The maker failed its own kind gate: v18 op 116 `branch` compiles as `connect` in s06. Stopped at that step (card chat-P2)

Offline only. Nothing launched. No stage tool, v18, s04/s05 file, recipe, gate or memory_model.json was edited (`prep_c146_a1_5_check_after.log:160`, A after == before
for 155 files). One LabVIEW.exe was running, PID 23484, 712 MB, title "LabVIEW" (`prep_c146_a1_5_check_after.log:161`). This card did not start it: it was absent from
`tasklist` at bind time (00:22) and appeared before 00:28 (`prep_c146_a1_5_check_before.log`). It is most likely the parallel s05 scratch, card 146-a1-4.

## 1. Start assumption (PROVISIONAL), `prep_c146_a1_5_mk.log:4-5`
- Predicted s05 file load = 605.4 (load_by_vi[95e408ff]) + 0.719 (`memory_model.json:70-73` load_growth_mb_per_op) x 17 compiled ops of s05 plan 1fc9b486 = **617.6**.
  Adding op0_read_mb 5.9 (the x10_start rule, `stage_prerun.py:2043-2052`) gives a **start of 623.5**.
- Counting s05's 21 actions instead of its 17 ops would give a start of 626.4 (`mk.log:6`). This is not used, because the model's growth figure is per op.

## 2. Cut, `prep_c146_a1_5_mk.log:11-16,35`
- s06 = v18 **ops 115..129**, which is 19 actions from `p4_w_arr_frameidx` to `p4_ia_bufdiff`. No 'of' group is split.
- MAIN X10 at 623.5 is the Executor figure plus 2 source reads x 2.53. MAIN = **679.3**, a margin of 0.7 under 680 and 15.7 under MEMSTOP 695. Executor alone = 674.2.
- The first op over the limit is 130 (MAIN 683.3). By the same formula, s07 would end at op 146. 61 of 190 ops are left after s06.
- Sensitivity of the cut to the start value:

| start | cut | MAIN peak | actions |
|---|---|---|---|
| 618.5 (-5 MB) | op 131 | 679.6 | 21 |
| 623.5 (assumed) | op 129 | 679.3 | 19 |
| 628.5 (+5 MB) | op 127 | 679.1 | 17 |

## 3. Plan build, `mk.log:39-45`
- C2: 9 cross refs, all to s05 symbols, all mapped to negative END5 uids: TS1 -1, LRVF1 -30, IAVF1 -32, IAVT1 -18, IAVR1 -25. There are no refs to s01..s04 symbols
  (SQ1 is first used at op 140). There are no refs to later sessions.
- Pass A replays. TIE: all 15 end rows are tied. Pass B is FINAL on the provisional base `sim/ring_p4_s06v18/s05end/base_provisional.json` (a6762a05).
  open_rows_match holds with 10 pairs.
- Compiled plan: N 15, R 5. Executor 674.2 matches the per-op table. MAIN is 679.3, which is at or under 680.

## 4. FAIL — first unexpected result, `mk.log:44,46`
- `GATE FAIL | X10s compiled plan: ... kinds == v18 ops 115..129 except wire_sr -> connect on an earlier register [(116, None)]`.
- v18 op 116 `p4_w_idx_frameidx` (src `new:TS1.outer`) compiles as `branch` in v18, because TS1 is a tunnel created earlier in the same plan (`stagexec.py:808-809`).
  In s06, TS1 was made in s05, so the src is the uid `{-1, outer}` and the op compiles as `connect` (`stagexec.py:812-813`). The plan text is at `plan_ring_p4_s06v18.json:85`.
- The memory figure is unaffected, since neither branch nor connect is a bind kind. The gate's whitelist, copied from the s05 maker, only allowed wire_sr -> connect.
- Not diagnosed and not retried, per card chat-P2. Nothing after this step was run: pred/EL, recipes, licence, dry, prerun. `prep_c146_a1_5_session.json` was not written.

## 5. #2626 at the sim end of s05 (`prep_c146_a1_5_probe2.log`), for the licence that is still owed
- `#2626 BuildArray` has inputs t2832, t4160 and t4165, all named 'array' and unwired, plus t4168, which is wired (w25283). s06 wires t4160 (op 118) and t4165 (op 119).
  t2832 is wired at op 132, which is in s07 at this cut. Op 150 (t4168) is in s07.

## 6. Files
| file | md5 |
|---|---|
| tools/bench/plan_ring_p4_s06v18.json | 8f33ad758acb6d054c69ae34317dbf7d |
| tools/bench/plan_ring_p4_s06v18_in.json | 08b8dbe2b9e9f0c4c1a547b610d5fdad |
| tools/bench/sim/ring_p4_s06v18/s05end/base_provisional.json | a6762a055fed468f1c3a2a6f58beb8f3 |
| tools/bench/prep_c146_a1_5_mk.py | 94275a2c6d5ba6861ccc64890a982c20 |
| tools/bench/prep_c146_a1_5_check.py | 03ee9cc130c14ae7a94f09c4d8f749cd |

Not written: `_pred.json`, `_licence.json`, both s06 recipes.

## 7. Jev ladder
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| prep_c146_a1_5_mk.log | no JEV-LADDER row yet in jev_gate.log | - | returned FAIL (chat-P2) | - |
