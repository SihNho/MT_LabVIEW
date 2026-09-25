ATTACK this claim (failed prediction, card 90-5, log tools/bench/diag_c90_t0_step3.log, script tools/bench/diag_c90_t0_step3.py, run 1).

CONTEXT: step 3 of PD196(d) (docs/d1-loop12-17-split-plan.md:1049-1105) instruments a byte copy of claudeDev\D1_s1_copy.vi with
t0stamp CLFN nodes (gscript.build_clfn, top level only) moved into nested diagrams by stagekit.move_in (OpMoveIn_v0 = GObject.Move
by uid). Each CLFN needs param1 `site` (t6) = an I32 constant and param2 `any` (t8) = a BRANCH of an existing wire
(OpConnectFromWire_v0).

OBSERVED (diag_c90_t0_step3.log:24-30, 32-53, 196-199):
 - S00: the constant was created on the CLFN's t6 while the CLFN was TOP LEVEL (gscript.create_const_loop_term 'for_n', uid #23090,
   err ''), then move_in(CLFN #22968 -> Diagram[43]) and move_in(const #23090 -> Diagram[43]) both returned err ''. Afterwards the
   CLFN's t6 wire reads 0 and the Tunnel/LoopTunnel/SelectorTunnel censuses are unchanged (468/132/146 before and after).
 - S02..S20 (7 While-body sites): CLFN moved first, then OpCreateConstOnTerm_v0 (WhileLoop[i].Diagram.Nodes[n].Terms[6]) created
   the constant in place, t6 wire non-zero. connect_from_wire(sink t8 <- Wire(site wire).Terms[source]) returned err '' and
   Is Broken? False but Wire count delta 0 (my gate expected +1).
 - E1 ExecState 0 at the end; computation_diff(S1, new) rows 0, removed 0, added 25 = CallLibrary + DigitalNumericConstant + 9 Invoke.

MY EXPLANATION (the claim to attack):
 1. GObject.Move of the two ends one at a time DROPS the wire between a top-level constant and a node once the node crosses into a
    nested diagram (no tunnel is auto-created by scripting, unlike a GUI drag); so a typed constant must be created IN PLACE with
    Terminal.Create Constant addressed through the owning Loop (WhileLoop or ForLoop [i].Diagram.Nodes[n]). A case FRAME cannot be
    addressed this way (CaseStructure has Diagrams[], no Loop.Diagram), so sites 6/7/14/15 are skipped in run 2.
 2. Wire delta 0 on connect_from_wire is the expected BRANCH outcome (skill law: a successful branch adds no Wire object); the right
    gate is the sink terminal's wire uid == the site wire (read by node_terms).
 3. ExecState 0 came from the 9 leftover junk `Invoke` nodes (unwired `reference` - docs/NAMES.md:307-313) minted by build_clfn /
    the creators, which run 1 purged only after connect_from_wire; run 2 purges after every creator.

ALREADY RULED OUT: the moves themselves erroring (err '' on both, node found on Diagram[43] uid echo); tunnels being created (censuses
equal); OpCreateConstOnTerm_v0 failing on While bodies (7/7 created, t6 wired).

Give: the strongest reason any of 1-3 is wrong; an alternative explanation for t6 wire 0 after the moves and for ExecState 0; what
would falsify each; the cheapest discriminating test. Also: is there ANY scripting route (VI Server method on Terminal / Diagram /
CaseStructure frame) to put a typed, wired constant on a node inside a case frame with the ops this project owns
(docs/toolkit-capabilities.md rows 69-71)?
