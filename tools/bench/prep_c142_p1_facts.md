---
type: facts
status: current
date: 2026-10-03
---
# Card 142-P1 facts: (1) v17 non-repair decomposition table, (2) rest of the slot-write repair as one bed session (offline, no LabVIEW)

## (1) Decomposition - `prep_c142_p1_subvi_table.md` / `.json` (maker `prep_c142_p1_table.py`, log `prep_c142_p1_table.log` 5/0)
- v17 e19d7e14: 235 actions = 50 `p4_rp*` + 185 non-repair (`prep_c142_p1_q1.log`). Graph has no type field (`prep_c142_p1_q2.log:3-7`); no
  boundary wire's `why` states a type -> every I/O type is UNSTATED in plan/graph.
- 185 = 59 in 10 computation groups (55 in the 6 PURE ones) + 72 boundary wires/RLE (bed wires to a group's terminals) + 54 bed glue
  (local 13, bed-to-bed wire 13, delete_wire 9, delete_object 1, tunnels of #10170 3 / of W1 3, shift reg 2 + 2 init constants, W1, Wait +
  its constant, FS4, 2 panel terminals + 2 donor constants) (`table.log` COUNTS).
- PURE groups: **G2** slot pick (20 actions: GT1, FMN1, SW1, KMX1, KMX2, AMM1, LT1, **OR1**), **G5** overwrite check + rollback (27: EQ2, GT2,
  AND1, DEC1, SLL1, SLD1, INC2, RB1..RB7; 21 inputs, 12 outputs), G7/G8/G10 one Index Array each, G9 Index Array + bed Q&R #10068/#29240
  (moved in). NOT pure: G1 RAB1 (border-crossing wires), G3 IAI1 (IMAQ pool -> #5058 Image In), G4 IAN1 / G6 IAZ1 (inside FS4.f0).
- One cross-group LINK: `p4_x_n2_out` IAN1 (FS4.f0) -> EQ2.y (G5) crosses the FS border.
- **142-1 boundary:** its 7 nodes lie in ONE group (G2); the 6 wires across its edge are exactly the ones brief_142-1 names (in: Num x2,
  last via TL1; out: min value -> TN1, min index -> TS1, Less? -> OR1.x). `found` (LT1) has ONE sink, OR1.x, and OR1 (+ StopAll local LRS1)
  drives W1's stop terminal (`p4_w_or_cond`); OR1 is the only other compute node joined to the group by a wire. Boundary CONFIRMED.

## (2) Remaining repair - `plan_ring_p4_rasrest.json` (maker `prep_c142_p1_mk.py`, log `prep_c142_p1_mk.log` 9/0)
- Remaining = v17 #25..#50 (26 actions, `p4_rp29048_dwo`..`p4_rp29316_out`) == s02's 26 `p4_rp*`; dependencies: symbols RX3 (s01) and
  RX4/RX5 (own) only, no non-repair action, every named uid in the s01 graph (`mk.log` DEP). No later v17 action uses RX4/RX5.
- Planned on s02's provisional base (2d0c2c99): FINAL, open_rows_match, 11 bed-declared pairs, end rows 16 == s02's 16 (`mk.log` SB).
  `plan_ring_p4_rasrest.json` **4ad2d288** (in 9bcd5280) - still PROVISIONAL.
- **FIRST UNEXPECTED RESULT - `--rebase` REFUSED** (`prep_c142_p1_rebase.log:3`): `BINDING: the created objects differ (name-free shape):
  GrowableFunction x3 simulated vs x1 real, GrowableFunction x0 simulated vs x2 real`. The plan file is unchanged (md5 4ad2d288, written
  only on success). Consistent with PD325(a) (`docs/d1/ring-p4b.md:58-61`: LabVIEW re-used deleted terminal uids 28004/28979 on the new
  #6942/#6805, so 2 of the 3 real RAS nodes show 3 new terminals, not 4) - not diagnosed further (card rule).
- Therefore NOT done: dry, prerun, X10 at 596.5, Error List prediction, `plan_ring_p4_rasrest_pred.json` (script written, not run:
  `prep_c142_p1_pred.py`). Recipe pair WRITTEN, not dry-run: `tools/recipes/stage_d1_ring_p4_rasrest.py` / `_scratch.py` (copies of the
  s02 pair, names only). Prior-art: not dispatched (no guard asked).
