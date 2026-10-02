# Card 138-4 facts (offline, 2026-10-02; no LabVIEW). Inputs v7 01ab0893, graph p3b2b 50595c62 (md5 gates, mkv8.log:140-141)
Maker tools/bench/prep_c138_4_mkv8.py -> tools/bench/plan_ring_p4_v8.json **059b5296**; log tools/bench/prep_c138_4_mkv8.log run 4 (:138-568).
Runs 1-3 stopped on the maker's own text vs stageplan/1 (goal 419>400, why 419>400, donor.uid null): :35,:80,:99; gate added.
## 1. Diff by action id (v7 172 -> v8 181; 166 unchanged, identical and in v7 order, :147-157)
- REMOVED p4_w_num_sel, p4_w_gt_sel, p4_w_sel_amm (each replaced by a tunnel group).
- MODIFIED p4_sel_mask (diagram new:W1.body -> new:FMN1.body, why); p4_k_max (const_row on SW1.f value -> const_donor on
  FMN1.body); p4_w_max_lt (src KMX1 -> KMX2). No top-level key changed (goal kept: 400-char cap).
- ADDED #26 p4_f_min ForLoop FMN1 on W1.body; #29 p4_k_max_found KMX2 const_donor on W1.body; #53-55 TFN1 group (IN, indexing,
  Num local -> Select.t); #56-58 TFB1 group (IN, indexing, GT1 Boolean[] -> Select.s); #59 p4_w_max_sel KMX1 -> Select.f;
  #60-62 TFS1 group (OUT, indexing, Select 's? t:f' -> AMM1.array).
- DEVIATION from PD311(b)'s wording: Greater? GT1 stays on W1.body on the arrays (v7 p4_gt_last unchanged; legal, measured
  diag_c137_7_types.log:220-224). Inside the For it needs `last` through TL1 then a 2nd tunnel; compile_plan's tunnel group
  (stagexec.py:685-694) needs each tunnel's out-wire right after it, and TL1.inner's only sink would be the later tunnel.
## 2. Route class per new / changed action (all whys in v8 carry the cite)
- p4_f_min create For: PRECEDENT (plan_disp.json:36-43; created in a plan-made While stage_d1_disp_r3.log:62-63). N unwired.
- TFN1/TFB1/TFS1 tunnel + 6 group wires: PRECEDENT (plan_disp.json:425-468 form); indexing on a plan-made For: prior-art says it
  RAN in the disp stage (stage_d1_disp_c104B3.log:90,130, ExecState 1 :311-324). IndexMode NOT enforced by the executor:
  index_mode_fix runs only inside `if lost:` (stagexec.py:2104-2109) -> real IndexMode UNMEASURED for v8.
- p4_sel_mask Select, scalar s: MEASURED donor #529 (diag_c128_2_donors.log:61-63) + scalar s unbroken (diag_c137_7_types.log:171-189);
  an auto-indexed Boolean tunnel feeding s: UNMEASURED.
- p4_k_max / p4_k_max_found const_donor I32 2147483647: UNMEASURED - NO donor exists (claudeDev: DonorSRInit_v0 #134 U32 max,
  #248 I32 0; DonorRingConst_v0 #249 I32 -1; docs/NAMES.md:1384). v8 names claudeDev\DonorI32Max_v0.vi uid 0 (SENTINEL; schema needs int).
- p4_w_max_sel / p4_w_max_lt: compile 'connect'; real route const 188(c) (stagexec.py:1330-1338): constant by report_all(class).
## 3. PD307(a) (constant in a NEW body via stagekit.address / Nodes[])
- Constants in new bodies: KMX1 (FMN1.body), KMX2 (W1.body), WK2 p4_wait_k (W1.body, const_row born wired - never addressed later).
- No v8 action addresses them by stagekit.address: both KMX wires take the const route (Addr.const, report_all, stagexec.py:1527-1541);
  sinks Select.f / Less?.y are primitives (found by every method, PD307(a)). UNMEASURED: report_all('DigitalNumericConstant')
  listing a new-body constant (PD307(a) measured Traverse Constant + read_terms, not report_all by this class).
- 's? t: f' occurrences: v7 0, v8 0 (mkv8.log:158); all Select terminals already 's? t:f' - nothing to fix.
## 4. Replay v8 on the bed graph (tools/bench/sim/c138_4_v8/ring_p4_v3/, rewritten plan 4e575a76)
- END: 182 steps (base + 181), no error, last step 181 p4_rle_x_n2_out; final False (mkv8.log:520-537).
- New steps 26,29,53-62 ok, cdiff 16 (mkv8.log:200-236). End cdiff 24 rows == v7's 24 exactly (only-in-v8 [] / only-in-v7 [], :563).
- vs open_rows (11): 13 rows match an open row (376 x2, 2626 array x4 / element x3, 5058 Image In, 11261 x2, 28083) = expected;
  11 rows unclassed vs open_rows, all carried from v7 (10068/10150/10382/11529/29240 'x', 10757/29625/8634 'array',
  5058 'Bead is good? array in' / 'pos in cal image in' / 'x,y,z array') :539-562. Declared open rows 8634 'index (col)',
  29625 'index (col)', 29973 'element' are NOT in the end cdiff. open_rows_match False, classed ok False (as v7).
## 5. compile_plan(v8) (mkv8.log:161-173)
- OK, 163 ops (v7 160); per meta step {1:35, 2:28, 3:37, 4:36, 5:27}, all <= 40. Actions per step {1:35, 2:42, 3:41, 4:36, 5:27}.
- kinds: tunnel 9 (+3: TFN1/TFB1/TFS1), create 50 (+2), connect 68 (-2), rest as v7; p4_f_min route 'for'.
## 6. Prior-art review (tools/bench/prep_c138_4_priorart.log; archive/peer/2026-10-02-priorart-c138-4-p4v8-forloop.md)
- verdict settled-already (+ already-built, helper-exists, unread-evidence) :52-57; card tools/bench/cards/verdict_priorart-c138-4-p4v8-forloop.json.
- Says: copy disp DLF1-in-DL1 pattern; add recipe-level index_mode_fix + read-back gate per tunnel as PD235(c)
  (docs/d1-loop12-17-split-plan.md:2212, stage_d1_qrt_pool.py:46-47, log :222); KMX2 by const_row after Less?.x is wired
  (stagekit.py:897-910; I32 then UNMEASURED); a new I32-MAX donor only for KMX1 (const_row looks up a WhileLoop, stagekit.py:903).
- Release (FIXED/REFUTED) not written: archive/ is outside this card's write flags; the plan is not changed on the review's advice.
OPEN: accept the GT1-outside deviation? build DonorI32Max_v0 (KMX1) / const_row for KMX2? release the prior-art verdict how?
