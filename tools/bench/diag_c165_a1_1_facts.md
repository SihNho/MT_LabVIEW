---
type: facts
status: current
date: 2026-10-10
card: 165-1-1
---
# 165-1-1 facts (offline, no LabVIEW): stub gates PASS; PRECEDENT FAILS (diag_c161:97's source #3934 was UNWIRED); route + self-test + r_in rows done
## 1. Hashes (prep_c165_a1_1_hash.log 10/0; prep_c165_a1_1_pre.log 5/0)
- VI claudeDev\D1_ring_p5s02d_20261010_152518.vi 6dcd5c3d506f69947a5ce259ccbe2221 (bytes only, not opened); graph_ring_p5s02d_20261010_154830.json 2a5fa0c40866f88111d3ab14e5f9c32d
- errorlist_expected_D1_ring_p5s02d_20261010_152518.json c74200f2d75b3139ee1f8ca477cd8470; memory_model.json ff0fabca220686e7222cfcb27aa622cd
- r_in before 9dadb0c1d3faeeb52f109a0af36929b5 (kept at %TEMP%\c165_a1_1\plan_ring_p5s02r_in_9dadb0c1.json), after 0b8959833a6e37259f3cadf4fc7c9ea8
- Step-4 BINDING RECORD: diag_c164_p5s02d_scratch.log 388a86d386ddc91dc23942db40916d85, STEPX `bound` lines :137 (-1: 12169), :153 (-3: 12170),
  :184 (-9: 31756, -10: 31764), :193 (-15: 31773), :208 (t_k3o -18: 31803 = OK3), :216 (t_k3i -23: 31807); run JSON diag_c164_p5s02d_scratch.json 49da3052.
- stagexec before a4df7e15 (pinned copy %TEMP%\c165_a1_1\stagexec_pre.txt; git HEAD is 69b1a301, NOT the pin), after 6ea6637f; stagesim 95a162ba and stagekit dd57c1ca UNCHANGED.
## 2. Stub gates from graph 2a5fa0c4 (prep_c165_a1_1_explore.log:5-8, read before any edit) - PASS
- w10362: exactly 1 row = t8776 'file progress' InnerTerminal of LoopTunnel #5204, frame 23405, is_source false. w25232: exactly 1 row = t24342 InnerTerminal of #10404, 23405, is_source false.
- #5204 / #10404 obj owner WhileLoop (:10, :12); owners['23405'] = ['WhileLoop', 23041], the only entry for 23041 (:17,19).
## 3. OK3/OK4 source + precedent - FAIL (pass item 3)
- OK3 = SelectorTunnel #31803 (binding :208); its OuterTerminal t31815 'file progress' is_source true, frame 23405, wire 31792 = WIRED (explore.log:13).
- OK4 is not in 2a5fa0c4 (K4 is step 5); in the plan it is wired by w_k4r before w_k4f (plan_ring_p5s02r_in.json:934-939 after the edit).
- **Cited precedent `connect_term_uid #24139 <- #3934` (diag_c161_p5s02b_scratch.log:97) is NOT from a wired source**: plan_ring_p5s02b.json f4520b10's own state
  before that op (sim/ring_p5s02b/step_08_delete_wire.json 3ead0987) has #3934 'error out' is_source true **wire_uid 0** (prep_c165_a1_1_prec.log:9); the run matched that
  state diff 0 (STEPX 04, diag_c161_p5s02b_scratch.log:94). The op was the R1 tunnel group acts [9,10,11] (prec.log:4-6), source = #376's moved, unwired 'error out'.
- Candidate (NOT judged): diag_c127_1_fsinner.log:81-82,92,102 - three `connect_term_uid ... <- #32868` all returned wire 32859, census {}, 'new wires []'
  (a branch off one existing wire), source a Flat Sequence inner face on a scratch copy - a connect_term_uid from a wired source, but another face class.
## 4. Change (made BEFORE step 3 was checked - order of the brief not kept; kept in place, revert copy at %TEMP%\c165_a1_1\stagexec_pre.txt)
- NEW stagexec.loop_inner_face_sink (tools/stagexec.py:6345-6375) + LOOP_FACE_SINK / _STATUS (:6340-6342): dst = LoopTunnel InnerTerminal sink with wire 0, owner one
  While/For loop whose ONE body is the face's frame (tunnel_owner + owners, as loop_inner_face_route :1673-1692), source a WIRED source on that same body; act =
  connect_term_uid(src term, face term), variant loop_inner_face_sink, census None (UNMEASURED). Anything else -> None -> the existing stop.
- Callers: connect_route :1534-1537 (kind 'connect_term_uid'); LVBackend.connect :3229-3230 and LVBackend.branch :3607-3609 -> new LVBackend.loop_face_sink :3676-3683
  (one connect_term_uid via the existing wrapper :3636); SimBackend.connect :4066-4067 and SimBackend.branch :4086-4089 (check.route 'connect_term_uid', act).
- The refusal text is unchanged, now at stagexec.py:1934 (was :1930). compile_plan unchanged. stagesim NOT changed: its op_wire already models the wire as a
  branch onto the source's wire after the delete (stagesim.py:1583-1584,1597; selftest A3), and its route check runs stagexec's SimBackend (stagesim.py:2794-2799).
## 5. Self-test tools/bench/selftest_c165_innerface.py -> selftest_c165_innerface.log:36-69 RESULT PASS 25/0 (:68), BGRUN END rc=0 73 s (run 1 :1-35 = loader error in the test, fixed)
- A1 compile r_in: w_k3f / w_k4f = 'branch' new:OK3 / new:OK4 outer, right after delete_wire (acts 72->73, 83->84). A2 step-5 form of A70 (src #31815) = ['delete_wire','connect'].
- A3 stagesim: w10362 / w25232 sourceless 1-row stubs, Wire object removed; wire #31815 -> face = 'branch' on w31792. A4 (A70 8776, A80 24342) route_on_state =
  'connect_term_uid', src 31815, dst loop 23041 WhileLoop, diag 23405. A5 SimBackend.connect / .branch (#31803 stand-in) = route connect_term_uid, 0 unroutable.
- Stops kept verbatim: S1 wired face t8776 (connect + branch); S2 SelectorTunnel #2451 face t2569; S3 FlatSequenceInnerTunnel #317 face t334 ('is a FlatSequenceInnerTunnel face');
  S4 owner relabelled CaseStructure; S5 unwired source #23444.
- B1 compile pre (a4df7e15) == new, byte-equal: p5s01a ed62e8d6 -> 5f95830f, p5s01b 75a77a00 -> b8b59791, p5s02a 4284c22a -> 46ab662f, p5s02b f4520b10 -> 7f5221aa,
  p5s02c 930699ec -> db6f32a7, p5s02d 97837e2a -> cb601533 (plan md5 -> compile md5). B2 dry_run pre == new, all PASS: 987d8764, 2c0f2238, c7e2753b, 5d39dfcf, 2648d808, 06272b90.
- Regressions: selftest_c157_innerface 13/0, selftest_c158_wire0face 24/0, stagesim selftest 106/0 (G67 negative still FAILS finalize), stagexec selftest 141/0
  (selftest_c165_innerface_reg_{c157,c158,stagesim,stagexec}.log).
## 6. r_in edit (prep_c165_a1_1_rin_compare.log 7/0): 82 -> 84 actions; added ONLY dw_10362 (delete_wire 10362) right before w_k3f and dw_25232 (delete_wire 25232)
  right before w_k4f, key set {id, op, why, wire_uid} == dw_cond / dw_23460; every other action and top-level key JSON-equal; validates stageplan/1. 9dadb0c1 -> 0b895983.
## 7. Side facts
- guard_write on every stagexec edit: "open card 160-c3-2 pins tools/stagexec.py at md5 ddf23a31" - stale before this card (the file was a4df7e15); not re-pinned here.
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| prep_c165_a1_1_prec.log | no JEV-LADDER row (grep jev_gate.log) | - | recorded, returned | FAIL 0/1: #3934 wire 0 |
OPEN: diag_c161:97 is a connect_term_uid from an UNWIRED source; does diag_c127_1_fsinner.log:81-102 (wired FS inner face, same wire back) count as the wired-source precedent, or is a scratch check owed?
OPEN: keep the stagexec change (6ea6637f) in place for the step-5 card, or revert to a4df7e15 until the precedent question is decided?
