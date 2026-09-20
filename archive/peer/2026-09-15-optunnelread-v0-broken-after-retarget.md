---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# optunnelread-v0-broken-after-retarget

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (51s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

BRIEF ATTACK (LabVIEW 2026 VI Scripting). tools/bench/build_optunnelread_v0.log run 2, script tools/recipes/build_optunnelread_v0.py: I derived OpTunnelRead_v0 from the verified OpWireSource_v5 by retargeting its lookup cast from Wire to Tunnel and replacing Wire.Terms[] with Tunnel.Inside Terminals[] 6356000. All three REFERENCE PROVENANCE gates pass - Tunnel-typed seed -> cast target class; cast output -> Inside Terminals[] node (268/268); Inside Terminals[] -> Index Array array (496/496) - but ExecState is 0 after the retarget (it was 1 before, went 0 when I deleted the three old wires plus the obsolete Wire.Terms[] node, and stayed 0 after rewiring). The deletions were: the Terms[] output wire, the Wire-typed seed wire into the cast target class, the Tunnel seed auto-wire, then the Wire.Terms[] NODE. MY HYPOTHESIS, from the same trap twice before: one of those wires was a BRANCH feeding a sink I did not enumerate (most likely the old cast output also fed the Is Source? / Connected Wire / Owner chain nodes, whose reference inputs are now unwired), so the fix is to re-feed every orphaned reference sink from the new cast output - I have added a dump of every unwired SINK terminal plus that repair, the same localisation that worked in OpWireSource_v5. QUESTIONS: (1) is that the likeliest cause, or should I suspect a TYPE break instead - the downstream nodes are class Terminal and the Index Array now carries Tunnel inner terminals, which should still be Terminal-typed, so I expect no type change; (2) when a cast is retargeted from Wire to Tunnel, do the property nodes downstream of the INDEX ARRAY (which consume terminals, not the cast output) need anything changed at all; (3) is there any risk that the Wire-typed seed control, now left unwired on the panel, breaks the VI - I believe an unwired control terminal is legal; (4) anything else that turns ExecState 0 after deleting a node whose output fed nothing. Read-only; cite what you read.

## Answer

Your branch-orphan hypothesis is the clear favorite, not a type break.

1. **Most likely: deleting a shared wire removed other branch sinks.** LabVIEW represents one source feeding multiple readers as a branched wire; deleting that wire object can therefore disconnect sinks you did not enumerate. Your three provenance gates prove the replacement route, while `ExecState 0` is consistent with another required `reference` input becoming unwired. NI identifies an unwired required input or broken wire as the usual reason a VI becomes nonexecutable. [NI: Using Wires to Link Block Diagram Objects](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html), [NI: Debugging Techniques](https://www.ni.com/en/support/documentation/supplemental/12/debugging-techniques-in-labview.html)

   The especially suspicious operation is `delete Wire.Terms[] node` followed by `Remove Bad Wires`: the node?셲 **input** was the cast-output branch. Your proposed orphan-sink dump and selective re-feed from the new cast output is exactly the right discriminator. The same failure and repair already occurred in `OpWireSource_v5`, as recorded in [STATUS.md](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/STATUS.md).

2. **No downstream changes should be required after Index Array.** `Inside Terminals[]` produces terminal references, so the indexed element remains Terminal-typed. Nodes consuming that element??Is Source?`, `Connected Wire`, `Owner`, and `Terminal.Diagram`?봮perate on the terminal reference, not on the Tunnel cast output. Retargeting `To More Specific Class` changes the cast wire?셲 type; it does not retroactively change an independently typed downstream Terminal wire. NI describes the target-class input as selecting the cast output class. [NI: Class Specifier Constant](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/constants/class-specifier.html)

   Attack condition: if reporter output shows the Index Array `element` wire or a downstream wire broken, then this conclusion is wrong. Your current 496/496 provenance only proves endpoint identity, not that the wire compiled cleanly.

3. **The abandoned Wire-typed panel control does not break this VI merely by being unwired.** A control terminal is a data source and may sit unused. ?쏳equired terminal unwired??applies to required inputs of functions/subVIs, not to an unused front-panel control terminal. [NI: Using Wires to Link Block Diagram Objects](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

   Caveat: if that control is assigned as a **required connector-pane input**, callers may be broken when they omit it; that is separate from the control?셲 own diagram terminal being unused.

4. Other plausible causes, in descending order:

   - `Remove Bad Wires` removed the entire shared cast-output wire rather than only the now-dangling branch.
   - Deleting the old property node also severed an error-chain branch or another required input.
   - A connected wire is type-broken despite matching endpoint UIDs; incompatible types produce a broken wire and prevent execution. [NI: Using Wires to Link Block Diagram Objects](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)
   - A downstream property node remained typed for `Wire` only if it was directly fed by the cast output. Such nodes must be retargeted or removed; Terminal-fed nodes do not.
   - Stale compilation is possible but materially less likely than a real orphan, given that `ExecState` changed exactly at destructive edits.

Best cheap check: dump every unwired non-error sink, re-feed only orphaned `reference` sinks formerly supplied by the cast-output net, then test `ExecState`. If it stays 0, obtain LabVIEW?셲 Error List text?봳he Error List is NI?셲 authoritative localization for broken VIs. [NI: Debugging Techniques](https://www.ni.com/en/support/documentation/supplemental/12/debugging-techniques-in-labview.html)

## Sources

(extract from answer)

## What was done with it

Confirmed the branch-orphan reading and ran the prescribed discriminator: the recipe now dumps every unwired SINK
after the retarget and re-feeds each orphaned `reference` from the new cast output (the same localisation that fixed
`OpWireSource_v5`). Two points taken as standing cautions rather than assumptions: endpoint-uid provenance proves
identity, NOT that a wire compiled — if the dump shows the Index Array `element` wire or a downstream wire broken,
the "nothing downstream needs changing" conclusion is wrong; and a node that was fed DIRECTLY by the cast output (as
the old `Wire.Terms[]` node was) must be retargeted or removed, while Terminal-fed nodes are unaffected. The
unwired Wire-typed seed control left on the panel is legal and is left in place.
