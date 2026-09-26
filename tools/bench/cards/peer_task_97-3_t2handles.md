ATTACK this claim about a failed prediction in tools/bench/selftest_c97_tools.log (script tools/bench/selftest_c97_tools.py, card 97-3; the tool is gscript.move_into_frame, tools/gscript.py, section "CARD 97-3").

Run: a never-saved scratch byte copy of D1_s1_copy.vi (~51.5k LabVIEW handles after load). 33 gates pass / 1 fail. The one FAIL (log line 120): "T2 handles over 26 op calls: flat +-100 (51555, 51668)" = +113 handles across ONE invocation of move_into_frame that moved 10 objects into a case frame and re-made 16 edges (log lines 70-117; edge table equal, lines 118-119).

What that one invocation ran (counted from the code): 10 OpMoveIn_v0 moves; 16 edge writes (9 OpConnectNested_v1, 2 ops/OpConstWire_v1, 1 OpWireCtl_v0, 4 OpConnectFromWire_v0 incl. one with inverted roles); 2 whole-VI OpAllTerms_v0 reads; 22 class counts (OpReport_v3); ~27 report_all(Invoke) junk checks; ~12 OpNodeTerms_v0, ~20 OpNodeLabels_v0 / report_all(Diagram) addressing reads; ~12 OpOwnerChain_v1 reads; 4 OpWireSource_v5 wire walks (10 terms each). Roughly 150+ op runs.

Other handle readings in the same run: T1H 20 case_in calls (build_case + OpMoveIn_v0 + OpOwnerChain_v1 + OpCaseFrames_v1) 51560 -> 51555 (line 51); T3 one move_into_frame invocation (2 moves, 3 edge writes: OpConnectNested_v1, OpTunOuterWire_v1, OpCtlSinkWire_v1, plus the same read pattern) 51668 -> 51704 (+36, line 147); T5 20 OpTunnelUseDefault_v0 calls 51726 -> 51725 (line 154); T4 20 OpLabelSet_v0 calls 51749 -> 51767 (line 160). Python-side VI refs opened 21 / closed 21 (line 164).

CLAIM: +113 is not a reference leak in the new tool. The +-100 criterion (CLAUDE.md "a new op is accepted only if 20 runs leave the handle count flat (+-100)") was written for 20 calls of ONE op; the T2 gate applied it to one composite invocation of ~150 op runs across ~12 different op VIs, so ~0.75 handle per op run is inside the noise the other readings show.

Alternative I cannot exclude: one of the connect writers (OpConnectNested_v1 / OpConnectFromWire_v0, never handle-audited) or OpAllTerms_v0 leaks ~4-7 handles per call.

Questions: (1) Strongest reason the claim is wrong? (2) Which alternative does our own record support (docs/toolkit-capabilities.md rows for OpAllTerms_v0, OpConstWire_v1, OpConnectNested_v1, OpConnectFromWire_v0; tools/bench/handle_audit.py)? (3) The cheapest discriminating test, in LabVIEW minutes (e.g. 20 consecutive idempotent OpConnectNested_v1 re-connects of an existing edge, 20 OpConnectFromWire_v0, 20 OpAllTerms_v0 reads on the same scratch, handles read between blocks).
