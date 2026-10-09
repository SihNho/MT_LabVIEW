---
type: facts
status: current
date: 2026-10-09
card: 157-a1-1
---
# Card 157-a1-1 facts: PD381 (b)(c)(d) built offline; self-test 13/0; op lists equal; only change in the suite = two stagekit md5 pin gates
## Built (stagexec 25a1494c -> 69b1a301, stagekit aec03c6c -> 0d8f6d25; stagesim eb99c6ba and addrcheck 207beb0d NOT edited)
- (b) owner of the stop text = stagexec (`_triple`, stagexec.py:1786). New `loop_inner_face_route` (stagexec.py:1626), called once from
  `connect_route` (:1563) just before the nested triple: a LoopTunnel INNER face, wire 0, whose owner (tunnel_owner) is ONE While/For
  loop with one body == the face's frame -> 'cfw' with info src_diag/src_loop/src_loop_cls/src_wire0. Wired faces never reach it (:1489-1490).
- `route_on_state` (stagexec.py:1648) = connect_route on a state with chosen faces at wire 0 (was a private copy in diag_c156_a3_1_route.py:64-79, left as the record).
- (c) READ_KINDS = ("move_in",) (stagexec.py:2025); `fate_lines` (:2036) called by Executor.run right after a checkpoint read of a
  READ_KINDS op (:2568); a non-checkpoint move_in logs `FATE-UNREAD` only (:2546). Sink terms = the wire's sink rows in step n-1;
  a term absent from the read prints `?`. step=<n> is the PLAN step (p5s02a ops 10-12 = acts [10],[11],[12], selftest r3 log:27).
- (d) `checkpoint_ops` (stagexec.py:2028) = {0, last} | BIND_KINDS ops | READ_KINDS ops; RingSession calls it (stagekit.py:1929).
## Measured (before: prep_c157_a1_1_before.log BGRUN END rc=0 820 s; after: prep_c157_a1_1_after.log 9/0, rc=0 1009 s)
- Op lists p5s01a 14 / p5s01b 8 / p5s02a 17 EQUAL; all 200 stored plans compile EQUAL (after.log A1, A2).
- CHECKPOINTS before -> after: p5s01a and p5s01b unchanged (no move_in); p5s02a [..,9,15,..] -> [0,1,3,6,8,9,10,11,12,15,16,17];
  stage_d1_ring_p5s02 (plan 285cb59a, also move_in 10-12) gains 10,11,12 too (after.log A3/A4).
- Suite before == after: stagexec 141/0, stagesim 106/0, c120 1/0, stagexec_gate 13/0, tunnel_naming 21/0, fs_c126 13/0, addrcheck
  selftest_s5 22/0, t7_ring 35/0; failing the same before and after: case_frame_c124 28/1 (V02), t6_regress 9/2.
- CHANGED: selftest_c156_passwire 20/0 -> 19/1 and selftest_c155_basecase_frame 21/0 -> 20/1; the one failing gate in each is the md5 PIN
  of stagekit.py (aec03c6c, selftest_c156_passwire.py:161, selftest_c155_basecase_frame.py:206); every other gate passes as before
  (suite out files under tools/bench/sim/ring_p5s02a_c157/).
## Self-test tools/bench/selftest_c157_innerface.py -> selftest_c157_innerface_r3.log RESULT 13/0 (:33), BGRUN END rc=0 29 s
- I1/I2: op16 #24360->5760 and op17 #24367->5778, on step_15 and on the executor's prev step (17 / 20): wired 'cfw', wire 0 'cfw',
  same dst (1,1,6) / (1,1,9), body #23405 of WhileLoop #23041 from the graph owners (r3 log:5-11).
- C1 recorded SelectorTunnel source inner face #1479 (#1445) wire 0 -> existing stop verbatim; C2 recorded FlatSequenceInnerTunnel
  #151 -> its existing stop; C3 #24360 with body owner relabelled CaseStructure -> existing LoopTunnel stop (r3 log:13-15).
- F1: dry_run of p5s02a on a synthetic read (#24360 wire 0 after ops 10-15, #24367 after 10-16, #3060 after 10) -> exactly six lines
  `FATE step=10`, src_wire 0 for 3060/24367/24360, kept 24091/24285/24312, sinks 5772/5787/5778/5683/5782/5760 sink_wire 0 (r3 log:17-24).
- F2 unpatched dry run: six FATE lines with the sim's kept wires; F3 synthetic run PASS like unpatched, ops 16/17 routed 'cfw' on reads with
  #24360 / #24367 at wire 0 (r3 log:26). K1 RingSession(p5s02a).CHECKPOINTS == checkpoint_ops == (0,1,3,6,8,9,10,11,12,15,16,17); K2 no
  recipe assigns .CHECKPOINTS; P pins stagesim/addrcheck/plan/step_15 unchanged (r3 log:29-31).
## Side facts
- Launch gate refused the first self-test form (a `connect` override on the SimBackend subclass = "calls connect"): logged fp-77
  (gate_fp_queue.jsonl); the test now records the read instead, no gate change.
- guard_write warned on every edit: open cards 149-a3-3 / 149-a3-4 pin stagexec 1bab9cf9 and stagekit 06b8d844 (stale before this card).
- No LabVIEW process at any point; no tools/hooks edit; no plan / pred / licence / recipe / P5 file edited.
OPEN: wire-0 route returns 'cfw', but LVBackend's cfw act calls `_cfw(int(rs["wire_uid"]))` = `_cfw(0, ...)` (stagexec.py:3135, :3028-3032 wire_source_owner) - with the wire really gone the LabVIEW op has no wire to connect from; which op the live act should use.
OPEN: selftest_c156_passwire / selftest_c155_basecase_frame pin stagekit aec03c6c; (d) required a stagekit edit - re-pin them to 0d8f6d25 (outside this card's write globs)?
OPEN: Executor's required-checkpoint set (stagexec.py:2488) still needs only BIND_KINDS + last; a caller passing its own list without the move_in ops gets FATE-UNREAD, not a refusal.
