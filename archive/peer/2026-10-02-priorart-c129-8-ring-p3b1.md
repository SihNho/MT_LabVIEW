# priorart-c129-8-ring-p3b1

- **agent:** claude
- **role:** priorart
- **model:** claude-opus-5-5 (effort medium; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $1.2985  in 12 / out 5005 / cache-create 131645 / cache-read 725918  (55s, 15 turn(s))
- **date:** 2026-10-02 02:44:01
- **outcome:** ANSWERED (59s)
- **verdict-card:** VERDICT-CARD priorart-c129-8-ring-p3b1 verdict=novel -> tools\bench\cards\verdict_priorart-c129-8-ring-p3b1.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id priorart-c129-8-ring-p3b1, role priorart) ---
CLAIM: The work under review (new-op) is novel - not already built, measured, refuted or covered by an existing helper in this project's files.
ATTACHMENT: tools\recipes\stage_d1_ring_p3b1.py (md5 5e25813aa1fd889e148e0352506c1922)
ATTACHMENT: docs\user-rules.md (md5 9e0396da1b6fd9227a6e0ca850337cd5)
--- END REVIEW CARD ---

PRIOR-ART REVIEW (trigger: new-op).

You are checking ONE thing: has this already been done here? Do not review the plan's merits -
other reviews do that. Answer in two parts, naming a FILE and LINE for every finding. A finding without a citation
cannot be acted on, because the only way this review is released is by someone opening your citation and showing in
writing that it does not cover their case.

PART A - THE DIRECTION (this is the part that matters most)
 A1 SETTLED ALREADY. Has this direction, or its central question, already been decided or answered in STATUS.md,
    docs/ or archive/? Quote the decision and its date.
 A2 REFUTED ALREADY. Has this direction already been tried, abandoned, or argued against - in an archived peer
    review, a retrospective, or a superseded plan section? Say what killed it and whether that still applies.
 A3 CONTRADICTED. Does any fact the plan cites conflict with something else in these files? Quote BOTH sides. A
    summary line that contradicts its own section 40 lines earlier counts, and has happened here.
 A4 UNREAD EVIDENCE. Which existing document should obviously have been consulted for this direction and clearly
    was not? Name it.

PART B - THE ARTIFACT, if the plan builds or changes one
 B1 ALREADY BUILT. Does an op, recipe, helper or VI already do this, possibly under another name? Check
    tools/gscript.py's functions, tools/recipes/, docs/toolkit-capabilities.md and the claudeDev VI names.
 B2 ALREADY FAILED. Has this exact build been attempted and failed? What did the record say was the cause, and
    does the new plan address that cause or repeat it?
 B3 HELPER EXISTS. Is the plan hand-rolling something the toolkit already provides - indexing, identification,
    wiring, saving, censusing? Name the call.
 B4 ALREADY MEASURED. Has the question this artifact would answer already been measured and written down?

PART C - THE USER'S RULES (card chat-P2, user 2026-09-28; docs/user-rules.md is attached in full below)
 C1 Does this plan contradict any rule in user-rules.md? Name the rule and the plan line. Quote both. A plan that
    puts a queue on a control signal or at the acquisition boundary, lets the camera loop wait, puts serial on the
    frame path, or changes a per-bead number is the kind of contradiction this question exists for. If the plan
    relies on a rule correctly, say nothing about it.

End with machine-readable lines, one per finding:
  PRIOR-ART: settled-already | refuted-already | contradicted | unread-evidence
  PRIOR-ART: already-built | already-failed | helper-exists | already-measured
  PRIOR-ART: user-rule-contradicted
  PRIOR-ART: novel
`novel` only if none apply. Do not invent slugs.

THESE VERDICTS STOP THE WORK. Any slug other than `novel` blocks the next build until someone opens your citation
and refutes it in writing. So be precise about what your citation actually covers: an over-broad match costs real
work, and a missed one costs a whole build cycle.

=== WHAT IS UNDER REVIEW ===
{
 "schema": "stageplan/1",
 "context": {
  "s1_key": "D1_s1_copy"
 },
 "open_rows": [
  {
   "node": 376,
   "term": "current frame data array in",
   "why": "carried from R2 (plan_l2r2_in.json): QRT (PD175)"
  },
  {
   "node": 376,
   "term": "frame index",
   "why": "carried from R2: QRT (PD175)"
  },
  {
   "node": 2626,
   "term": "array",
   "why": "carried from R2: licensed rename (plan_l2b1_licence.json)"
  },
  {
   "node": 2626,
   "term": "element",
   "why": "carried from R2: QRT (PD182(c)/D5)"
  },
  {
   "node": 5058,
   "term": "Image In",
   "why": "carried from R2: QRT (PD177(e))"
  },
  {
   "node": 8634,
   "term": "index (col)",
   "why": "carried from R2: QRT (D5)"
  },
  {
   "node": 11261,
   "term": "array",
   "why": "carried from R2: PD227(d)"
  },
  {
   "node": 11261,
   "term": "element",
   "why": "carried from R2: QRT (D5)"
  },
  {
   "node": 28083,
   "term": "Magnet position",
   "why": "carried from R2: QRT (D5)"
  },
  {
   "node": 29625,
   "term": "index (col)",
   "why": "carried from R2: QRT (D5)"
  },
  {
   "node": 29973,
   "term": "element",
   "why": "carried from R2: QRT (D5)"
  }
 ],
 "stage": "ring_p3b1",
 "goal": "RING P3b-1 (card 129-1 split of plan_ring_p3b_in.json 08fa2241; PD261(d)): FS + f0 Num(i)=-1 + IMAQ Copy + f2 Num(i)=BufNum with the status guard (PD261(a), PD262(b))",
 "base": {
  "path": "tools/bench/graph_ring_p3a_20261001_190155.json",
  "md5": "2fa6ce0c3e8a3014fa916085cb852f68"
 },
 "actions": [
  {
   "op": "wire_remove_loose_ends",
   "id": "p3b_rle_w27378",
   "wire_uid": 27378,
   "why": "ROUTE wire_remove_loose_ends | MEASURED | gscript.py:4972 OpWireRemoveLooseEnds_v0; diag_c126_4_op.log:52-60; diag_c126_6_cross.log:61-65 | PD253(d)/PD255(b) P3a stub w27378 (Error List 55 -> 54)"
  },
  {
   "op": "create",
   "id": "p3b_fs",
   "class": "FlatSequence",
   "as": "FS1",
   "diagram": 27219,
   "pos": [
    200,
    40
   ],
   "why": "ROUTE fs_create | MEASURED | PD246(c) A1 | diag_c125_5_fsscr.log:27 (FS on this same #27219 of a P3a copy)"
  },
  {
   "op": "create",
   "id": "p3b_fr2",
   "class": "FlatSequenceFrame",
   "diagram": "new:FS1.f0",
   "why": "ROUTE fs_frame | MEASURED | PD246(c) A1 | diag_c125_5_fsscr.log:32 (add(0,T) new at 1, add(1,T) new at 2)"
  },
  {
   "op": "create",
   "id": "p3b_fr3",
   "class": "FlatSequenceFrame",
   "diagram": "new:FS1.f1",
   "why": "ROUTE fs_frame | MEASURED | PD246(c) A1 | diag_c125_5_fsscr.log:32 (add(0,T) new at 1, add(1,T) new at 2)"
  },
  {
   "op": "create",
   "id": "p3b_lr_num1",
   "class": "Local",
   "diagram": "new:FS1.f0",
   "as": "LRN1",
   "label": "Num",
   "mode": "read",
   "pos": [
    20,
    220
   ],
   "terminals": [
    {
     "name": "Num",
     "is_source": true,
     "term_class": "Terminal"
    }
   ],
   "why": "ROUTE local_read (create_local_read + move_in) | PRECEDENT | PD246(c) A2 | run on loop body #639 (plan_l2a3_in.json:16); placement in a FS frame never run"
  },
  {
   "op": "create",
   "id": "p3b_ras_num1",
   "class": "GrowableFunction",
   "diagram": "new:FS1.f0",
   "as": "RAN1",
   "pos": [
    120,
    220
   ],
   "prim": "Replace Array Subset",
   "donor": {
    "donor": "$work",
    "uid": 29157
   },
   "terminals": [
    {
     "name": "array",
     "is_source": false,
     "term_class": "Terminal"
    },
    {
     "name": "output array",
     "is_source": true,
     "term_class": "Terminal"
    },
    {
     "name": "index",
     "is_source": false,
     "term_class": "Terminal"
    },
    {
     "name": "new element/subarray",
     "is_source": false,
     "term_class": "Terminal"
    }
   ],
   "why": "ROUTE primitive $work donor #29157 | PRECEDENT | PD246(c) A2 Replace Array Subset | route measured in P3a (stage_d1_ring_p3a.log, Equal?/Increment/Q&R); class GrowableFunction never copied: census UNPREDICTED"
  },
  {
   "op": "create",
   "id": "p3b_k_m1",
   "class": "DigitalNumericConstant",
   "diagram": "new:FS1.f0",
   "as": "KM1",
   "pos": [
    60,
    160
   ],
   "prim": "const_donor",
   "donor": {
    "donor": "C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\DonorRingConst_v0.vi",
    "uid": 249
   },
   "terminals": [
    {
     "name": "",
     "is_source": true,
     "term_class": "Terminal"
    }
   ],
   "why": "ROUTE primitive const_donor | MEASURED | PD238(c) Num(i)=-1 | const in a FS frame: diag_c125_5_fsscr.log:41-47 (C-3a); I32 -1 = DonorRingConst_v0 #249 (PD247(a))"
  },
  {
   "op": "create",
   "id": "p3b_lw_num1",
   "class": "Local",
   "diagram": "new:FS1.f0",
   "as": "LWN1",
   "label": "Num",
   "mode": "write",
   "pos": [
    220,
    220
   ],
   "terminals": [
    {
     "name": "Num",
     "is_source": false,
     "term_class": "Terminal"
    }
   ],
   "why": "ROUTE local_write (create_local_write -> dest diagram) | PRECEDENT | PD246(c) A2 | stagexec.py:206 route; placement in a FS frame never run"
  },
  {
   "op": "create",
   "id": "p3b_ia",
   "class": "IndexArray",
   "diagram": "new:FS1.f1",
   "as": "IA1",
   "pos": [
    120,
    60
   ],
   "prim": "Index Array",
   "donor": {
    "donor": "$work",
    "uid": 3163
   },
   "terminals": [
    {
     "name": "array",
     "is_source": false,
     "term_class": "Terminal"
    },
    {
     "name": "element",
     "is_source": true,
     "term_class": "Terminal"
    },
    {
     "name": "index",
     "is_source": false,
     "term_class": "Terminal"
    }
   ],
   "why": "ROUTE primitive $work donor #3163 | PRECEDENT | PD246(d) Index Array(pool, i) | route as P3a; class IndexArray never copied: census UNPREDICTED"
  },
  {
   "op": "create",
   "id": "p3b_copy",
   "class": "SubVI",
   "diagram": "new:FS1.f1",
   "as": "CP1",
   "pos": [
    160,
    40
   ],
   "subvi_path": "C:\\Program Files\\NI\\LVAddons\\nivision\\1\\vi.lib\\vision\\Management.llb\\IMAQ Copy",
   "terminals": [
    {
     "name": "error in (no error)",
     "is_source": false,
     "term_class": "Terminal"
    },
    {
     "name": "Image Dst",
     "is_source": false,
     "term_class": "Terminal"
    },
    {
     "name": "",
     "is_source": false,
     "term_class": "Terminal"
    },
    {
     "name": "error out",
     "is_source": true,
     "term_class": "Terminal"
    },
    {
     "name": "",
     "is_source": false,
     "term_class": "Terminal"
    },
    {
     "name": "Image Src",
     "is_source": false,
     "term_class": "Terminal"
    },
    {
     "name": "",
     "is_source": false,
     "term_class": "Terminal"
    },
    {
     "name": "Image Dst Out",
     "is_source": true,
     "term_class": "Terminal"
    }
   ],
   "why": "ROUTE subvi (drop_subvi llb member) | PRECEDENT | PD241(d) IMAQ Copy | IMAQ Create llb member in For body (diag_c118_p1b_plan.json:8); path docs/NAMES.md:967"
  },
  {
   "op": "create",
   "id": "p3b_lr_num3",
   "class": "Local",
   "diagram": "new:FS1.f2",
   "as": "LRN3",
   "label": "Num",
   "mode": "read",
   "pos": [
    20,
    320
   ],
   "terminals": [
    {
     "name": "Num",
     "is_source": true,
     "term_class": "Terminal"
    }
   ],
   "why": "ROUTE local_read (create_local_read + move_in) | PRECEDENT | PD246(c) A2 | run on loop body #639 (plan_l2a3_in.json:16); placement in a FS frame never run"
  },
  {
   "op": "create",
   "id": "p3b_ras_num3",
   "class": "GrowableFunction",
   "diagram": "new:FS1.f2",
   "as": "RAN3",
   "pos": [
    120,
    320
   ],
   "prim": "Replace Array Subset",
   "donor": {
    "donor": "$work",
    "uid": 29157
   },
   "terminals": [
    {
     "name": "array",
     "is_source": false,
     "term_class": "Terminal"
    },
    {
     "name": "output array",
     "is_source": true,
     "term_class": "Terminal"
    },
    {
     "name": "index",
     "is_source": false,
     "term_class": "Terminal"
    },
    {
     "name": "new element/subarray",
     "is_source": false,
     "term_class": "Terminal"
    }
   ],
   "why": "ROUTE primitive $work donor #29157 | PRECEDENT | PD246(c) A2 Replace Array Subset | route measured in P3a (stage_d1_ring_p3a.log, Equal?/Increment/Q&R); class GrowableFunction never copied: census UNPREDICTED"
  },
  {
   "op": "create",
   "id": "p3b_lw_num3",
   "class": "Local",
   "diagram": "new:FS1.f2",
   "as": "LWN3",
   "label": "Num",
   "mode": "write",
   "pos": [
    220,
    320
   ],
   "terminals": [
    {
     "name": "Num",
     "is_source": false,
     "term_class": "Terminal"
    }
   ],
   "why": "ROUTE local_write (create_local_write -> dest diagram) | PRECEDENT | PD246(c) A2 | stagexec.py:206 route; placement in a FS frame never run"
  },
  {
   "op": "create",
   "id": "p3b_ub_status",
   "class": "Unbundler",
   "diagram": "new:FS1.f2",
   "as": "UB1",
   "pos": [
    60,
    120
   ],
   "prim": "Unbundle",
   "donor": {
    "donor": "C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\DonorErrSel_ErrToWarning.vi",
    "uid": 157
   },
   "terminals": [
    {
     "name": "cluster",
     "is_source": false,
     "term_class": "Terminal"
    },
    {
     "name": "element",
     "is_source": true,
     "term_class": "Terminal"
    },
    {
     "name": "element",
     "is_source": true,
     "term_class": "Terminal"
    },
    {
     "name": "element",
     "is_source": true,
     "term_class": "Terminal"
    }
   ],
   "why": "ROUTE primitive vilib_donor DonorErrSel_ErrToWarning #157 | MEASURED | PD261(a) guard Unbundle (status) | create_primitive_nested on a claudeDev byte copy, diag_c128_2_donors.log:56-58,83"
  },
  {
   "op": "create",
   "id": "p3b_sel",
   "class": "Function",
   "diagram": "new:FS1.f2",
   "as": "SEL1",
   "pos": [
    120,
    120
   ],
   "prim": "Select",
   "donor": {
    "donor": "C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\DonorErrSel_MergeErrors.vi",
    "uid": 529
   },
   "terminals": [
    {
     "name": "s? t:f",
     "is_source": true,
     "term_class": "ParameterTerminal"
    },
    {
     "name": "f",
     "is_source": false,
     "term_class": "ParameterTerminal"
    },
    {
     "name": "s",
     "is_source": false,
     "term_class": "ParameterTerminal"
    },
    {
     "name": "t",
     "is_source": false,
     "term_class": "ParameterTerminal"
    }
   ],
   "why": "ROUTE primitive vilib_donor DonorErrSel_MergeErrors #529 | MEASURED | PD261(a) guard Select | create_primitive_nested on a claudeDev byte copy, diag_c128_2_donors.log:61-63"
  },
  {
   "op": "create",
   "id": "p3b_k_m3",
   "class": "DigitalNumericConstant",
   "diagram": "new:FS1.f2",
   "as": "KM3",
   "pos": [
    60,
    200
   ],
   "prim": "const_donor",
   "donor": {
    "donor": "C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\DonorRingConst_v0.vi",
    "uid": 249
   },
   "terminals": [
    {
     "name": "",
     "is_source": true,
     "term_class": "Terminal"
    }
   ],
   "why": "ROUTE primitive const_donor | MEASURED | PD238(c) Num(i)=-1 | const in a FS frame: diag_c125_5_fsscr.log:41-47 (C-3a); I32 -1 = DonorRingConst_v0 #249 (PD247(a)) (guard t = -1)"
  },
  {
   "op": "wire",
   "id": "p3b_w_n1_arr",
   "src": "new:LRN1.value",
   "dst": "new:RAN1.array",
   "why": "ROUTE connect same-diagram (connect_nested_v1) | PRECEDENT | PD246(c) A2 frame 1 | same-frame wire, as p3a_w_k20 in case frame 27219; inside a FS frame never run"
  },
  {
   "op": "wire",
   "id": "p3b_w_m1_new",
   "src": "new:KM1.value",
   "dst": "new:RAN1.new element/subarray",
   "why": "ROUTE connect same-diagram (connect_nested_v1) | PRECEDENT | PD238(c) Num(i) = -1 | same-frame wire, as p3a_w_k20 in case frame 27219; inside a FS frame never run"
  },
  {
   "op": "wire",
   "id": "p3b_w_n1_out",
   "src": "new:RAN1.output array",
   "dst": "new:LWN1.value",
   "why": "ROUTE connect same-diagram (connect_nested_v1) | PRECEDENT | PD246(c) A2 frame 1 | same-frame wire, as p3a_w_k20 in case frame 27219; inside a FS frame never run"
  },
  {
   "op": "wire",
   "id": "p3b_w_ia_dst",
   "src": "new:IA1.element",
   "dst": "new:CP1.Image Dst",
   "why": "ROUTE connect same-diagram (connect_nested_v1) | PRECEDENT | PD238(c) IMAQ Copy Dst = Img(i) | same-frame wire, as p3a_w_k20 in case frame 27219; inside a FS frame never run"
  },
  {
   "op": "wire",
   "id": "p3b_w_n3_arr",
   "src": "new:LRN3.value",
   "dst": "new:RAN3.array",
   "why": "ROUTE connect same-diagram (connect_nested_v1) | PRECEDENT | PD254(d) frame 3 second Num read | same-frame wire, as p3a_w_k20 in case frame 27219; inside a FS frame never run"
  },
  {
   "op": "wire",
   "id": "p3b_w_n3_out",
   "src": "new:RAN3.output array",
   "dst": "new:LWN3.value",
   "why": "ROUTE connect same-diagram (connect_nested_v1) | PRECEDENT | PD246(c) A2 frame 3 | same-frame wire, as p3a_w_k20 in case frame 27219; inside a FS frame never run"
  },
  {
   "op": "wire",
   "id": "p3b_w_err_ub",
   "src": "new:CP1.error out",
   "dst": "new:UB1.cluster",
   "why": "ROUTE fs_frame_to_frame (f1 -> f2) | MEASURED | PD258(c) IMAQ Copy error out -> guard | stagesim FS_MEASURED; diag_c128_2_donors.log:80-83"
  },
  {
   "op": "wire",
   "id": "p3b_w_ub_sel",
   "src": "new:UB1.element#0",
   "dst": "new:SEL1.s",
   "why": "ROUTE connect same-diagram (connect_nested_v1) | PRECEDENT | PD262(b) s = status (element#0) | same-frame wire, as p3a_w_k20 in case frame 27219; inside a FS frame never run"
  },
  {
   "op": "wire",
   "id": "p3b_w_m3_sel",
   "src": "new:KM3.value",
   "dst": "new:SEL1.t",
   "why": "ROUTE connect same-diagram (connect_nested_v1) | PRECEDENT | PD261(a) t = -1 | same-frame wire, as p3a_w_k20 in case frame 27219; inside a FS frame never run"
  },
  {
   "op": "wire",
   "id": "p3b_w_sel_n3",
   "src": "new:SEL1.s? t:f",
   "dst": "new:RAN3.new element/subarray",
   "why": "ROUTE connect same-diagram (connect_nested_v1) | PRECEDENT | PD258(c) element = status ? -1 : BufNum | same-frame wire, as p3a_w_k20 in case frame 27219; inside a FS frame never run"
  },
  {
   "op": "wire",
   "id": "p3b_x_i_f1",
   "src": {
    "uid": 27373,
    "term": "x-y*floor(x/y)"
   },
   "dst": "new:RAN1.index",
   "why": "ROUTE connect_term_uid ACROSS FS border (case frame 27219 -> FS f0) | MEASURED | PD246(c)(d) i = count mod 20 | census_samples.json connect_term_uid case_frame_to_fs_frame (diag_c126_4_fs.log:53)"
  },
  {
   "op": "wire_remove_loose_ends",
   "id": "p3b_rle_i_f1",
   "of": "p3b_x_i_f1",
   "why": "ROUTE wire_remove_loose_ends | MEASURED | gscript.py:4972 OpWireRemoveLooseEnds_v0; diag_c126_4_op.log:52-60; diag_c126_6_cross.log:61-65 | PD256(b) every wire of crossing p3b_x_i_f1"
  },
  {
   "op": "wire",
   "id": "p3b_x_i_f3",
   "src": {
    "uid": 27373,
    "term": "x-y*floor(x/y)"
   },
   "dst": "new:RAN3.index",
   "why": "ROUTE connect_term_uid ACROSS FS border (27219 -> f2), source already wired | MEASURED | PD246(c) i | census_samples.json connect_term_uid case_frame_to_fs_frame_branch: a NEW FS outer tunnel per frame (diag_c126_4_fs.log:57)"
  },
  {
   "op": "wire_remove_loose_ends",
   "id": "p3b_rle_i_f3",
   "of": "p3b_x_i_f3",
   "why": "ROUTE wire_remove_loose_ends | MEASURED | gscript.py:4972 OpWireRemoveLooseEnds_v0; diag_c126_4_op.log:52-60; diag_c126_6_cross.log:61-65 | PD256(b) every wire of crossing p3b_x_i_f3"
  },
  {
   "op": "wire",
   "id": "p3b_x_i_ia1",
   "src": {
    "uid": 27373,
    "term": "x-y*floor(x/y)"
   },
   "dst": "new:IA1.index",
   "why": "ROUTE connect_term_uid ACROSS FS border (27219 -> f1), 1st sink of i into f1 | MEASURED | PD246(c) i | census_samples.json connect_term_uid case_frame_to_fs_frame_branch: a NEW FS outer tunnel per frame (diag_c126_4_fs.log:57)"
  },
  {
   "op": "wire_remove_loose_ends",
   "id": "p3b_rle_i_ia1",
   "of": "p3b_x_i_ia1",
   "why": "ROUTE wire_remove_loose_ends | MEASURED | gscript.py:4972 OpWireRemoveLooseEnds_v0; diag_c126_4_op.log:52-60; diag_c126_6_cross.log:61-65 | PD256(b) every wire of crossing p3b_x_i_ia1"
  },
  {
   "op": "wire",
   "id": "p3b_x_bn_n3",
   "src": {
    "uid": 6810,
    "term": "current image number"
   },
   "dst": "new:SEL1.f",
   "why": "ROUTE connect_term_uid ACROSS case border (639 -> 27219) + FS border (-> f2) | MEASURED | PD238(c)/PD258(c) Select f = BufNum; new sink on w3747 only (PD241(d)) | census_samples.json connect_term_uid loop_body_wired_src_to_fs_frame_in_case (diag_c126_6_cross.log:49,60): source net RE-CREATED (PD256(c)) B1 exact"
  },
  {
   "op": "wire_remove_loose_ends",
   "id": "p3b_rle_bn_n3",
   "of": "p3b_x_bn_n3",
   "why": "ROUTE wire_remove_loose_ends | MEASURED | gscript.py:4972 OpWireRemoveLooseEnds_v0; diag_c126_4_op.log:52-60; diag_c126_6_cross.log:61-65 | PD256(b) every wire of crossing p3b_x_bn_n3"
  },
  {
   "op": "wire",
   "id": "p3b_x_img_src",
   "src": {
    "uid": 6810,
    "term": "Image Out"
   },
   "dst": "new:CP1.Image Src",
   "why": "ROUTE connect_term_uid ACROSS case border (639 -> 27219) + FS border (-> f1) | MEASURED | PD241(d) Src = #6810 Image Out t6865 (w3040, 0 sinks) | census_samples.json connect_term_uid loop_body_wired_src_to_fs_frame_in_case (diag_c126_6_cross.log:49,60): source net RE-CREATED (PD256(c)) (same form, other terminal)"
  },
  {
   "op": "wire_remove_loose_ends",
   "id": "p3b_rle_img_src",
   "of": "p3b_x_img_src",
   "why": "ROUTE wire_remove_loose_ends | MEASURED | gscript.py:4972 OpWireRemoveLooseEnds_v0; diag_c126_4_op.log:52-60; diag_c126_6_cross.log:61-65 | PD256(b) every wire of crossing p3b_x_img_src"
  },
  {
   "op": "wire",
   "id": "p3b_x_pool",
   "src": {
    "uid": 23099,
    "term": "New Image"
   },
   "dst": "new:IA1.array",
   "why": "ROUTE connect_term_uid ACROSS For #23093 exit (indexing) + FS2/FS1 + #637 + case + FS | MEASURED | PD241(d)/PD247(b) pool refnums, route nested | census_samples.json connect_term_uid for_body_unwired_src_to_fs_frame_multi_border (diag_c126_6_cross.log:77-78): While tunnel IndexMode 0 B3 exact"
  },
  {
   "op": "wire_remove_loose_ends",
   "id": "p3b_rle_pool",
   "of": "p3b_x_pool",
   "why": "ROUTE wire_remove_loose_ends | MEASURED | gscript.py:4972 OpWireRemoveLooseEnds_v0; diag_c126_4_op.log:52-60; diag_c126_6_cross.log:61-65 | PD256(b) every wire of crossing p3b_x_pool"
  },
  {
   "op": "wire",
   "id": "p3b_x_err_in",
   "src": {
    "uid": 6810,
    "term": "error out"
   },
   "dst": "new:CP1.error in (no error)",
   "why": "ROUTE connect_term_uid ACROSS case border (639 -> 27219) + FS border (-> f1) | MEASURED | PD258(c) Copy runs after #6810, upstream error skips it; #649 kept (PD256(c)) | census_samples.json connect_term_uid loop_body_wired_src_to_fs_frame_in_case (diag_c126_6_cross.log:49,60): source net RE-CREATED (PD256(c)) (same form, error net w653)"
  },
  {
   "op": "wire_remove_loose_ends",
   "id": "p3b_rle_err_in",
   "of": "p3b_x_err_in",
   "why": "ROUTE wire_remove_loose_ends | MEASURED | gscript.py:4972 OpWireRemoveLooseEnds_v0; diag_c126_4_op.log:52-60; diag_c126_6_cross.log:61-65 | PD256(b) every wire of crossing p3b_x_err_in"
  }
 ],
 "final": true,
 "finalized": {
  "base": {
   "path": "tools/bench/graph_ring_p3a_20261001_190155.json",
   "md5": "2fa6ce0c3e8a3014fa916085cb852f68"
  },
  "plan_in": {
   "path": "tools/bench/plan_ring_p3b1_in.json",
   "md5": "0f4f40b27277e6260e35d0ccb0f9ff93"
  },
  "last_step": {
   "path": "tools/bench/sim/ring_p3b1/step_40_wire_remove_loose_ends.json",
   "md5": "a59e434ae8195d1b25e21bde245c0527"
  },
  "summary": {
   "path": "tools/bench/sim/ring_p3b1/summary.json",
   "md5": "a05b650c8cc264aaf43357e2065c9624"
  },
  "end_cdiff_rows": [
   "11261|Terminal|array|0",
   "11261|Terminal|element|0",
   "2626|Terminal|array|0",
   "2626|Terminal|array|1",
   "2626|Terminal|array|2",
   "2626|Terminal|array|3",
   "2626|Terminal|element|0",
   "2626|Terminal|element|1",
   "2626|Terminal|element|2",
   "28083|Terminal|Magnet position|0",
   "29625|Terminal|index (col)|0",
   "29973|Terminal|element|1",
   "376|Terminal|current frame data array in|0",
   "376|Terminal|frame index|0",
   "5058|Terminal|Image In|0",
   "8634|Terminal|index (col)|0"
  ],
  "failed": null,
  "first_divergent": {
   "n": 0,
   "op": "base",
   "id": null,
   "rows_from_here": 16
  },
  "open_rows": [
   [
    376,
    "current frame data array in"
   ],
   [
    376,
    "frame index"
   ],
   [
    2626,
    "array"
   ],
   [
    2626,
    "element"
   ],
   [
    5058,
    "Image In"
   ],
   [
    8634,
    "index (col)"
   ],
   [
    11261,
    "array"
   ],
   [
    11261,
    "element"
   ],
   [
    28083,
    "Magnet position"
   ],
   [
    29625,
    "index (col)"
   ],
   [
    29973,
    "element"
   ]
  ],
  "open_rows_match": true,
  "open_rows_match_legacy": true,
  "open_rows_classed": {
   "ok": false,
   "want": [],
   "c4_n": 0,
   "c4_keys": 0,
   "c4_bad": [],
   "unclassed": [
    [
     376,
     "current frame data array in"
    ],
    [
     376,
     "frame index"
    ],
    [
     2626,
     "array"
    ],
    [
     2626,
     "element"
    ],
    [
     5058,
     "Image In"
    ],
    [
     8634,
     "index (col)"
    ],
    [
     11261,
     "array"
    ],
    [
     11261,
     "element"
    ],
    [
     28083,
     "Magnet position"
    ],
    [
     29625,
     "index (col)"
    ],
    [
     29973,
     "element"
    ]
   ]
  },
  "cdiff_inputs": {
   "labels": "node_labels_default",
   "labels_n": 626,
   "fs_pairs": "state",
   "fs_pairs_n": 576
  },
  "step_files": [
   {
    "n": 0,
    "op": "base",
    "path": "tools/bench/sim/ring_p3b1/step_00_base.json",
    "md5": "9a9bacd1a84aa1550c8fc17c3597f1bb"
   },
   {
    "n": 1,
    "op": "wire_remove_loose_ends",
    "path": "tools/bench/sim/ring_p3b1/step_01_wire_remove_loose_ends.json",
    "md5": "0280f5e1c3a232b9c084226624423506"
   },
   {
    "n": 2,
    "op": "create",
    "path": "tools/bench/sim/ring_p3b1/step_02_create.json",
    "md5": "f45b06423795def0dcfa03511e174186"
   },
   {
    "n": 3,
    "op": "create",
    "path": "tools/bench/sim/ring_p3b1/step_03_create.json",
    "md5": "0af9ffee09b1e1a760a18988f72a269c"
   },
   {
    "n": 4,
    "op": "create",
    "path": "tools/bench/sim/ring_p3b1/step_04_create.json",
    "md5": "9daca50d6fe7c7c667beb374b5dfa5f1"
   },
   {
    "n": 5,
    "op": "create",
    "path": "tools/bench/sim/ring_p3b1/step_05_create.json",
    "md5": "cdb7e6667fafb29fd52e2eb0bf6454c4"
   },
   {
    "n": 6,
    "op": "create",
    "path": "tools/bench/sim/ring_p3b1/step_06_create.json",
    "md5": "69e5c54a46cbf7694dab3f759622e9b6"
   },
   {
    "n": 7,
    "op": "create",
    "path": "tools/bench/sim/ring_p3b1/step_07_create.json",
    "md5": "037863b22186fb7faeb22a96d0ce33ed"
   },
   {
    "n": 8,
    "op": "create",
    "path": "tools/bench/sim/ring_p3b1/step_08_create.json",
    "md5": "529373bc96a580e5772bbf9f4a708c71"
   },
   {
    "n": 9,
    "op": "create",
    "path": "tools/bench/sim/ring_p3b1/step_09_create.json",
    "md5": "60f4138857ca5dfebb8573fbf8eaa9cd"
   },
   {
    "n": 10,
    "op": "create",
    "path": "tools/bench/sim/ring_p3b1/step_10_create.json",
    "md5": "6b517507f0a66e6e175ed578ddcea708"
   },
   {
    "n": 11,
    "op": "create",
    "path": "tools/bench/sim/ring_p3b1/step_11_create.json",
    "md5": "25f8a1e2c4feafb5a29db7e60e407fd1"
   },
   {
    "n": 12,
    "op": "create",
    "path": "tools/bench/sim/ring_p3b1/step_12_create.json",
    "md5": "67597349df2a14f3748b0a29648cd8ed"
   },
   {
    "n": 13,
    "op": "create",
    "path": "tools/bench/sim/ring_p3b1/step_13_create.json",
    "md5": "2c854800d5b531a1d185902b4d5b6904"
   },
   {
    "n": 14,
    "op": "create",
    "path": "tools/bench/sim/ring_p3b1/step_14_create.json",
    "md5": "12c9ea84852c4af493b8eacc8f05b07f"
   },
   {
    "n": 15,
    "op": "create",
    "path": "tools/bench/sim/ring_p3b1/step_15_create.json",
    "md5": "2f6047e911586edaa5e54ec06a16c013"
   },
   {
    "n": 16,
    "op": "create",
    "path": "tools/bench/sim/ring_p3b1/step_16_create.json",
    "md5": "0209f2d2b11e83c58f2b760fc3e9d802"
   },
   {
    "n": 17,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_17_wire.json",
    "md5": "21ddf0c361c2ebd80ed0d23e9d7c0b34"
   },
   {
    "n": 18,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_18_wire.json",
    "md5": "ec8e7498f07a3353914f09b9e7ba8b0f"
   },
   {
    "n": 19,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_19_wire.json",
    "md5": "b10a791d9eca3f17d13b823c351ab770"
   },
   {
    "n": 20,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_20_wire.json",
    "md5": "8321b9a62b0a598bb19aa8c71e0c0694"
   },
   {
    "n": 21,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_21_wire.json",
    "md5": "17ac0ee28738ba42963c5734751828d3"
   },
   {
    "n": 22,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_22_wire.json",
    "md5": "b12df1e62e7fb8fe9df81dd635101139"
   },
   {
    "n": 23,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_23_wire.json",
    "md5": "0e3746dd6bdf3f63b7a149365c64d8b8"
   },
   {
    "n": 24,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_24_wire.json",
    "md5": "fce3dc77831782ce4fde33c1d0f84826"
   },
   {
    "n": 25,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_25_wire.json",
    "md5": "ef22954ec31a5d613f3fbb0477beee61"
   },
   {
    "n": 26,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_26_wire.json",
    "md5": "993fff21a24dd4b7f2a0f94619fb1992"
   },
   {
    "n": 27,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_27_wire.json",
    "md5": "d246e1b46593be452556f7c1f3c2410b"
   },
   {
    "n": 28,
    "op": "wire_remove_loose_ends",
    "path": "tools/bench/sim/ring_p3b1/step_28_wire_remove_loose_ends.json",
    "md5": "5be37278ae53a9cdb055eba34096e455"
   },
   {
    "n": 29,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_29_wire.json",
    "md5": "d82d2101e5c21d45c9ca9cb7a21ccfe7"
   },
   {
    "n": 30,
    "op": "wire_remove_loose_ends",
    "path": "tools/bench/sim/ring_p3b1/step_30_wire_remove_loose_ends.json",
    "md5": "359ab94a2ff6e4b8fbb837c8bb3e63c8"
   },
   {
    "n": 31,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_31_wire.json",
    "md5": "d19522e09b99303531be77c1698f87f4"
   },
   {
    "n": 32,
    "op": "wire_remove_loose_ends",
    "path": "tools/bench/sim/ring_p3b1/step_32_wire_remove_loose_ends.json",
    "md5": "894dce35b1a755be4441423354d0632e"
   },
   {
    "n": 33,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_33_wire.json",
    "md5": "45558e0967d7063438d8a2266a1a6ad5"
   },
   {
    "n": 34,
    "op": "wire_remove_loose_ends",
    "path": "tools/bench/sim/ring_p3b1/step_34_wire_remove_loose_ends.json",
    "md5": "f8e94aef36250c280b8dcb93be158307"
   },
   {
    "n": 35,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_35_wire.json",
    "md5": "9b57c5d7fba76709c4d4be4d61dfffcd"
   },
   {
    "n": 36,
    "op": "wire_remove_loose_ends",
    "path": "tools/bench/sim/ring_p3b1/step_36_wire_remove_loose_ends.json",
    "md5": "aaf383835863c778eb0a6aaf6bb7efd3"
   },
   {
    "n": 37,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_37_wire.json",
    "md5": "6e6bcac49878f89f49c21484361fabbe"
   },
   {
    "n": 38,
    "op": "wire_remove_loose_ends",
    "path": "tools/bench/sim/ring_p3b1/step_38_wire_remove_loose_ends.json",
    "md5": "ec5d87a764082e5322942d803d1af898"
   },
   {
    "n": 39,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3b1/step_39_wire.json",
    "md5": "821df4d8fb00579dddff3c5866372612"
   },
   {
    "n": 40,
    "op": "wire_remove_loose_ends",
    "path": "tools/bench/sim/ring_p3b1/step_40_wire_remove_loose_ends.json",
    "md5": "a59e434ae8195d1b25e21bde245c0527"
   }
  ],
  "undecided": 0,
  "at": "2026-10-02 02:27:10"
 }
}

=== docs/user-rules.md IN FULL (the user's standing design rules; PART C asks about these) ===
---
type: reference
status: current
date: 2026-09-28
tags: [user-rules, design-check, prior-art, card-chat-P2]
---
# The user's standing DESIGN rules ??every new design is checked against this list before it is built

Card chat-P2 item 1 (user 2026-09-28 17:xx, "洹몃젃寃?1~4踰??곸슜?섏뿬 ?섏젙?섎㈃ ?섍쿋??). The largest single loss in cycles
84??20 was not a bad build but a design direction (the image pool with `Q_free`/`Q_work` queues, PD233??37) that
contradicted rules the user had already given; nobody compared the plan with them before building. This file is that
comparison's input. Every row is the user's own words, dated, with where it was recorded.

How it is used (mechanical):
- `tools/prior_art_review.py` attaches this file to EVERY prior-art dispatch and asks one fixed question: *does this
  plan contradict any rule in user-rules.md? Name the rule and the plan line.* A contradiction is the verdict
  `PRIOR-ART: user-rule-contradicted` ??a non-`novel` verdict, released only by the usual `REFUTED:` / `FIXED:` lines.
- A judgement session that writes a new Pre-decided DESIGN item reads this file first and puts a `USER-RULES:` line in
  the item (the rule ids it relies on, or `USER-RULES: none apply`); `tools/doc_lint.py` L9 warns when a Pre-decided
  item numbered 238 or later lacks one.
- A row is added only from a user statement (quote + date + source). A row is never re-worded; a later user statement
  that changes a rule is a NEW row that names the row it supersedes.

| id | rule (one line) | the user's words (verbatim) | date | source |
|---|---|---|---|---|
| U1 | The original's computation (per-bead maths, its parameters, its numbers) never changes; only scheduling may. | "?먮낯???곗궛諛⑸쾿 ?먯껜瑜?諛붽씀硫??덈뤌. ?닿굔 瑗?紐낆떖?섍퀬." 쨌 "?대?吏瑜?遺꾩꽍?댁꽌 ?섏튂?뷀븯??紐⑤뜽怨?洹??곗궛 諛⑸쾿 諛?寃곌낵媛 諛붾뚮㈃ ?덈맂?ㅻ뒗 留먯씠吏." | 2026-08-30 | CLAUDE.md:25-37 (rule 1a); memory preserve_the_original_computation.md |
| U2 | Hardware access follows the rig state (disassembled / assembled / experiment running); the ASI is a motor like any other. | "紐⑦꽣 ?묎렐 諛?移대찓???묎렐??'由ш렇 遺꾪빐 / 由ш렇 議곕┰ / ?ㅽ뿕以? ?곹깭???곕씪 ?ㅻⅤ寃??먮뒗寃?留욌뒗?? ???대뒗 Piezo stage??ASI 而⑦듃濡ㅻ윭瑜??ы븿?섎뒗 ?댁슜 (ASI? ?ㅻⅨ 紐⑦꽣瑜?援щ텇?섏뿬 沅뚰븳 ?먯? 留먭쾬)." | 2026-09-16 | CLAUDE.md:39-44 (rule 1b) |
| U3 | No VISA/serial call anywhere on the frame acquisition path; serial lives in its own loop with a non-blocking handoff. | "I don't want to have even a single frame loss coming from the motor communication if possible. And it is so clear that serial communication through VISA can somehow stall the loop, and cause unwanted frame stop." | 2026-09-16 | CLAUDE.md:89-100 (rule 1c); memory no_serial_on_the_frame_path.md |
| U4 | Loop-to-loop CONTROL signals go by local variable (latest value), never by queue; queues only for lossless data streams. | "?먮? ?ｌ뼱踰꾨┛?ㅻ㈃ ??猷⑦봽 ?ъ씠???곴?愿怨꾧? ?앷꺼踰꾨┛?ㅻ뒗 寃?媛숈??? 洹몃윴 由ъ뒪?щ? 媛먮떦???꾩슂媛 ?덈뒗吏 紐⑤Ⅴ寃좎쓬. 洹몃깷 Boolean 媛?諛??寃?媛믪쓣 local variable濡??꾨떖?섎뒗寃???醫뗭? ?딆쓣吏?" | 2026-09-25 | CLAUDE.md:102-124 (rule 1c''); memory locals_not_queues_focus_loop_own_clock.md |
| U5 | The ASI autofocus loop runs on its own clock, not in step with frame acquisition. | "ASI autofocus 猷⑦봽???좎큹??frame acquisition 猷⑦봽? ?숈떆?????꾩슂媛 ?놁쓣??" | 2026-09-25 | CLAUDE.md:102-124 (rule 1c''); memory locals_not_queues_focus_loop_own_clock.md |
| U6 | The camera free-runs; nothing we build may throttle, block or pace acquisition (the PC is a reader, never a gate). | "移대찓?쇰뒗 湲곕낯?곸쑝濡??먯떊??猷⑦봽瑜?而댄벂?곗? ?낅┰?곸쑝濡??뚯븘???섎ŉ 洹몃젃寃??뚭퀬 ?덉쓬. 而댄벂?곕? ?듯븳 移대찓???꾨젅??而⑦듃濡ㅼ쓣 ?좊ː?????녾린 ?뚮Ц?? ?곕씪??Lossy Enqueue Element ?뱀? 湲고? ?ㅻⅨ ?대뼚??諛⑸쾿??移대찓??frame acquisition???곹뼢??二쇱뼱?쒕뒗 ?덈맖." | 2026-09-15 | docs/decisions.md:21; memory camera_free_runs_never_gate_it.md |
| U7 | The buffer number is the time axis (frame N happened at N/framerate); never a software timestamp. | "?쒓컙 媛꾧꺽? 而댄벂??猷⑦봽???蹂꾧컻濡??꾨젅?꾩씠 媛숇떎硫??숈씪?? 移대찓??猷⑦봽??acquisition ?뺣낫??frame rate??蹂꾨룄???섎뱶?⑥뼱濡??듭젣?섍린 ?뚮Ц. 洹몃윭???곗씠???꾨떖?먯꽌 ?앷린???쒓컙 遺덇퇏?쇱? ?ш쾶 以묒슂?섏? ?딆쓬." | 2026-09-15 | docs/decisions.md:24; memory camera_free_runs_never_gate_it.md |
| U8 | Overload, acquisition ??tracking: discard the backlog and take the newest frame (latest-wins). | "?먮? 踰꾨━怨??덈줈 ?ㅼ뼱?ㅻ뒗 ?꾨젅?꾩쓣 ?쎈뒗 寃껋씠 媛??諛붾엺吏곹븿. ?대뒗 ?쒓퀎???곗씠?곗쓽 ?꾨??깆쓣 ?꾪븿." | 2026-09-15 | docs/decisions.md:25; memory prefer_the_freshest_frame_over_a_complete_backlog.md |
| U9 | No corruption: image memory and its buffer number change together and the consumer verifies them; a gap is fine, a mismatched pair is corruption. | "留뚯빟 buffer number 媛깆떊???대젮???곹솴?몃뜲 IMAQ 硫붾え由щ쭔 諛붾뚯뿀???쇨퀬 ?쒕떎硫??뺣쭚 ?곗씠??而ㅻ읇?섏쑝濡?遊먯빞?좊벏." | 2026-09-15 | docs/decisions.md:27; memory prefer_the_freshest_frame_over_a_complete_backlog.md |
| U10 | Authorised fallback: acquisition and tracking may stay in ONE sequential loop if the handoff cannot be made provably safe. | "2踰덉씠 臾몄젣媛 ?쒕떎硫?Acquisition 諛?異붿쟻? ?숈씪 猷⑦봽???먭퀬 ?쒗??泥섎━瑜??섎뒗 寃껊룄 愿쒖갖??寃?媛숈쓬." | 2026-09-15 | docs/decisions.md:31; memory prefer_the_freshest_frame_over_a_complete_backlog.md |
| U11 | Frame rules have a PRIORITY ORDER: (1) no corruption, (2) latest-wins, (3) the sequential fallback. Search these rows before asking the user a frame question. | "?꾩뿉 ?꾨젅??愿?⑦빐?쒕뒗 ?닿? 留먰븳 ?댁슜???덉쓬. ?ㅼ떆 李얠븘遊? ?곗꽑?쒖쐞媛 ?덈뒗?? | 2026-09-28 | memory prefer_the_freshest_frame_over_a_complete_backlog.md |
| U12 | Pure-display indicators (plots) are drawn by a SEPARATE display loop on its own clock, fed by local variables; never an every-N-frames gate inside the frame loop. | "洹몃옒???뚮’ 湲곕뒫???뱀떆 蹂꾨룄 猷⑦봽濡??먮뒗 寃껋? ?대뼡吏? 濡쒖뺄 蹂?섏뿉 ?곗씠?곕뱾? ???낅젰?섍퀬 ?곗씠???뚮’? 蹂꾨룄 猷⑦봽濡? ??"?대?濡?吏꾪뻾" | 2026-09-26 | memory display_in_separate_loop_fed_by_locals.md; docs/d1-loop12-17-split-plan.md Pre-decided 210 |
| U13 | Frame handoff 1.1 ??1.2 is a RING BUFFER of 20 IMAQ slots (slot = camera loop counter mod 20), seqlock per slot, no `Q_free`/`Q_work` queues; on overwrite jump to the newest slot; slot numbers come from the camera loop. Supersedes the pool-queue design (PD233??37) and cancels the "option C" rollback. | "1踰?吏?곸? ?뚮???遺遺?/ 2踰????뱀젙 ?꾨젅?꾩? ?볦퀜踰꾨┫ ?섎룄 ?덉쑝?덇퉴 / 3踰???踰꾪띁濡?20 ?꾨젅?꾩씠 ?덉뼱??臾몄젣媛 ?앷릿?ㅻ㈃ 理쒖떊 移몄쑝濡??吏곸씠?붽쾶 留욎쓬 / 4踰???移?踰덊샇??移대찓??猷⑦봽瑜????섎컰???놁? ?딅굹?" | 2026-09-28 16:3x | docs/ring-buffer-design.md:10-38 |

## Reading the rows together (what a reviewer checks first)

- A **queue** between two of our loops is allowed only for a lossless DATA stream (tracking ??file writer). A queue that
  carries a control signal (U4) or sits at the acquisition boundary (U6, U13) contradicts the rules.
- Anything whose failure mode is "the camera loop waits" contradicts U6; anything that can put serial on the frame path
  contradicts U3; anything that changes a per-bead number contradicts U1.
- A frame-handling design must say how it meets U9 (pair verified), then U8 (latest-wins), then U13 (ring + seqlock) ??
  in that order (U11).


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-20
tags: [hand-off]
---
STOP ??CHAT 2026-10-02 ~02:1x for the user's approved doc reorganisation ("臾몄꽌 ?뺣━???꾩껜 ???대젃寃??섍퀬 ?쒕쾲 ?뚯뒪?명빐蹂댁옄"): graceful ??cycle 129 finishes, the runner exits, the chat runs card chat-D1 (freeze long docs in place + short index + per-topic decision files + doc_lint line cap), then removes this line and relaunches; cycle 130 is the test. Not a rig/experiment stop.
??STARTED ??USER 2026-10-01 (chat): "?꾩옱??由ш렇 ?ъ슜?섏? ?딆쓬. 洹몃?濡?肄붾뵫 ?몄씠???뚮━?꾨줉" (rig 議곕┰; the user's LabVIEW was closed by the user first; runner relaunched by the chat via runner_supervisor; first act = ## NEXT). The user may announce ?ㅽ뿕以?tonight ??then write a STOP line here (graceful).
(history) The superseded top banner lines (STOP/START/REDIRECT markers 2026-09-26 .. 2026-09-28, all lifted or superseded) RELOCATED VERBATIM (rule 4, card 123-6) ??`archive/2026-10-01-status-cycle123-relocate.md` 짠1
?뱦 **NEW CHAT? Read `docs/chat-handoff.md` right after this file** (2026-09-28 19:4x): the chat's duties (30-min usage ??`run_mode.py write`, report_gate acks, the tick), today's decisions, and the OPEN proposals awaiting the user.

# STATUS ??read this first. One screen. Detail is one layer down, never appended here. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this. Narrative ??**`archive/2026-09-19-status-cycle47-relocate.md` (latest ??T2's block diff and what it closes, the readable-ORIGINAL correction, the five killed retrospectives)** + `archive/2026-09-19-status-cycle39-judgement.md` + `archive/2026-09-18-status-cycle34-n1.md` + `??cycle23-close.md` + the `archive/2026-09-1[678]-status-*.md` set.
?뵷 **The DELIVERED line (display-loop VI ACCEPTED functionally in cycle 110; D1 S1/S2/S3/S3a/S3b artefacts) and the superseded bed narratives (L2-A3 back to M3a-3b row D) RELOCATED VERBATIM ??`archive/2026-10-01-status-cycle123-relocate.md` 짠2.** The live bed is the `current-bed:` key in ## NEXT.
?넅 **USER RULE 17:5x = `docs/cycle27-plan.md` Pre-decided 9 ??EVERY GUI action is capture ??locate ??act ??capture ??confirm; derived or remembered coordinates are NEVER clicked blind.** It turned v4's 13/3 into v5's 39/1.


## START HERE
1. **Cycle plan = `docs/cycle27-plan.md`** (cycle20/21 plans `superseded`; motor plan `docs/motor-limit-assurance-plan.md` **짠A.1 + "P2 live findings"**; master `docs/pre-rig-master-plan.md`; decisions `docs/decisions.md`; D1 `docs/d1-route-b-plan.md`, paused).
2. ?뵶 **NEVER patch a file with a `py - <<'EOF'` heredoc** ??one truncated **this file to 0 bytes** on 2026-09-17.
3. ?좑툘 `peer.ps1` only as `powershell -Command "& 'tools/peer.ps1' ??-TaskFile <f>"`, `-TimeoutSec >= 780`. ?넅 **2026-09-18 (user, TRIAL): codex's roles ??claude roles** ??failed prediction = `-Agent claude -Role hypothesis` SINGLE arm (`-Dual` only for a second opinion on our own tools); `-Kind fact`/`-Kind prose` with no `-Agent` ??fable/low thin; `outcome_review.py` ??fable/medium thin. Check routing free with `-DryRun`.
4. Six more operating hints (prior-art log naming 쨌 front panel open for edits 쨌 `guard_cycle`'s `FIXED:` release 쨌 `py_compile` tripping BUILD_RE 쨌 짠11u unsound 쨌 짠10 not authorised): **`archive/2026-09-18-status-cycle1-census.md` 짠1**. ?좑툘 `BUILD_RE` also fires on a plain `cp a.py tools/recipes/b.py` ??quote both paths (cycle23-close 짠3).

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  relocated_c81: lock keys owner_c74m8s3/owner_c74m8/owner_c73l7r/owner_c72ff/relocated_c72/owner_step6/owner_step5b2/owner_step5b/owner_step4b/owner_step4/step4_delivered/owner/v1_delivered/purpose/step3_delivered/owner_s1s2/purpose_step1_delivered/purpose_s2_delivered/known_limit_s3/purpose_s1s2/relocated_c68 RELOCATED VERBATIM -> `archive/2026-09-25-status-cycle81-relocate.md` 짠1
```
?뵷 **THE WHOLE CHAINED `purpose:` NARRATIVE ("PREVIOUS PURPOSE, unchanged and still true ????, cycles up to 64, 12,560 bytes on one line) RELOCATED VERBATIM (rule 4) ??`archive/2026-09-22-status-cycle64-locknotes.md` 짠1** ??nothing deleted, nothing rewritten; the `purpose:` key above now states only the CURRENT state.
?뵷 **ALL 50 HISTORICAL LOCK-BLOCK ENTRIES (cycles 48??7: 48 `owner_*`/`lock_*` keys, the superseded `status:` line, and the `motor:` key) RELOCATED VERBATIM (rule 4) ??`archive/2026-09-21-status-cycle67-locknotes.md` 짠1** ??that file also carries the three older `lock_relocated_*` pointers (into `??cycle5556-relocate.md`, `??cycle54-relocate.md`, `??cycle5153-relocate.md`, `??cycle49-relocate.md`, `??cycle48-lockkeys.md`). **Motor state, unchanged and still true:** limits LEFT ON since 2026-09-18 15:37 (PI TMN 0 / TMX 39 in RAM, ASI SL/SU 짹2 mm), ports closed. ?좑툘 The motor clause quoted in this line is HISTORICAL; the live motor state is the rig-state line below.
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.

## HARDWARE ??permission follows the RIG STATE. Current: **議곕┰ / ASSEMBLED, not in use** (user 2026-10-01 "?꾩옱??由ш렇 ?ъ슜?섏? ?딆쓬"; machine key `rig-state:` below; ?ㅽ뿕以?2026-09-29 ??10-01 ended)
遺꾪빐 = motors ??ASI ??camera ??쨌 **議곕┰ ??WE ARE HERE (user 2026-09-23 14:2x "?ㅽ뿕 留덉묠")** = camera ?? motors/ASI ONLY through `tools/motor_gate.py` inside the envelope, LabVIEW allowed 쨌 ?ㅽ뿕以?= ??????and no LabVIEW use (was the state 12:3x??4:2x; header corrected 2026-09-23 23:4x by the cycle-68 material session). ?좑툘 ASI carve-out **RETIRED** (rule 1b); **only the user announces a state change**.
Rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??the acquisition loop applies `tools/bench/camera_contract.py`. **No beads on the rig.**
?넅 **SAFE MOTION ENVELOPE = THE CONTROLLER LIMITS + the gate's command-class denies** (user, 2026-09-18 15:2x at the
rig). PI `SPA 1 0x15/0x30` ??TMN 0 / TMX 39 (RAM, **never WPA**) 쨌 **PI DIRECTION (user 2026-09-27 18:2x, at the rig): 0 mm = CEILING (magnet farthest from the sample, = the negative limit switch `FNL` goes to); larger mm = DOWN, toward the sample** ??so a reference move is the safe direction and any "magnet is low" report means a LARGE mm value 쨌 ASI `SL/SU` absolute mm X ??.8475??.1525, Y ??.7744?╈닋0.7744 (persistent, **never SS Z**),
written+verified by `py tools/motor_gate.py --session start|end` from the user-editable `tools/bench/motor_limits.json`; `--execute` refuses without the session file (tools/bench/motor_session.json, present ONLY while a session is open) **and** a fresh matching readback.
The gate still refuses ?ㅽ뿕以? every ASI home/zero/save, PI GOH/FRF/DFH/RON/POS/SPA/WPA and all rotor motion (self-test `selftest_motor_gate2.py` 85/85, 2026-09-24; FAIL-exit self-test 10/10).
rig-state: 議곕┰   <!-- 2026-10-01 USER (chat): "?꾩옱??由ш렇 ?ъ슜?섏? ?딆쓬. 洹몃?濡?肄붾뵫 ?몄씠???뚮━?꾨줉. ?꾨쭏 ?ㅻ뒛 諛ㅼ젙???ъ슜?좎???紐⑤Ⅴ寃좊뒗?? 洹??뚮뒗 ?닿? ?ъ쟾??留먰븯?꾨줉 ?섍쿋??" ??back to 議곕┰: LabVIEW allowed, motors/ASI only through motor_gate inside the envelope under the 2026-09-24 grant (reference + limits verified), LabVIEW closed at every cycle end. The user will announce the next ?ㅽ뿕以?in advance (possibly tonight) ??graceful runner stop. Previous: ?ㅽ뿕以???2026-09-29 USER (chat): "怨??ㅽ뿕 ?쒖옉 ?덉젙?대씪 LabVIEW???ъ슜?섎㈃ ?덈맖. 洹??꾩뿉 ?⑸럭 臾닿??섍쾶 泥섎━ 媛?ν븳 ?꾨줈?몄뒪媛 ?덈떎硫??숈떆 吏꾪뻾?섎뒗嫄?愿쒖갖?꾨벏" ??no LabVIEW, no camera, no motor/ASI; offline (LabVIEW-free) work only. Runner stays stopped. Motor limits were already released at cycle 121 end. Previous: 議곕┰ ??2026-09-24 20:xx USER GRANT: "?밸텇媛??닿? 留먰븯湲??꾧퉴吏??紐⑦꽣 ?묒냽 ?덉슜?? ?ㅻ쭔 ?먯젏 ?뺤씤 諛?紐⑦꽣 由щ컠, ??媛吏??瑗??뺤씤 ?꾩슂" ??motors (PI, rotor, ASI) may be driven by the gate AND by a running main VI while the rig stays assembled, until the user withdraws it; PI reference + verify at session start and limits set/released with readback are never skipped; "?ъ씠??醫낅즺?섍퀬?쒕뒗 ?쒕?濡?LabVIEW ?꾨뒗寃??딆? 留먭쾬 (?뱁엳 移대찓?쇨? 怨꾩냽 Acquisition ?섎㈃ 湲곌퀎??醫뗭? ?딆쑝??" = runner end hook closes LabVIEW and verifies the process is gone. Earlier: 2026-09-23 14:2x user: "?ㅽ뿕 留덉묠. ?ㅼ떆 ?몄뀡 ?ㅼ뼱媛??臾닿??? ??rig stays assembled; motors/ASI only through motor_gate inside the envelope, LabVIEW allowed. Before: ?ㅽ뿕以?13:43 ("吏湲??ㅽ뿕以묒씠??) ??limits RELEASED and read back (PI 0..52, ASI 짹500, `tools/bench/motor_session_end_20260923c.log`), PI referenced at 0 (FNL, 13:36), servo on; no motor/ASI/camera/LabVIEW use until the user says otherwise. Earlier 13:3x, on the user's order ("?덇? ?쒕쾲 PI 紐⑦꽣 ?吏곸뿬蹂쇰옒? 0?쇰줈 ?대룞, 5珥??뺤?, 30?쇰줈 ?대룞, 5珥??뺤?, 0?쇰줈 ?대룞"): PI test moves through the gate to diagnose "PI doesn't respond to the main VI". Before that: ?ㅽ뿕以? restored 2026-09-23 13:11 after ONE `motor_gate.py --session end` on the user's order ("寃뚯씠?몃줈 ?댁쨾"): limits RELEASED and read back ??PI TMN 0 / TMX 52, ASI SL/SU 짹500 mm, position unchanged (`tools/bench/motor_session_end_20260923.log`). Set ?ㅽ뿕以?2026-09-23 12:3x on the user's words ("?닿? 怨??ㅽ뿕???쒖옉?섎땲 ??LabVIEW ?쒖슜? ?섏? 留먮룄濡?) ??no motor, no ASI, no camera, and NO LabVIEW use at all until the user announces otherwise. Previous: 議곕┰, set 2026-09-17 23:0x on the user's words ("?ㅽ뿕 1李⑤줈 ?앸궗?붾뜲, 由ш렇???좎??섎뒗 以? + "議곕┰ ?곹깭?먯꽌????踰붿쐞 ?덉씠硫?紐⑦꽣 ?덉슜??) 쨌 the gate's ONE machine-readable key, parsed by motor_gate.rig_state(); ONLY the user's announcement may set it to 遺꾪빐 / 議곕┰ / ?ㅽ뿕以? Keep it at the start of the line, unquoted. -->

## Where things stand ??the three ??lines VERBATIM in `archive/2026-09-18-status-cycle36-relocate.md` 짠4
??tunnel ops BUILT + FUNCTIONALLY VERIFIED (38/38, ?좑툘 **do NOT re-run the recipe, run 1 is the record**) 쨌 ??the "ZERO runnable experimental VIs" gap is BROKEN ??`tools/bench/drive_original_copy_v5.py` drives a plain copy of the original unattended end to end, twice 쨌 ??N1 accepted ??the GPU kernel is cleared for D1. **Order is D0 ??D1 ??D2** (`docs/cycle27-plan.md` Pre-decided 1). Prose VERBATIM ??`archive/2026-09-21-status-cycle67-locknotes.md` 짠3; earlier ??`archive/2026-09-18-status-cycle22-close.md` 짠2.

## OPEN ??**items 1??0 VERBATIM in `archive/2026-09-17-status-runner-build.md` 짠2**; the five CLOSED items (32 쨌 55 쨌 56 쨌 51/52/52a 쨌 53's mechanical half) VERBATIM in `archive/2026-09-19-status-cycle46-relocate.md` 짠5, which forwards to `??026-09-18-status-cycle36-relocate.md` 짠5?벬?. ?좑툘 Two riders survive there: 32 is NOT to be closed unilaterally (the next outcome review judges it), and `audit_cycle` C4 still understates spend (retrospective-cycle31 F4). Only the live items below.
38/39/41. ?윞 **LIVE PART ONLY: `SR_QUEUE_AUTHORISED` stays False for good; `TEMP_SINK_AUTHORISED` is True for the `Z/dZ` row only** (Pre-decided 13 + 13a), and `Z/dZ` is now MEASURED WIRED (Pre-decided 19). `VI.Get Errors` 452 NOT built and `docs/d1-route-b-plan.md` 짠10 NOT AUTHORISED. ??the stall-watchdog liveness item is CLOSED by cycle 40's repair. Full text + run-3 history ??`archive/2026-09-19-status-cycle40-close.md` 짠2.
53. ?뵶 **The JUDGEMENT half STAYS OPEN, both review arms:** `POS` only declares the present location to be a coordinate and PI's `0x15/0x30` are relative to that zero, so **nothing we can read proves the controller zero still equals the ORIGINAL physical zero** ??i.e. that 0??9 still fences the intended physical window. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠9; dispositions `archive/peer/2026-09-18-pi-err5-unreferenced-{codex,opus}.md`.
54. ?뵶 **TWO RULES YOU MUST FOLLOW, reasoning relocated ??`archive/2026-09-19-status-cycle40-close.md` 짠3.** (a) **The retrospective is the LAST thing a session runs** ??`guard_bash.py:226-227` marks the session retro-done on ANY `retrospective.py` in command position, and `guard_session` then refuses every later dispatch; nothing clears the mark. (b) **Dispatch in the FOREGROUND and wait; when something must run in the background, HOLD THE TURN OPEN until it lands** ??a `claude -p` session cannot take results as they arrive, and ending the turn kills the child. Repair named, deliberately NOT BUILT.
42/43/46/47. ?윞 **LIVE PART ONLY** ??42 ?좑툘 undisposed reviews + `audit_cycle` A2/A3 SELF-REFERENTIAL, not fixed (?좑툘 A4 counts a whole DAY, so it charges the previous cycle's files to this one ??retrospective-cycle40 F4) 쨌 46 ??**CLOSED 2026-09-23 ??FALSE PREMISE**: `SetCommand_signed.vi` IS on disk (`claudeDev\SetCommand_signed.vi`, md5 `ec87a265??, hardware-verified 2026-09-14); the "no disk" claim was a search-scope artefact. The real remaining item is the stage-2 repoint of the nine rotor call sites (Pre-decided 133) 쨌 **47 ?뵶 JUDGEMENT: the audit A1/A2/A3 remedy is NOT a `logclass` entry.** 43 and 48/48a/49/50 ??CLOSED. Full text ??`archive/2026-09-19-status-cycle40-close.md` 짠4.
57. ?윞 **NEEDS JUDGEMENT RATIFICATION (cycle 68, material):** `guard_peer.py` now (a) formats its refusal through a drive-safe `_rel()` ??the same helper `guard_cycle.py:518` has carried since 2026-09-17; without it the hook RAISED instead of refusing when the failing log sat on another drive (`tools/bench/jev_discharge.log:21-26`, rc=99) ??and (b) skips a failing log whose LAST `BGRUN START` command is a **Jev script**, the other half of the user's 2026-09-22 "Jev??硫댁젣" exemption (until now wired only into `RUNNER_RE`, the COMMAND side, so a Jev self-test bundle's fixture text ??`STOP:`/`FAIL` by construction ??armed the gate against every other run). Scoped by the COMMAND, never the filename. Self-test `tools/bench/selftest_guard_peer_jev.py` **17 pass / 0 fail**, two new cases: C7 (a newer Jev log does not become the blocking log) and C7b (a non-Jev build that merely MENTIONS a Jev script still gates).
58. ?윞 **FOR THE USER ??three known limits of the new autofocus loop (loop 1.5) in `D1_s3_loop15.vi`** (decision: `docs/connectivity-map-plan.md` Pre-decided 147(b)). The new loop starts an autofocus when the "focus now" signal switches from off to on. (1) If **Frame rate** is set to 1 the signal is on every frame, so the new loop focuses once instead of every frame. (2) If you run the VI again without reopening it, the first autofocus can be skipped when the previous run stopped on a focus frame. (3) If loop 1.5 falls more than one frame (~11 ms) behind, that one scheduled autofocus is skipped; focus values are not saved data. Tell us if any of these matters for your experiments.

## NEXT
?뵷 **PARALLELISM RULE (user 2026-09-28 19:3x, "洹멸쾶 醫뗪쿋?? 洹몃젃寃?吏꾪뻾?섏옄"):** keep at most 2 live cards (1 LabVIEW build + 1 offline). The offline slot takes ONLY work that cannot be changed by the ring-buffer outcome: the next ring step's prep, FACT CENSUS OF THE ORIGINAL VI (motor / display / scheduler / focus nodes and wires ??the original never changes), and tool/test debt. NO design of the display, motor, scheduler, focus or GPU tracks until the ring buffer (P2?밣6) is done ??they all take the ring's final shape as input (user: "???몄씠?댁쓣 留덉낀?????ㅼ쓬 ?몄씠?댁뿉 蹂?숈씠 ?앷린???쇱씠?쇨퀬 ?섎㈃, 蹂묐젹???덈릺??嫄곗옏??). After P6: ONE interface-contract step (every loop's published/read locals: names, types, writer, cadence; checked against docs/user-rules.md), then the remaining tracks may be designed in parallel. **How (user 2026-09-28 19:4x, "寃곌뎅 怨꾪쉷??議곗쑉?섍퀬 ?뺤젙?섎뒗嫄??먮떒 ?몄뀡??吏꾪뻾?댁빞??):** parallel track sessions only PROPOSE ??each writes its changes (original nodes touched, target loop, locals created with name/type, contract values read) to ONE shared change ledger; a script checks conflicts mechanically; a combined offline stagesim runs all proposals in build order on one graph; the JUDGEMENT session alone reconciles conflicts, fixes the build order and finalises the plan in the plan document. Track sessions never negotiate or decide with each other directly. Ledger format + conflict checker are built in the interface-contract step.
?윟?윟 **FIRST ACT of cycle 129 = build ring step P3b-1 ??`docs/d1-loop12-17-split-plan.md` Pre-decided 263(b) (read 261??63).** Pipeline:
   - Card 1 (offline, first): split `tools/bench/plan_ring_p3b_in.json` (md5 `08fa2241??, 70 actions, replays end to end) into `plan_ring_p3b1.json` / `plan_ring_p3b2.json`, each ??40 actions (user D-2026-10-01-01 = ANSWERED option 1), dependency-closed, IMAQ Copy + the U9 guard (Unbundler `element#0` ??Select) in the same half, RLE rows with their loose ends; finalize, predictions, recipes `stage_d1_ring_p3b1.py`/`_p3b2.py`; dry + prerun OUT OF PROCESS; `--scratch-required`; prior-art for P3b-1 (new classes Unbundler, Select). Also: c106e E1 rerun listing every FAIL line, then drain fp-19. ?좑툘 `plan_ring_p3b.json` (4003eaa5), its `_pred` and `stage_d1_ring_p3b.py` are STALE ??never launch them.
   - Card 2 (LabVIEW, after card 1 PASS): P3b-1 FULL scratch run on a P3a byte copy (prediction: Unbundler's bound output reads back `status` after its wire), ONE Error List read, then ONE launch ??`claudeDev\D1_ring_p3b1_*.vi`. Broken-file count becomes 3 of 6; P3b-2, P4, P5 then use 4?? and P6 must RUN (no slack for another split without asking the user, PD261(d)).
- **CYCLE 128 in brief ??the guard's creation route found; the P3b plan with the guard replays end to end; no new VI:**
  - 128-2 FAIL 46/1 (LabVIEW): `Select` and `Unbundle` donors EXIST in shipped error VIs (127-5's "none" was a search typo, review `archive/peer/2026-10-02-c128-2-errsel-donor.md`); form C1 (error out ??Unbundler ??Select ??/BufNum) wired with 5 unbroken wires. Donor copies `claudeDev\DonorErrSel_ErrToWarning.vi` (uid 157) / `DonorErrSel_MergeErrors.vi` (uid 529). Decided PD261(a).
  - 128-1 FAIL 7/1 ??128-3 FAIL 5/1 ??128-4 FAIL 23/1 (offline): multi-object frame-keyed binder built (stagexec self-test 134/0); X5's refusal was a gate false positive (41 = 26 wiring + 15 RLE) ??fixed, self-test 5/0, fp-19 logged; stage_prerun `open` restore fixed. P3b with the guard = ~70 actions > the user's ~40 ??split (PD261(d)).
  - 128-5 FAIL 2/3 (budget): `name#k` addressing of repeated terminal names (stagesim 80/0, stagexec 136/0); guard rows in the plan; 70-action input replays end to end (PD263(a)).
  - Carries: fp-20 (X16 refuses a `Local` create; `selftest_stage_prerun_c106e` red since cycle 125); `census_predict` has no row branches for wire/RLE/FS rows (tool debt, not a launch precondition, PD261(c)); plan line 2818 "16 NamedUnbundler" is wrong (12 + 3 Unbundler).
- **CYCLE 127 in brief ??P3b's last measured gaps closed; two new tool gaps found; no new VI:**
  - 127-1 FAIL 2/2 (diagnostic hit its 40-min deadline): the "second sink into an FS frame already entered" route is MEASURED on 3 of 4 rows (the 4th, BufNum ??`Latest`, ran but its census was not read; P3b's scratch reads it) (`connect_term_uid` from the inner face branches the existing wire, census {}, no second tunnel). Four ~7-min Error List GUI reads ate the time ??rule PD258(a): ONE Error List read per diagnostic. Automatic Error Handling is not readable over COM (not needed after PD258(c)).
  - 127-2 PASS 5/0 (offline): stageplan op `wire_remove_loose_ends`; crossings compile to `connect_term_uid`; stagesim models them; the P3b plan input replays end to end (cdiff 16, old sinks kept); `errorlist_check` OCR aliases; fp-15/16/18 queued.
  - DECIDED PD258(c): `IMAQ Copy` error in ??`#6810` error out; error out ??`Unbundle status` ??`Select` ??`Num(i)` element, so a failed copy leaves the slot at ?? (U9 no corruption) and no auto-error dialog can suspend the camera loop (U6).
  - 127-3 FAIL 4/1 ??127-4 FAIL 3/2 (offline): final plan `plan_ring_p3b.json` (63 actions), IMAQ Copy terminals measured, recipe written (not launched); simulator renumber bug fixed (self-test 130/0); next stop = the multi-object binder (PD260(b)). Prediction file written.
  - 127-5 FAIL 16/1: no creation route for `Select`/`Unbundle By Name` found in the donors searched so far (per-file row counts not logged, so not yet proven absent; PD260(c)). Retrospective cycle 127: `inference-over-measurement` (24 min) ??brief time arithmetic is now stated in every brief; next offline dry audits ALL rows at once.
- Tools now available (cycles 126??27): `gscript.hygiene_run` (EVERY op hygiene check goes through it); ops `OpFsAddFrame_v0`, `OpFsDiagrams_v0`, `OpWireRemoveLooseEnds_v0` + `gscript.wire_remove_loose_ends`; stagexec routes `fs_create` / `fs_frame` / `fs_frame_to_frame` / `fs_border` / `fs_border_inner_branch`.
- **CYCLE 126 in brief ??the hygiene runner is built, Flat Sequence creation works and is in the plan format, the stub wire can be removed, and every P3b crossing kind is measured:**
  - 126-1 PASS 38/0: `gscript.hygiene_run` built (the repeated-failure-class device); `OpFsAddFrame_v0` hygiene PASS (closed-state handles max dev 7 ??125-5's +116 was the never-closed copies); 3-frame FS scratch 15/0.
  - 126-3 PASS 13/0 (offline): FS routes and models; 126-1's "one-terminal wire" is the normal FS tunnel graph shape, not a stub.
  - 126-2 FAIL 3/1 ??126-4 FAIL 13/1: both FAILs were our own gates (method-name literal; OCR'd Error List keys `subvi`/`subvl` ??a variant already in 161 recorded Error List files). 126-5's FAIL was the known duplicate-row case that `V.dedupe_rows` has handled since 2026-09-24. Three one-off diagnostics broke the 120-line rule (retrospective cycle 126, `VIOLATION: none`). Measured: `RemoveLooseEnds` on w27378 clears the loose end, `Is Broken?` True ??False, terminals kept, Error List 55 ??54 (PD255(a)).
  - 126-6 PASS 48/0: case frame ??FS frame, branch to another frame, BufNum / While `i` / pool For exit ??FS frame ??all by `connect_term_uid`; While-border array tunnel non-indexed (rule 1a holds). Census samples recorded.
  - 126-5 FAIL ??126-7 FAIL ??126-8 PASS 18/0 (offline): P3b plan input written (45 actions + 2 released rows + 14 loose-end removal rows). Rule-1a check: in the ORIGINAL, `#30117`/`#4580` Value feed the per-frame record `#2626` ??`save trace.vi`, so PD238(c) holds; `#4580`'s sink was opened by design at L2-B1 (PD257(a)).
  - Carries: `docs/NAMES.md` lacks the measured Wire method ids (`6370C05` CleanUpWire, `6370C08` RemoveLooseEnds, `6370C0B` DeleteJoint, `6370C0D` DisconnectTerminal ??`diag_c126_2_op.log:8-16`) and the FS methods; `errorlist_check.py` `norm()` OCR aliases (`vl`??vi`); `selftest_fs_c126.py` not in `protocol.OFFLINE_SELFTESTS`; `diag_c126_2_fs.py` still calls the old `g.wire_cleanup` name (superseded by `diag_c126_4_fs.py`).
- **CYCLE 125 in brief ??gates cleaned, the 55th item traced, both Flat Sequence ops built (one awaits a hygiene rerun):**
  - 125-1 PASS 38/0: gate false positives fp-10..fp-13 drained (`guard_peer.py:946` RULE-OFFLINE-CMD; `protocol.py:398` OFFLINE_SELFTESTS). New prerun check X16 (`stage_prerun.py:1904`).
  - 125-3 PASS 5/0: the review `archive/peer/2026-10-01-c125-1-x16-hyp.md` showed X16 wrongly refused constants (their class equals the simulator's default); X16 now skips constants (fp-14 drained).
  - 125-2 FAIL 13/1: the real P3a graph is read (`tools/bench/graph_ring_p3a_20261001_190155.json`). My "exactly one new loose wire" prediction failed: terminal counts cannot see the item (review `?쫈125-2-loose-hyp.md`).
  - 125-4 FAIL 3/3: the 55th item is `w27378`, one dangling segment end left by P3a's `connect_term_uid` row across the case border (`diag_c125_joints.log:26,39`). FlatSequence `Add Frame` = method `3578B800`.
  - 125-5 FAIL 22/2: `OpFsDiagrams_v0` hygiene PASS; `OpFsAddFrame_v0` works but its hygiene failed on handles (+116, the test never closed its copies). The stub did not reproduce on a minimal scratch VI (PD253(d)).
  - Carries: `c125_1_regress.py`'s glob catches three P2b companion files that are not final plans (X1 fail, expected); a card that edits `stagexec.py`/`stagekit.py`/a listed self-test reruns `tools/bench/c125_1_offline_measure.py` (PD252(a)); `diag_c125_5_opfs.py` is 203 lines (one-off).
- **CYCLE 124 in brief ??P3a DELIVERED (the new bed); the case-tunnel tools built:**
  - 124-8 PASS 5/0: `claudeDev\D1_ring_p3a_20261001_180540.vi` md5 `4dfa44aa??. Scratch 22/0, ONE launch 22/0, census == prediction; Error List 55 == pin (54 + 1 new `Wire has loose ends`, the plan's alternative); expected file `tools/bench/errorlist_expected_D1_ring_p3a_20261001_180540.json` reverdicts OK. STRUCTURAL, ExecState 0 by design, never run. Broken-file count: 2 of 6.
  - 124-7 FAIL 10/2: the scratch stopped at op 1, because the plan left created-node `term_class` undeclared (the simulator said `Terminal`, LabVIEW said `ParameterTerminal`). Fixed in the plan by 124-8; the review kept the cause.
  - 124-5 PASS 25/0: the new op passed its 2,000-call hygiene check. P3a's counter was proven on a scratch: register ??case crossings by `connect_term_uid`, the True-frame pass-through, and a second sink that LabVIEW branches.
  - 124-1 / 124-4 FAIL: two bugs in our own build script (an owner check on the top-level diagram, and the op called outside `hygiene_probe`). Both fixed.
  - 124-2 BLOCKED (gate false-positive fp-12) / 124-3 FAIL: the plan-format `frame` field was built. 124-3 found the real gap was the register crossing, which 124-5 closed.
  - Carries: gate false-positives fp-10..fp-13 queued (fp-12/13: census hook-in and stagexec self-tests refused under `labview: none`); the cycle-123 carries below still stand.
- **CYCLE 123 in brief RELOCATED VERBATIM ??`archive/2026-10-01-status-cycle126-relocate.md` 짠1.** Still live from it: user decision D-2026-10-01-01 ??ANSWERED 2026-10-01 (option 1: ??~40 edit operations per ring step, full scratch run before each, 6-file cap kept); carries `docs/d1-build-plan.md` still `status: current` (L5), decisions item 13 over 300 chars, cycle 122's carries (stagekit donor declaration, `_check_units`, RULE-OFFLINE-CARD reverse, `requires` for routes/donors, fp-10).
- **CYCLE 122 in brief RELOCATED VERBATIM ??`archive/2026-10-01-status-cycle123-relocate.md` 짠6** (its carries are repeated in the cycle-123 brief above).
- **CYCLE 121 in brief and the cycle-121-start FIRST ACT block (chat-P3, then the ring-buffer plan) RELOCATED VERBATIM ??`archive/2026-10-01-status-cycle123-relocate.md` 짠3.**
?뵶 **USER RULE, re-confirmed 2026-09-28 15:3x (chat) ??the POOL's overload branch (D-2026-09-28-01, now ANSWERED): the user decided this on 2026-09-15 and it has a PRIORITY ORDER.** (1) NO CORRUPTION: an image and its buffer number change together and the consumer verifies them ??a pixel/number mismatch is corruption. (2) LATEST-WINS: when tracking falls behind, discard the queued backlog and read the newest frame ("?먮? 踰꾨━怨??덈줈 ?ㅼ뼱?ㅻ뒗 ?꾨젅?꾩쓣 ?쎈뒗 寃껋씠 媛??諛붾엺吏곹븿. ?대뒗 ?쒓퀎???곗씠?곗쓽 ?꾨??깆쓣 ?꾪븿"); a gap recorded by the buffer number is fine. (3) FALLBACK: if (1)+(2) cannot be made provably safe, acquisition and tracking may stay in ONE sequential loop. **The planned "full Q_work ??skip the newest read" (d1-build-plan.md 짠9, PD233/234) VIOLATES (2)** ??the judgement session re-decides the overload branch against this order before any real run (memory `prefer_the_freshest_frame_over_a_complete_backlog`, `docs/decisions.md:25`). Structure already built (the 20-slot pool) may stay; only the overload behaviour changes.
?윞 **CARRY (from the 2026-09-25 verification review `archive/peer/2026-09-25-hyp-lintverify-20260925.md`, not blocking): card flags are checked only on the top-level command (a child process could reach LabVIEW under labview=none); a stage run launched outside bgrun is not counted by the retry cap; a bgrun record failure is only logged (`tools/bgrun.py:219-220`). Close in a tooling cycle, deliverable-first.**
current-bed: D1_ring_p3a_20261001_180540.vi
<!-- ^ machine key read by tools/errorlist_check.py current_bed_text(); without it the bed is chosen by mtime among D1_*.vi names in this file, and the newer D1_s1_kswap_* would silently take over (review archive/peer/2026-09-26-c88-reuse-stalepin.md). Change it only when a new bed is accepted. Moved 2026-10-01 by cycle 124 (PD251(a)): ring P3a accepted (md5 4dfa44aac8fb32f706b3eb792ee7d3cc, expected Error List tools/bench/errorlist_expected_D1_ring_p3a_20261001_180540.json, 55 items). Before: ring P2b (cycle 123, PD246(a), md5 652b1447ebbda761a7d5ba36455a0fa1). -->
?뵷 **THE WORK VI (bed) IS NOW `claudeDev\D1_ring_p3a_20261001_180540.vi`, md5 `4dfa44aac8fb32f706b3eb792ee7d3cc` (cycle 124, PD251(a)): P2b plus loop 1.1's control ??`Wait (ms)` 1, the previous-BufNum register (I32, ??), `Equal?`, the duplicate/new-frame case, the new-frame counter (I32, 0; incremented in False, passed through in True), `i = count mod 20`. Error List 55; STRUCTURAL, ExecState 0 by design, never run; broken-file count 2 of 6.** Its input P2b (below) is kept.
?뵷 **THE WORK VI (bed) IS NOW `claudeDev\D1_ring_p2b_20261001_140658.vi`, md5 `652b1447ebbda761a7d5ba36455a0fa1` (cycle 123, PD246(a)): P2a plus the five ring indicators `Num`/`TransPos`/`RotPos`/`FrameIdx`/`Latest` and their initial values on FS1 frame `#4866`; Error List 54 items, expected file `tools/bench/errorlist_expected_D1_ring_p2b_20261001_140658.json`; STRUCTURAL, ExecState 0 by design, never run; broken-file count 1 of 6.** (history) Its input `claudeDev\D1_ring_p2a_20260928_191739.vi`, md5 `c22a473f26ebcc67296d1c2441f8a47a` (cycle 121, PD238(l)), is kept: the pool bed below minus its two queues; Error List 54 items, expected file `tools/bench/errorlist_expected_D1_ring_p2a_20260928_191739.json`. The bed before it was `claudeDev\D1_qrt_pool_20260928_141055.vi`, md5 `9353936895141d3ec2f890649c5cf22f`. It is the POOL stage: 20 image buffers `Cam_pool00`??19` and the two queues Q_free / Q_work, added to R2 and not yet consumed. Expected Error List file `tools/bench/errorlist_expected_D1_qrt_pool_20260928_141055.json`: 53 items (== R2's), reverdict OK (PD236(a)). STRUCTURAL, ExecState 0 by design, never run. Its input R2 (`D1_l2_r2_20260928_110756.vi`, md5 `7dac9f04??) is kept.
- **Cycles 82??20: the FIRST ACT blocks, the cycle briefs, the cycle-84 L2-A1 run plan and the cycle-101 stage pass criteria RELOCATED VERBATIM ??`archive/2026-10-01-status-cycle123-relocate.md` 짠4.**
- Standing: card `peers` = hypothesis, outcome, priorart. Every card that builds or edits a VI carries `gui: true`; on ExecState 0, read the Error List first.
?뵷 **CYCLES 68??0 DONE records, old FIRST ACT paragraphs and carries RELOCATED VERBATIM ??`archive/2026-09-25-status-cycle81-relocate.md` 짠2** (card 81-1). Still-live items there, one line each:
- ?윞 FOR THE USER: `.claude/settings.json` guard_session matcher `Agent|Task` ??`Agent|Task|SendMessage` (only you can apply it); `git commit` at cycle close needs your approval-list entry (짠2).
- ?뵶 Rule: desk-check PREDICTED VALUES, not only gates ??Pre-decided 132 (짠2).
- ?윞 Carries not ahead of the deliverable: cp949 print helper in stagekit, audit A1 vs `jev_gate.log`, bgrun END guarantee under a tree kill (짠2).
- ?좑툘 Per-session cap 180 min: write `## NEXT` by minute 150; every new stage/diagnostic ??20 lines on stagekit (짠2).
- Still the user's to overturn: N1 on the pre-bead-loss window, bead-4 FLIP mask, harness records 60 controls and sets none, `background VIs_COPY` untouched (짠2).

## Where to look ??**`docs/handover-2026-09-22.md` (???몄뀡? ?닿쾬遺??** 쨌 `CLAUDE.md` 쨌 `docs/secrets-and-handover.md` (API keys, ?ъ슜??援먯껜 泥댄겕由ъ뒪?? 쨌 `docs/jev-integration-plan.md` (Jev ?쎌엯 ?먮━, 2026-09-22) 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.

## RUNNER STOPPED history (2026-09-22 09:58, 2026-09-24 07:29, 2026-09-25 01:02, 2026-09-25 10:30) ??`archive/2026-09-25-status-cycle81-relocate.md` 짠3

## RUNNER STOPPED 2026-09-27 08:25:46 (cycle 107, lifted) ??`archive/2026-10-01-status-cycle123-relocate.md` 짠5


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"priorart-c129-8-ring-p3b1","verdict":"<one of: novel | settled-already>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

Still checking, nearly done: I'm confirming that the changed P3b-1 build-script bytes only bring in patterns that already exist here.

**Verdict: `novel`.** Nothing in the project files blocks the P3b-1 build. The build script changed since the last review (md5 `4dc77962…` → `5e25813a…`), but the change only reuses a decided pattern. The one earlier failure of this step has its cause fixed.

**PART A: direction**
- **A1, decided already (not a blocker):** the direction was settled before this review. The full record is in `archive/peer/2026-10-02-priorart-c129-2-ring-p3b1.md:1311-1317`: the ring buffer (U13), the write order (PD238(c)), the guard form (PD261(a)), `element#0` (PD262(b)), the split (PD261(d)/PD264(a)), and a scratch run before ONE launch (PD264(e)). That review returned `novel` at `:1334` and the cycle-129 judgement accepted it at `:1345`.
- **The one new item, the checkpoint set, is also decided:** `docs/d1-loop12-17-split-plan.md:2931` says "(c) DECIDED: P3b-1 and P3b-2 use PD193(a)'s checkpoint set `{0, len(ops)} | BIND`". The recipe copies it at `tools/recipes/stage_d1_ring_p3b1.py:24-25`, from `tools/recipes/stage_d1_l2b3.py:17-18`. This carries out a decision; it is not a repeat of one.
- **A2, refuted already:** nothing found.
- **A3, contradicted:** only the documentation conflict the last review found. `docs/ring-buffer-design.md:23-24` says there is no copy; PD238(c) overrules it (c129-2 review `:1319`, `:1349`). It is still not marked as superseded. That is doc cleanup, not a blocker.
- **A4, unread evidence:** nothing found. The recipe and card 129-8's brief cite the memory measurement (`diag_c129_6_mem.log:55,87`) and the pin2 log.

**PART B: the build file**
- **B1, already built:** no. There is no `D1_ring_p3b1_*.vi` in `claudeDev` (glob, 0 hits). The trigger says `new-op`, but the script adds no new op; it uses `SX.Executor` and `SX.BIND_KINDS` as `stage_d1_l2b3.py` does.
- **B2, already failed:** the scratch run of this build failed once. Its cause is addressed, so I give no slug.
  - **The failure:** `tools/bench/stage_d1_ring_p3b1_scratch_pin2.log:477` stopped at op 33 (`p3b_x_bn_n3`). The simulator left a FlatSequence outer tunnel's terminals unnamed; LabVIEW named them `current image number`.
  - **The review:** `archive/peer/2026-10-02-hyp-c129-4-ring-p3b1-fsot.md:47-52` warned that copying the source name onto every tunnel would break ops 27/29/31.
  - **The fix:** card 129-7 (`tools/bench/cards/result_129-7.json:11-15`) names tunnels from the net instead (`CROSS_NAME_FROM_CLS`). The stagesim self-test is 88/0, the simulated step 33 now names the tunnel, and the dry run shows STEPX 33 diff 0.
  - **The second risk in pin2:** private memory reached 697.3 MB against the 700 MB stop. Card 129-6 measured about 2.5 MB per whole-VI read (`diag_c129_6_mem.log:55`). Cutting reads to the decided checkpoint set (BIND ops plus the two ends) is the change under review.
- **B3, an existing helper already does this:** no hand-rolled work. The script uses `SX.Executor(checkpoints=…)`, `SX.compile_plan` and `gscript.wire_remove_loose_ends` (`gscript.py:4972`).
- **B4, already measured:** each part is measured on its own (c129-2 review `:1326`). The combined 40-operation run is still unmeasured; the scratch run (pin3) measures it.

**PART C: the user's rules.** No conflicts.

PRIOR-ART: novel

VERDICT {"schema":"verdict/1","id":"priorart-c129-8-ring-p3b1","verdict":"novel","alternative":"Bytes changed only by PD265(c)'s decided checkpoint set {0,len}|BIND (split-plan:2931, copied from stage_d1_l2b3.py:17-18); the pin2 op-33 failure's cause (unnamed FSOT in the simulator) was fixed by card 129-7.","discriminating_test":"P3b-1 scratch run pin3 on a P3a byte copy: op 33 STEPX diff 0 with the FSOT named 'current image number', peak private memory below 700 MB, every checkpoint == its simulated step.","violations":[],"sources":["docs/d1-loop12-17-split-plan.md:2931","tools/recipes/stage_d1_ring_p3b1.py:24-25","tools/recipes/stage_d1_l2b3.py:17-18","tools/bench/stage_d1_ring_p3b1_scratch_pin2.log:477","tools/bench/cards/result_129-7.json:11-15","tools/bench/diag_c129_6_mem.log:55","archive/peer/2026-10-02-priorart-c129-2-ring-p3b1.md:1334"],"note":"ring-buffer-design.md:23-24 (no copy) is still not marked superseded by PD238(c); doc cleanup only. The FSOT naming model rests on one named net (result_129-7 open)."}

## Sources

(extract from answer)

## What was done with it

(cycle 129 judgement, 2026-10-02 03:0x)
- `PRIOR-ART: novel` accepted for the checkpoint-set bytes of `tools/recipes/stage_d1_ring_p3b1.py` (md5 `5e25813a…`).
- Its discriminating test (scratch pin3: op 33 named, peak < 700 MB, every checkpoint == sim) is NOT run on these bytes as
  they stand: card 129-8 predicts P3b-1's peak at 688.5 MB (R 25 reads, `diag_c129_8_mempred.log:3`), 1.5 MB under X10's
  690 and 6.5 MB under the measured error-2 point. PD266 re-balances the P3b split by predicted memory first (cycle 130's
  first card); the recipe bytes will change again and the launch gate will ask for a review of those.
- Doc note (`ring-buffer-design.md:23-24` not yet marked superseded by PD238(c)): cycle 130's tooling card.
