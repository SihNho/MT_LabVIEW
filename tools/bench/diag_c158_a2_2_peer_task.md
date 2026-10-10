ATTACK this claim about a failed LabVIEW VI-Scripting stage run (log tools/bench/diag_c156_p5s02a_scratch.log, LAST segment from line 285;
recipe tools/recipes/stage_d1_ring_p5s02a_scratch.py -> stage_d1_ring_p5s02a.py; executor tools/stagexec.py md5 7a712ccb).

CLAIM: the run failed (16/5: D, CEN2, TD, PB) because the move_in of SubVI #376 into a new Case frame (op 10, mv_376) made LabVIEW DROP three
wires that the simulator keeps as "ambiguous / allow_either" (24091 src LoopTunnel #25223 inner t25235 -> #376 'selected path' t5787; 24153 src
t24367 -> 'file size' t5778; 24330 src t24360 -> 'cal cluster path' t5760), and the two NEW wire-0 loop-face acts on ops 16/17
(gscript.connect_term_uid, src = loop inner face, sink = #376 input; stagexec.py:3578 LVBackend.loop_face_wire0, built by card 158-a2-1) returned
err '' but did NOT leave persisting wires on 'cal cluster path' / 'file size', so the end read has those two open (PB extra) and the sim's
re-wire of 24091 has no real counterpart (TD unwired (25223,1,InnerTerminal); D new 21 vs sim 22).

FACTS (log lines of diag_c156_p5s02a_scratch.log):
- :505 and neighbours: real FATE step=10 lines show src_wire=0 for wires 24091, 24153, 24330 (dry run of the same plan kept src_wire=24091/24153/24330);
  24285 and 24312 kept. E1 diff 0 at op 12 anyway (stagexec allow_either, stagexec.py:2533-2534 per the previous review).
- :535 `OP connect_term_uid #5760 <- #24360 -> err '' (6.3 s)`, node census 704 -> 704; :540 STEPX 16 diff 0.
- :543 `OP connect_term_uid #5778 <- #24367 -> err '' (6.3 s)`; :548 STEPX 17 diff 0. Ops 16/17 ARE checkpoints and E1 passed there.
- :552 FAIL D new wires 21 == sim's 22; lost 12 == 12. :553 FAIL CEN2 measured Wire 12 / OuterTerminal 6 / InnerTerminal 10 vs declared 1/1/2.
- :557 FAIL TD unwired (25223, 1, 'InnerTerminal', True); lost == plan deletes. :559 FAIL PB extra open pairs (376,'cal cluster path'), (376,'file size').
- Base graph tools/bench/graph_ring_p5s01_20261009_125622.json: #376 t5760 'cal cluster path' w24330, t5778 'file size' w24153, t5787 'selected path' w24091.
- Previous run's review: archive/peer/2026-10-09-c156-a2-2-p5s02a-innerface.md (predicted the ambiguous-wire fate explanation).

QUESTIONS: (1) Strongest reason the claim is wrong - e.g. connect_term_uid DID wire but to another terminal/position, or E1 at ops 16/17 is blind
(allow_either) so the sim itself ends with those terminals open, or the PB pred (29 rows) is the side that is wrong. (2) An alternative explanation.
(3) What observation in the existing log / json (tools/bench/diag_c156_p5s02a_scratch.json, sim files under tools/bench/sim/ring_p5s02a/) would
falsify each. (4) The cheapest OFFLINE discriminating test (no LabVIEW) before any retry.
