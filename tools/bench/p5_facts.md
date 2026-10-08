---
type: facts
status: current
date: 2026-10-09
card: 153-a1-1
---
# P5 fact census F1..F8 (PD370(f), docs/d1/ring-p4d.md:141-161) - facts only, no design
Sources: s09 graph `graph_ring_p4s09_20261009_062044.json` 22f967b5 (bed eb1d0f31), EL expected 5146f980 + its read 080255ad,
S1 wiki `docs/wiki/subvi/D1_s1_copy.json` 3e3d23ce, `docs/wiki/subvi/save trace.json`, `memory_model.json` 6f2b5687.
Readers: `tools/bench/diag_c153_a1_1_census{,2,3,4}.py` -> `.log` (offline, json only). **LabVIEW reads: 0**. Detail: `p5_facts.json`.

## F1: each input terminal of the file writer `#376` in S1: source, wire, type; its s09 location and wired state
S1 side `c73_l7r_facts.log:92-150`; s09 side `diag_c153_a1_1_census.log:4-15`, `census2.log:3-32`. #376 sits on 23405 = loop 1.7 body.
| t | terminal | S1 source (wire) | type | s09 |
|---|---|---|---|---|
| 2 | error in | LSR #1108 (w4880), init #4910 | UNMEASURED | LSR #24133 (w24285), init #4910 on 686; #1108 gone |
| 5 | current frame data array in | #2626 BuildArray 'appended array' t2813 (**w4517**) | Array1D<DBL> `facts_c120_types.json:194-227` | **UNWIRED** (t5754 w0); #2626 is in **loop 1.2** (23166), its output t2813 w0 |
| 6 | cal cluster path | LoopTunnel #3644 (w3629) | UNMEASURED | in-tunnel #24357 <- #1748 FS inner tunnel (686) |
| 7 | frame index | #637 iteration terminal i #644 (**w3268**) | I32 `facts_c120_types.json:70-95` | **UNWIRED** (t5763 w0); #644 still in **loop 1.1**, w29454 -> 6 sinks |
| 8 | saved file refnum | ControlReferenceConstant #3052 'File # Saved' (**w1397**) | control refnum (descriptor UNMEASURED) | WIRED w10394 <- #3052, which now sits **inside 1.7** |
| 9 | file size | LoopTunnel #2294 (w1581) | UNMEASURED | in-tunnel #24361 <- #2484 FS inner tunnel (686) |
| 10 | total data array in | LSR #51 (w3497), init #781 | UNMEASURED | LSR #24187, init #781 'initialized array' |
| 11 | selected path | LoopTunnel #5096 (w5090) | UNMEASURED | in-tunnel #25223 <- #4693 FS inner tunnel (686) |
Outputs: t0 -> RSR #24083 -> #6384 'error in'; t1 -> RSR #24150 -> #2048; t3 -> indicator #3453 (in 1.7) + tunnel #5204; t4 -> tunnel #10404 -> #6384.
- The S1 t7 value is also a per-slot value in s09: #644 -> SelectorTunnel #29440 -> FS #29411 -> FrameIdx write #6859 (`census4.log:3-5`,
  `census3.log:16-19`); 1.2 reads it as #30240 FrameIdx[min slot] element w30278 -> #29240/#10068 'x' (`census2.log:132`).
- UNMEASURED: types of t2/t6/t9/t10/t11 and t8's refnum descriptor - cheapest: `gscript.read_term_type` on #376's 12 terminals, ONE read of an s09 byte copy.

## F2: the 45 items of the s09 Error List, each mapped to an object uid; 1.7's open rows
| class (expected file) | n | object |
|---|---|---|
| Build Array: Contains unwired or bad terminal | 1 | #2626 by the file's cite (`expected.json:17-18`); s09: 4 inputs wired, output t2813 w0 |
| two terminals of different types (1D Void -> 1D cluster of 2) | 1 | UNMEASURED (cite "B1-new src+sink RBW wires" `:25-26`; detail `el_read.json:111`) |
| wire not connected to anything (9+11+1+1) | 22 | s09 has exactly **22 termless Wire objects**: 23556 31166 31059 32890 29787 11352 28847 10908 9868 17393 17287 10573 10312 5709 9012 4906 10187 6363 6096 730 5975 5637 (`census.log:118-119`); pairing per item UNMEASURED |
| Wire: Wire has loose ends (20+1) | 21 | 2 one-sided wires: w12256 (#11608 src only), w10103 (#10114 src only) (`census.log:120-121`); 19 UNMEASURED |
- **class level; per-item uids unmeasured** (PD371(a), `docs/d1/ring-p4d.md:167-171`). **Per-item uid: UNMEASURED.** Every read item has `uid: null`, `uid_route: "needs a Selection List[] 6349400 op (unbuilt)"` (`el_read.json:96-98`).
- 1.7's open rows: plan open rows (376,'current frame data array in') and (376,'frame index') (`plan_ring_p4_s09v18.json:73-82`), both w0
  in s09. No expected entry cites #23041/#376; save trace.vi is not in `subvi_requiredness.json` (`census3.log:64`) => 0 of 45 items mapped to 1.7.

## F3: loop 1.7 `#23041` in s09: body, shift registers, stop source, wait/timing, every node per iteration
`census.log:17-35`, `census2.log:3-36`. Body Diagram #23405 on 686. Per iteration: #376, #3052 const, indicator #3453 'file progress', #23042 Equal?.
- SR 1: RSR #24083 / LSR #24133 = #376 error out -> error in; init #4910 ClusterConstant (w4969); exit -> #6384 'error in' (w9610).
- SR 2: RSR #24150 / LSR #24187 = #376 total data array out -> in; init #781 'initialized array' (w3543); exit -> #2048 'array' (w5050).
- In tunnels #24357 cal path, #24361 file size, #25223 selected path, #23501 (stop scaffold); out tunnels #5204 file progress, #10404 file #.
- Stop: cond t23456 <- #23042 'x = y?', x and y both on w23460 from #23501 (outer w23519 <- #8486 'x+1', 686); Stop-if-True (`ring-p4.md:263`).
- `i` t23444 unwired. **No Wait node** in the body.

## F4: the ORIGINAL's call of `#376`: structure, condition, order vs tracking kernel, what 'frame index' is
- Enclosing: S1 owner = Diagram #639 = While #637 body, **no case** (`c73_l7r_facts.log:92`); original: diagram 43 WhileLoop
  (`docs/main-vi-subvi-identity.md:98`, `docs/main-vi-stop-and-save.md:125`). No enable input in its pane (`save trace.json:11-84`) => every #637 iteration.
- Inside save trace.vi (`save trace.json:816-1066`): Q&R(frame index, file size); remainder -> Replace Array Subset 'index (row)' (accumulate,
  every call); Equal?(remainder, file size - 1) -> case; frame d110 = save N xyz traces.vi #116 + Property 'Value' <- floor(x/y) on
  'saved file refnum'. => accumulate every frame, write every 'file size' frames. Which selector value is d110: UNMEASURED (d101 only passes error).
- Order: after #5058 by data: #5058 'x,y,z array out' -> #2626 array|0 -> #376 t5 (`ring-p4c.md:325-326`); no #376 -> #5058 path (`c73_l7r_facts.log:118-127`).
- Frame index = **#637 loop i** (#644, I32), the only source of w3268 (`cycle27-plan.md:3748-3751`). Not BufNum. BufNum - LastBufferNumber
  (#5119 x-y, U32 `facts_c120_types.json:100-124`) goes into the record as #2626 element|0; element|1 <- #30117 Value, |2 <- #4580 Value.
- Doc conflict: `docs/NAMES.md:112` and `docs/fixture-recording.md:18` say frame index is fed by #5119; the graph reads above say #637 i. **Corrected 2026-10-09 (card 153-a2-7)**: both lines now carry a dated note (frame index <- loop `i`, w3268 <- #644/#639, not #5119; `diag_c153_a2_6_orig_read.log:11-13`, `cycle27-plan.md:3748-3751`).

## F5: loop 1.2 in s09: the valid-frame boolean and the rolled-back Select outputs: uids and terminals
`census.log:37-61`, `census2.log:37-71`. RingSeqCheck_v0 SubVI **#29724** on 23166: n1 t29996 (<- W1 tunnel #30094 'min Num'), n2 t29970
(<- FS tunnel #30743 t30768), last t29962 (<- LSR #29548), Latest t29959 (<- Local #30001), discards t29952 (<- LSR #29655);
**valid t29900 w30457** (7 sinks = the Selects' `s`), next last t29907 -> RSR #29403, next discards t29903 -> RSR #29648.
The rule n1==n2 AND n1>last lives inside `RingSeqCheck_v0.vi` (PD293(c) `ring-p4.md:33`), not in the s09 graph.
| Select | t <- | f <- | output -> |
|---|---|---|---|
| #4538 | tunnel #9227 | LSR #10544 | t25638 -> RSR #9603 |
| #4576 | tunnel #29616 | LSR #25582 | t30613 -> RSR #25545 |
| #4577 | #9647 AND | Local #30675 reseed flag | t30661 -> indicator t25557 'autofocus reseed flag (1.2 to 1.1)' |
| #4586 | SelectorTunnel #11336 'Value' | LSR #25382 | t30408 -> RSR #25371 + indicator t25573 'autofocus reset count (1.2 to 1.1)' |
| #4590 | #5058 'Bead is good? array out' | LSR #25344 | t30417 -> RSR #25339 |
| #4594 | #5058 'x,y,z array out' | LSR #25240 | **t30473 w30522 -> #2626 'array' t4168** + RSR #10850 |
| #30398 | #5058 'pos in cal image out' | LSR #23792 | t30424 -> #10757 'array' + RSR #23508 |
- #2626's elements t2832/t4160/t4165 <- #30300 BufDiff / #30119 TransPos / #30216 RotPos [min slot] (raw slot reads, no Select); 'appended array' t2813 w0.

## F6: how loops 1.2 and 1.7 stop in s09 (StopAll local, `stop (end)` latch) and their shutdown order
`census.log:62-116`, `census3.log:46-48`.
- 1.1: cond t648 <- #11639 CompoundArithmetic (w3457); 'stop (end)' t642 (Mechanical Action 4 = latch, `ring-p4.md:263`) w6929 -> #11639 + Local
  **#6899 StopAll write** every 1.1 iteration. All bed While loops are Stop-if-True (`ring-p4.md:263`).
- 1.2: cond t23246 <- **Local #6902 StopAll** read (w29405). W1 = While #16483 (body 29699) in 1.2: cond <- #29818 Or(#29719 'found', Local #29811 StopAll).
- 1.7: cond <- #23042 x=y on one wire (scaffold); **no StopAll read** in 1.7.
- Order: no wire links 1.7's stop to StopAll or 1.2; #6384 (686) waits on 1.7's exit values (RSR #24083/#24150). Run-time order UNMEASURED (never run).

## F7: ops / routes / donors that created and removed the pool queues, hygiene records, `protocol.py requires`
- Created: QRT POOL `tools/recipes/stage_d1_qrt_pool.py`, plan `plan_qrt_pool.json` routes 'queue' x3 (:733-753), `stage_d1_qrt_pool.log:262` 21/0.
  Objects: Obtain Q_free #23105, Q_work #23118 (element data type <- #13938 'New Image', w14741 branch), Enqueue #23136 in For #23093,
  I32 20 constant #26017 (max size, donor #214), queue LoopTunnel #25898 (`plan_ring_p2a_make.log:3-4`).
- Removed: P2a 4 delete_wire + 4 delete_object, retire [23136, 23105, 23118, 26017], auto-removed [25898] (`plan_ring_p2a_make.log:9`);
  `stage_d1_ring_p2a.log:161` 27/0.
- Ops/routes: `gscript.queue_node` (`gscript.py:1480`, obtain/enqueue/dequeue/release `:1475-1476`); stagexec route 'queue' obtain/enqueue
  (+dequeue, card 120-3) `stagexec.py:252-257`; **no stagexec route for release**. Functional test `test_opqueue.log:43-51` 7/7.
- Hygiene: **no record** for OpQueue*_v0 in `tools/bench/op_hygiene/` (12 files) and none found by grep.
- `protocol.check_requires` (in-memory list, no card file): **11/11 FOUND** - 4 OpQueue*_v0.vi, verbs queue_node / delete_object
  (`gscript.py:2808`) / delete_wire (`stagekit.py:672`), 4 `opqueue_*_labels.json` (`census3.log:3-14`). Lint: `stage_prerun.py:1110-1125`.

## F8: the s09 load (596.7) and the X10 headroom for a P5 session, quoted from `memory_model.json`
- `load_by_vi[eb1d0f31…]` value **596.7** (cite `diag_c152_b3_1_graph.log:24`); start_rule = load + op0_read_mb **5.9**; formula
  `peak = start + R*2.53 + N*(0.58 + 0.8) + 17.4`; fail_above_mb **680.0**; memstop_mb **695.0** (`census3.log:65-76`).
- P5 headroom: UNMEASURED - memory_model.json stores no P5 figure; cheapest = `stage_prerun` X10 on a P5 plan.
**Invariants** unchanged, 11/0 before and after (`diag_c153_a1_1_md5_before.log`, `_after.log`): stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, stagesim 128bacfb, vigraph 13be0847, s09 eb1d0f31, graph 22f967b5, EL 5146f980, memory_model 6f2b5687.
