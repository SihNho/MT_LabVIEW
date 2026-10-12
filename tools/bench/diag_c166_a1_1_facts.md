---
type: facts
status: current
date: 2026-10-12
card: 166-a1-1
---
# 166-a1-1 facts: P5 close-out read PASSED - graph read 15/0, rule-1a tunnel check EQUAL (21/0), load_by_vi 647.8 written, pred census written; LabVIEW gone.
## 1 Hashes (diag_c166_a1_1_hash.py, CALLS protocol.input_md5_changes + prep_c156_a1_1_lib; VI name list copied from diag_c165_a3_4_hash.py:23-25 + 75773b0d)
- before (diag_c166_a1_1_hash_before.log) 8/0: 16 card inputs equal; 75773b0d 7f2582ae eb1d0f31 94ffff94 f9ae7751 564d8cbe 6dcd5c3d equal (:3-12).
- after (diag_c166_a1_1_hash_after.log) 8/0: 14 inputs equal (memory_model + pred excluded), all seven VIs unchanged (:3-12).
## 2 Graph read: diag_c165_a3_4_graph.py UNCHANGED (df5b47b5), check_launch ALLOW, log absent before; RESULT PASS 15/0 (graph.log:336), BGRUN END rc=0 245 s (:338)
- `MEM after load: 647.8 MB private; handles 45935` (:24); after full read 659.5 (:280); handles 45935 -> 46230 (:306).
- WROTE tools/bench/graph_ring_p5s02e_20261012_173009.json md5 7815af0993bd8aeb1f14c7d3d76b0da1: 6224 rows, 10859 objs, 25 loops, 23 FS (:307).
- E5 PASS (:305) 5 made objects with classes, 2 deleted wires absent, 8 new wires present; G1 (:308) G2 (:309) G3 (:310) FS1 (:311) B 7 UNMEASURED none used (:313) X (:314) PASS.
- H5 refs opened 4 == closed 4 (:319); H4 scratch deleted (:321); H2 input md5 unchanged (:322); H3 (:328); H6 files left [] (:330); `LabVIEW gone at exit: True` (:337).
## 3 Terminal sets (diag_c166_a1_1_q_p5s02e.log vs _q_p5s02d.log, _q_p5s01.log, _q_simend.log)
- w4337: outer t9631 (#5204) + sinks t6480 (SubVI #6384) + t3182 (#2048) in 2a5fa0c4 (q_p5s02d:4,8,10) and in the new graph (q_p5s02e:4,16,18): EQUAL; t9631 is_source false -> TRUE.
- w9636: outer t24363 (#10404) + sink t6511 (#6384) (q_p5s02d:5,9 / q_p5s02e:5,17): EQUAL; t24363 is_source false -> TRUE. Same as P5-1 7f2582ae (q_p5s01:4-5, both true).
- t8776 (#5204 inner): real w31792, source t31815 OuterTerminal of SelectorTunnel #31803 (OK3), other sink RSR #31756 t31767 (q_p5s02e:6,12,14) == sim end step_13 (q_simend:4,5,7).
- t24342 (#10404 inner): real w31837, source t31858 outer of SelectorTunnel #31847, other sink RSR #31812 t31820 (q_p5s02e:7,13,15) == sim end -10 / -1 on w-15 (q_simend:6,8,9); -10 = 31847, -1 = 31812 by the scratch's bind (diag_c165_p5s02e_scratch.log:92,116).
- Only difference: the sim's new OK4 outer face has term_name '' (q_simend:9), the real t31858 is 'file number to append out' (q_p5s02e:7); the source identity is equal.
## 4 Rule-1a tunnel check (diag_c166_a1_1_tun.py + plan diag_c166_a1_1_tun_plan.json; dry PASS, prerun 15/0 _tun_prerun2.log, check_launch ALLOW): RESULT PASS 21/0 (tun.log:70), rc 0 146 s
- Verbs found by protocol.check_requires: gscript.tunnels tools/gscript.py:1270, gscript.read_term_type :4646, OpTunnels_v0, OpTermDataType_v0 (tun.log:4-5). No new op or verb.
- #5204: IndexMode 0 in 75773b0d and 7f2582ae (:44); outer t9631 type I32, label-exact sig 00134003000d...'file progress' equal (:45).
- #10404: IndexMode 0 in both (:46); outer t24363 type I32, sig 001f4003001966...'file number to append out' equal (:47). Outer faces source in both (:27,29,39,41).
- Byte copies only; LabVIEW restarted between them (602.8 MB > 600 after closing the first, :32-35); loads 599.4 / 599.4 MB, peak 603.5 (:25,37,48).
- Hygiene: X both md5 unchanged (:49); H5 refs 5 == 5 (:54); handles 34005 -> 34352 (:35,55); H6 files left [] (:64); `LabVIEW gone at exit: True` (:71). tasklist: no LabVIEW; no scratch_c16* in claudeDev.
## 5 memory_model.json (diag_c166_a1_1_mm.py, log diag_c166_a1_1_mm.log 6/0)
- New load_by_vi key 75773b0ded2a08586bb1a542ddda5af6 = 647.8, cite diag_c165_a3_4_graph.log:24; JSON compare: only load_by_vi differs by that key, old keys equal, fail_above_mb 680.0 (M5).
- ff0fabca220686e7222cfcb27aa622cd -> d12bcd3b1ed3c776ab361fa71b55df4d; backup diag_c166_a1_1_memory_model_before.json.
- The same file loaded at 599.4 MB in the tunnel read (tun.log:25), 48.4 MB below the graph read's 647.8 (graph.log:24).
## 6 Pred census (diag_c166_a1_1_census.py, log diag_c166_a1_1_census.log 6/0; after the mm log PASS, gate C0)
- census = stagekit.scratch_census of diag_c165_p5s02e_scratch.log:148 (== _sum.json): DigitalNumericConstant 1, InnerTerminal 6, LeftShiftRegister 1, OuterTerminal 4, RightShiftRegister 1, SelectorTunnel 2, Terminal 1, Wire 5.
- census_overall MEASURED-SCRATCH; census_source cites the log, net :147, lost :149, graph.log:305 and the graph json objs 31812/31817/31824/31847/31855; only these 3 keys changed (C5).
- 825cbf6581004267438d820a483723af -> 1cba18c2be709884e5d9000ec705824a; backup diag_c166_a1_1_pred_before.json.
## Not done / not touched
- No original opened, no VI saved, no STATUS / INDEX / recipe / plan / licence / EL / stage-tool / hook edit, no motor or camera. No gate failed, so no Jev ladder row and no peer.
- The JSON rewrite helper diag_c166_a1_1_lib.py (self-test _lib_selftest.log 2/0) has one older inline copy at prep_c164_a3_7_write.py:53-59; stagekit is outside this card's write globs.
