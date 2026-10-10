---
type: facts
status: current
date: 2026-10-10
card: 158-a2-4
---
# Card 158-a2-4 facts: gate mutation table on graph 6716c499 (offline, no LabVIEW, no gate / tool / recipe / hook edited)
Script `diag_c158_a2_4_mut.py` (md5 461d4f3a; calls vigraph.build4 / computation_diff(_frame), stagekit.term_identity_gates / pb_check /
s1_frame_graph, stagexec.compare / classify_step_diff) -> `diag_c158_a2_4_mut.log` (BGRUN END rc=0 after 91s, RESULT PASS 36/0). Shape probe: `diag_c158_a2_4_probe.log`.
- Tables: `mutation_table_p5.md` 72e54d232a7b087372f1a37d0f87ebf1 (47 lines), `mutation_table_p5.json` 2d9fd0513a5490b91ea191872708275a (every row + gate detail).
- Graph 6716c49948f097b8ac0e1780930bfab1 before (log :3) and after (log :72): unchanged; each mutation on its own deep copy in memory.
- Set-up: base = sim end = unmutated graph, real end = mutated copy, bind {}; PB pred = cdiff(S1, G0) frame-keyed, 21 rows / 19 open pairs (log :6).
  Control M0 passes every gate (log :7-9). Targets: first / middle / last of uid-sorted eligible lists (COMP 427, CONST 301, WIRES 861; log :5).
- Rows: 1 control, 12 invariant (M1 x3, M2 x3, M3c x3, M6 x3), 16 representation (M3r x3, M3t x3, M4 x5, M5n x3, M5w x3, M5a x1).
- Blocks per gate, invariant / representation (md :47): CD 9/4, CDF 9/4, TD 8/4, D 9/7, PB 7/4, E1 9/7, INV 0/0 (n.a.).
## (1) INVARIANT rows passing every gate (gaps): M6.0, M6.1, M6.2
- Constant value changed: the stored graph has NO value column (terminals fields: frame_diagram, is_source, owner_class, owner_uid, term_class,
  term_name, term_uid, wire_uid; objs: class, owner, pos, uid - probe log :4-8), so no gate can see a constant's value. M6 was written as a new `value` key.
## (2) REPRESENTATION rows that block (false blocks): M3t.0-2, M5n.0-2, M5a.0
- M3t (node moved into another diagram, each wire relayed by a new Tunnel): CD / CDF / TD / PB PASS; D BLOCK (d_new 4 vs sim_new 0, d_lost 2) and
  E1 BLOCK (only_real_terms 4, only_real_edges 4) - json M3t.0 :912-933. This is the move_in shape of P5 with the sim end NOT carrying the tunnels.
- M5n (one node's owner + term uids renumbered): every gate BLOCKs (CD nodes_added 1 / removed 1). M5a (all uids + 9000000): every gate BLOCKs
  (CD nodes_added 1031 / removed 1024). M5w (wire uid only) passes every gate: wires are keyed by ends, nodes by uid.
## Other facts
- M3r (diagram field changed, wires kept) and M4 (5 tunnel classes renamed) pass every gate: no gate reads a node's diagram or a tunnel's name.
- M1.1 / M2.1 (sink on #30398 'f'): CD rows 2 / 1 but PB PASS (extra 0, missing 0; json :149, :353); TD PASS on M2.1 (re-sourced sink stays wired, :351).
  Why PB's slot sets stay equal there was not measured.
- Gates not callable on a graph pair: INV = invcheck.run_inv pins file md5s / snapshots (tools/invcheck.py:7-12, :97). EL / CEN2 not in the brief's list.
- No shared graph-mutation helper exists (only inline `mut`, tools/bench/selftest_c153_compdiff_poskey.py:51); the builders are local to the script.
OPEN: M3t is classed representation by the stated rule (sources kept through relays); judgement owed on whether a tunnel-relayed move is the steer's "M3 changes a connection".
OPEN: PB PASS on M1.1 / M2.1 while CD blocks - is #30398 absent from S1 or its slot already in the 21 pred rows (PB compares slot SETS, stagekit.py:1822-1827)?
OPEN: M6 gap - a constant-value check needs a value read that the stored graph format does not carry; whether to add one is a judgement call.
