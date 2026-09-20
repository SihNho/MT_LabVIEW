---
type: peer-review
status: historical
date: 2026-09-06
tags: [peer-review, plan]
disposition: legacy
---

# connect-ladder-plan-attack

- **agent:** codex
- **date:** 2026-09-06
- **outcome:** ANSWERED (86s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW 2026 VI Scripting; cite sources (labviewwiki.org class pages, NI docs/forums, github erdosmiller/lv-scripting). We build "op" VIs driven from Python COM: each op takes plain data (vi path, class name, index, position) and does the refnum work inside. Existing verified facts: erdosmiller Create Property Node.vi / Create Invoke Node.vi make TYPED nodes from a class string + Unique ID with reference unwired; a Diagram-typed wire (To More Specific Class output) into a Diagram-class Property Node keeps it typed; a GObject-typed wire into a Node-class PN re-types it to GObj (downcast refused); Wire Inputs.vi wires by terminal NAME and can branch when types match; delete_object (Generic.Delete) works on nodes AND on broken Wire objects; GObject.Move op verified.
PLAN TO ATTACK (find what will fail, and the cheapest test): typed references by a script-only ladder with no class constant: Diagram -> AbstractDiagram.Nodes[] (6375809) -> Index Array -> Node -> Node.Terminals[] (6359000) -> Index Array -> Terminal, then (a) Terminal.Create Control (6349C01) on that terminal to add a wired front-panel control, and (b) Terminal.Connect Wire (6349C03) with the second ladder's terminal as the wire source to wire two arbitrary terminals by indices.
Questions: (1) Is the order of Diagram.Nodes[] stable and equal to the order Traverse for GObjects.vi returns for class Node (or do they differ; which is the documented order)? (2) Node.Terminals[] order: documented? does it include input and output terminals, and for Index Array / subVIs is it connector-pane order? (3) Terminal.Connect Wire: exact parameter names on the Invoke node (the wire-source terminal parameter) and semantics: does it create a new wire between two unwired terminals, and can it branch from an already-wired source terminal? (4) erdosmiller Create Index Array.vi has inputs Diagram in, location (0, 0), array (a refnum) and error in: is `array` required, and what refnum class is it (Terminal? GObject? Wire?) - if unwired does it still create an Index Array node? (5) Terminal.Create Control: parameter names, and does it work on an unwired INPUT terminal of an Index Array (index) producing a numeric control wired to it? Give a verdict per question and name any step you predict will fail.


## Answer

Verdict: the ladder is technically plausible, but indexing `Diagram.Nodes[]` is not a safe object-identification scheme. The most likely failure is selecting the wrong node, followed by assuming generic `Node.Terminals[]` indices for growable nodes such as Index Array.

1. `Diagram.Nodes[]` order

**Verdict: undocumented; do not assume it matches `Traverse for GObjects.vi`.**

`AbstractDiagram.Nodes[]` only promises ?쐒eferences to all the nodes in the diagram.??It specifies no ordering contract. [LabVIEW Wiki: `AbstractDiagram.Nodes[]`](https://www.labviewwiki.org/wiki/AbstractDiagram_class/Nodes()_property)

`Traverse for GObjects.vi` recursively searches container objects, whereas `Nodes[]` describes nodes in one diagram. Thus they can differ immediately when structures or nested diagrams exist. [NI forum: Traverse recursively finds nested objects](https://forums.ni.com/t5/LabVIEW/get-references-to-all-controls-on-front-panel/m-p/694003/highlight/true)

NI forum evidence also shows that traversal order is distinct from other object-array orderings; for example, `Panel.AllObjs[]` follows Z-order while Traverse does not follow tab order. [NI forum: object-array and Traverse ordering](https://forums.ni.com/t5/LabVIEW/String-reference/m-p/4430231)

**Cheap test:** create three distinguishable top-level nodes, record their labels/class names/positions through both APIs, then add one node and move another. Repeat after save/reload. Even if they currently match, treat that only as an observed implementation detail.

**Prediction:** relying on node index will eventually address the wrong node after a creation, deletion, replacement, or reload.

2. `Node.Terminals[]` ordering and contents

**Verdict: it contains the node?셲 terminals, including sources and sinks, but its usable ordering contract is the terminal index reported by LabVIEW?봭ot geometric order or a universal inputs-then-outputs rule.**

The documented instruction is to use the terminal index displayed in Context Help to index `Node.Terminals[]`. [LabVIEW Wiki: `Node.Terminals[]`](https://www.labviewwiki.org/wiki/Node_class/Terminals%28%29_property)

NI forum guidance confirms that Context Help exposes those indices for Functions and SubVIs. It also recommends inspecting `Is Source?`, terminal name, and datatype when an index alone is insufficient. [NI forum: Scripting?봗erminal Information](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)

For a SubVI, the indices correspond to its displayed connector terminals, but I found no authoritative promise that the raw array follows a visually intuitive connector-pane traversal. Connector-pane terminal numbering itself is pattern-specific. [NI forum: connector-pane terminal order](https://forums.ni.com/t5/LabVIEW/Get-Control-Reference-From-Connector-Pane/td-p/3070203)

For Index Array specifically, avoid generic indices where possible: its scripting class exposes `Array Input Terminal`, `Index Terminals[][]`, and `Output Terminals`. [NI forum: Index Array-specific terminal properties](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)

**Prediction:** fixed `Terminals[]` indices for Index Array will be fragile as it grows or changes dimension. The specialized properties are safer.

3. `Terminal.Connect Wire`

**Verdict: the exact parameters are:**

- `Wire Source` ??required
- `Auto Wire? (T)` ??optional
- `Wiring Specs` ??optional 2D string array
- `Auto Route? (F)` ??optional

The invoked-on terminal is the destination. `Wire Source` may be another Terminal or a Node, and the method ?쐁onnects a wire to the terminal.??[LabVIEW Wiki: `Terminal.Connect Wire`](https://www.labviewwiki.org/wiki/Terminal_class/Connect_Wire_method)

For two explicit terminal references, use:

- invoke on the intended sink terminal;
- wire the source Terminal refnum to `Wire Source`;
- set `Auto Wire?` false unless you deliberately want node/name-based autowiring;
- optionally set `Auto Route?` true.

The documentation supports creating a connection between compatible terminals, but it does **not explicitly document branch behavior when the source already owns a wire**. A branch is plausible, but should be treated as unverified.

**Cheap test:** source terminal ??sink A; call `Connect Wire` on unwired sink B with the same source terminal. Verify both sinks??`Connected Wire`/wire references and VI broken state. Also test invoking on a source terminal accidentally; directionality may reject it.

4. Erdos Miller `Create Index Array.vi` input `array`

**Verdict: unresolved from publicly rendered GitHub documentation. Do not assume `array` is required for node creation.**

The repository describes itself as a convenience library for VI Scripting, but GitHub does not expose the connector-pane types or internal diagram of this binary VI through its rendered source listing. [erdosmiller/lv-scripting](https://github.com/erdosmiller/lv-scripting)

My best inference is that `array` is the upstream object/reference which the wrapper optionally connects to the Index Array?셲 array-input terminal?봭ot the object needed to instantiate the Index Array itself. The likely broad type is a scripting object such as `GObject`, rather than Terminal or Wire, because these helpers conventionally accept objects and perform terminal selection/wiring internally. This is an inference, not documented evidence.

I therefore expect an invalid/default `array` refnum may either:

- create the Index Array and leave its array input unwired; or
- fail inside the wrapper?셲 wiring helper after creation.

Whether `array` is connector-pane Required is a separate question from whether the underlying primitive can be created without it.

**Cheapest decisive evidence:** ask the manager for the reporter output for `Create Index Array.vi`: connector controls with exact refnum class, requiredness, and the calls made after `New VI Object`. That settles this without opening the VI.

5. `Terminal.Create Control`

**Verdict: likely yes for an unwired Index Array index input.**

The method has only:

- return value `Create Control` ??`Control Refnum`;
- optional input `Value` ??Variant.

It ?쐁reates a control for the terminal??and returns its reference. [LabVIEW Wiki: `Terminal.Create Control`](https://www.labviewwiki.org/wiki/Terminal_class/Create_Control_method)

An Index Array index terminal is a sink with a defined integer datatype, so invoking `Create Control` on that terminal should produce the corresponding numeric front-panel control and connect its block-diagram terminal to the Index Array index input. That final Index Array-specific behavior is a strong inference from the method contract, not explicitly demonstrated on the class page.

**Cheap test:** create an untyped Index Array, obtain `Index Terminals[][]` if available, invoke `Create Control`, then verify:

- returned reference is valid;
- control datatype is integer;
- target terminal now has a connected wire;
- VI remains executable.

Overall prediction: `Create Control` should work. `Connect Wire` probably works for an unoccupied compatible sink, but branching needs a direct test. The design?셲 weak point is positional lookup through `Nodes[]` and generic `Terminals[]`, not typed-reference propagation.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
