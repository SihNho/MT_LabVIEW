---
type: peer-review
status: historical
date: 2026-09-01
tags: [peer-review, plan]
disposition: legacy
---

# 2026-09-01-opwireref-donor-plan-attack

- **agent:** codex
- **date:** 2026-09-01
- **outcome:** ANSWERED (84s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this construction plan - find what breaks, cite sources (labviewwiki.org, NI forums, github.com/erdosmiller/lv-scripting). LabVIEW 2026, ActiveX-driven op-VI fleet.

GOAL: script wiring between UNNAMED terminals (primitive outputs, tunnel outer terminals, property-node reference), which named-based Wire Inputs cannot reach.

PLAN: (P1) DONOR_prims.vi built once by hand: Index Array, 3-output Decimate, 3-input Interleave, To More Specific Class, each given an owned LABEL so the existing label-based cross-VI copier can fetch them. (P2) OpWireRef_v0: open target -> Traverse for GObjects(class A, index i) -> obtain a TERMINAL refnum of that object -> same for (class B, index j) -> feed both to vi.lib Erdos Miller 'Conditionally Connect Wire.vi' -> creates the wire. Terminal refnums obtained via scripting properties: LoopTunnel has 'Inside Terminals[]' and 'Outside Terminal' (confirmed in the property picker); for generic nodes we assume a 'Terminals[]' property on the Node class, indexed to pick input/output.

QUESTIONS: (1) Node class 'Terminals[]' - does it exist, what ORDER are terminals returned in (documented?), and is the order stable across LabVIEW versions/saves for primitives like Interleave/Decimate? How does one reliably identify WHICH element is 'array 0' vs output? (2) 'Conditionally Connect Wire.vi' - its exact inputs (two Terminal refnums? a 'connect?' boolean? direction constraints - must one be a source?) and failure modes: what happens on illegal type pairs, already-wired source (branch?), cross-diagram pairs (does it auto-create tunnels on border crossing like manual wiring does)? (3) The label plan: 'Node.Label' wiki page warns the label must have been DISPLAYED before Label/Text is reliable - does writing Label.Text FORCE visibility, or must 'Visible Items>Label' be toggled first (scriptable property 'Label.Visible'?)? Do owned labels on primitives SURVIVE a cross-VI copy (Generic:Duplicate + move)? (4) Copy semantics: does duplicating a GROWN primitive (3-output Decimate) preserve its terminal count in the copy? (5) Alternative you should score: skip Terminals[] entirely - for LoopTunnels use Outside Terminal/Inside Terminals[]; for primitives, wire by creating them fresh with the Create *.vi family (Create Index Array takes wire-source refnums and RETURNS terminal refnums) inside ONE fused op per topology - is that more robust than a generic OpWireRef? What does the erdosmiller library itself use to find terminals of existing nodes?

## Answer

The plan?셲 weak point is not whether `Node.Terminals[]` exists?봧t does. The weakness is treating terminal-array indices, copied labels, and diagram-crossing behavior as a durable addressing protocol. They are not sufficiently documented for that role.

## Verdict

- `OpWireRef_v0` is acceptable as a low-level wiring primitive only after both endpoints have already been resolved semantically.
- `(class, traversal index, terminal-array index)` is too brittle to be the persistent topology description.
- For growable primitives, use their specific scripting classes/properties or topology-specific creation VIs.
- Do not assume `Conditionally Connect Wire.vi` creates tunnels or safely handles arbitrary endpoint order.
- The donor-label scheme has a bootstrap problem and should not be the sole identity mechanism.
- Score: generic `OpWireRef` 4/10; fused topology-specific creators 8/10.

## 1. `Node.Terminals[]`

It exists. It is the read-only `Node.Terminals[]` property and returns terminal references. LabVIEW Wiki explicitly says that the way to select one is the terminal index shown by Context Help?봭ot geometric or array order inferred by the caller. [LabVIEW Wiki: Node.Terminals[]](https://www.labviewwiki.org/wiki/Node_class/Terminals%28%29_property)

NI forum guidance confirms:

- Ordinary Function/SubVI terminal indices can be displayed by enabling ?쏡isplay additional VI Scripting information in Context Help.??- Growable functions are the exception: their generic terminal array is not sufficiently self-describing, so specific subclasses may expose semantic properties.
- `IndexArray`, for example, exposes `Array Input Terminal`, `Index Count`, `Index Terminals[][]`, and `Output Terminals`.
- For less-specialized nodes, terminal properties such as name, `Is Source?`, and datatype can help classify endpoints. [NI: Scripting?봗erminal Information](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/m-p/4303374)

Attack on the plan:

1. There is no cited contract that generic array position means ?쐔op-to-bottom,???쐇nputs then outputs,??or ?쏿rray 0, array 1, output.??2. The wiki?셲 instruction to use Context Help indices implies that indices are node-defined identifiers, not something you should derive from layout.
3. The available sources do not promise stability across LabVIEW versions, primitive mutation, save/load, or replacement.
4. Decimate and Interleave are growable primitives?봳he exact category for which the NI answer recommends specific subclass facilities rather than generic `Terminals[]`.

Therefore, do not identify ?쏿rray 0??using only `Terms[][n]`. Resolution should prefer, in order:

1. Primitive-specific properties such as input/output terminal arrays.
2. A fixed terminal index captured from LabVIEW 2026 Context Help and verified against terminal direction/datatype.
3. Terminal geometry only as a guarded last resort.
4. Fail closed if the resulting signature differs from the expected count/directions/types.

For a property node reference input, terminal properties can distinguish the conventional reference/error terminals from item terminals, but the NI example is descriptive, not a version-stability guarantee. [NI: Scripting?봗erminal Information](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/m-p/4303374)

## 2. `Conditionally Connect Wire.vi`

I could not establish its exact connector pane from the public GitHub rendering. The repository publishes LabVIEW binary VIs and describes the package broadly, but its HTML-visible source does not document this VI?셲 connector terminals. Any confident claim about ?쐔wo terminal refs plus connect boolean??would therefore be a guess. [Erdos Miller lv-scripting repository](https://github.com/erdosmiller/lv-scripting)

What can be established about underlying LabVIEW wiring:

- LabVIEW?셲 scripting connection operation works between terminal/node endpoints; some object classes, notably Flat Sequence, do not participate normally because they do not inherit from `Node`. [NI: Connect a Terminal to a Flat Sequence Structure](https://forums.ni.com/t5/LabVIEW/Scripting-Connect-a-Terminal-to-a-Flat-Sequence-Structure/td-p/2672239)
- Endpoint order can materially change tunnel wiring behavior. A case-tunnel example reports different incorrect results after swapping the two terminal parameters. [NI: wiring a pass-through tunnel](https://forums.ni.com/t5/LabVIEW/LabvVIEW-Scripting-wiring-a-pass-through-tunnel-inside-a-case/m-p/3945608)
- Connecting terminals across a structure boundary can automatically create a tunnel. [NI: Programmatically creating a tunnel](https://forums.ni.com/t5/LabVIEW/Programmatically-creating-a-tunnel-with-LV-scripting/td-p/1830745)
- That behavior does not mean it will reuse the particular tunnel you intended, choose the desired tunnel mode, or route through the desired subdiagram.
- Existing loose/broken wires cannot simply be reattached through the ordinary terminal connection operation; a successful workaround deletes and recreates the wire using `Create Described Wire`. [NI: connect loose wires to case tunnels](https://forums.ni.com/t5/LabVIEW/Script-connect-existing-loose-wires-to-case-tunnels/m-p/4195933)

Expected failure classes that `OpWireRef` must expose and verify:

- sink-to-sink or otherwise directionally invalid endpoints;
- incompatible datatypes;
- endpoints belonging to different VIs;
- endpoints residing in incompatible subdiagrams;
- accidental branch creation when the source already owns a wire;
- attempted second driver on an already-wired sink;
- automatic creation of an unwanted tunnel;
- connection to the wrong inside terminal of a multi-frame structure;
- broken wire created instead of a rejected operation.

Do not trust ?쐍o ActiveX error??as success. After connection, inspect the returned wire/reference if available, verify each endpoint?셲 connected-wire state, verify both endpoints??owning diagrams, and verify the target VI is not broken.

Before using the Erdos Miller helper, have the manager produce reporter output for its connector pane and block diagram. That is the only safe way here to settle its exact inputs and internal behavior.

## 3. Donor labels

The warning is real: `Node.Label` returns the label reference, and the label must have been displayed at least once before it can reliably return its text. [LabVIEW Wiki: Node.Label](https://labviewwiki.org/wiki/Node_class/Label_property)

Nothing in that source says that writing `Label.Text` implicitly displays or initializes the label. In fact, obtaining the text-object reference through `Node.Label` is the operation affected by the ?쐂isplayed once??precondition. So ?쐗rite text first and assume visibility is forced??is circular and unsupported.

Safer donor construction:

1. Manually show each owned label when the donor is authored.
2. Assign unique text.
3. Save, close, reopen, and confirm through reporter output that the label and text remain.
4. The label may then be hidden if reporter verification shows its reference/text remains usable.

I found no authoritative source promising that primitive-owned label state survives every cross-VI `Duplicate + Move` operation. Copies normally preserve object configuration, but that is not enough evidence for a critical addressing mechanism. There is also a separate scripting hazard: some duplicate/move workflows return the original object reference rather than the new copy, and forum guidance recommends other creation mechanisms or before/after discovery. [NI: get reference of duplicate element](https://forums.ni.com/t5/LabVIEW/VI-Scripting-get-reference-of-the-duplicate-element/td-p/1882509)

Thus labels should be treated as discovery hints, followed by structural verification?봭ot identity.

## 4. Copying grown primitives

A true object duplication would be expected to preserve the donor?셲 grown state, but I found no source in the requested source families that documents this as a cross-version contract for Decimate or Interleave. Treat it as unverified.

The important distinction is:

- Copying/duplicating the configured object should ordinarily clone its current form.
- Creating a new primitive ?쐎f the same style??may produce its default terminal count.
- A duplicate API may not return the new object reference reliably. [NI: duplicate element reference](https://forums.ni.com/t5/LabVIEW/VI-Scripting-get-reference-of-the-duplicate-element/td-p/1882509)

Required cheap acceptance test: reporter output before and after duplication must compare node class, bounds, terminal count, per-terminal source/sink direction, datatype, and any grow-count property. Do this specifically in LabVIEW 2026 after save/reopen.

## 5. Better alternative

Use fused, topology-specific creators.

For tunnels:

- Resolve `Outside Terminal` and the correct element of `Inside Terminals[]`.
- Also verify the inside terminal?셲 owning subdiagram. A tunnel has one outer terminal and an inside terminal per case/frame; selecting merely by array position without owner verification is risky. [NI: pass-through tunnel scripting](https://forums.ni.com/t5/LabVIEW/LabvVIEW-Scripting-wiring-a-pass-through-tunnel-inside-a-case/m-p/3945608)

For growable primitives:

- Create/configure them inside the same op that wires them.
- Prefer factory VIs that accept source-wire references and return semantic terminal references.
- Otherwise use primitive-specific properties such as `IndexArray.Array Input Terminal`, `Index Terminals[][]`, and `Output Terminals`. [NI: Scripting?봗erminal Information](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/m-p/4303374)

This removes four unstable joins:

```text
donor label
??copied-object rediscovery
??generic terminal-array interpretation
??later cross-op reference reconstruction
```

The Erdos Miller library?셲 published description says it supplies higher-level, concise code-generation VIs and examples, but the web-visible repository does not establish that it has a universal semantic terminal finder for existing growable nodes. [Erdos Miller lv-scripting](https://github.com/erdosmiller/lv-scripting) Until reporter output shows otherwise, assume its create-family VIs avoid terminal rediscovery by retaining references returned during creation?봭ot that they solve arbitrary existing-node terminal identity.

## Recommended redesign

Keep `OpWireRef`, but narrow its contract:

```text
OpWireResolvedTerminals(source terminal ref, sink terminal ref)
```

It should not perform generic `(class, occurrence, terminal index)` lookup. Put semantic endpoint resolution in topology-specific ops, validate direction/owner/datatype before connecting, and validate the resulting wire afterward.

The plan should not proceed until reporter output settles:

- `Conditionally Connect Wire.vi` connector pane and diagram;
- LabVIEW 2026 terminal signatures for each exact grown donor;
- duplicate/save/reopen preservation of grow count and owned labels;
- behavior for already-wired source, already-wired sink, and cross-boundary connection.

## Sources

(extract from answer)

## What was done with it

**Dispositioned 2026-09-17, sixteen days late** — surfaced by
`archive/peer/2026-09-17-priorart-priorart-connectfromwire.md` A2, which found this file un-dispositioned while
reviewing an op of the same shape. **verdict: ADOPTED, and it was right on both counts.**

* **Its verdict was followed, though not by name.** *"Score: generic `OpWireRef` 4/10; fused topology-specific
  creators 8/10"* — no generic `OpWireRef` was ever built. What the fleet has instead is a family of fused,
  topology-specific writers: `OpConnect_v0` / `OpConnect2_v0` / `OpConnectCtl_v0` / `OpConnectNested_v0` /
  `OpConnectNested_v1` / `OpStopFromNode_v0` / `OpCreateConstOnTerm_v0` (`docs/toolkit-capabilities.md`). That is
  this review's recommendation, arrived at by attrition rather than by reading this file.
* **Its condition governs the next one.** *"`OpWireRef_v0` is acceptable as a low-level wiring primitive **only
  after both endpoints have already been resolved semantically**"* is now the licence under which
  `OpConnectFromWire_v0` is built: the endpoints are resolved OFFLINE first
  (`tools/bench/d1_rewire_sources.json` 109/109, `tools/bench/d1_tunnel_sources.json` 18/18), and the indices are
  recomputed immediately before each call rather than stored as the topology description.
* **Its failure-class list (`:77-89`) is the acceptance matrix**, including the one that actually bit us —
  *"broken wire created instead of a rejected operation"* — and its closing instruction, *"verify each endpoint's
  connected-wire state, verify both endpoints' owning diagrams, and verify the target VI is not broken"*, replaced
  the unsound RBW-uid gate on 2026-09-17 (`docs/d1-build-plan.md` §11u.1). Had this disposition been written in
  September, run 9's gate would not have been built the way it was.
* **Not adopted:** the `Conditionally Connect Wire.vi` / donor-label parts are moot — the fleet uses
  `Terminal.Connect Wire` 6349C03 directly and addresses donors by traverse index, not by copied labels.
