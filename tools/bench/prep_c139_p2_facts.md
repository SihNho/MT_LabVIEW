# Card 139-P2 facts (offline, 2026-10-02; no LabVIEW). Inputs v10 9032dfcd, gates 386a0546, mkv10 0a5170db, graph 50595c62 (mkv11.log:3-6)
Maker `tools/bench/prep_c139_p2_mkv11.py` -> `plan_ring_p4_v11.json` **e398c447** (= stagesim plan_out), raw input
`plan_ring_p4_v11_in.json` 4cf93ed2 (finalized POPPED), recipe notes `plan_ring_p4_v11_recipe_gates.json` ed85c4f8 (stop_route.actions
+ init updated, donor_bind unchanged: KSF1 DonorBoolF_v0 uid 0 SENTINEL still pending).
Log `tools/bench/prep_c139_p2_mkv11.log`: **23 pass / 0 fail**, BGRUN END rc=0 after 313 s (:402-403). One run.
## 1. Diff v10 -> v11 by action id (185 -> 185; 182 kept, identical, v10 relative order; :10-14)
- REMOVED: #4 p4_i_stopall (indicator on CT t642), #6 p4_lw_stopall_init (Local write on #4866), #7 p4_w_stopall_init.
- KEPT unchanged: p4_c_stopall_f = KSF1 BooleanConstant const_donor on #4866 (now #4).
- ADDED: #5 `p4_i_stopall_k` (ISK1, ControlTerminal 'StopAll', indicator, born_on new:KSF1, #4866 = P2b p2b_i_Num form);
  #6 `p4_lw_stopall_639` (LWS2, Local WRITE 'StopAll', diagram 639); #7 `p4_w_stopall_639` (src {uid 642, term_uid 642} -> LWS2.value).
- MODIFIED: none. Top-level `goal` rewritten; `final`/`finalized` from the finalize, never copied.
## 2. Who reads StopAll (pass 3; :15-17)
- Exactly ONE ControlTerminal labelled StopAll in v11 (p4_i_stopall_k); the bed graph has no 'StopAll' label (0 hits), so every
  StopAll Local can only bind to it.
- Locals: #6 p4_lw_stopall_639 write (639); #8 p4_lr_stop12 read (23166 = loop 1.2 body); #38 p4_lr_stop_w1 read (new:W1.body). All after #5.
## 3. Replay + fs_routes (pass 2, 4)
- Replay on the bed graph: **END**, 186 steps, no error, last p4_rle_x_n2_out (:376-377).
- Step 5 ISK1 on #4866 with a new wire from KSF1 (:379); step 7 = BRANCH on existing w6929 from t642 (how 'branch', :381), old sink kept.
- cdiff vs v10: per-step equal at every shared id (0 differ, :382); end 24 rows == v10's 24 (:385-386). open_rows_match False (carried).
- fs_routes regenerated: keys {17,19,180,182,184} == v10's, each key's action id == stored id (:374-375).
## 4. Compile + routes (pass 4, 5)
- compile_plan: v10 167, v11 **167**; per meta step {1:39, 2:28, 3:37, 4:36, 5:27}, all <= 40 (:390-392).
- Route compare v10 -> v11 by action-id tuple: 6 differing ops, all on the 3 removed / 3 added ids, 0 OTHER (:393-399):
  p4_i_stopall_k create/indicator; p4_lw_stopall_639 create/local_write; p4_w_stopall_639 connect (route 'cfw').
- Advisory route check (plan not final): ROUTE 5 p4_i_stopall_k 'indicator', 6 'local_write', 7 'cfw' - no UNROUTABLE (:207-210).
  UNROUTABLE set v10 {p4_i_stopall, p4_w_stop12, p4_t_last(+_in,_out)} -> v11 {p4_w_stop12, p4_t_last(+_in,_out)} (:387-389).
## 5. Carried, not caused by v11
- ROUTE 9 p4_w_stop12 "node #23166 not in Diagram[122] (#23166).Nodes[]" (:212) and ROUTE 53 p4_t_last "node #10000038 not in
  Diagram[122]" (:256): identical to v10 (prep_c139_p1_facts.md:28).
- KSF1 donor DonorBoolF_v0.vi uid 0 SENTINEL: still unbuilt (prep_c139_p1_facts.md:30). Steps 4-6 ran on the PROVISIONAL const rule
  (opmodels/const.json has no sim params, mkv11.log:22-24); a Local write in a While body (#639) is unmeasured on that diagram.
OPEN: KSF1's Boolean-False donor still needs building + read-back before launch, and p4_w_stop12 / p4_t_last remain UNROUTABLE
(Diagram[122] addressing of #23166) - which route replaces them is a judgement call.
