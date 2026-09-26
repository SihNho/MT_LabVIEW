ATTACK this claim about a failed prediction in tools/bench/diag_c97_tools_t124b.log (script tools/bench/diag_c97_tools_t124.py, card 97-2).

The script built a scratch fixture: byte copy of claudeDev\EMPTY_v0.vi -> g.while_loop(FIX,(300,300)) (top-level While, OpWhileLoop_v0) -> g.loop_in("for", FIX, didx(FIX, DW), (40,40)) where DW is the new While body's Diagram uid and didx() its index in report_all(FIX,'Diagram') (diag_c97_tools_t124.py:105-111). Prediction F: a For loop is created inside the While body. Observed (t124b.log:11-14): RuntimeError "loop_in(for): error 1055: To More Specific Class in OpForLoopIn_v0.vi (new [])" - no ForLoop created.

CLAIM: the 1055 is our call, not the op and not the diagram index: gscript.loop_in defaults src_cls to "SubVI", index 0 (tools/gscript.py:1266) and OpForLoopIn_v0 takes its input tunnels from Traverse(src_cls)[src_index] cast by To More Specific Class; the fixture had NO SubVI yet (the three subVIs are dropped only after the loop, t124.py:113-115), so the source Traverse was empty and the cast got an invalid refnum -> 1055. The same failure with the same explanation was recorded before for the While twin: tools/recipes/build_opstopfromnode_v0.py:406-411 and tools/bench/build_opstopfromnode_v0.log:51-53 (loop_in("while", SCRATCH, 0, ...) on EMPTY_v0 -> 1055 in OpWhileLoopIn_v0).

Alternative named by the run itself: the Diagram index was wrong (didx over report_all('Diagram') may not equal the op's Traverse('Diagram') index space, or the new While body is not yet a Traverse member).

Already ruled out: LabVIEW crash (handles read 33965 after restart; gates H PASS, t124b.log:15-17); input file (S1 md5 pinned PASS).

Consequence already decided by judgement (card 97-3): the fixture is now a byte copy of D1_s1_copy.vi (a real For #1359 inside While #637), so loop_in is not called at all.

Questions: (1) Which explanation does our own record support, and what is the strongest reason the SubVI-default explanation is wrong? (2) What is the cheapest discriminating test (e.g. loop_in with src_cls='Diagram', src_index=0, src_names=[] on the same fixture; or drop one SubVI first) - and does the 97-3 fixture change make it moot? (3) What would falsify "OpForLoopIn_v0 works on a nested diagram when a source object exists" (tools/bench/test_oploopin.log 6/6, docs/toolkit-capabilities.md:34)?
