---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# opshiftregs-v0-fail1-loop-body-index

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (50s)
- **why asked:** failed prediction in build_opshiftregs_v0.log run 1 (ExecState 0 after wiring Inside Terminals[] into a second For loop)
- **verdict:** unverified

## Question

FAILED PREDICTION, attack my explanation (one paragraph). tools/bench/build_opshiftregs_v0.log (recipe tools/recipes/build_opshiftregs_v0.py, donor OpWhileCast_v0 which ALREADY contains one For loop over Loop.Shift Registers[]). Steps 2-7 all met their predictions (Index Array on Shift Registers[], GObject.Class Name, Tunnel.Outside Terminal chain, Tunnel.Inside Terminals[] node: ExecState 1 throughout). Step 8a created a SECOND For loop on the top diagram (ForLoop 1->2, ExecState 0 expected: empty loop, no N). Step 8b built PN_IN Terminal[Name] 'inside the new body' - the body was chosen as the Traverse 'Diagram' index owned by a ForLoop that was NOT in the set captured before creation (set difference of INDICES). Step 8c wired PN_IT's Inside Terminals[] array into PN_IN.reference: LoopTunnel +1, Wire +2 (a loop crossing, as in the proven OpTunnels_v0 build) but ExecState stayed 0 - PREDICTED 1 (an auto-indexed array input supplies N). MY EXPLANATION: Traverse's Diagram ordering changed when the second loop's diagram was inserted, so the index I took as 'new' pointed at the OLD loop's body; PN_IN was built inside the old loop (whose auto-indexed input is Shift Registers[]), the wire from PN_IT crossed into the OLD loop (tunnel +1 fits), and the NEW loop is still empty with no N -> broken. ALTERNATIVES: (a) the new input tunnel defaulted to NON-indexing (then N missing) - but the same construction indexed by default in OpTunnels_v0; (b) mixing two auto-indexed inputs of different lengths on one loop is fine in LabVIEW (min N), so it is not that. DISCRIMINATING TEST I plan: read node_labels per diagram (which diagram holds PN_IN uid 800) and the new loop's tunnels count; FIX: identify the new body by its Diagram UID (report_all rows carry uid) rather than by index, and require 'the new loop has 1 tunnel' after 8c. QUESTIONS: is Traverse for GObjects' order for class Diagram creation-ordered or spatial/z-ordered (NI docs?) - i.e. is index-based identification of diagrams ever safe; anything else that would leave ExecState 0 after a legal auto-indexed input on a fresh For loop?

## Answer

Your explanation is plausible but overclaims the mechanism: NI documents neither creation-order nor spatial/z-order for traversal?봧ts `All Objects[]` contract only promises an array of top-level objects?봲o index identity is never safe, but the evidence does not yet prove PN_IN landed in the old body; your proposed UID/owner test is the right discriminator, preferably following PN_IN?셲 owner/parent chain to the enclosing ForLoop UID rather than merely correlating `node_labels` by diagram index, and verifying that the intended new loop owns the added tunnel ([NI API](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/abstractdiagram/allobjects.html), [NI Community UID example](https://forums.ni.com/t5/LabVIEW/finding-insane-objects/td-p/3844027)). Alternative (a) remains live until you inspect the tunnel?셲 indexing property: NI says array tunnels on For Loops normally default to indexing and then supply the iteration count, but ?쐍ormally??does not establish that your scripting construction produced that mode ([NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG)); alternative (b) is correctly excluded because multiple indexed arrays use the shortest length and do not break the loop ([NI](https://www.ni.com/en/support/documentation/supplemental/08/labview-arrays-and-clusters-explained.html)). Other credible causes of ExecState 0 are a broken/type-incompatible wire, an unwired required terminal on PN_IN, or a conditionally configured For Loop whose conditional terminal is unwired; NI explicitly says a conditional For Loop requires that terminal plus either N or an indexed input, and recommends the Error List as the authoritative broken-VI diagnosis ([NI conditional loops](https://www.ni.com/en/support/documentation/supplemental/07/configuring-labview-for-loops-to-exit-conditionally.html), [NI debugging](https://www.ni.com/en/support/documentation/supplemental/12/debugging-techniques-in-labview.html)).

## Sources

(extract from answer)

## What was done with it

Ran the discriminator (build_opshiftregs_v0.log run 2): the new loop's body appeared at Traverse Diagram index 1
(uid 1030), not after the old body — so the index-difference method had built PN_IN inside the OLD loop; identified
by diagram UID and checked by membership (node_labels of the new body lists PN_IN), the wire crossed into the NEW
loop, its tunnel read index_mode 1 (alternative (a) excluded by inspection, as asked) and ExecState went to 1. Rule
recorded in docs/NAMES.md: never identify a diagram by index across a structure creation. Verdict: correct.
