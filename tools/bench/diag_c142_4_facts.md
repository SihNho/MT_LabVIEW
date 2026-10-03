---
type: facts
status: current
date: 2026-10-03
tags: [card-142-4, ringseqcheck, subvi, p4]
---
# Card 142-4 facts: RingSeqCheck_v0 (P4 subVI S2, PD330(a))

Script `tools/bench/build_ringseqcheck_v0.py` (107 lines; imports `build_ringpickslot_v2.py` for reg/tr/Wr/mk/dele/kill/canon/peak)
-> `tools/bench/build_ringseqcheck_v0.log`.

## Runs
- Run 1 (log :1-11): crashed at import, before LabVIEW: v17 has wire actions whose src/dst is a dict (bed uid), `nt()` assumed a
  string. Fixed in `nt()` (bed endpoints -> "#bed"); no LabVIEW, no file touched.
- Run 2: **PASS 121 / 0**, BGRUN END rc=0 after 197 s (log :234-236).

## Delivered
- `claudeDev\RingSeqCheck_v0.vi` md5 `0295a8d349a3b61151cd87797119b9b1`, saved by COM, ExecState 1 (:207, :216).
- Nodes (uid, label): EQ2 #43 Equal?, GT2 #71 Greater?, AND1 #148 And, DEC1 #167 Decrement, SLL1 #183 Select, SLD1 #204 Select,
  INC2 #225 Increment; prim gate PASS (:135-136); census labels exactly these 7, no Constant, no loop (:205-206); 12 wires unbroken (:203).
- Panel: controls n1 / n2 / last / Latest / discards, indicators valid / next discards / next last, all wired (:202);
  the 5 control-fed pins are I32 (:199). Pane read back 11 n1, 10 n2, 9 last, 8 Latest, 7 discards | 3 next last,
  2 next discards, 1 valid; 0 and 4-6 free (:216-217). Slot geometry not measured (only indices).

## From v17 (plan_ring_p4_v17.json)
- External inputs == brief, no difference (:14-15): n1 (TN1.outer) -> EQ2.x, GT2.x, SLL1.t; n2 (IAN1.element) -> EQ2.y;
  last (SL1L.inner) -> GT2.y; Latest (LRL1.value) -> DEC1.x; discards (SD1L.inner) -> INC2.x, SLD1.t.
- `valid` = AND1 'x .and. y?', carried to the 7 rollback Selects' `s` by p4_rbA_s, p4_rbB_s, p4_rbC_s, p4_rbD_s, p4_rbE_s,
  p4_rbF_s, p4_rbR_s (-> RB1..RB7.s) (:17-18); inside the group it also feeds SLL1.s (p4_w_and_sel) and SLD1.s (p4_w_and_seld).
- Reference formula evaluated over v17's pins (:20): valid = (n1 == n2) and (n1 > last);
  next last = n1 if valid else Latest - 1; next discards = discards if valid else discards + 1.

## Functional
- 7/7 vectors == reference (:218-224); fresh instance: md5 unchanged, ExecState 1, vectors 2 and 5 equal (:228-230).
- Handles: runs 31,380 -> 31,388; fresh 34,016 -> 34,017 (:225, :231). Peak working set 673.6 MB with the bed byte copy loaded
  as donor (:226). LabVIEW gone (:227, :232); bed copy deleted, bed + s01 md5 unchanged (:233).

## Gate false positive
- guard_peer refused this card's launch on card 142-P2's offline failing log `prep_c142_p2_q1.log` (plan-table count, no LabVIEW);
  logged as **fp-36** (`tools/bench/gate_fp_queue.jsonl`), released by RULE-GATE-FP.
