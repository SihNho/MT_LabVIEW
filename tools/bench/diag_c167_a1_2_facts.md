---
type: facts
status: current
date: 2026-10-12
card: 167-a1-2
---
# diag_c167_a1_2 facts (C rows, PD404(f)) - offline, LabVIEW reads 0
- Outputs: `tools/bench/p6_crows.md` a0188541b461c2a9d93729daac709692; `tools/bench/p6_crows.json` abfc108153cd79ff5ac07f0692b694a7
- Gates: 10 pass / 0 fail; first fail: None (log `tools/bench/diag_c167_a1_2_crows.log`)
- Hash before == after: card inputs (protocol.input_md5_changes) and the seven VIs D1_ring_p5_20261010_172913.vi 75773b0d, D1_ring_p5s01_20261009_124542.vi 7f2582ae, D1_ring_p4s09_20261009_060515.vi eb1d0f31, D1_ring_p5s02a_20261010_023239.vi 94ffff94, D1_ring_p5s02b_20261010_105511.vi f9ae7751, D1_ring_p5s02c_20261010_125755.vi 564d8cbe, D1_ring_p5s02d_20261010_152518.vi 6dcd5c3d
- No LabVIEW process before or after (tasklist).
- #1114: P5 loop 1.1; S1 d639; every iteration of 1.1 (no CaseStructure between d639 and the While; chain d639 in WhileLoop#637 (1.1) < d686 in FlatSequence#681 < d536 TopLevelDiagr; counter read: no
- #2136: P5 loop 1.1; S1 d639; every iteration of 1.1 (no CaseStructure between d639 and the While; chain d639 in WhileLoop#637 (1.1) < d686 in FlatSequence#681 < d536 TopLevelDiagr; counter read: no
- #29411: P5 loop 1.1; S1 absent; only in a case frame of 1.1: in CaseStructure #22694 frame d27219 (frame name 'False' (tools/bench/stage_d1_ring_p3a.json:187)) - selector Tunnel #271; counter read: no
- #12045: P5 loop 1.1; S1 d16565; every iteration of 1.1 (no CaseStructure between d16565 and the While; chain d16565 in FlatSequence#16543 < d639 in WhileLoop#637 (1.1) < d686 in Flat; counter read: no
- #3162: P5 loop 1.1; S1 d3292; only in a case frame of 1.1: in CaseStructure #3191 frame d3292 (frame name unread) - selector Tunnel #3302 t3307 <- #3057 Function 'x = 0?' t3067; counter read: no
- #1628: P5 loop outside every While; S1 d686; outside every While: d686 (d686 in FlatSequence#681 < d536 TopLevelDiagram); not per-iteration of 1.1 and not in the new-frame case; counter read: no
- #30240: P5 loop 1.2; S1 absent; every iteration of 1.2 (no CaseStructure between d23166 and the While; chain d23166 in WhileLoop#10170 (1.2) < d686 in FlatSequence#681 < d536 TopLeve; counter read: no
- #29240: P5 loop 1.2; S1 d639; every iteration of 1.2 (no CaseStructure between d23166 and the While; chain d23166 in WhileLoop#10170 (1.2) < d686 in FlatSequence#681 < d536 TopLeve; counter read: no
- #10068: P5 loop 1.2; S1 d639; every iteration of 1.2 (no CaseStructure between d23166 and the While; chain d23166 in WhileLoop#10170 (1.2) < d686 in FlatSequence#681 < d536 TopLeve; counter read: no
- Repeated BufNum: A legs (S1 byte copy) steps_le0 = [0, 0, 0, 0]; P1 C-API bench Last rows: 4.
- Duplicated logic (not importable, re-written here): diag_c166_a1_5_census.py:139-153 diagram_chain, :58-61 lv_running; Graph gets graph_summary via a json.loads hand-off (census:105-115).
- Limits: S1 json has no owners map; tra col 0 = BufNum not read; WLC 'index i' use inside the subVI unmeasured (frameidx_consumers.md U1).
