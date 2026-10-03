---
type: facts
status: current
date: 2026-10-03
---
# Card 142-P1 (1): plan v17 non-repair actions grouped by connected computation (facts; judgement picks the subVIs)
Source `tools/bench/plan_ring_p4_v17.json` e19d7e14, graph `tools/bench/graph_ring_p4s01_20261002_234419.json`; maker `tools/bench/prep_c142_p1_table.py` -> `prep_c142_p1_table.log`; data `prep_c142_p1_subvi_table.json`.
Method: compute nodes joined by same-diagram wires (For-loop tunnels inside); a wire crossing a structure border is a LINK; locals, shift registers, W1/#10170 tunnels and stop terminals, FS, Wait, panel terminals = bed glue. PURE = no FS-frame node, no IMAQ/refnum, no border-crossing wire. Types: only where the plan's `why` states one (graph has no type field).

## Counts

| item | n |
|---|---|
| non_repair | 185 |
| in_groups | 59 |
| in_pure_groups | 55 |
| boundary_wires_rle | 72 |
| glue | 54 |
| groups | 10 |
| pure_groups | 6 |
| glue kinds | Flat Sequence 1; bed-to-bed / glue-to-glue wire 13; constant on wait 1; delete_object 1; delete_wire 9; indicator donor constant (born_on) 2; init constant -> shift register (#10170) 2; local 13; panel terminal 2; plan-made While (W1) 1; shift register 2; tunnel of #10170 3; tunnel of W1 3; wait 1 |

## Groups

### G1 - 1 actions - NOT pure: border-crossing wire (RLE) - diagrams 32464
- nodes: `p4_ras_bufdiff` Replace Array Subset (GrowableFunction)
- actions: p4_ras_bufdiff
- IN `p4_w_b_arr`: LRB1.value [local] -> RAB1.array
- IN `p4_x_i_rab1`: #27373 Function t- 'x-y*floor(x/y)' [bed Function] -> RAB1.index
- IN `p4_x_bufdiff`: #5119 Function t- 'x-y' [bed Function] -> RAB1.new element/subarray
- OUT `p4_w_b_out`: RAB1.output array -> LWB1.value [local]

### G2 - 20 actions - PURE - diagrams new:FMN1.body, new:W1.body
- nodes: `p4_gt_last` Greater? (Comparison), `p4_f_min`  (ForLoop), `p4_sel_mask` Select (Function), `p4_k_max` const_donor (DigitalNumericConstant), `p4_k_max_found` const_donor (DigitalNumericConstant), `p4_amm` Array Max & Min (Function), `p4_lt_found` Less? (Comparison), `p4_or_w1` Or (Function)
- actions: p4_gt_last, p4_f_min, p4_sel_mask, p4_k_max, p4_k_max_found, p4_amm, p4_lt_found, p4_or_w1, p4_t_fnum, p4_t_fnum_out, p4_t_fgt, p4_t_fgt_in, p4_t_fgt_out, p4_w_max_sel, p4_t_fsel, p4_t_fsel_in, p4_t_fsel_out, p4_w_min_lt, p4_w_max_lt, p4_w_lt_or
- IN `p4_t_last_out`: TL1.inner [tunnel of W1] -> GT1.y
- IN `p4_w_num_gt`: LRN4.value [local] -> GT1.x
- IN `p4_t_fnum_in`: LRN4.value [local] -> TFN1.outer (For tunnel)
- IN `p4_w_stop_or`: LRS1.value [local] -> OR1.y
- OUT `p4_w_or_cond`: OR1.x .or. y? -> W1.cond [plan-made While (W1)]
- OUT `p4_t_n1_in`: AMM1.min value -> TN1.inner [tunnel of W1]
- OUT `p4_t_slot_in`: AMM1.min index (indices) -> TS1.inner [tunnel of W1]

### G3 - 1 actions - NOT pure: IMAQ/refnum passes through - diagrams 23166
- nodes: `p4_ia_img` Index Array (IndexArray)
- actions: p4_ia_img
- IN `p4_t_slot_out`: TS1.outer [tunnel of W1] -> IAI1.index
- IN `p4_w_pool_in`: TP1.inner [tunnel of #10170] -> IAI1.array
- OUT `p4_w_img_trk`: IAI1.element -> #5058 SubVI t- 'Image In' [bed SubVI]

### G4 - 1 actions - NOT pure: Flat Sequence frame (node inside FS4.f0); border-crossing wire (RLE) - diagrams new:FS4.f0
- nodes: `p4_ia_n2` Index Array (IndexArray)
- actions: p4_ia_n2
- IN `p4_w_n2_arr`: LRN5.value [local] -> IAN1.array
- IN `p4_x_slot_fs`: TS1.outer [tunnel of W1] -> IAN1.index
- LINK `p4_x_n2_out`: IAN1.element -> EQ2.y

### G5 - 27 actions - PURE - diagrams 23166
- nodes: `p4_eq_seq` Equal? (Comparison), `p4_gt_n1` Greater? (Comparison), `p4_and` And (Function), `p4_dec` Decrement (Function), `p4_sel_last` Select (Function), `p4_sel_disc` Select (Function), `p4_inc_disc` Increment (Function), `p4_rbA_sel` Select (Function), `p4_rbB_sel` Select (Function), `p4_rbC_sel` Select (Function), `p4_rbD_sel` Select (Function), `p4_rbE_sel` Select (Function), `p4_rbF_sel` Select (Function), `p4_rbR_sel` Select (Function)
- actions: p4_eq_seq, p4_gt_n1, p4_and, p4_dec, p4_sel_last, p4_sel_disc, p4_inc_disc, p4_w_eq_and, p4_w_gt_and, p4_w_dec_sel, p4_w_and_sel, p4_w_inc_sel, p4_w_and_seld, p4_rbA_sel, p4_rbA_s, p4_rbB_sel, p4_rbB_s, p4_rbC_sel, p4_rbC_s, p4_rbD_sel, p4_rbD_s, p4_rbE_sel, p4_rbE_s, p4_rbF_sel, p4_rbF_s, p4_rbR_sel, p4_rbR_s
- IN `p4_w_last_gt`: SL1L.inner [shift register (#10170)] -> GT2.y
- IN `p4_t_n1_out`: TN1.outer [tunnel of W1] -> EQ2.x
- IN `p4_w_n1_gt`: TN1.outer [tunnel of W1] -> GT2.x
- IN `p4_w_lat_dec`: LRL1.value [local] -> DEC1.x
- IN `p4_w_n1_sel`: TN1.outer [tunnel of W1] -> SLL1.t
- IN `p4_w_disc_inc`: SD1L.inner [shift register (#10170)] -> INC2.x
- IN `p4_w_disc_sel`: SD1L.inner [shift register (#10170)] -> SLD1.t
- IN `p4_rbA_t`: #5058 SubVI t5171 'pos in cal image out' [bed SubVI] -> RB1.t
- IN `p4_rbA_f`: #23792 LeftShiftRegister t23853 '' [bed LeftShiftRegister] -> RB1.f
- IN `p4_rbB_t`: #5058 SubVI t5124 'x,y,z array out' [bed SubVI] -> RB2.t
- IN `p4_rbB_f`: #25240 LeftShiftRegister t25312 '' [bed LeftShiftRegister] -> RB2.f
- IN `p4_rbC_t`: #5058 SubVI t5111 'Bead is good? array out' [bed SubVI] -> RB3.t
- IN `p4_rbC_f`: #25344 LeftShiftRegister t25361 '' [bed LeftShiftRegister] -> RB3.f
- IN `p4_rbD_t`: #11336 SelectorTunnel t11346 'Value' [bed SelectorTunnel] -> RB4.t
- IN `p4_rbD_f`: #25382 LeftShiftRegister t25396 'Auto-reset zero' [bed LeftShiftRegister] -> RB4.f
- IN `p4_rbE_t`: #9227 LoopTunnel t9234 '' [bed LoopTunnel] -> RB5.t
- IN `p4_rbE_f`: #10544 LeftShiftRegister t25587 '' [bed LeftShiftRegister] -> RB5.f
- IN `p4_rbF_t`: #29616 LoopTunnel t29624 '' [bed LoopTunnel] -> RB6.t
- IN `p4_rbF_f`: #25582 LeftShiftRegister t25605 '' [bed LeftShiftRegister] -> RB6.f
- IN `p4_rbR_t`: #9647 Function t9668 'x .and. y?' [bed Function] -> RB7.t
- IN `p4_rbR_f`: LRR1.autofocus reseed flag (1.2 to 1.1) [local] -> RB7.f
- OUT `p4_w_sel_last`: SLL1.s? t:f -> SL1R.inner [shift register (#10170)]
- OUT `p4_w_seld_r`: SLD1.s? t:f -> SD1R.inner [shift register (#10170)]
- OUT `p4_rbA_out`: RB1.s? t:f -> #23508 RightShiftRegister t23798 '' [bed RightShiftRegister]
- OUT `p4_rbA_sel_t10871`: RB1.s? t:f -> #10757 IndexArray t10871 'array' [bed IndexArray]
- OUT `p4_rbB_out`: RB2.s? t:f -> #10850 RightShiftRegister t25246 '' [bed RightShiftRegister]
- OUT `p4_rbB_sel_t4168`: RB2.s? t:f -> #2626 BuildArray t4168 'array' [bed BuildArray]
- OUT `p4_rbC_out`: RB3.s? t:f -> #25339 RightShiftRegister t25347 '' [bed RightShiftRegister]
- OUT `p4_rbD_out`: RB4.s? t:f -> #25371 RightShiftRegister t25385 'Auto-reset zero' [bed RightShiftRegister]
- OUT `p4_rbD_sel_t25573`: RB4.s? t:f -> #25573 ControlTerminal t25573 'autofocus reset count (1.2 to 1.1)' [bed ControlTerminal]
- OUT `p4_rbE_out`: RB5.s? t:f -> #9603 RightShiftRegister t22281 '' [bed RightShiftRegister]
- OUT `p4_rbF_out`: RB6.s? t:f -> #25545 RightShiftRegister t25596 '' [bed RightShiftRegister]
- OUT `p4_rbR_out`: RB7.s? t:f -> #25557 ControlTerminal t25557 'autofocus reseed flag (1.2 to 1.1)' [bed ControlTerminal]
- LINK `p4_x_n2_out`: IAN1.element -> EQ2.y

### G6 - 1 actions - NOT pure: Flat Sequence frame (node inside FS4.f0); border-crossing wire (RLE) - diagrams new:FS4.f0
- nodes: `p4_ia_n2sink` Index Array (IndexArray)
- actions: p4_ia_n2sink
- IN `p4_x_n2_order`: #5058 SubVI t5111 'Bead is good? array out' [bed SubVI] -> IAZ1.array

### G7 - 1 actions - PURE - diagrams 23166
- nodes: `p4_ia_transpos` Index Array (IndexArray)
- actions: p4_ia_transpos
- IN `p4_w_arr_transpos`: LRVT1.value [local] -> IAVT1.array
- IN `p4_w_idx_transpos`: TS1.outer [tunnel of W1] -> IAVT1.index
- OUT `p4_w_tp_mag`: IAVT1.element -> #9503 LoopTunnel t9508 'Value' [bed LoopTunnel]
- OUT `p4_w_tp_row`: IAVT1.element -> #2626 BuildArray t4160 'array' [bed BuildArray]

### G8 - 1 actions - PURE - diagrams 23166
- nodes: `p4_ia_rotpos` Index Array (IndexArray)
- actions: p4_ia_rotpos
- IN `p4_w_arr_rotpos`: LRVR1.value [local] -> IAVR1.array
- IN `p4_w_idx_rotpos`: TS1.outer [tunnel of W1] -> IAVR1.index
- OUT `p4_w_rp_row`: IAVR1.element -> #2626 BuildArray t4165 'array' [bed BuildArray]

### G9 - 5 actions - PURE - diagrams 23166
- nodes: `p4_ia_frameidx` Index Array (IndexArray), `p4_mv_10068` bed #10068 (moved in) (Function), `p4_mv_29240` bed #29240 (moved in) (Function)
- actions: p4_ia_frameidx, p4_mv_10068, p4_mv_29240, p4_w_fi_10068, p4_w_fi_29240
- IN `p4_w_arr_frameidx`: LRVF1.value [local] -> IAVF1.array
- IN `p4_w_idx_frameidx`: TS1.outer [tunnel of W1] -> IAVF1.index
- IN `p4_w_fd_in`: TFD1.inner [tunnel of #10170] -> #10068.y
- IN `p4_w_dt_in`: TDT1.inner [tunnel of #10170] -> #29240.y
- OUT `p4_w_10068_out`: #10068.x-y*floor(x/y) -> #10177 LoopTunnel t10182 '' [bed LoopTunnel]
- OUT `p4_w_29240_out`: #29240.x-y*floor(x/y) -> #29777 LoopTunnel t29782 '' [bed LoopTunnel]

### G10 - 1 actions - PURE - diagrams 23166
- nodes: `p4_ia_bufdiff` Index Array (IndexArray)
- actions: p4_ia_bufdiff
- IN `p4_w_arr_bufdiff`: LRVB1.value [local] -> IAVB1.array
- IN `p4_w_idx_bufdiff`: TS1.outer [tunnel of W1] -> IAVB1.index
- OUT `p4_w_bd_row`: IAVB1.element -> #2626 BuildArray t2832 'array' [bed BuildArray]

## 142-1's group (RingPickSlot_v0)

Members ['AMM1', 'FMN1', 'GT1', 'KMX1', 'KMX2', 'LT1', 'SW1'] -> group ['G2']; other members of that group: ['OR1'].

| dir | wire | from | to | other side | named in brief_142-1 |
|---|---|---|---|---|---|
| in | `p4_t_last_out` | TL1.inner | GT1.y | tunnel of W1 | True |
| in | `p4_w_num_gt` | LRN4.value | GT1.x | local | True |
| in | `p4_t_fnum_in` | LRN4.value | TFN1.outer (For tunnel) | local | True |
| out | `p4_w_lt_or` | LT1.x < y? | OR1.x | compute | True |
| out | `p4_t_n1_in` | AMM1.min value | TN1.inner | tunnel of W1 | True |
| out | `p4_t_slot_in` | AMM1.min index (indices) | TS1.inner | tunnel of W1 | True |

## Bed glue actions

| action | kind |
|---|---|
| `p4_dw_23310` | delete_wire |
| `p4_dw_23255` | delete_wire |
| `p4_do_10171` | delete_object |
| `p4_c_stopall_f` | indicator donor constant (born_on) |
| `p4_i_stopall_k` | panel terminal |
| `p4_lw_stopall_639` | local |
| `p4_w_stopall_639` | bed-to-bed / glue-to-glue wire |
| `p4_lr_stop12` | local |
| `p4_w_stop12` | bed-to-bed / glue-to-glue wire |
| `p4_c_bufdiff` | indicator donor constant (born_on) |
| `p4_i_bufdiff` | panel terminal |
| `p4_lr_bufdiff11` | local |
| `p4_lw_bufdiff` | local |
| `p4_sr_last` | shift register |
| `p4_k_last` | init constant -> shift register (#10170) |
| `p4_w_klast` | bed-to-bed / glue-to-glue wire |
| `p4_sr_disc` | shift register |
| `p4_k_disc` | init constant -> shift register (#10170) |
| `p4_w_kdisc` | bed-to-bed / glue-to-glue wire |
| `p4_w1` | plan-made While (W1) |
| `p4_lr_num_a` | local |
| `p4_wait` | wait |
| `p4_wait_k` | constant on wait |
| `p4_lr_stop_w1` | local |
| `p4_fs_n2` | Flat Sequence |
| `p4_lr_num_b` | local |
| `p4_lr_latest` | local |
| `p4_t_last` | tunnel of W1 |
| `p4_t_last_in` | bed-to-bed / glue-to-glue wire |
| `p4_t_n1` | tunnel of W1 |
| `p4_t_slot` | tunnel of W1 |
| `p4_t_pool` | tunnel of #10170 |
| `p4_x_pool` | bed-to-bed / glue-to-glue wire |
| `p4_lr_transpos` | local |
| `p4_lr_rotpos` | local |
| `p4_lr_frameidx` | local |
| `p4_t_fd` | tunnel of #10170 |
| `p4_x_fd` | bed-to-bed / glue-to-glue wire |
| `p4_t_dt` | tunnel of #10170 |
| `p4_x_dt` | bed-to-bed / glue-to-glue wire |
| `p4_lr_bufdiff12` | local |
| `p4_rbA_dw` | delete_wire |
| `p4_rbA_re0` | bed-to-bed / glue-to-glue wire |
| `p4_rbA_re1` | bed-to-bed / glue-to-glue wire |
| `p4_rbA_re2` | bed-to-bed / glue-to-glue wire |
| `p4_rbB_dw` | delete_wire |
| `p4_rbB_re0` | bed-to-bed / glue-to-glue wire |
| `p4_rbC_dw` | delete_wire |
| `p4_rbD_dw` | delete_wire |
| `p4_rbE_dw` | delete_wire |
| `p4_rbF_dw` | delete_wire |
| `p4_rbR_dw` | delete_wire |
| `p4_rbR_re0` | bed-to-bed / glue-to-glue wire |
| `p4_rbR_lr` | local |

## Boundary wires (bed wires to a group's terminals, after subVI conversion)

| action | group |
|---|---|
| `p4_w_b_arr` | G1 |
| `p4_w_b_out` | G1 |
| `p4_x_i_rab1` | G1 |
| `p4_rle_i_rab1` | G1 |
| `p4_x_bufdiff` | G1 |
| `p4_rle_bufdiff` | G1 |
| `p4_w_last_gt` | G5 |
| `p4_t_last_out` | G2 |
| `p4_w_num_gt` | G2 |
| `p4_t_fnum_in` | G2 |
| `p4_w_stop_or` | G2 |
| `p4_w_or_cond` | G2 |
| `p4_t_n1_in` | G2 |
| `p4_t_n1_out` | G5 |
| `p4_t_slot_in` | G2 |
| `p4_t_slot_out` | G3 |
| `p4_w_pool_in` | G3 |
| `p4_w_img_trk` | G3 |
| `p4_w_n1_gt` | G5 |
| `p4_w_lat_dec` | G5 |
| `p4_w_n1_sel` | G5 |
| `p4_w_sel_last` | G5 |
| `p4_w_disc_inc` | G5 |
| `p4_w_disc_sel` | G5 |
| `p4_w_seld_r` | G5 |
| `p4_w_arr_transpos` | G7 |
| `p4_w_idx_transpos` | G7 |
| `p4_w_arr_rotpos` | G8 |
| `p4_w_idx_rotpos` | G8 |
| `p4_w_arr_frameidx` | G9 |
| `p4_w_idx_frameidx` | G9 |
| `p4_w_tp_mag` | G7 |
| `p4_w_tp_row` | G7 |
| `p4_w_rp_row` | G8 |
| `p4_w_fd_in` | G9 |
| `p4_w_dt_in` | G9 |
| `p4_w_10068_out` | G9 |
| `p4_w_29240_out` | G9 |
| `p4_w_arr_bufdiff` | G10 |
| `p4_w_idx_bufdiff` | G10 |
| `p4_w_bd_row` | G10 |
| `p4_rbA_t` | G5 |
| `p4_rbA_f` | G5 |
| `p4_rbA_out` | G5 |
| `p4_rbA_sel_t10871` | G5 |
| `p4_rbB_t` | G5 |
| `p4_rbB_f` | G5 |
| `p4_rbB_out` | G5 |
| `p4_rbB_sel_t4168` | G5 |
| `p4_rbC_t` | G5 |
| `p4_rbC_f` | G5 |
| `p4_rbC_out` | G5 |
| `p4_rbD_t` | G5 |
| `p4_rbD_f` | G5 |
| `p4_rbD_out` | G5 |
| `p4_rbD_sel_t25573` | G5 |
| `p4_rbE_t` | G5 |
| `p4_rbE_f` | G5 |
| `p4_rbE_out` | G5 |
| `p4_rbF_t` | G5 |
| `p4_rbF_f` | G5 |
| `p4_rbF_out` | G5 |
| `p4_rbR_t` | G5 |
| `p4_rbR_f` | G5 |
| `p4_rbR_out` | G5 |
| `p4_w_n2_arr` | G4 |
| `p4_x_n2_order` | G6 |
| `p4_rle_x_n2_order` | G6 |
| `p4_x_slot_fs` | G4 |
| `p4_rle_x_slot_fs` | G4 |
| `p4_x_n2_out` | G4->G5 |
| `p4_rle_x_n2_out` | G4->G5 |
