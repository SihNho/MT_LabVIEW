---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, plan]
---

# wiregraph-frame-loop-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (73s)
- **why asked:** See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
- **verdict:** see 'What was done with it' / STATUS.md 2026-09-14

## Question

PLAN REVIEW (attack; be concrete). GOAL: restructuring stage 1 - derive the FUNCTIONAL UNITS of the main VI's frame loop (diagram 43, WhileLoop, 75 nodes) from the WIRE GRAPH, offline, no LabVIEW. The user ran Clean Up Diagram so positions mean nothing; wiring is intact. DATA NOW AVAILABLE: tools/bench/main_vi_nodeterms.json - for every node of every diagram: Nodes[] index, node UID, and per terminal (index, name, Is Source? [TRUE = output], connected-wire UID or 0); tools/bench/main_vi_subvis.json - subVI call identity per uid (diagram 43: IMAQ Write TIFF File 2, WLC function sub.vi, ASI_adjust focus-subvi.vi, Track N beads four-fold over-kernel-v3.vi #5058, save trace.vi, get buff image-lost frames.vi); tools/bench/diagram_tree_main.json - owner structure per diagram and structure uids (WhileLoop/ForLoop/CaseStructure/Sequence/EventStructure lists). METHOD: build the directed graph of diagram 43: edge = wire uid shared by an output terminal (Is Source? TRUE) of node A and an input terminal of node B; a wire uid seen on only ONE node inside the diagram = crosses the loop boundary (tunnel / shift register) or reaches a structure's own terminal - list those as boundary edges with the node+terminal; then (1) backward slice from the kernel call (#5058): every node that feeds it, per input terminal; (2) forward slice: every consumer of its outputs; (3) weakly connected components of the remaining nodes = candidate functional units; (4) label each component by its subVI identities + terminal names (e.g. 'save trace.vi' + file path terminals = the saving unit; 'IMAQdx Get Image'/'get buff image-lost frames' = acquisition; 'ASI_adjust focus' = focus unit; property nodes with 'Value' rows = display/UI unit); (5) nested structures inside diagram 43 (case structures / loops whose bodies are other diagrams) appear as single nodes with tunnel terminals - keep them as one node each, but list their child diagrams (tree) and the subVIs inside them; (6) output docs/frame-loop-wire-graph.md + tools/bench/frame_loop_graph.json. ATTACK: (a) a wire uid with multiple sinks (fan-out) - does the same wire uid appear on every sink terminal, so edges are 1-to-N correctly? (b) structures' boundary: for a Case Structure node inside 43, its terminals in Node.Terminals[] are the tunnels? or none - what does the sweep show for structure nodes (I can check: node uids 15173/25380? - the sweep rows) - if tunnels are NOT terminals, wires into a nested case appear as boundary edges and the nested body's nodes are in another diagram: how to stitch them (tunnel terminals inside the child diagram carry the same wire uid on both sides? or different wires); (c) shift registers / the loop's own terminals (i, N) - how they show; (d) is 'weakly connected component' the right unit, given error-cluster wires and the VISA/session refs thread through almost everything (error chains connect unrelated units) - propose which wire classes to CUT before componentizing (error clusters by terminal name 'error in'/'error out'; refnums by 'VISA'/'session' names; the image ref) and the risk of over-cutting; (e) any way to get the datatype of a terminal cast-free (Terminal.'Data Type'? id) to cut by type instead of by name. Keep it to failure scenarios + the cheapest check each.

## Answer

The plan is directionally good, but two assumptions can silently corrupt the graph: ?쐗ire UID = logical net??and ?쐎ne occurrence = loop boundary.??Validate those before doing any slicing.

1. Fan-out may not be one UID

NI distinguishes a logical wire from its individual branches and segments; one source may feed many sinks, while each branch is a separate portion of the drawn wire. Therefore, do not assume a branched net necessarily has one scripting UID across every sink. [NI: Using Wires to Link Block Diagram Objects](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

Failure scenario: the source-to-junction branch and junction-to-sink branches have different UIDs. Exact-UID grouping then produces a source with no consumers plus several apparent boundary inputs.

Cheapest check:

- Histogram each nonzero wire UID by `source_count` and `sink_count`.
- Find one visually/reportably known fan-out.
- Verify whether all sinks share the source UID.
- Flag any UID with `source_count > 1`; ordinary LabVIEW wires have one source, so that indicates reporter semantics, malformed data, or incorrect direction classification. [NI wire documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

If fan-out uses different UIDs, the current data is insufficient to reconstruct nets. The reporter must additionally emit wire connectivity?봟ranches/segments/junctions or a canonical source terminal for every wire object.

2. ?쏶een once??is not necessarily a diagram boundary

A singleton UID can mean:

- a true diagram boundary;
- the other endpoint is a tunnel GObject omitted from `Nodes[]`;
- a structure terminal represented outside the node?셲 terminal list;
- one branch of a fan-out;
- a reporter traversal omission.

Treat these initially as `unresolved_half_edges`, not confirmed boundary edges.

Cheapest check: classify singletons by asking whether the connected wire?셲 other terminal owner is:

- the diagram?셲 owning While Loop;
- a Tunnel/LoopTunnel/ShiftRegister;
- a nested structure;
- another ordinary node missing from the export.

Only the first two justify ?쐄rame-loop boundary.??
3. Nested structures probably need explicit tunnel objects

LabVIEW defines tunnels as connection points on structure borders. Structures have subdiagrams, but the tunnel is conceptually the object joining the outer diagram to those subdiagrams. [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999e.pdf) VI Scripting also exposes structure tunnels separately?봣or example through `Tunnels[]`, with loop tunnels requiring a more specific class. [NI Community example](https://forums.ni.com/t5/LabVIEW/How-to-change-tunnel-mode-using-vi-scripting/m-p/3969401)

Consequently, I would not expect UIDs 15173/25380?셲 generic `Node.Terminals[]` alone to be a reliable inventory of Case Structure tunnels.

Cheapest check for each of those UIDs:

- Emit runtime class name.
- Emit `Node.Terminals[]`.
- Emit `Structure.Tunnels[]`.
- For every tunnel, emit tunnel UID, owner UID, terminal UID/index, connected-wire UID, terminal direction, and associated subdiagram(s).

Do not assume the outside and inside wires have the same UID. Stitch using the tunnel identity:

```text
outer wire ??tunnel UID ??child-diagram wire
```

For a Case Structure, retain per-case connections. An output tunnel may have a distinct inside wire in every case, and collapsing those into a single unconditional edge would invent impossible execution paths.

Also list all child diagrams, including empty cases. ?쏶ubVIs found in child diagrams??should be keyed by case/frame identity, not merely unioned under the structure node.

4. Shift registers and loop-owned terminals need separate semantics

Shift registers pass the right-side value from one iteration to the left side on the next iteration; they are state edges, not ordinary same-iteration dataflow. [NI: Using Shift Registers](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YKYuCAO&l=en-US)

Failure scenario: joining both sides as an ordinary edge creates a false instantaneous cycle and pollutes kernel slices.

Represent them explicitly:

```text
right terminal --[next_iteration]--> left terminal
outside initializer --> left terminal --[initial_iteration]-->
right terminal --> outside result
```

The While Loop iteration terminal `i` is an internal source, while the conditional terminal is a loop-owned sink; neither is an ordinary tunnel. A While Loop begins with iteration value zero. [NI example](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019R1XSAU&l=en-US)

Cheapest check: enumerate all GObjects owned directly by the While Loop and report their concrete class, not just the loop node?셲 `Terminals[]`. Then classify `IterationTerminal`, `ConditionalTerminal`, `Tunnel`, and `ShiftRegister` separately.

5. Raw weakly connected components will likely collapse the frame

WCC is useful only after removing ubiquitous infrastructure edges. Error clusters, VISA/session references, image references, and possibly timestamps/configuration clusters can connect otherwise distinct functional units.

However, cutting purely by terminal-name substrings is unsafe:

- `error in/out` is usually sequencing infrastructure, but sometimes error inspection or recovery is the unit?셲 actual function.
- VISA/session references identify hardware-resource continuity; removing them can split one coherent acquisition/control pipeline.
- The image reference is probably semantically central to acquisition ??tracking ??saving/display. Cutting it may manufacture exactly the functional separation you hoped to discover.

Recommended approach:

- Keep the complete graph as ground truth.
- Tag edges by role: `payload`, `error`, `resource_ref`, `image_ref`, `UI/config`, `state`.
- Compute candidate WCCs on `payload` edges after excluding only `error` and generic resource-reference edges initially.
- Produce a second componentization with image-reference edges excluded as a sensitivity test.
- Report which components merge when each edge class is restored.

Do the same for kernel slicing:

- `full causal slice`;
- `payload slice`, excluding error/resource sequencing;
- optionally `image lineage`.

Otherwise the backward slice from #5058 can include most of the frame merely because the error chain reaches it.

Cheapest sanity check: report node/component counts under four policies:

```text
all edges
minus error
minus error + resource refs
minus error + resource refs + image refs
```

A dramatic collapse or explosion identifies the problematic backbone immediately.

6. Prefer datatype over names, but verify the representation once

VI Scripting terminals expose both `Is Source?` and `Data Type`; NI Community?셲 terminal-scripting example explicitly recommends these properties when names are ambiguous. [NI Community: Scripting ??Terminal Information](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)

`Terminal.Data Type` is therefore the cheapest cast-free classification route. Export its returned variant/type representation and canonicalize it. LabVIEW represents terminal and wire types using type descriptors, including nested aggregate types. [NI: Type Descriptors](https://www.ni.com/docs/ar-SD/csh?context=lvcore_lvconcepts_type_descriptors)

Cautions:

- Do not stringify a displayed default value and call that the type.
- Preserve the complete descriptor for arrays, clusters, refnums and typedef-backed values.
- Keep terminal names as secondary evidence.
- Verify known examples: Boolean, path, error cluster, image ref, VISA/session ref and numeric array.
- Record the LabVIEW version with the descriptor because NI documents historical descriptor-format changes. [NI: Type Descriptors](https://www.ni.com/docs/ar-SD/csh?context=lvcore_lvconcepts_type_descriptors)

7. Output should preserve uncertainty

For each inferred edge, include something like:

```json
{
  "confidence": "exact-wire-uid | tunnel-stitched | inferred-branch",
  "edge_role": "payload | error | resource_ref | image_ref | state",
  "crosses_diagram": true,
  "structure_uid": 15173,
  "tunnel_uid": null
}
```

Do not label a component as a definitive ?쐄unctional unit??solely from WCC membership. Call it a candidate, attach the subVI/terminal evidence, and list the backbone edges whose removal created it.

Bottom line: first validate wire-UID fan-out semantics and export explicit tunnel/shift-register objects. Without those checks, the proposed graph can look internally consistent while losing fan-out, misclassifying nested-structure connections as boundaries, and turning iteration state into same-frame cycles.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
