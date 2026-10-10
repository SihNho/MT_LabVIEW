---
card: 165-3-1
date: 2026-10-10
status: current
---
# 165-3-1 facts (offline; no LabVIEW) - PASS: PRIME skips the two stub-holding LoopTunnel inner faces (PD402(b)); step-5 plan finalizes
**1. md5 before any edit** (`prep_c165_a3_1_hash.log`, 18/0, python hashlib bytes only): all 16 card inputs == pins; VI claudeDev\D1_ring_p5s02d_20261010_152518.vi
6dcd5c3d506f69947a5ce259ccbe2221; stagexec 6ea6637f, r_in 0b895983, graph 2a5fa0c4, stagesim 95a162ba, stagekit dd57c1ca, stage_prerun 7605116f, stage_shared b688edd4.
No drift. Pre-change copy %TEMP%\c165_a3_1\stagexec_pre.py == 6ea6637f; untouched-set snapshot prep_c165_a3_1_hash_pre.json (hooks, memory_model, VI, inputs).
**2. Change (tools/stagexec.py only, 6ea6637f -> 1d5309f4cc8a5df3bd5bcad2d5c95ca2):**
- NEW `prime_deleted_face_skip(A, ops, checkpoints, i, r, lo=0)` `tools/stagexec.py:6384-6408`: returns a skip record only when the end is a LoopTunnel
  (LOOP_ROUTED) InnerTerminal SINK, its base wire == `wire_uid` of a delete_wire ACTION n < i whose op k_del is dispatched (lo < k_del) and comes before
  the op holding action i, and k_del is a checkpoint (checkpoints None = every op). Otherwise None.
- PRIME pass `tools/stagexec.py:2630-2635`: called just before `be.addr.triple`; a skip is appended to `ex.prime_skips`, logged `  PRIME-SKIP <line>`, and
  the end is not primed; every other end primes as before. `:2602` init; `:2642-2643` report[0]['primed']['skipped'] written ONLY when a skip happened.
- stagesim NOT changed: it has no PRIME of its own (grep PRIME / addr.triple = 0 hits); its route check is stagexec.dry_run (`tools/stagesim.py:2538-2544`).
**3. Self-test `tools/bench/selftest_c165_prime.py` (120 lines) -> `selftest_c165_prime.log:120` RESULT PASS 38/0, BGRUN END rc=0 48 s (:121)**
- (a) make_step_plan (called, prep_c165_a2_1_mk.py:63-65 arguments, outputs in tools/bench/sim/ring_p5s02e/_selftest165p): chosen K3f+K4+K4f, 13 rows,
  MAIN 665.0 (:98); SB REALSIM FINAL 13/13, 0 PROVISIONAL, route PASS, 0 UNROUTABLE (:97, :102); ROUTE k=2 connect w_k3f / k=9 branch w_k4f = connect_term_uid
  (:88, :95); C-OUT, IDS, X8, X17 PASS (:98-101). Self-test plan ab0552c1 (NOT the launch plan; plan_ring_p5s02e.json 20bde81a untouched).
- (b) non-collect SimBackend (be.unroutable = None) Executor: PRIME silent, run completes 9 ops (:107-108). Skip lines (:104-105):
  `PRIME-SKIP end #8776 (LoopTunnel #5204 inner sink, base w10362) of action 2 (w_k3f, op 2): left to its step - w10362 is deleted by checkpointed op 1 (action 1 dw_10362)`
  `PRIME-SKIP end #24342 (LoopTunnel #10404 inner sink, base w25232) of action 13 (w_k4f, op 9): left to its step - w25232 is deleted by checkpointed op 8 (action 12 dw_25232)`
  `PRIME 0 terminal indexes proved at base; ... unprovable []` (:106).
- (c) negatives refuse, each `PRIME: 1 wired end(s) not addressable at base - stop before op 1: ["ADDRESS: #8776 is an INNER face of LoopTunnel #5204: only the
  outer face's owner route is measured (l2a1_faces_81.log)"]`, #24342 still skipped: N1 no delete op (:110), N2 delete of w25232 instead (:111), N2b delete op
  not a checkpoint (:112), N3 delete op after the connect op (:113). Unit: U0 #8776 positive control -> skip (:114); U3 delete ACTION after connect -> None
  (:115); N4 wired SelectorTunnel inner sink t1104 (#1034, w817) -> None (:116); N4 wired FlatSequenceInnerTunnel sink t334 (#317, w357) -> None (:117).
**4. Stored plans + regressions** (logs `selftest_c165_prime_reg_*.log`, all BGRUN END rc=0):
- selftest_c165_innerface.py --pre %TEMP%\c165_a3_1\stagexec_pre.py 6ea6637f: 25/0; B0 pre copy 6ea6637f (:18); compile byte-equal + dry equal, 6ea6637f vs 1d5309f4
  (:19-30): p5s01a ed62e8d6 -> 5f95830f / dry 987d8764, p5s01b 75a77a00 -> b8b59791 / 2c0f2238, p5s02a 4284c22a -> 46ab662f / c7e2753b, p5s02b f4520b10 -> 7f5221aa /
  5d39dfcf, p5s02c 930699ec -> db6f32a7 / 2648d808, p5s02d 97837e2a -> cb601533 / 06272b90 (all dry PASS) - identical to 165-1-1's values.
- selftest_c157_innerface 13/0; selftest_c158_wire0face 24/0; stagesim selftest 106/0; stagexec selftest 141/0.
- Re-pinned: none (no self-test pins stagexec 6ea6637f; grep 6ea6637f in tools/**/*.py = only this card's hash helper). Extended: selftest_c165_innerface.py
  9244f800 -> a35c946a gains `--pre <path> <md5 prefix>` (default a4df7e15 path/pin unchanged; `selftest_c165_innerface.py:53-55,214,253`).
**5. UNCHANGED after the work** (`prep_c165_a3_1_hash_post.log` 28/0): r_in 0b895983, graph 2a5fa0c4, VI 6dcd5c3d, memory_model ff0fabca, plan doc ring-p5c.md ffb92f59,
stagesim 95a162ba, stagekit dd57c1ca, stage_prerun 7605116f, stage_shared b688edd4, every tools/hooks/*.py, every other card input. Changed: stagexec, innerface test.
Helpers: `prep_c165_a3_1_hash.py` (pre / post / arts).
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| selftest_c165_prime.log | no failing log (no JEV-LADDER row owed) | - | built + ran | PASS 38/0 |
OPEN: the skip trusts that the post-delete read shows the face with wire 0 and loop_inner_face_sink routes it; that step is measured only in sim (SimBackend), as before (LOOP_FACE_SINK_STATUS UNMEASURED).
