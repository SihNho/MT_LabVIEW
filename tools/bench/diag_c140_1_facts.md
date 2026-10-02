---
type: facts
status: current
date: 2026-10-02
---
# Card 140-1 facts — P4 v14 sessions under X10 (OFFLINE, LabVIEW not opened; measured only, no cut picked, no tool built)
Script `prep_c140_1_sessions.py` (113 lines) -> `prep_c140_1_sessions_r2.log` rc 0, 5/0 (`:27`); data `diag_c140_1_sessions.json`. First run `prep_c140_1_sessions.log` rc 1 failed G2 on the script's own arithmetic (`len(B1 - {39}) == 28`; op 39 is both BIND and end); every number identical.
## 1. X10 model
- peak = start + R x 2.53 + N x (0.58 + 0.8) + 17.4 (`stage_prerun.py:2005-2026`, `memory_model.json:10-29`); R = {from_step} | checkpoints | every BIND op
  (add_sr, tunnel, create, connect_term_uid, `stagexec.py:1790`) | last op. FAIL > 690 (`memory_model.json:26-29`); 675 = card/meta planning limit.
  Step 1: 606.1 + 29 x 2.53 + 39 x 1.38 + 17.4 = **750.7** reproduced exactly (`r2.log:4`).
- Start 606.1 = 600.2 load of bed 39511877 + 5.9 op-0 read (`memory_model.json:55-58,30-33`), used for EVERY session in the tables. X10 itself uses start_mb
  **570.0** when the input VI's load is unmeasured (`stage_prerun.py:2319-2321,1991-2002`). With load growth 0.719 MB/op (`memory_model.json:61-64`, one pair)
  an EMPTY session exceeds 675 from op 63 (`r2.log:26`). Prerun also adds the recipe's own whole-VI reads x 2.53 (`stage_prerun.py:2322-2327`), not in tables.
## 2. Step 1's 29 reads = k 0 + 28 BIND ops (op 39 is BIND and end). BIND op -> first use (op), ids `p4_`-prefixed (json step1_binds)
- 4 c_stopall_f->i_stopall_k(5) · 5 i_stopall_k->none · 6 lw_stopall_639->w_stopall_639(7) · 8 lr_stop12->w_stop12(9) · 10 c_bufdiff->i_bufdiff(11) · 11 i_bufdiff->none ·
  12 lr_bufdiff11->w_b_arr(15) · 13 ras_bufdiff->w_b_arr(15) · 14 lw_bufdiff->w_b_out(16) · 17 x_i_rab1->rle_i_rab1(18) · 19 x_bufdiff->rle_bufdiff(20) · 21 sr_last->w_klast(23) ·
  22 k_last->w_klast(23) · 24 sr_disc->w_kdisc(26) · 25 k_disc->w_kdisc(26) · 27 w1->lr_num_a(28) · 28 lr_num_a->w_num_gt(55) · 29 gt_last->t_last(54) · 30 f_min->sel_mask(31) ·
  31 sel_mask->t_fnum(56) · 32 k_max->w_max_sel(58) · 33 k_max_found->w_max_lt(61) · 34 amm->t_fsel(59) · 35 lt_found->w_min_lt(60) · 36 wait->wait_k(37) · 37 wait_k->none ·
  38 lr_stop_w1->w_stop_or(63) · 39 or_w1->w_lt_or(62). Binder: While/For creates (27, 30) bind object + body from the op RETURN (`stagexec.py:2329-2368`); all others by `bind_new`: real new nodes since the last read
  vs the op's simulated new nodes, by CLASS only (owner not keyed), then terminal key (`stagexec.py:891-967`); add_sr + track_new (`:2119-2127`); ctu +
  bind_fs_tunnel/bind_case_faces (`:2116-2117`).
## 3. Merge facts
- Minimal reads (each BIND read after its op and before its first use; + k 0 + end): step 1 **14** (was 29): 0,4,6,8,10,14,17,19,22,25,27,30,36,39; whole v14
  (185 actions, 167 ops, 69 BIND ops, 71 reads now) **31** (json merge).
- Ambiguous for the CURRENT binder (2 new objects of one class in one read -> ExecStop `stagexec.py:938-939`): s1 {11-14} Local x2, {31-36} DigitalNumericConstant x2 +
  Function x3; v14 adds {42-52} Comparison/Function/IndexArray/Local, {54-67} and {101-106} LoopTunnel (LoopTunnel -> bind_by_frames `:935-937,1005-1029`, frame-key
  uniqueness NOT computed, counted ambiguous). Unambiguous: 11 of 13 groups (s1), 25 of 30 (v14).
- Step 1 as ONE session still fails: R 14 -> 712.7, R 22 (unambiguous only) -> 733.0, both > 690 (formula above, by hand). Deferred bind supported? **NO**: a checkpoint set lacking a BIND op -> ExecStop CHECKPOINT (`stagexec.py:2031-2037`); bind_new diffs only THIS op's sim step
  (`:2053-2054,2116-2118`) vs the real delta since the last read -> class mismatch ExecStop (`:926-930`); `_bind_create` only at a read (`:2100-2101`). Needs a stagexec edit.
## 4. Table A - current reads, start 606.1, each <= 675 (`r2.log:7-15`): TOTAL **9** (7 at <= 690). s: ops first..last acts/N/R/peak kinds
- 1: 1-17 dw_23310..x_i_rab1 17/17/11/674.8 create 9, connect 3, del_w, del_o, rle, stop, ctu · 2: 18-32 rle_i_rab1..k_max 15/15/12/674.6 create 8, rle 2, add_sr 2, connect 2, ctu
- 3: 33-44 k_max_found..eq_seq 12/12/13/672.9 create 12 · 4: 45-57 gt_n1..t_fgt_out 19/13/12/671.8 create 8, tunnel 3, wire_sr, connect
- 5: 58-82 w_max_sel..lr_transpos 33/25/6/673.2 connect 13, tunnel 4, wire_sr 4, branch 2, stop, create · 6: 83-102 ia_transpos..w_dt_in 24/20/8/671.3 connect 8, create 5, branch 3, move_in 2, tunnel 2
- 7: 103-128 w_10068_out..rbC_dw 26/26/6/674.6 connect 18, create 4, delete_wire 3, branch · 8: 129-154 rbC_sel..rbR_re0 26/26/6/674.6 connect 18, create 4, delete_wire 4
  · 9: 155-167 rbR_sel..rle_x_n2_out 13/13/7/659.1 connect 5, ctu 3, rle 3, create 2
## 5. Table B - merged reads, unambiguous groups only, same start/limit (`r2.log:16-23`): TOTAL **8** (7 at <= 690)
- 1: 1-17 dw_23310..x_i_rab1 17/17/10/672.3 · 2: 18-34 rle_i_rab1..amm 17/17/10/672.3 · 3: 35-49 lt_found..sel_last 15/15/11/672.0 · 4: 50-66 sel_disc..t_slot_out 29/17/10/672.3
- 5: 67-94 t_pool..w_tp_mag 30/28/5/674.8 · 6: 95-118 w_tp_row..rbA_out 28/24/7/674.3 · 7: 119-144 rbA_sel_t10871..rbE_f 26/26/6/674.6 · 8: 145-167 rbE_s..rle_x_n2_out 23/23/7/673.0
  With +0.719 MB/op growth: A fits 13 sessions to op 63, B 11, then every session from op 64 exceeds 675 (`r2.log:26`).
## 6. Dependency check: every `new:`/`of` use follows its creator in op order (G3 PASS `r2.log:6`), so every greedy prefix is dependency-closed; later sessions reference earlier sessions'
  `new:` symbols (A 2/21/15/21/6 out of s1-s5; B 2/21/30/13/4/1/2 out of s1-s7; json uses_cut) - each later plan must resolve them from the saved file.
- **Both tables cut s1|s2 between p4_x_i_rab1 (op 17) and p4_rle_i_rab1 (op 18, `of` p4_x_i_rab1)**: an `of` naming an action outside the plan is a compile ExecStop
  (`stagexec.py:761-764`); PD261(d) "each RLE with its loose end". Other cuts inside a meta unit: A U02, U05, U11, U14 (SR C); B U02, U04, U05, U12, U14 (SR A), U14 (SR E).
OPEN: table A or B and which start rule (606.1 / 570.0 fallback / +0.719 per op, which stalls at op 64); how to place the s1|s2 RLE cut; whether a deferred-bind stagexec edit (sec. 3) is worth 1 session.
