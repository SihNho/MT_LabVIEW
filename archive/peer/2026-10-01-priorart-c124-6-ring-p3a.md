# priorart-c124-6-ring-p3a

- **agent:** claude
- **role:** priorart
- **model:** claude-opus-5-5 (effort medium; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $1.1518  in 12 / out 4334 / cache-create 117041 / cache-read 643671  (51s, 11 turn(s))
- **date:** 2026-10-01 17:10:39
- **outcome:** ANSWERED (55s)
- **verdict-card:** VERDICT-CARD priorart-c124-6-ring-p3a verdict=novel -> tools\bench\cards\verdict_priorart-c124-6-ring-p3a.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id priorart-c124-6-ring-p3a, role priorart) ---
CLAIM: The work under review (new-op) is novel - not already built, measured, refuted or covered by an existing helper in this project's files.
ATTACHMENT: tools\recipes\stage_d1_ring_p3a.py (md5 3aa685dea0abfb69203f1a5832a4b84c)
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
 "stage": "ring_p3a",
 "goal": "RING P3a (PD246(c)(d), 247, 248): loop-1.1 control on the SAVED P2b bed; v3 (card 124-6): routes connect_term_uid (R1/R2) and case_frame_wire branch (R4)",
 "base": {
  "path": "tools/bench/graph_ring_p2b_20261001_154542.json",
  "md5": "69b23e0821482acf118bb268d92589fe"
 },
 "context": {
  "s1_key": "D1_s1_copy"
 },
 "actions": [
  {
   "op": "create",
   "id": "p3a_wait",
   "class": "Function",
   "diagram": 639,
   "as": "WT1",
   "pos": [
    3200,
    60
   ],
   "prim": "Wait (ms)",
   "donor": {
    "donor": "C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\OpWaitDonor_v0.vi",
    "uid": 163
   },
   "terminals": [
    {
     "name": "milliseconds to wait",
     "is_source": false
    },
    {
     "name": "millisecond timer value",
     "is_source": true
    }
   ],
   "why": "PD246(d): Wait (ms) 1 in loop 1.1, no data dependency on the frame path (donor facts_c100_oplabels.json:266-273)"
  },
  {
   "op": "create",
   "id": "p3a_wait_k",
   "class": "DigitalNumericConstant",
   "diagram": 639,
   "as": "WK1",
   "pos": [
    3150,
    60
   ],
   "on": "new:WT1.milliseconds to wait",
   "value": 1,
   "why": "PD246(d): the wait is 1 ms (const_on_term, a node in a While body)"
  },
  {
   "op": "add_shift_reg",
   "id": "p3a_sr_prev",
   "loop": 637,
   "body": 639,
   "parent": 686,
   "as": "SP1",
   "why": "PD246(c) A3: previous-BufNum register on #637"
  },
  {
   "op": "create",
   "id": "p3a_k_prev",
   "class": "DigitalNumericConstant",
   "diagram": 686,
   "as": "KP1",
   "pos": [
    -200,
    400
   ],
   "prim": "const_donor",
   "donor": {
    "donor": "C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\DonorRingConst_v0.vi",
    "uid": 249
   },
   "terminals": [
    {
     "name": "",
     "is_source": true
    }
   ],
   "why": "PD246(c) A3 / PD247(a): I32 -1 (BufNum is I32, t6897) = DonorRingConst_v0 #249"
  },
  {
   "op": "wire",
   "id": "p3a_w_kprev",
   "src": "new:KP1.value",
   "dst": "new:SP1L.outer",
   "why": "PD247(a): const_sr - register initialised at loop start"
  },
  {
   "op": "wire",
   "id": "p3a_w_bn_r",
   "src": {
    "uid": 6810,
    "term": "current image number"
   },
   "dst": "new:SP1R.inner",
   "why": "PD246(c) A5: the register's right terminal takes BufNum (branch of w3747), outside the case"
  },
  {
   "op": "create",
   "id": "p3a_eq",
   "class": "Comparison",
   "diagram": 639,
   "as": "EQ1",
   "pos": [
    3300,
    1500
   ],
   "prim": "Equal?",
   "donor": {
    "donor": "$work",
    "uid": 10019
   },
   "terminals": [
    {
     "name": "x = y?",
     "is_source": true
    },
    {
     "name": "y",
     "is_source": false
    },
    {
     "name": "x",
     "is_source": false
    }
   ],
   "why": "PD246(c) A4 / PD247(b): Equal? $work dup of #10019 (Comparison {x = y?, y, x})"
  },
  {
   "op": "wire",
   "id": "p3a_w_bn_x",
   "src": {
    "uid": 6810,
    "term": "current image number"
   },
   "dst": "new:EQ1.x",
   "why": "Equal? x = BufNum (branch of w3747; PD248(b) branch proven, diag_c123_wired.log:51)"
  },
  {
   "op": "wire",
   "id": "p3a_w_prev_y",
   "src": "new:SP1L.inner",
   "dst": "new:EQ1.y",
   "why": "Equal? y = previous BufNum"
  },
  {
   "op": "create",
   "id": "p3a_case",
   "class": "CaseStructure",
   "diagram": 639,
   "as": "CS1",
   "selector_as": "SEL1",
   "pos": [
    3600,
    1450
   ],
   "frames": [
    "False",
    "True"
   ],
   "src": "new:EQ1.x = y?",
   "why": "PD248(a): case_wired, True = duplicate (empty), False = new frame"
  },
  {
   "op": "add_shift_reg",
   "id": "p3a_sr_cnt",
   "loop": 637,
   "body": 639,
   "parent": 686,
   "as": "SC1",
   "why": "PD246(c) A3 / PD247(d): new-frame counter on #637"
  },
  {
   "op": "create",
   "id": "p3a_k_cnt",
   "class": "DigitalNumericConstant",
   "diagram": 686,
   "as": "KC1",
   "pos": [
    -200,
    480
   ],
   "prim": "const_donor",
   "donor": {
    "donor": "C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\DonorSRInit_v0.vi",
    "uid": 248
   },
   "terminals": [
    {
     "name": "",
     "is_source": true
    }
   ],
   "why": "PD247(d): counter I32 0 = DonorSRInit_v0 #248"
  },
  {
   "op": "wire",
   "id": "p3a_w_kcnt",
   "src": "new:KC1.value",
   "dst": "new:SC1L.outer",
   "why": "PD247(a): const_sr"
  },
  {
   "op": "create",
   "id": "p3a_inc",
   "class": "Function",
   "diagram": "new:CS1.f0",
   "as": "INC1",
   "pos": [
    60,
    60
   ],
   "prim": "Increment",
   "donor": {
    "donor": "$work",
    "uid": 1978
   },
   "terminals": [
    {
     "name": "x+1",
     "is_source": true
    },
    {
     "name": "x",
     "is_source": false
    }
   ],
   "why": "PD247(b): Increment $work dup of #1978"
  },
  {
   "op": "tunnel",
   "id": "p3a_t_in",
   "loop": "new:CS1",
   "body": "new:CS1.f0",
   "parent": 639,
   "dir": "in",
   "as": "TI1",
   "why": "count into the case (False frame)"
  },
  {
   "op": "wire",
   "id": "p3a_w_cnt_in",
   "src": "new:SC1L.inner",
   "dst": "new:TI1.outer",
   "why": "the register's left value enters the case"
  },
  {
   "op": "wire",
   "id": "p3a_w_cnt_inc",
   "src": "new:TI1.inner",
   "dst": "new:INC1.x",
   "why": "PD246(c) A5: +1 only on a new frame"
  },
  {
   "op": "tunnel",
   "id": "p3a_t_out",
   "loop": "new:CS1",
   "body": "new:CS1.f0",
   "parent": 639,
   "dir": "out",
   "as": "TO1",
   "why": "count out of the case"
  },
  {
   "op": "wire",
   "id": "p3a_w_inc_out",
   "src": "new:INC1.x+1",
   "dst": "new:TO1.inner",
   "why": "False frame: count + 1"
  },
  {
   "op": "wire",
   "id": "p3a_w_out_r",
   "src": "new:TO1.outer",
   "dst": "new:SC1R.inner",
   "why": "the case output feeds the counter's right terminal"
  },
  {
   "op": "wire",
   "id": "p3a_w_true_pass",
   "src": {
    "uid": "new:TI1",
    "side": "inner",
    "frame": "True"
   },
   "dst": {
    "uid": "new:TO1",
    "side": "inner",
    "frame": "True"
   },
   "why": "PD246(c) A5: the True (duplicate) frame passes the count straight through; v2 (card 124-2, PD249(d)): `frame` = the frame NAME (was 'new:CS1.f1', which stageplan/1 did not accept)"
  },
  {
   "op": "create",
   "id": "p3a_qr",
   "class": "Function",
   "diagram": "new:CS1.f0",
   "as": "QR1",
   "pos": [
    60,
    160
   ],
   "prim": "Quotient & Remainder",
   "donor": {
    "donor": "$work",
    "uid": 2136
   },
   "terminals": [
    {
     "name": "floor(x/y)",
     "is_source": true
    },
    {
     "name": "x-y*floor(x/y)",
     "is_source": true
    },
    {
     "name": "y",
     "is_source": false
    },
    {
     "name": "x",
     "is_source": false
    }
   ],
   "why": "PD247(b): Q&R $work dup of #2136; remainder (i) unconnected until P3b"
  },
  {
   "op": "wire",
   "id": "p3a_w_qr_x",
   "src": {
    "uid": "new:TI1",
    "side": "inner",
    "frame": "False"
   },
   "dst": "new:QR1.x",
   "why": "x = the count (left value through the case); v3 (card 124-6, PD250(c)): addressed by frame 'False' on TI1's inner face, already wired by its group -> case_frame_wire variant branch (R4, census {}, diag_c124_p3a_scratch.log:77,80)"
  },
  {
   "op": "create",
   "id": "p3a_k20",
   "class": "DigitalNumericConstant",
   "diagram": "new:CS1.f0",
   "as": "K20",
   "pos": [
    0,
    200
   ],
   "prim": "const_donor",
   "donor": {
    "donor": "C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\DonorPool_v0.vi",
    "uid": 214
   },
   "terminals": [
    {
     "name": "",
     "is_source": true
    }
   ],
   "why": "y = I32 20 (DonorPool_v0 #214, plan_qrt_pool_in.json p_i32)"
  },
  {
   "op": "wire",
   "id": "p3a_w_k20",
   "src": "new:K20.value",
   "dst": "new:QR1.y",
   "why": "ring size 20"
  }
 ],
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
 "final": true,
 "finalized": {
  "base": {
   "path": "tools/bench/graph_ring_p2b_20261001_154542.json",
   "md5": "69b23e0821482acf118bb268d92589fe"
  },
  "plan_in": {
   "path": "tools/bench/plan_ring_p3a_in_v3.json",
   "md5": "65a6c3baee706bbd0b3bb886efe9d72f"
  },
  "last_step": {
   "path": "tools/bench/sim/ring_p3a/step_25_wire.json",
   "md5": "a480d26f352593bb1289629f6a0f5743"
  },
  "summary": {
   "path": "tools/bench/sim/ring_p3a/summary.json",
   "md5": "5e50fb4d4752e83c0aa0473dcb5e5e6f"
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
    "path": "tools/bench/sim/ring_p3a/step_00_base.json",
    "md5": "e1235840f2486ba87720e184df5f630a"
   },
   {
    "n": 1,
    "op": "create",
    "path": "tools/bench/sim/ring_p3a/step_01_create.json",
    "md5": "8398889c9ad00b393665856250ce218a"
   },
   {
    "n": 2,
    "op": "create",
    "path": "tools/bench/sim/ring_p3a/step_02_create.json",
    "md5": "d898b68499a3cab4997b103cc5180a85"
   },
   {
    "n": 3,
    "op": "add_shift_reg",
    "path": "tools/bench/sim/ring_p3a/step_03_add_shift_reg.json",
    "md5": "43853812e2d9cd6028286e779151d4ae"
   },
   {
    "n": 4,
    "op": "create",
    "path": "tools/bench/sim/ring_p3a/step_04_create.json",
    "md5": "92b182f2149d58cef072cc3eec2ab853"
   },
   {
    "n": 5,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3a/step_05_wire.json",
    "md5": "cdcb53e02aa4e0ed6d6883d9c5f92812"
   },
   {
    "n": 6,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3a/step_06_wire.json",
    "md5": "9e6934c97b1e5f40bc327db0d2d44db6"
   },
   {
    "n": 7,
    "op": "create",
    "path": "tools/bench/sim/ring_p3a/step_07_create.json",
    "md5": "05ef1fd0f4b1a3c0d174d01306426c24"
   },
   {
    "n": 8,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3a/step_08_wire.json",
    "md5": "1caf3c71422e3f4fc18ab223dc5884e3"
   },
   {
    "n": 9,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3a/step_09_wire.json",
    "md5": "c90d8bbeca996d1acc88918d798fba6e"
   },
   {
    "n": 10,
    "op": "create",
    "path": "tools/bench/sim/ring_p3a/step_10_create.json",
    "md5": "6abf29d806aeb9745251a9e37fc4aa51"
   },
   {
    "n": 11,
    "op": "add_shift_reg",
    "path": "tools/bench/sim/ring_p3a/step_11_add_shift_reg.json",
    "md5": "c10b2a43472429984751469579eb4acc"
   },
   {
    "n": 12,
    "op": "create",
    "path": "tools/bench/sim/ring_p3a/step_12_create.json",
    "md5": "1d22971e0f4efa2da71a31002ec3502b"
   },
   {
    "n": 13,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3a/step_13_wire.json",
    "md5": "91091011f13bc85b9795ff4363a27dc8"
   },
   {
    "n": 14,
    "op": "create",
    "path": "tools/bench/sim/ring_p3a/step_14_create.json",
    "md5": "73befd9d825508593dde338da5183beb"
   },
   {
    "n": 15,
    "op": "tunnel",
    "path": "tools/bench/sim/ring_p3a/step_15_tunnel.json",
    "md5": "a9a9f6d647353019e81e3182efc176c4"
   },
   {
    "n": 16,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3a/step_16_wire.json",
    "md5": "c7460b5c296fdb556713571bf001850c"
   },
   {
    "n": 17,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3a/step_17_wire.json",
    "md5": "b4ec31f18bc40adba1f48bf634282329"
   },
   {
    "n": 18,
    "op": "tunnel",
    "path": "tools/bench/sim/ring_p3a/step_18_tunnel.json",
    "md5": "b5813f0d5a15603a03a81901ce8415c9"
   },
   {
    "n": 19,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3a/step_19_wire.json",
    "md5": "230d01baa4ce2ca7181585e03d264ffe"
   },
   {
    "n": 20,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3a/step_20_wire.json",
    "md5": "ce4743a71d38e240f69b2d6676bfa9f4"
   },
   {
    "n": 21,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3a/step_21_wire.json",
    "md5": "930bb8f4d2165664e8ebf3d81e7a1b6f"
   },
   {
    "n": 22,
    "op": "create",
    "path": "tools/bench/sim/ring_p3a/step_22_create.json",
    "md5": "81d94838b57accdefef9c0ca9a54c9ac"
   },
   {
    "n": 23,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3a/step_23_wire.json",
    "md5": "0df3bb615e69c2daadbea8bcd4edf870"
   },
   {
    "n": 24,
    "op": "create",
    "path": "tools/bench/sim/ring_p3a/step_24_create.json",
    "md5": "295eab108f91d06632d1105dfef93f7a"
   },
   {
    "n": 25,
    "op": "wire",
    "path": "tools/bench/sim/ring_p3a/step_25_wire.json",
    "md5": "a480d26f352593bb1289629f6a0f5743"
   }
  ],
  "undecided": 0,
  "at": "2026-10-01 17:06:44",
  "route_check": {
   "status": "PASS",
   "first_fail": null,
   "rows": [
    {
     "k": 1,
     "op": "create",
     "ids": [
      "p3a_wait"
     ],
     "route": "primitive",
     "how": null,
     "unroutable": null
    },
    {
     "k": 2,
     "op": "create",
     "ids": [
      "p3a_wait_k"
     ],
     "route": "const_on_term",
     "how": "order-proof",
     "unroutable": null
    },
    {
     "k": 3,
     "op": "add_sr",
     "ids": [
      "p3a_sr_prev"
     ],
     "route": "add_sr",
     "how": null,
     "unroutable": null
    },
    {
     "k": 4,
     "op": "create",
     "ids": [
      "p3a_k_prev"
     ],
     "route": "primitive",
     "how": null,
     "unroutable": null
    },
    {
     "k": 5,
     "op": "connect",
     "ids": [
      "p3a_w_kprev"
     ],
     "route": "const_sr",
     "how": "unique live name '' on loop #637 (tracked index 25)",
     "unroutable": null
    },
    {
     "k": 6,
     "op": "wire_sr",
     "ids": [
      "p3a_w_bn_r"
     ],
     "route": "wire_sr:RightIn",
     "how": "cached index (proved by its wire uid while wired)",
     "unroutable": null
    },
    {
     "k": 7,
     "op": "create",
     "ids": [
      "p3a_eq"
     ],
     "route": "primitive",
     "how": null,
     "unroutable": null
    },
    {
     "k": 8,
     "op": "connect",
     "ids": [
      "p3a_w_bn_x"
     ],
     "route": "cfw",
     "how": "order-proof",
     "unroutable": null
    },
    {
     "k": 9,
     "op": "wire_sr",
     "ids": [
      "p3a_w_prev_y"
     ],
     "route": "wire_sr:LeftIn",
     "how": "order-proof",
     "unroutable": null
    },
    {
     "k": 10,
     "op": "create",
     "ids": [
      "p3a_case"
     ],
     "route": "case_wired",
     "how": "order-proof",
     "unroutable": null
    },
    {
     "k": 11,
     "op": "add_sr",
     "ids": [
      "p3a_sr_cnt"
     ],
     "route": "add_sr",
     "how": null,
     "unroutable": null
    },
    {
     "k": 12,
     "op": "create",
     "ids": [
      "p3a_k_cnt"
     ],
     "route": "primitive",
     "how": null,
     "unroutable": null
    },
    {
     "k": 13,
     "op": "connect",
     "ids": [
      "p3a_w_kcnt"
     ],
     "route": "const_sr",
     "how": "unique live name '' on loop #637 (tracked index 27)",
     "unroutable": null
    },
    {
     "k": 14,
     "op": "create",
     "ids": [
      "p3a_inc"
     ],
     "route": "primitive",
     "how": null,
     "unroutable": null
    },
    {
     "k": 15,
     "op": "connect_term_uid",
     "ids": [
      "p3a_t_in",
      "p3a_w_cnt_in",
      "p3a_w_cnt_inc"
     ],
     "route": "connect_term_uid",
     "how": "gscript.connect_term_uid(target, sink_uid, src_uid) - OpConnectTermUid_v0, any terminal -> any terminal by uid; the register inner face <-> node in a case frame makes ONE SelectorTunnel (R1/R2, diag_c124_p3a_scratch.log:53,61); junk Invokes purged inside the verb",
     "unroutable": null
    },
    {
     "k": 16,
     "op": "connect_term_uid",
     "ids": [
      "p3a_t_out",
      "p3a_w_inc_out",
      "p3a_w_out_r"
     ],
     "route": "connect_term_uid",
     "how": "gscript.connect_term_uid(target, sink_uid, src_uid) - OpConnectTermUid_v0, any terminal -> any terminal by uid; the register inner face <-> node in a case frame makes ONE SelectorTunnel (R1/R2, diag_c124_p3a_scratch.log:53,61); junk Invokes purged inside the verb",
     "unroutable": null
    },
    {
     "k": 17,
     "op": "case_frame_wire",
     "ids": [
      "p3a_w_true_pass"
     ],
     "route": "case_frame_wire",
     "how": null,
     "unroutable": null
    },
    {
     "k": 18,
     "op": "create",
     "ids": [
      "p3a_qr"
     ],
     "route": "primitive",
     "how": null,
     "unroutable": null
    },
    {
     "k": 19,
     "op": "case_frame_wire",
     "ids": [
      "p3a_w_qr_x"
     ],
     "route": "case_frame_wire",
     "how": null,
     "unroutable": null
    },
    {
     "k": 20,
     "op": "create",
     "ids": [
      "p3a_k20"
     ],
     "route": "primitive",
     "how": null,
     "unroutable": null
    },
    {
     "k": 21,
     "op": "connect",
     "ids": [
      "p3a_w_k20"
     ],
     "route": "const",
     "how": "order-proof",
     "unroutable": null
    }
   ]
  }
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
?윟?윟 **FIRST ACT of cycle 124 = the case-tunnel tool, then ring P3a ??`docs/d1-loop12-17-split-plan.md` Pre-decided 249(c)(d) (read 246??49).**
   - Step 1 (LabVIEW tooling card, PD249(d)(f)): no existing function reaches a case tunnel's INNER face in a given frame (123-9 measured it: `tools/bench/diag_c123_casetun.log:69-70`). Build a NEW op that returns a tunnel's inner terminal for a frame and wires inner ??inner in that frame, with its hygiene record (??2,000 calls). Then add the `frame` field for case-tunnel faces to stageplan/stagesim/stagexec, prove the True-frame pass-through on a P2b byte copy, and add the same junk-`Invoke` purge that `case_wired` has to `connect_nested_v1` / `connect_from_wire`. Self-tests.
   - Step 2 (P3a): resume from `tools/bench/plan_ring_p3a_in.json` (25 actions on the real P2b graph `graph_ring_p2b_20261001_154542.json`; only action 20's addressing changes). Then: FINAL plan, census and Error List predictions, `tools/recipes/stage_d1_ring_p3a.py`, dry + prerun (census line X15) + prior-art, `--scratch-required` (exit 3 expected), the scratch run on a P2b byte copy, ONE launch ??`claudeDev\D1_ring_p3a_<ts>.vi` + `errorlist_expected_D1_ring_p3a_<ts>.json`. Card flags `gui: true`.
   - P3a, in loop 1.1 (While `#637`, body `639`): `Wait (ms)` 1; a previous-BufNum shift register (BufNum is I32 ??initial ?? from `DonorRingConst_v0` `#249`) + `Equal?` + a case (True = duplicate, count passed through; False = new frame); a new-frame counter register (I32, initial 0) incremented in the False frame; `i = count mod 20` (`Quotient & Remainder`).
   - Offline slot beside Step 1 or 2 (PARALLELISM RULE above): only the fact census of the ORIGINAL VI. No gate edits while a LabVIEW card is live.
   - After P3a: the Flat Sequence creator (a NEW op with its hygiene record, PD248(c)) in its own LabVIEW card, then P3b. P3b's size waits for the user's answer to **D-2026-10-01-01**; if it is unanswered when P3b is ready, P3b is one step with a full scratch run first (PD246(d)).
- **CYCLE 123 in brief ??P2b DELIVERED (the new bed); the image types match; P3 is designed; three tools built:**
  - 123-1 PASS 7/0: `claudeDev\D1_ring_p2b_20261001_140658.vi` md5 `652b1447??. ONE launch 41/0; Error List 54 == pin; the expected file reverdicts OK (PD246(a)). Broken-file count: 1 of 6. All three `IMAQ Create` Image Type rings read 0, so the slot copy converts no pixels (PD246(b)).
  - 123-2 BLOCKED (offline): P3 facts and step list (`tools/bench/ring_p3_steps.md`). P3 is about 74 rows, and two routes were missing. The design is decided in PD246(c): flat-sequence order, local read-modify-write, initialised registers, `Equal?`, and the counter in the new-frame frame.
  - 123-3 PASS 6/0: a shift register's initial value can now come from a constant, built on existing ops (`gscript.sr_init_const`, route `const_sr`, donor `claudeDev\DonorSRInit_v0.vi`). Also measured: the `Equal?`/`Increment`/`Quotient & Remainder` donors, and the For exit gives an indexing tunnel (PD247).
  - 123-4 PASS 14/0 (offline) + 123-7 PASS 7/0: the census device from the violation decision of 2026-10-01 13:56 is BUILT.
    - Files: `tools/census_predict.py` + `tools/bench/census_samples.json`.
    - `stage_prerun --prerun` line X15 fails a declared class count that differs from the measured samples. An unmeasured count forces the scratch run. stagekit's dry-mode census line prints `UNVERIFIED-DRY`.
    - Cycle 122's +1 now fails offline; P2b's prerun passes 14/0.
  - 123-5 FAIL 12/1 ??123-7 PASS: the case creator with a wired selector (`gscript.case_wired`, route `case_wired`, donor `claudeDev\DonorCase_v0.vi`) works and can be used in plans. The FAIL was a wire-count gate on a branch (review `archive/peer/2026-10-01-c123-5-s1a-branch.md`, ACCEPTED). The Flat Sequence creator is NOT built (PD248(c)).
  - 123-6 PASS 5/0: STATUS.md 601 ??95 lines; the history is VERBATIM in `archive/2026-10-01-status-cycle123-relocate.md`.
  - 123-8 FAIL 1/1: the real P2b graph is read (`tools/bench/graph_ring_p2b_20261001_154542.json`; BufNum is I32) and the P3a plan input has 25 actions. Its stagesim check failed on a TOOL GAP: the counter's pass-through wire in the case's True frame cannot be written in the plan format. Decided in PD249(c): keep the design and build the tool, because P4 needs it too.
  - 123-9 FAIL 13/1 (a time-boxed tool card): input and output tunnels on the case were measured (`Is Broken?` False), but no existing function reaches a tunnel's inner face in a given frame. Decided in PD249(f): build that op (P4 needs it too) rather than redesign the counter. No code was half-changed (the code step was not started).
  - Carries:
    - `docs/d1-build-plan.md` is still `status: current` (lint L5);
    - `decisions_pending.json` item 13 (D-2026-09-28-01, the chat's) still breaks the 300-character limit;
    - cycle 122's carries: stagekit donor declaration, `_check_units`, the reverse direction of RULE-OFFLINE-CARD, `requires` for routes/donors, fp-10.
  - **User decision open: D-2026-10-01-01** (the 6-file limit vs 15??5 rows per step). Recommendation: keep 6 and allow ~40 rows per step for P3b/P4, each with a full scratch run.
- **CYCLE 122 in brief RELOCATED VERBATIM ??`archive/2026-10-01-status-cycle123-relocate.md` 짠6** (its carries are repeated in the cycle-123 brief above).
- **CYCLE 121 in brief and the cycle-121-start FIRST ACT block (chat-P3, then the ring-buffer plan) RELOCATED VERBATIM ??`archive/2026-10-01-status-cycle123-relocate.md` 짠3.**
?뵶 **USER RULE, re-confirmed 2026-09-28 15:3x (chat) ??the POOL's overload branch (D-2026-09-28-01, now ANSWERED): the user decided this on 2026-09-15 and it has a PRIORITY ORDER.** (1) NO CORRUPTION: an image and its buffer number change together and the consumer verifies them ??a pixel/number mismatch is corruption. (2) LATEST-WINS: when tracking falls behind, discard the queued backlog and read the newest frame ("?먮? 踰꾨━怨??덈줈 ?ㅼ뼱?ㅻ뒗 ?꾨젅?꾩쓣 ?쎈뒗 寃껋씠 媛??諛붾엺吏곹븿. ?대뒗 ?쒓퀎???곗씠?곗쓽 ?꾨??깆쓣 ?꾪븿"); a gap recorded by the buffer number is fine. (3) FALLBACK: if (1)+(2) cannot be made provably safe, acquisition and tracking may stay in ONE sequential loop. **The planned "full Q_work ??skip the newest read" (d1-build-plan.md 짠9, PD233/234) VIOLATES (2)** ??the judgement session re-decides the overload branch against this order before any real run (memory `prefer_the_freshest_frame_over_a_complete_backlog`, `docs/decisions.md:25`). Structure already built (the 20-slot pool) may stay; only the overload behaviour changes.
?윞 **CARRY (from the 2026-09-25 verification review `archive/peer/2026-09-25-hyp-lintverify-20260925.md`, not blocking): card flags are checked only on the top-level command (a child process could reach LabVIEW under labview=none); a stage run launched outside bgrun is not counted by the retry cap; a bgrun record failure is only logged (`tools/bgrun.py:219-220`). Close in a tooling cycle, deliverable-first.**
current-bed: D1_ring_p2b_20261001_140658.vi
<!-- ^ machine key read by tools/errorlist_check.py current_bed_text(); without it the bed is chosen by mtime among D1_*.vi names in this file, and the newer D1_s1_kswap_* would silently take over (review archive/peer/2026-09-26-c88-reuse-stalepin.md). Change it only when a new bed is accepted. Moved 2026-10-01 by cycle 123 (PD246(a)): ring P2b accepted (md5 652b1447ebbda761a7d5ba36455a0fa1, expected Error List tools/bench/errorlist_expected_D1_ring_p2b_20261001_140658.json). -->
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
VERDICT {"schema":"verdict/1","id":"priorart-c124-6-ring-p3a","verdict":"<one of: novel | settled-already>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

The answer is **novel**. Nothing in the project files duplicates this work, refutes it, or contradicts it. The recipe is the P3a build that the design decisions call for, and it uses tools the project has already built and measured.

**PART A: the direction**
- **A1 (already settled):** Yes, and it was settled *for* this work, not against it. The P3a design comes from `docs/d1-loop12-17-split-plan.md:2408-2433` (PD246(c)(d), 2026-10-01). Those lines set the shape:
  - two shift registers on While `#637`, initialised from constants on `686`;
  - `Equal?`, with True meaning a duplicate frame;
  - the counter is incremented in the False frame and passed through in the True frame;
  - the slot number is the count mod 20;
  - `Wait (ms)` 1.

  The routes come from `:2544-2549` (PD250(c)(d)). This is the decision the recipe carries out, so it does not count as prior art against it.
- **A2 (already refuted):** No. The earlier failures were tool gaps, not a wrong direction:
  - 123-8 failed because no tool could address the face of a case tunnel in a given frame (`:2504-2510`).
  - 123-9 failed for a related reason: no existing tool could reach a case tunnel's inner face in a given frame (`:2520-2529`).

  Both rulings kept the counter design (A5) and built the tool. PD250(a) says that tool is now built (`:2532-2540`).
- **A3 (contradicted):** No.
  - The plan's I32 −1 constant from `DonorRingConst_v0` `#249` matches PD249(b) (`:2500-2502`), which supersedes the U32 possibility in PD246(c) A3 (`:2419`).
  - The I32 0 counter constant from `#248` matches PD247(d) (`:2460`).
  - The `$work` donors `Equal?` `#10019`, `Increment` `#1978` and `Quotient & Remainder` `#2136` have the terminal sets measured in PD247(b) (`:2452-2454`).
- **A4 (unread evidence):** No. The recipe's docstring cites PD246–250 and `diag_c124_p3a_scratch.log:53,61,71,77`, which are the right sources.

**PART B: the build**
- **B1/B3 (already built, or a helper exists):** The build reuses existing helpers rather than duplicating them: `gscript.connect_term_uid` (`tools/gscript.py:4903`), `case_frame_wire` (`:4949`), `case_wired` (`:4840`) and `sr_init_const` (`:2241`). It also follows the `stage_d1_ring_p2b.py` executor pattern. The review was triggered as "new-op", but the only new op, `OpConnectTermUid_v0`, was built with its hygiene record in card 124-1 (`:2533-2534`). The recipe itself says "No new op" (`tools/recipes/stage_d1_ring_p3a.py:9`).
- **B2 (already failed):** No launch of this recipe has been made. The only logs are a dry run and a pre-run check; the dry log reports PASS 1/0 twice (`tools/bench/stage_d1_ring_p3a_dry.log:82,165`). One thing to look at, outside prior-art scope: a dry pass of only 1/0 suggests the run stopped after the L0 gate and never executed the plan.
- **B4 (already measured):** Only the parts were measured. Each route was measured once on a scratch copy: R1/R2 (one SelectorTunnel), R3 (wire +1, no tunnel) and R4 (a branch, census {}) (`:2536-2539`). The full P3a build on the P2b work VI has never been measured.

**PART C: the user's design rules**
- **C1:** No contradiction. The two places worth checking both follow the rules:
  - **Control signals by local variable, never by queue (U4):** the new registers are local to loop 1.1, and the plan creates no queue.
  - **The camera loop must never wait (U6):** the `Wait (ms)` 1 has no data dependency on the frame path. PD246 lists U6 as a rule it relies on (`:2396`), and the ring design keeps the camera loop from ever waiting on loop 1.2 (`:2257`).
- **Original computation unchanged (U1):** no number computed per bead is touched. This step adds control logic only.

PRIOR-ART: novel

VERDICT {"schema":"verdict/1","id":"priorart-c124-6-ring-p3a","verdict":"novel","alternative":"Executes the design settled in PD246(c)(d)/247/249/250 with already-built tools (connect_term_uid, case_frame_wire, case_wired, sr_init_const); no duplicate, refutation or user-rule conflict found.","discriminating_test":"Scratch run on a P2b byte copy: ST gate (2 SelectorTunnels, one inner face per frame) and R4 (Q&R.x on Increment.x's wire) pass, as R1-R4 did in diag_c124_p3a_scratch.log:53,61,71,77.","violations":[],"sources":["docs/d1-loop12-17-split-plan.md:2408-2433","docs/d1-loop12-17-split-plan.md:2500-2510","docs/d1-loop12-17-split-plan.md:2520-2549","tools/gscript.py:4903","tools/gscript.py:4949","tools/recipes/stage_d1_ring_p3a.py:9"],"note":"Merit, not prior art: the dry log shows only 1 gate PASS (stage_d1_ring_p3a_dry.log:82,165); check that the dry run executed the plan beyond L0."}

## Sources

(extract from answer)

## What was done with it

(cycle 129 judgement, 2026-10-02 01:2x — owed since cycle 124; its placeholder held card 129-1's prior-art dispatch at guard_peer)
- `PRIOR-ART: novel` accepted; the build went ahead. P3a was delivered by card 124-8: scratch 22/0, ONE launch 22/0,
  census == prediction, Error List 55 (`claudeDev\D1_ring_p3a_20261001_180540.vi`, md5 `4dfa44aa…`; STATUS cycle-124 brief).
- B2's note (dry PASS 1/0 only): consistent with 124-7, whose scratch stopped at op 1 because created-node `term_class` was
  undeclared in the plan; 124-8's corrected plan ran every row in the scratch and in the launch.
- B4 (only the parts measured): the full build was then measured by 124-8's scratch run before the launch.
