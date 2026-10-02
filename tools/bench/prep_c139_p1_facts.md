# Card 139-P1 facts (offline, 2026-10-02; no LabVIEW). Inputs v8 059b5296, v9 b91cf4d7, gates d9d0f269, graph 50595c62 (mkv10.log:3-6)
Maker `tools/bench/prep_c139_p1_mkv10.py` -> `plan_ring_p4_v10.json` **9032dfcd** (= stagesim plan_out), raw input
`plan_ring_p4_v10_in.json` ddc77f9e (finalized POPPED, mkv10.py:136), recipe notes `plan_ring_p4_v10_recipe_gates.json` 386a0546.
Log `tools/bench/prep_c139_p1_mkv10.log`: **24 pass / 0 fail**, BGRUN END rc=0 after 311 s (:416-417). One run.
## 1. Diff v8 -> v10 by action id (181 -> 185; 174 unchanged, identical, v8 order; :12-25)
- ADDED at #4-#7: `p4_i_stopall` (v9's, by id), `p4_c_stopall_f` (BooleanConstant const_donor on #4866, as KSF1),
  `p4_lw_stopall_init` (Local WRITE `StopAll` on #4866, as LWS1), `p4_w_stopall_init` (KSF1.value -> LWS1.value). REMOVED none.
- MODIFIED 7: p4_lr_stop12 / p4_lr_stop_w1 label+terminals+why (= v9's); p4_k_max / p4_k_max_found donor+why (uid 0 -> **127**,
  PD313(a)); p4_t_fnum / p4_t_fgt / p4_t_fsel why (= v9's, gates file renamed to v10) (:23).
- Top-level: `goal` rewritten; `final`/`finalized` from the finalize, never copied.
## 2. fs_routes REGENERATED (pass 2) by the existing finalize path stagesim.simulate (stagesim.py:2510 fs_routes_of)
- v10 keys {17 p4_x_i_rab1 fs_inner_branch, 19 p4_x_bufdiff fs_border, 180 p4_x_n2_order, 182 p4_x_slot_fs, 184 p4_x_n2_out fs_exit};
  every key's action id == its stored id (:383, :385). v8's stored table had only 13/15 (:384).
## 3. Replay + compile (pass 3)
- Replay on the bed graph: **END**, 186 steps (base + 185), no error, last p4_rle_x_n2_out (:387-388). New steps 4-7 ok (:389-392).
- cdiff vs v8: per-step equal at every shared id (0 differ, :400); end 24 rows == v8's 24 (:403-404). open_rows_match False /
  classed ok False, as v8 (carried).
- compile_plan: v8 163 ops, v10 **167** (+4); per meta step {1:39, 2:28, 3:37, 4:36, 5:27}, all <= 40 (:405-407).
## 4. Route compare v8 -> v10 by action-id tuple (pass 4): 4 differing ops, all on ADDED actions, 0 other (:408-412)
- p4_c_stopall_f create/primitive; p4_i_stopall create/indicator; p4_lw_stopall_init create/local_write; p4_w_stopall_init connect.
- The 3 wires of the v9 defect (p4_w_b_out, p4_x_bufdiff, p4_x_i_rab1) compile as in v8.
- Side: v8 stored vs v8 regenerated table compile equal (:413); v9's simulator output vs v8 differ only on p4_i_stopall (:414)
  = the review's test (a), confirming the stale copied table was the whole v9 defect.
## 5. Review c138-6-p1cmp-routes (pass 5): disposition + `FIXED: ... prep_c139_p1_mkv10.py:136 ...` under "What was done with it".
## 6. Carried, not caused by v10 (advisory finalize route check FAIL, non-final plan, :403)
- ROUTE 4 p4_i_stopall UNROUTABLE: "create_indicator_nested addresses Traverse('Node') by uid; #642 'stop (end)' belongs to Diagram
  #639, which is not a Node" (:216); identical in v9 (prep_c138_p1_mkv9.log:245), not in 138-P1's facts.
- ROUTE 9 p4_w_stop12 "node #23166 not in Diagram[122].Nodes[]" (:221) and ROUTE 53 p4_t_last (:265): same rows in v9 (mkv9.log:247,291).
## 7. Pending binds before launch (recipe_gates donor_bind)
- KMX1/KMX2 = DonorI32Max_v0 uid 127 BOUND. KSF1 = `claudeDev\DonorBoolF_v0.vi` uid 0 SENTINEL: no Boolean-False donor exists in
  claudeDev (Donor*.vi: 8 files, none Boolean; DonorRingConst/DonorSRInit hold I32/U32/DBL, NAMES.md:1384).
- Local write on #4866 and a BooleanConstant const_donor are UNMEASURED routes (precedents: local_write on FS frame 32464; const_donor
  ArrayConstant/I32 on #4866).
OPEN: StopAll's False source needs a Boolean donor VI (or another measured False-constant route) built and read back by a LabVIEW
card; and p4_i_stopall's indicator-on-a-ControlTerminal route is UNROUTABLE in the finalize route check - which route replaces it?
