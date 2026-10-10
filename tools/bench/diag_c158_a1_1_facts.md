---
type: facts
status: current
date: 2026-10-09
card: 158-a1-1
---
# Card 158-a1-1 facts: RETURNED before any tool edit - part (a) has no graph row for the body-diagram source triple
## Baseline stored (measurement 1), tools untouched: stagexec 69b1a301, stagekit 0d8f6d25, stagesim eb99c6ba, addrcheck 207beb0d
- `prep_c158_a1_1_regress.py before` -> `prep_c158_a1_1_before.log` RESULT 1/0 (:22), BGRUN END rc=0 after 884 s (:23);
  before.json under tools/bench/sim/ring_p5s02a_c158/ (200 stored plans compiled, :8). It CALLS prep_c157_a1_1_regress's
  record() / gate / suite list (top-level defs executed from its source by ast, OUT re-pointed) and adds c157_innerface to the suite.
- Suite at base (:9-21): stagexec 141/0, stagesim 106/0, c155_basecase_frame 21/0, c120 1/0, case_frame_c124 28/1 (V02),
  stagexec_gate 13/0, tunnel_naming 21/0, fs_c126 13/0, t6_regress 9/2, addrcheck_s5 22/0, t7_ring 35/0, c156_passwire 20/0,
  c157_innerface 13/0. c155 / c156 ALREADY pass on stagekit 0d8f6d25 - the brief's step-4 re-pin is not owed there.
- Checkpoints at base (:4): p5s02a [0,1,3,6,8,9,10,11,12,15,16,17]; p5s02 [..,9,10,11,12,15..19]; move_in ops 10-12 in both (:5).
## Part (a): the source triple (body diagram idx, node idx, terminal idx) for a wire-0 LoopTunnel inner face - row MISSING
- Probe `prep_c158_a1_1_probe.py` (SimReader / V.node_of / listed_as_node, recorded sim steps) -> `prep_c158_a1_1_probe.log`.
- step_15: #24360 = LoopTunnel #24357 InnerTerminal, frame 23405, wire 24330, source; node_of 24357, listed_as_node False (:4);
  #24367 = LoopTunnel #24361 InnerTerminal, frame 23405, wire 24153, node_of 24361, listed_as_node False (:6). Same on step_16 (:11,:13).
- Body #23405 (owners -> WhileLoop #23041, diagram idx 126, :3) Nodes[] = [23042, -7, -28]: neither the loop nor tunnels 24357/24361 (:8).
- No Diagram.Nodes[] entry on ANY diagram lists #24360 or #24367 in its Terminals[] (GATE N PASS, step_15 :5 :7, step_16 :12).
  The loop #23041 is a node of its parent #686 only; its Terminals[] = outer faces/registers [23514, 24366, ..] (:9).
- Why by the code: a tunnel is outside the Node branch (stagexec.py:1337-1344 listed_as_node); a loop is listed on its PARENT
  diagram only (stagexec.py:3563-3567); a LoopTunnel inner face has no measured Nodes[] route (stop text stagexec.py:1830-1832);
  connect_nested_v1 addresses Diagram[d].Nodes[n].Terminals[t] only (tools/recipes/build_opconnectnested_v1.py:418-420); the inner
  face is reached in LabVIEW by `Tunnel.Inside Terminals[]` 6356000 (docs/NAMES.md:1141-1144), not by a Nodes[] index.
- Card rule "Return if ... a graph row needed for the body-diagram triple is missing" applied: stagexec / stagekit NOT edited;
  part (b) (run-closing checkpoints) not started; no self-test written or re-pinned.
## Side facts
- The probe ran out of its own 2-min bgrun deadline (BGRUN TIMEOUT 122 s, log :14-18) in the step_16 #24367 node scan (an
  all-diagram node_terms sweep); the step_15 result for both faces and step_16 for #24360 were complete before the kill.
- No LabVIEW process at any point; no tools/hooks edit; no plan / pred / licence / recipe / P5 file edited; no gate refused a command.
OPEN: which address the live act should use for a wire-0 LoopTunnel inner face (e.g. an op by tunnel uid + Inside Terminals[] index, or the outer face via the loop's Terminals[]) - no Nodes[] triple exists on body #23405.
OPEN: part (b) is independent of (a); re-issue it alone (baseline before.json above stays valid while stagexec 69b1a301 / stagekit 0d8f6d25 are unchanged)?
