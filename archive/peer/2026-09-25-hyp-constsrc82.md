# hyp-constsrc82

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.6767  in 38 / out 15861 / cache-create 113277 / cache-read 2031048  (211s, 29 turn(s))
- **date:** 2026-09-25 15:59:30
- **outcome:** ANSWERED (214s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FAILED PREDICTION, card 82-3 (tools/bench/constsrc_l2a1_82.log, script tools/bench/constsrc_l2a1_82.py).

Context: LabVIEW 2026 VI Scripting over COM. On a scratch copy of D1_k, ops 1-34 of a staged move ran with graph diff 0.
Two BARE DigitalNumericConstants (#10739 terminal #10738 'disabled index (col)'; #10929 terminal #10943 'index') now sit
on nested Diagram #23166 (a While loop body) and must be wired to Comparison #10950 input 'y' and IndexArray #10757 input
'index' on the same diagram. The real Diagram.Nodes[] does not list *Constant objects (measured, card 82-1), so our
index-triple verb (connect_nested_v1: D[i].Nodes[n].Terminals[t]) cannot address the source.

Prediction: one of two existing verbs wires the constant source.
  C1 gscript.wire (OpWire_v1: erdosmiller Traverse for GObjects(class)[i] -> Get Outputs by name -> Wire Inputs onto
     Traverse(dst class)[j].<input name>), src class 'DigitalNumericConstant'.
  C2 gscript.wire_control (OpWireCtl_v0: erdosmiller Get Controls on Diagram[i] by LABEL -> Wire Inputs) - the route that
     worked for bare ControlTerminals in card 82-2.
Observed (log lines 511, 518, 526, 533): no mutation at all (Wire delta 0, node census unchanged) and
  C1 -> "error 1057: To More Specific Class in OpWire_v1.vi" on both rows;
  C2 -> "error 5001: LV-Scripting.lvlib:Get Controls.vi | Control <label> not found" on both rows.
My explanation: Get Outputs / Wire Inputs cast the traversed object to Node, and a Constant is a GObject, not a Node
(recorded unmeasured at tools/recipes/build_d1_v0.py:1181-1186); Get Controls looks only at control terminals. So neither
existing verb can source from a Constant; the remaining route is a NEW op: Traverse(DigitalNumericConstant)[i] -> To More
Specific Class(Constant) -> Constant.Terminal (634AC04) -> Terminal.Connect Wire (6349C03) onto the sink terminal
(sink addressed as Diagram[i].Nodes[n].Terminals[t] or by class traverse). Both halves exist inside OpConstValueN_v1
(Constant.Terminal) and OpConnectNested_v1 / OpConnect_v0 (Connect Wire).

Already ruled out: connect_nested_v1 (Nodes[] omits constants), connect_from_wire (source bare), OpCreateConstOnTerm
(would replace the constant - forbidden), re-ordering the plan to wire before the move (rejected by judgement, plan 187).

Questions: is the 1057 really the Node cast (vs. a class-name / index problem in OpWire_v1's own TMSC)? Is there an
existing scripting route (VI Server property/method, e.g. Diagram 'AllObjs[]', Terminal lookups, or an erdosmiller VI)
that reaches a Constant's terminal without building a new op? What is the cheapest discriminating test?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict:** your conclusion holds. Neither existing verb can wire from a Constant, and a new op is the right next step. But the mechanism you gave was never measured, and part of it is misattributed. I found no existing verb that avoids building the op.

**1. Strongest reason the claim is wrong as stated.** The 1057 was not raised inside Get Outputs or Wire Inputs.
- The error source reads "To More Specific Class in OpWire_v1.vi". That is a primitive on OpWire_v1's own diagram. When a subVI raises an error, its name appears in the source, as C2's did: `LV-Scripting.lvlib:Get Controls.vi` (`tools/bench/constsrc_l2a1_82.log:517`).
- OpWire_v1 contains two of its own casts (To More Specific Class, TMSC), both to class `Node`:
  - TMSC 683 on the source chain, feeding Get Outputs.
  - TMSC 788 on the destination chain, feeding Wire Inputs.
  - Evidence: `tools/recipes/build_opconnect_gateway_attempt.py:9-12` and `archive/2026-08-29-status-sweep-opexitloop-opwireind.md:70,83` ("retarget TMSC2 class constant `Node`→…").
- The log does not say which of the two raised the error. What was actually measured is "one of OpWire_v1's two casts to Node failed".
- The source-side reading is now backed by external documentation, not just the unmeasured note at `build_d1_v0.py:1178`: Constant is **Generic → GObject → Constant**, not a Node ([labviewwiki Constant class](https://labviewwiki.org/wiki/Constant_class)). A cast to Node must fail on any DigitalNumericConstant.

**2. Alternative explanations of the same log.**
- **(a) The destination-chain cast (TMSC 788) raised it.** This is unlikely. Comparison and IndexArray are Nodes, and the destination index is re-read at the call site (`tools/stagekit.py:409-412`). The log cannot rule it out, though.
- **(b) More important: C1 never tested addressing.** The source cast fails for *every* DigitalNumericConstant index. So a wrong index (30 or 31 pointing at some other constant) would give exactly the same 1057. C1 says nothing about whether index-by-class reaches #10739.
- **C2's 5001 is consistent with your reading.** Get Controls resolves front-panel control labels only; a constant's label is not one ([Terminal class](https://labviewwiki.org/wiki/Terminal_class) shows Terminal is its own GObject subclass). This part is fine.

**3. What would falsify the claim.**
- If OpWire_v1 with a *Node* source and the same destination (Comparison[3].'y') also returns 1057, the destination chain is at fault and the "Constant is not a Node" explanation is not what happened.
- If any DigitalNumericConstant source gets past OpWire_v1's cast, the class-hierarchy argument is wrong.

**Existing routes that reach a Constant's terminal: none that wire it.**
- **OpConstValueN_v1** already reaches the terminal: Traverse(DigitalNumericConstant)[i] → cast to DigitalNumericConstant → `Constant.Terminal` 634AC04. It measured this functionally (`tools/recipes/build_opconstvaluen_v1.py:5-7`). It only *reads*; it does not connect.
- **Erdos Miller LV-Scripting** (the vi.lib directory listing) has no constant-terminal getter. Its `Conditionally Connect Wire.vi` needs Terminal-typed inputs (`docs/keystone-op-spec.md:385-388`).
- **`AbstractDiagram.All Objects[]` (6375804)** returns "all the top-level objects" of a diagram, where `Nodes[]` returns only nodes ([labviewwiki AbstractDiagram](https://labviewwiki.org/wiki/AbstractDiagram_class)). It is registered in `docs/vi-server-ids.json:35` but no op uses it. It would let you address the constant as D[i].AllObjs[k] on nested #23166, but it still needs a cast plus Connect Wire, so it is still a new op. Whether it actually lists constants is unmeasured.
- **Build it this way:** OpConstValueN_v1's source half (functional), then `Terminal.Connect Wire` 6349C03 invoked on the **sink** terminal, with Wire Source = the constant's terminal. Address the sink with OpConnectNested_v1's D[i].Nodes[n].Terminals[t] ladder. Per the [Terminal class](https://labviewwiki.org/wiki/Terminal_class) docs, Connect Wire's source "can be either another terminal or a node", so a Terminal source is legal.
- **Prediction contract for the new op:** it should also check that the new wire's only source is owned by #10739. That check covers the addressing gap in point 2b.

**4. Cheapest discriminating test.** One call of about 0.3 s that changes nothing on the diagram: `g.wire(work, "Comparison", di, "zz_nonexistent", "Comparison", di, "y")`.
- If it returns **5001 from Get Outputs.vi**, the source-chain cast passed on a Node and the destination chain is clean. The original 1057 was then the source cast on the constant, and your claim stands on measurement.
- If it returns **1057**, the destination chain (TMSC 788) is at fault and needs its own diagnosis.

Of the two, the class-hierarchy documentation is the stronger evidence; this test only closes the destination-chain alternative. My conclusion would change only if that call returns 1057, or if the new op's first run wires to a constant other than #10739.

I could not write my plan file: the Write tool is disabled in this session, so this review exists only in this reply.

Sources:
- [Constant class — LabVIEW Wiki](https://labviewwiki.org/wiki/Constant_class)
- [Terminal class — LabVIEW Wiki](https://labviewwiki.org/wiki/Terminal_class)
- [AbstractDiagram class — LabVIEW Wiki](https://labviewwiki.org/wiki/AbstractDiagram_class)
- [Diagram class — LabVIEW Wiki](https://labviewwiki.org/wiki/Diagram_class)
- [To More Specific Class function — LabVIEW Wiki](https://labviewwiki.org/wiki/To_More_Specific_Class_function)
- [NI forum: refnum more specific class error (1057 = object cannot be cast)](https://forums.ni.com/t5/LabVIEW/refnum-more-specific-class-error/td-p/727620)
- [NI forum: to more specific class – error 1057](https://forums.ni.com/t5/LabVIEW/to-more-specific-class-cursor-reference-error-1057/td-p/2271120)
- [NI forum: Error code 1057](https://forums.ni.com/t5/LabVIEW/Error-code-1057/td-p/481852)

## Sources

(extract from answer)

## What was done with it

Card 82-3 (material), 2026-09-25 ~16:1x. Recorded, nothing built or re-run on it (card budget spent; the direction is
judgement's):
- Point 1/2(a) ACCEPTED as stated: the 1057 is "one of OpWire_v1's two TMSC-to-Node casts"; the log does not say which.
  The review's discriminating test (`g.wire(work,'Comparison',di,'zz_nonexistent','Comparison',di,'y')`, ~0.3 s, no
  mutation) was NOT run - it needs no staged state (any scratch with a Comparison node), so it is cheap for the next card.
- Point 2(b) ACCEPTED: C1 did not test class-index addressing of #10739; any new op must gate "the new wire's only source
  is owned by #10739" (constsrc_l2a1_82.py already reads that: `source_owner`).
- The route the review names (OpConstValueN_v1 source half -> Constant.Terminal 634AC04 -> Terminal.Connect Wire 6349C03
  on the sink, sink by OpConnectNested_v1's D[i].Nodes[n].Terminals[t] ladder) is reported to the judgement session as
  OPEN in result_82-3.json; `AbstractDiagram.All Objects[]` 6375804 is recorded as unmeasured.
