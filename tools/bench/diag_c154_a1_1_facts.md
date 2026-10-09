---
card: 154-a1-1
status: current
date: 2026-10-09
---
# 154-a1-1 facts - P5-1 plan NOT made: two queue placements in PD374(a) have no existing route (offline, LabVIEW reads 0)

## Targets read from the real s09 graph 22f967b5 (`diag_c154_a1_1_targets.log`, reader `diag_c154_a1_1_targets.py`)
- `#4866` = FlatSequenceFrame (owners['4866']), frame index 7 of FS `#681` [3628, 81548, 113, 124, 5031, 3121, 1817, **4866**, **686**, 759]; 686 is the NEXT frame (index 8). Holds the P2b initialisers (Num/TransPos/RotPos/FrameIdx/Latest/StopAll/BufDiff ControlTerminals).
- `#2626` BuildArray on 23166: idx 1273 t2813 'appended array' src w0; idx 1277 t4168 'array' <- w30522; 3 'element' sinks wired. Matches PD374(a)/F1.
- `#29724` SubVI on 23166: idx 1215 t29900 'valid' src w30457; w30457 has 7 sinks ('s' of #4577 #4576 #4538 #4586 #4590 #4594 #30398) - the case selector would be the 8th. Matches F5.
- Loop 1.2 = WhileLoop `#10170` (loops[1]), body Diagram `#23166` (owners['23166']=['WhileLoop',10170]), loop on 686 (owners['10170']=['Diagram',686]). Loop 1.7 `#23041` body 23405 not touched.
- No target differs from PD374(a).

## Route gaps (code read; why no plan / rebase / replay / X10 / pred / recipes were made)
1. **Enqueue inside a NEW Case frame has no route.** The only creator is route 'queue' (`gscript.queue_node`, gscript.py:1480-1507), which
   ALWAYS wires `src` (Traverse src_cls[idx] Get Outputs by name) into 'queue'. stagexec real backend: src must be on the node's diagram or the
   diagram must be a LOOP body (`stagexec.py:3085-3089`: "...is not a loop body (queue route: same diagram, or the creator's auto tunnel into a
   loop body - PD234(i))"); a case frame's owner is CaseStructure. Dry backend: src on the same diagram or st.diagrams parent (`stagexec.py:3586-3593`),
   and stagesim the same (`stagesim.py:2318-2342`, st['diagrams'] = plan-made only, `stagesim.py:313`).
   The refnum inside the True frame can only be a case tunnel's inner face, and `_node_end` refuses any non-Node src: "addresses Traverse('Node')
   by uid; ... which is not a Node (a tunnel face / register / constant / panel terminal)" (`stagexec.py:3538-3541`).
2. **Obtain on `#4866` typed DBL 1-D has no Node source.** The same `_node_end` rule refuses a constant as `src` (`stagexec.py:3538`), so neither
   the existing DBL[20] ArrayConstant `#25632` t25623 'x,y,z array' (TransPos init, P2b donor DonorRingConst_v0 uid 101) nor a new donor-101
   constant can type the Obtain. Node outputs on #4866 (`targets.log`): #1986/#2359/#5426/#5556 arithmetic, #4865 SubVI (cosine windows),
   #6288 SubVI (index arrays), #24144 Property 'Value', #10330 Q&R; their types UNMEASURED and none is the element by design.
3. No other placement fits PD374(a) with existing routes: an Enqueue directly on 23166 would need its src on 686 (the Obtain is on 4866) and
   23166 is not plan-made (stagesim refuses); the `primitive` route (create_primitive_nested, donor file + uid) has NO measured Enqueue/Obtain
   donor (claudeDev Donor*_v0.vi set: Pool, RingConst, SRInit, Case, Fs, ErrSel x2, I32Max, BoolF, RAS1D; no queue primitive recorded in any
   `tools/bench/*.json` except op/library paths).
- Parts with existing, proven routes (not exercised here): case_wired on an existing loop body from a node output (P3a #639), add_shift_reg on an
  existing loop (P3a 637), const_donor I32 0 (DonorSRInit_v0 #248) / I32 -1 (DonorRingConst_v0 #249), indicator born_on const on 4866 (P2b),
  local_write (CREATE_ROUTES `stagexec.py:244`), case tunnels + case_frame_wire (P3a).

## Not done (return condition "a missing route/op kind", brief step 3 + card rule 2)
plan_ring_p5s01*.json, sim, rebase, replay, X10, pred, licence, recipes, dry/prerun: none created. No tool edited.

## Invariants (md5 now = card pins): stagekit 604529e8, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, stagesim 78b8d5a1,
vigraph a7eb58c7, graph 22f967b5, memory_model 6f2b5687, ring-p5.md 58f168cb; s09 VI never opened. P4 s09 plan 9d622c95 / recipe 4be3ff28
untouched (not written by this card). LabVIEW processes at end: 0.

OPEN: which route closes both gaps - e.g. a donor VI holding Obtain/Enqueue(/Dequeue/Release) primitives for the existing `primitive` route
(unwired create, then wire / case_frame_wire), or a queue route variant whose src may be a case-tunnel inner face / a constant - a tool card.
