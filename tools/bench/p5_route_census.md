---
card: 154-a2-3
status: current
date: 2026-10-09
---
# P5-1 route census (PD374(a)(c) + PD375(a), 1.2 side only) - offline, LabVIEW 0
Fragment of 23 actions + 3 refnum forms applied IN MEMORY by stagesim to s09 graph 22f967b5; stagexec.create_route / compile_plan
and stage_prerun.prim_donor_check read only. Script `diag_c154_a2_3_census.py`, log `diag_c154_a2_3_census.log:46-98` (RESULT 7/0).
`X` = stagexec.py, `S` = stagesim.py, log = census log line.

| # | row | route (kind) | X file:line | S file:line | proven-by | status |
|---|---|---|---|---|---|---|
| 1 | 1-D DBL const on #4866 (DonorQueue_v0 #52 const_donor, term 'x,y,z array') | create primitive (const_donor) | X:442-445, 3068-3082 | S:2298-2349 (log:53) | const_donor on #4866 plan_ring_p4_s02v18.json:342-359 | OK |
| 2 | Obtain Queue on #4866 (DonorQueue_v0 #108, 8 terms) | create primitive | X:442-445, 3068-3082 | S:2298-2349; termclass ParameterTerminal (log:54,77) | ext. donor prim plan_ring_p3a.json:13-41 | OK (X17 refuses, row 20) |
| 3 | const -> Obtain 'element data type' | connect 'const' (OpConstWire_v1) | X:1453-1461 | S:1478-1573 same diagram (log:55) | plan_ring_p3a.json:381-386 | OK |
| 4 | I32 -1 const on #4866 (DonorRingConst_v0 #249) | create primitive (const_donor) | X:3068-3082 | S:2298-2349 (log:56) | plan_ring_p3a.json:65-88 | OK |
| 5 | indicator 'records final (1.2 to 1.7)' born_on row 4 | create indicator on const | X:244-246, 497-508, 3041-3043 | S:2271-2292 (log:57) | plan_ring_p4_s02v18.json:362-373 | OK |
| 6 | Case on #23166, selector <- #29724 t29900 'valid' (8th sink, branch) | create case_wired | X:262-264, 422-426, 3106-3130 | S:1629+ _create_case wired (log:58) | plan_ring_p3a.json:158-174 (unwired src; branch census X:262-264) | OK |
| 7 | Enqueue Element in True frame (DonorQueue_v0 #44, 7 terms) | create primitive on new:CQ1.f1 | X:3068-3082 | S:2298-2349; termclass ParameterTerminal (log:59,78) | in a case frame plan_ring_p3a.json:216-243 | OK (X17 refuses) |
| 8 | #2626 t2813 -> case tunnel (in, True) -> Enqueue 'element' | tunnel group, kind 'tunnel' -> connect nested | X:766-791, 2522-2526, 1474-1476 | S:1313-1349 (log:60-62) | none launched; scratch diag_c123_casetun.log:38,45,69 (S:1319-1322) | OK |
| 9 | refnum Obtain 'queue out' (#4866) -> loop 1.2 #23166 | NONE: base-FS frame 7 -> frame 8 crossing | X:656-711 (FS ops plan-made FS only), 304-305, 2570-2573 | S:1499-1505; Va/Vc refused S:2150-2152 (log:79,81); Vb CRASH S:1783 (log:80) | none | **GAP** |
| 10 | refnum loop tunnel -> case tunnel -> Enqueue 'queue' | NONE: tunnel group out-wire must be in the next 2 actions; only SR-inner -> case tunnel routed | X:766-791, 776-787 | S:1506-1508 (no cross-border plain wire) | none | **GAP** |
| 11 | I32 count SR on loop 1.2 (#10170, body 23166, parent 686) | add_shift_reg | X:764-765 | S:1289-1310 (log:63) | plan_ring_p3a.json:56-63, 175-183 | OK |
| 12 | I32 0 const on 686 (DonorSRInit_v0 #248) -> SR left outer | create primitive + connect 'const_sr' | X:1437-1452 | S:2298-2349, 1478-1573 (log:64-65) | plan_ring_p3a.json:184-214 | OK |
| 13 | Increment in True frame ($work #1978, present in s09 log:51) | create primitive | X:3068-3082 | S:2298-2349 (log:66) | plan_ring_p3a.json:216-243 | OK |
| 14 | SR L.inner -> case tunnel in -> Increment x | connect_term_uid register_end_case_border (R1) | X:776-787 | S:1313-1349 (log:67-69) | plan_ring_p3a.json:244-267 | OK |
| 15 | Increment x+1 -> case tunnel out -> SR R.inner | connect_term_uid R2 | X:776-787 | S:1313-1349 (log:70-72) | plan_ring_p3a.json:268-291 | OK |
| 16 | False frame pass-through (tunnel in -> tunnel out) | case_frame_wire new_wire | X:800-801, 593-650 | S:1560-1570 (log:73) | plan_ring_p3a.json:292-306 | OK |
| 17 | Local write 'records final (1.2 to 1.7)' on 686 | create local_write | X:244, 3025-3032 | S:2298-2349 (log:74) | plan_ring_p4_s02v18.json:374-390 (on #639; on 686 none) | OK |
| 18 | SR R.outer (1.2 exit value) -> Local write | connect 'nested' (SR outer face by loop Terminals[]) | X:1474-1476, 1700-1725 | S:1478-1573 same diagram (log:75) | none found (no `R.outer"` source in tools/bench/plan_*.json) | OK |
| 19 | compile of rows 1-8, 11-18 | 17 ops: create x9, connect x4, tunnel 1, add_sr 1, connect_term_uid x2, case_frame_wire 1 | X:729-813 | - | (log:92) | OK |
| 20 | X17 prim_donor_check on rows 2, 7 | READ only | stage_prerun.py:2802-2809, 2858-2861 | - | refused: DonorQueue_v0 uid 108 / 44 "label UNMEASURED (not in PRIM_DONORS)" (log:94) | (not a route) |

## GAP rows verbatim (rows 9-10) and the code searched
- Row 9: `Va` wire new:QO1.queue out -> new:EQ1.queue: "FS exit to diagram #-19, the FS #681 sits on #536 - only ONE border (frame -> the
  FS's own diagram) is MEASURED (U6/U6')" (log:79); `Vc` same refusal into a case tunnel outer on #23166 (log:81); `Vb` tunnel on #10170 +
  wire into its outer on 686 -> stagesim `_fs_frame_wire` raises **TypeError** (`int(st["diagrams"].get(str(fi)))`, S:1783: a BASE FS frame
  has no `diagrams` entry) - a crash, not a SimError (log:80). Searched: S:1499-1508 op_wire FS dispatch (fs_of true for base frames
  4866/686 via fs_measured, log:52), S:1766-1806, S:2028-2116 (`_fs_border_wire` only for a source OFF an FS frame), S:2136-2195;
  X:656-726 fs_wire_ops (plan-made FS only), X:304-305 + S:2513 (fs_routes carry fs_border/fs_inner_branch/fs_exit, not
  fs_frame_to_frame), X:2570-2573 (a connect whose sim effect is fs_frame_to_frame is refused), X:2522-2526 ('tunnel' kind: no FS check).
- Row 10: X:766-775 "tunnel ... must be followed by exactly one wire into it and one out of it"; X:776-787 the only tunnel-to-tunnel
  route is a plan-made SR INNER face -> case tunnel (R1/R2); S:1506-1508 refuses a plain cross-border wire. A loop-tunnel inner face
  -> case tunnel needs the loop group's out-wire to end on the case tunnel created after it: no plan order expresses it.

## Registration
No edit made: GAP rows are a return condition (brief "Return conditions"). Fact: the `primitive` route reads NO class/terminal table
in either tool - X:442-445 accepts any `prim`, X:3068-3082 checks the read-back label only (X:472-484); S:2298-2349 takes the plan's
declared terminals; the only queue table `QUEUE_TERM_TABLE` (S:1605-1607) is read by `_dequeue_check` for `queue_kind` dequeue only
(S:2296-2297). Rows 2/7 replay with donor-json names without any registration (log:77-78). Self-tests not run (nothing changed).
X17 entries that would be needed (stage_prerun.py:2802, NOT edited): ("DonorQueue_v0.vi",108) Obtain Queue / (44) Enqueue Element /
(45) Dequeue Element / (46) Release Queue, class "Function", md5 81dba822efec5226123b3b88ee4383bc, cite tools/bench/donor_queue_v0.json.

OPEN (154-a2-3, answered by PD376): which route carries the refnum from #4866 into the new True frame (rows 9-10).

# Card 154-a3-1 - refnum forms S and L (PD376(a)(b)(d)), offline, LabVIEW 0
Script `diag_c154_a3_1_census.py` (copy of the a2-3 census); log `diag_c154_a3_1_census.log` (S rows :6-48, L rows :49-87,
P5-2 :91-193, RESULT 6/0) and, after the X17 edit, `diag_c154_a3_1_census_registered.log` (same rows, RESULT 6/0). Rows 9-10
above stay as history. Both forms reuse rows 4-8 and 11-18 unchanged (ROW ok again in both logs, e.g. S :11-37, L :54-80).

## Form S (Obtain + const on 686, refnum SR on 1.2 #10170) - every row OK
| # | row | route (kind) | X file:line | S file:line | proven-by | status |
|---|---|---|---|---|---|---|
| S1 | 1-D DBL const on 686 (DonorQueue_v0 #52) | create primitive (const_donor) | X:442-445, 3068-3082 | S:2298-2349 (log:6-7) | const_donor plan_ring_p4_s02v18.json:342-359 (on #4866) | OK |
| S2 | Obtain Queue on 686 (#108) | create primitive | X:3068-3082 | S:2298-2349 (log:8-9) | ext. donor prim plan_ring_p3a.json:13-41 | OK |
| S3 | const -> Obtain 'element data type' (686) | connect | X:813 | S:1478-1573, how=new (log:10) | plan_ring_p3a.json:381-386 | OK |
| S4 | refnum SR on #10170 (body 23166, parent 686) | add_shift_reg | X:764-765 | S:1289-1310 (log:38) | plan_ring_p3a.json:56-63 (= row 11) | OK |
| S5 | Obtain 'queue out' -> SR L.outer (686) | connect (plain, same diagram) | X:813 | S:1478-1573, how=new (log:39) | none: no plan wires a NODE output into L.outer (only consts, row 12) | OK |
| S6 | SR L.inner -> case tunnel in -> Enqueue 'queue' | connect_term_uid R1 | X:776-787 | S:1313-1349 (log:40-42) | = row 14, plan_ring_p3a.json:244-267 | OK |
| S7 | Enqueue 'queue out' -> case tunnel out -> SR R.inner | connect_term_uid R2 | X:776-787 | S:1313-1349 (log:43-45) | = row 15, plan_ring_p3a.json:268-291 | OK |
| S8 | False frame refnum pass-through | case_frame_wire new_wire | X:800-801, 593-650 | S:1560-1570 (log:46) | = row 16, plan_ring_p3a.json:292-306 | OK |
| S9 | SR R.outer left unwired (P5-2) | - | - | - | - | n/a |
| S10 | compile all S rows | 22 ops: + connect x2, add_sr, connect_term_uid x2, case_frame_wire | X:729-813 | - | (log:47) | OK |

## Form L (Obtain on #4866, refnum indicator + local read) - every row OK
| # | row | route (kind) | X file:line | S file:line | proven-by | status |
|---|---|---|---|---|---|---|
| L1-L3 | const + Obtain + type wire on #4866 | = rows 1-3 | = rows 1-3 | (log:49-53) | = rows 1-3 | OK |
| L4 | indicator 'queue (1.2 to 1.7)' born_on Obtain 'queue out' | create indicator (Nodes[] triple) | X:245-246, 3033-3045 | S:2271-2292 (log:81-82) | node-terminal born_on plan_l2a3.json:22-25 (base node) | OK |
| L5 | local_read 'queue (1.2 to 1.7)' in True frame new:CQ1.f1 | create local_read | X:243, 3015-3024 | S:2298-2349 (log:83-84) | local_read in a FS frame plan_ring_p3b.json:103-121; in a case frame none | OK |
| L6 | local -> Enqueue 'queue' (same frame) | connect | X:813 | S:1478-1573 (log:85) | local_read on #639 plan_l2a3.json:44-60; local -> node wire not checked | OK |
| L7 | compile all L rows | 20 ops | X:729-813 | - | (log:86) | OK |

CHOSEN: S

Rule PD376(b) applied mechanically: every S row OK (log:48 `GAPS S: []`, gate P2 log:88) -> S; L also clean (log:87, gate P3 log:89).

## P5-2 refnum rows - REPORT-ONLY (PD376(d)), they do not change CHOSEN
- S-mirror (log:132-143, `P52 S: all OK`, 29 ops): SR on 1.7 #23041 (body 23405, parent 686) add_sr X:764-765; Obtain 'queue out' ->
  SR L.outer = 2nd branch (S:1491 how=branch, X:813 connect); Dequeue (#45) in #23405 primitive; L.inner -> Dequeue 'queue' wire_sr
  LeftIn X:806-807; Dequeue 'queue out' -> R.inner wire_sr RightIn X:804-805; Release (#46) on 686; R.outer -> Release 'queue' connect
  X:813 (row-18 route). Status OK, no GAP.
- L-mirror (log:179-193, `P52 L: all OK`, 26 ops): local reads in #23405 and on 686 -> Dequeue / Release 'queue'. OK.

## X17 (PD376(c))
`stage_prerun.py:2809-2813` four DonorQueue_v0 entries; census registered run: no refusal for c_obt/c_enq/c_deq/c_rel in either form
(`diag_c154_a3_1_census_registered.log:195,197`); before the edit all four refused UNMEASURED (`diag_c154_a3_1_census.log:194-197`).
