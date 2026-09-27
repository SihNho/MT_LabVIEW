ATTACK this claim (card 113-1 P2, failed prediction in tools/bench/diag_c113b_plan.log, script tools/bench/diag_c113b_plan.py).

PREDICTION that failed: the 9-row L2-B2b plan (tools/bench/plan_l2b2b.json, base tools/bench/graph_l2b2a_20260928.json = the SAVED
B2a bed) finalizes with the route check PASS. The judgement's PD226(e) (docs/d1-loop12-17-split-plan.md, "Its tools now exist: the
owner route (v), base-flip seeding for B2-08, and ctltun for B2-16") predicted every row routes.

OBSERVED (diag_c113b_plan.log ROUTE-ROW lines): 6 rows route (b2_01 nested, b2_02 cfw, b2_03 nested, b2_06 cfw, b2_08 cfw,
b2_16 ctltun); 3 are UNROUTABLE:
 - b2_04 bare ControlTerminal #28170 -> LoopTunnel #31051 outer face t31055 (loop #1359): CONNECT-NO-VERB
 - b2_05 bare ControlTerminal #29091 -> LoopTunnel #31137 outer face t31158 (loop #1359): CONNECT-NO-VERB
 - b2_07 bare LoopTunnel #29172 outer face t29178 (loop #29874) -> bare ControlTerminal indicator #28786: CONNECT-NO-VERB
The simulation otherwise closes 13 of the bed's 28 cdiff pairs and opens none; open_rows re-declared -> 15 (open_rows_match True).

CLAIM (my explanation): this is a TOOL GAP, not a planning or simulator error. tools/stagexec.py connect_route (:748-835):
 - the ctltun branch (:782) fires only for rd owner_class in OWNER_ROUTED = ("SelectorTunnel", "Tunnel") (:614); a LoopTunnel is
   in LOOP_ROUTED (:626), so a bare CT -> LoopTunnel outer face falls through to :800-804 and is refused (the comment at :624-625
   says class-traverse verbs are refused on LoopTunnel faces by design);
 - a bare-source -> panel-CT sink goes to 'ctlsink' (:764-773), which refuses a source in LOOP_ROUTED (:768).
 So no existing route kind covers CT <-> LoopTunnel outer face in either direction. S1 wires exactly these
 (S1 w31059 #28170 -> #31051; w31166 #29091 -> #31137 + #30896; w32890 #29172 -> #28786 only sink, docs/wiki/subvi/D1_s1_copy.json).
 b2_06 routes only because b2_05 would have wired #29091 first (cfw).

Question: is there an EXISTING route (verb) in tools/stagexec.py / tools/gscript.py that reaches these three rows that I missed
(e.g. a row ordering, a different source/sink orientation, 'cfw' from some existing wire, wire_indicators), so that the fix is a
plan change rather than a tool change? What is the cheapest discriminating test? Do NOT propose the design; I only report.
