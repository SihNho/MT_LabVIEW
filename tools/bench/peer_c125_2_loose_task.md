ATTACK this claim (failed prediction in tools/bench/diag_c125_loose.log, script tools/bench/diag_c125_loose.py, card 125-2).

PREDICTION: the saved P3a bed (claudeDev\D1_ring_p3a_20261001_180540.vi) has exactly ONE more LabVIEW Error List item than
its input P2b (55 vs 54; the extra one is "Wire: Wire has loose ends.", pinned by tools/bench/plan_ring_p3a_pin.json), so a
graph diff should show exactly ONE new wire that has fewer than one source terminal + one sink terminal.

OBSERVED (diag_c125_loose.log): graphs tools/bench/graph_ring_p3a_20261001_190155.json (read today by
tools/bench/diag_c125_graph_p3a.py, same reader as diag_c123_graph_p2b.py: wiki_build.read_live) vs
tools/bench/graph_ring_p2b_20261001_154542.json: 28 "loose" wires in each, the SAME 28; 0 new. The 11 new wires (27073, 27167,
27245, 27331, 27337, 27350, 27378, 27404, 27911, 39296, 39360) each have >= 1 source row and >= 1 sink row; one old wire
(w3747, BufNum) gained two sink rows (27084, 27161); no wire lost; no terminal lost its wire.

MY EXPLANATION (attack it): "Wire has loose ends" in LabVIEW means a wire SEGMENT with an unattached end, which can sit on a
wire that otherwise has a source and sinks (precedent: tools/bench/errorlist_expected_D1_ring_p3a_20261001_180540.json, PD230
"dangling branches where a retired SR sink was cut"). read_live reports terminal rows per wire, not segments, so no terminal-row
diff can single the new one out. The likely carrier is one of the branch-making writes of the P3a stage
(tools/bench/stage_d1_ring_p3a.log: connect_from_wire onto w3747, wire_sr RightIn from BufNum, case_frame_wire branch R4 on
w27331, connect_term_uid across the case border). Alternatives I can name: (a) the extra item is not a wire of P3a's rows at all
but an Error List ordering/merge artefact (two P2b items reported once each before, now one segment reported twice);
(b) read_live misses terminals of some owner classes (e.g. SelectorTunnel inner faces), so a truly loose wire looks complete.

Give: the strongest reason the explanation is wrong; what would falsify it; the cheapest discriminating test that does NOT
need a new op (we have no Selection List[] reader; the Error List reader already double-clicks each item and saves a block-diagram
screenshot, tools/bench/errorlist_D1_ring_p3a_20261001_180540_20261001_181801.json, uid_route "none").
