Failed prediction: `tools/bench/sim_l2a1_81.log` (script `tools/bench/sim_l2a1_81.py`, offline stage simulation of
L2-A1 on D1_k, no LabVIEW) ended 13 PASS / 3 FAIL. First failure P2: SimError at step 33, `wire rw_5705_5999`, address
`{uid 5702, term_uid 5705}` resolves to 0 source terminals. P3b and P3 fail only because the simulation stopped.

Hypothesis under attack (review card above): the stop is a gap in `tools/stagesim.py`'s move_in model
(`_flip_orphaned_output_tunnels` and the card-80-6 params in `tools/bench/opmodels/move_in.json`: closure, sequential,
flip_moved_inputs, flip_needs_wired, bare_half_wire). It flips the input SelectorTunnels of the moved Case `#5540`
(`#5702 #5725 #5825 #5967`, plus `#10750` of `#10445`) to sinks, and nothing restores the inner as a source when the
plan re-wires them. It is not a wrong row in the plan (`tools/bench/sim/l2a1/plan_l2a1.json`).

Read: the log (all 66 lines), `stagesim.py` around the move_in/flip code and the wire op's address resolution
(search `resolves to`), `sim_l2a1_81.py` where the RECONNECT rows are built, `result_81-2.json` facts 3-4.

Questions:
1. Is `rw_5705_5999` even the right row? In S1, is t5705 the INNER (frame-side) terminal of `#5702`, a source inside
   the Case? Or is the plan addressing the wrong face of the tunnel, so the defect is in the reconnect builder?
2. Would real LabVIEW flip a SelectorTunnel's direction on move_in when its outer loses its wire? Cite the measured
   evidence in this repo (the `l2a1_tunflip_80.log` / 178(i) scratch measurement) for or against.
3. The cheapest offline test that separates "simulator flip rule wrong" from "plan addresses the wrong terminal" from
   "plan order wrong (inner used before outer re-wired)".
