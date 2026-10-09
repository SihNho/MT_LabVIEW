ATTACK this claim (card 154-a3-3b, failed-prediction gate on tools/bench/diag_c154_a3_3_nodes.log, script tools/bench/diag_c154_a3_3_nodes.py).

CLAIM: diag_c154_a3_3_nodes.log (first segment) failed gate `N every made / bound uid has >= 1 terminal row` with [30726, 31071] only because
the READ-ONLY report script I wrote this card keyed node rows by `owner_uid` alone. In the graph json
(tools/bench/graph_ring_p5s01a_20261009_103621.json, written by diag_c154_a3_3_graph.py, 15/0) a CaseStructure owns no terminal row:
its selector is a separate object, Tunnel #30897 (`{"uid": 30897, "class": "Tunnel", "owner": "CaseStructure"}`, rows 30893 outer wire 30457 /
30906, 30908 inner on frames 30914 / 30922), and a ControlTerminal is itself a row of its diagram
(`{"term_uid": 31071, "term_name": "records final (1.2 to 1.7)", "owner_uid": 4866, "owner_class": "Diagram", "term_class": "ControlTerminal", "wire_uid": 31163}`).
The graph read itself is not in question: E5 found all 8 made objects with the scratch's classes (CaseStructure 30726, ControlTerminal 31071 among them)
and all 10 new wires (diag_c154_a3_3_graph.log:302); case #30726 has its 2 frames [30914, 30922] (gate C PASS in the same nodes log).
Fix made in the script (records only, no stage tool): a node's rows = owner_uid == u OR term_uid == u; the case is reported through its
selector #30897, whose outer wire source is printed.

Already ruled out: graph read fault (G1/G2/G3/FS1/B/E5/X PASS, diag_c154_a3_3_graph.log:302-311); the made-uid list is wrong (mkgraph C gate 8/8 bound,
diag_c154_a3_3_mkgraph.log).

Questions: the strongest reason the claim is wrong (e.g. #30726 or #31071 truly missing from the file's graph); an alternative explanation;
what would falsify it; the cheapest discriminating test.
