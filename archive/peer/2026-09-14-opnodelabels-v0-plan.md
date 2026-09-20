---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, plan]
---

# opnodelabels-v0-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (35s)
- **why asked:** plan review before building OpNodeLabels_v0 (cast-free Node.Label reader for the 88 implicit Value property nodes; crash risk from spec s30)
- **verdict:** unverified

## Question

PLAN REVIEW (attack; one paragraph). GOAL: attribute the main VI's 88 IMPLICIT Value property nodes to their front-panel controls, cast-free. Your previous answer (archive/peer/2026-09-14-implicit-property-node-linked-object.md): Property.Linked Control 636F806 needs a Property-typed ref (no cast available); the cast-free fallback is Node.Label 6359001 -> Text.Text, whose text is the implicit node's header (control name), with LabVIEW Wiki's caveat that the label must have been displayed once. PLAN: new op OpNodeLabels_v0 = copy of OpNetInfo_v1 (proven donor of OpSubVIs_v1: Traverse Diagram by index -> TMSC -> Diagram.Nodes[]), creator subVI deleted as before; wire Nodes[] into a For loop; inside: Property node class Node [Label 6359001, UID 632A813] -> Property node class Text [Text 632D800] fed from 'Label'; exit_loop Text + UID -> two auto-indexed array indicators. Wrapper node_labels(target, diagram) -> [{uid,label}]. TESTS: T1 scratch copy of OpFPLabels_v0 (known node set; expect labels of its own property nodes, mostly empty) ; T2 main VI diagram 1 (3 implicit Value PNs, uids 10399/10793/12476 from the terminal sweep) with the panel CLOSED, expect their labels to be panel control names present in docs/main-vi-panel-map.md (114 labels); T3 sweep all 170 diagrams, join by uid with the Value census; PREDICTION: >= 80 of 88 implicit PN labels are panel labels; explicit (reference-wired) PNs give '' . KNOWN RISK (keystone-op-spec s30, 2026-09-07): a node_info op reading Node.Label+Node.Style CRASHED LabVIEW in 8 s on op VIs containing To More Specific Class / class-specifier constants; never isolated which property or node type. The main VI census (626 nodes) has no TMSC/ClassSpecifierConstant (classes: Function, Property, SubVI, IndexArray, GrowableFunction, CaseStructure, ControlReferenceConstant 21, BuildArray, ForLoop, Bundler, NamedUnbundler, Comparison, Local, Global, PolymorphicSubVI, Sequence, CompoundArithmetic, Unbundler, WhileLoop, FlattenString, InRangeAndCoerce, EventStructure, FormatScanString, NamedBundler, ArrayToCluster, Invoke 1, ReadWriteFile). Mitigation: the op reads Label only (no Style), bgrun deadline, main VI opened by reference only (never saved), LabVIEW restart is pre-authorised. ATTACK: (a) is the 2026-09-07 crash more plausibly Node.Style (a ring/style read) or Node.Label, and is a crash on ControlReferenceConstant / Invoke / EventStructure nodes a real risk for Node.Label; (b) does the 'must be displayed at least once' caveat mean a headless read (panel closed, block diagram never opened in this instance) returns '' for implicit PN headers - if so what is the cheapest cast-free workaround (open the block diagram window once? Node.Label is a Text refnum: does Text.Text still read?); (c) any better cast-free identity for an implicit property node (e.g. Node.Terminals[] 'reference' terminal's Name, already measured as 'reference'; Property.Property Names; GObject.Description) - one paragraph.

## Answer

Attack: the plan is reasonable but the predicted ??0/88 is not yet justified. The 2026-09-07 evidence cannot distinguish `Node.Style` from `Node.Label`; if forced, I would suspect the `Label ??Text.Text` dereference more than `Style`, because NI documents `Style` as a simple read-only string that does not load either window, whereas `Label` returns an optional `Text` reference whose existence depends on display history ([NI: Node.Style](https://www.ni.com/docs/en-NF/csh?context=lvcore_lvscript_node_style), [LabVIEW Wiki: Node.Label](https://labviewwiki.org/wiki/Node_class/Label_property)). There is no published basis for expecting `Node.Label` itself to crash on `ControlReferenceConstant`, `Invoke`, or `EventStructure`; nevertheless, T1 does not exercise those classes, so the cheapest safety gate is a disposable mixed-node fixture containing exactly those classes before touching the main VI. The caveat means the **label object must previously have been displayed**, not merely that the VI or block-diagram window was opened: opening the diagram once is therefore not a reliable workaround, and `Text.Text` cannot rescue a null/invalid label refnum. More importantly, although NI says an implicitly linked property node displays the linked control?셲 label/name, this does not prove that the displayed header is the same object exposed by generic `Node.Label` ([NI: implicit versus explicit nodes](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000wwBXCAY&l=en-US)); T2 should therefore be treated as the decisive feasibility test, preferably first on a tiny scratch VI whose implicit-node label has never been manually shown. `Terminals[]` names, property-item names, UID, and `GObject.Description` cannot identify the linked control; they describe interface, operation, instance, or documentation respectively. The only authoritative identity is `Property.Linked Control`, explicitly documented to return the linked control or null/error when none exists ([LabVIEW Wiki](https://labviewwiki.org/wiki/Property_class/Linked_Control_property)). If T2 yields blanks, abandon the 170-diagram sweep: the cheapest robust cast-free workaround is likely to invert the query by iterating the 114 controls and calling `Control.Create:Property Node` on a disposable diagram, whose return is already Property-typed, then use that typed seed/donor to access `Linked Control`; otherwise a one-time typed Property cast seed is cleaner than opening/showing 88 labels.

## Sources

(extract from answer)

## What was done with it

Built and tested as planned with T2 as the decisive test (test_opnodelabels.log 14:45): 7/7 PASS — the three
implicit nodes of diagram 1 read 'Auto-reset zero', '# of Auto-Reset', 'Lost Frame Message' (all panel labels) with
the panel closed, then 88/88 over all 170 diagrams; no crash on 626 nodes including ControlReferenceConstant /
Invoke / EventStructure; handles flat. The mixed-node fixture gate was not built (the main VI itself was the gate,
with restart pre-authorised). The typed-seed fallback (Control.Create Property Node) was not needed and is recorded
in docs/toolkit-capabilities.md as the route to Linked Control if ever required. Verdict: correct; the caution on
the displayed-once caveat was right to raise and turned out not to bite.
