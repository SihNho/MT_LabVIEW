---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# implicit-property-node-linked-object

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (49s)
- **why asked:** API fact search before building a reader for the 88 implicit Value property nodes (which scripting property names the bound control, and is it reachable cast-free)
- **verdict:** unverified

## Question

API FACT question (external search please; cite NI docs / labviewwiki / forums). LabVIEW 2026 VI Scripting. The main VI has 88 IMPLICIT property nodes (Value property, reference terminal unwired, the node header shows the bound front-panel control's name). We can enumerate them cast-free (Traverse for GObjects class 'Property' -> GObject refs; Diagram.Nodes[] -> Node refs; Node.Terminals[] rows: the 'reference' terminal Name/Is Source/Connected Wire; GObject.Label.Text). We CANNOT cast a reference to a more specific class (no retargetable class-specifier constant yet). Questions: 1) Which scripting property on a Property Node returns the object an IMPLICIT property node is linked to? (candidates I half-remember: 'PropertyNode:Linked Object', 'Linked Control', 'Node:Linked Object'? and its class in All Types[] - 'PropertyNode'? 'PropItem'?) 2) Is that property defined on a class we can reach WITHOUT a cast - i.e. on GObject or Node (both reachable typed via Diagram.Nodes[]), or only on the PropertyNode class? 3) Does GObject.Label.Text (or Node's 'Name'/'Description') of an implicit property node carry the bound control's label, i.e. is the header text a Label we can read cast-free? 4) Same three questions for Local Variables (class 'Local'): the property that names their bound control (e.g. 'LocalVariable:Object'?). One paragraph plus a short table (class : property : returns : needs cast?).

## Answer

The exact APIs are `Property class: Linked Control` and `Local class: Control`. Both return a front-panel `Control` refnum, but both are declared only on their concrete scripting classes?봭ot on `Node` or `GObject`?봲o your current `GObject[]`/`Node[]` references cannot select them without a downcast. For the cast-free fallback, the implicit Property Node?셲 displayed control name is its node label: LabVIEW Wiki explicitly says the referenced control?셲 name appears in the Property Node label, and `Node.Label` returns that label reference; however, NI?셲 scripting metadata warns that the label must have been displayed at least once before its text can be returned. Thus `Node.Label ??Text.Text` should recover the header cast-free for your existing implicit nodes, but treat it as presentation-derived rather than authoritative identity. `Node.Name` is not documented; `Node.Description` is independent metadata, not the binding. Locals similarly expose a visible/owned label, but the authoritative cast-free-looking name property, `Control Name`, is still declared on `Local`, so neither `Control Name` nor `Control` is reachable from a merely `Node`-typed reference. NI confirms locals are associated using the front-panel objects??owned labels, making displayed label text a reasonable fallback, subject to duplicate/change ambiguity. ([Property class](https://labviewwiki.org/wiki/Property_class), [Linked Control](https://labviewwiki.org/wiki/Property_class/Linked_Control_property), [Node class](https://labviewwiki.org/wiki/Node_class), [Control References](https://labviewwiki.org/wiki/Control_References), [Local class](https://labviewwiki.org/wiki/Local_class), [NI Local Variables](https://www.ni.com/docs/en-GB/bundle/labview/page/local-variables.html))

| Class | Property | Returns | Needs cast from `Node`/`GObject`? |
|---|---|---|---|
| `Property` | `Linked Control` (`LinkedControl`, ID `636F806`) | Bound `Control` refnum; null/error if not control-linked | **Yes** |
| `Node` | `Label` ??`Text.Text` | Displayed implicit-node header/control name, if label has been displayed | **No** from `Diagram.Nodes[]` |
| `Local` | `Control` (ID `6355403`) | Bound `Control` refnum | **Yes** |
| `Local` | `Control Name` (ID `6355400`) | Bound control?셲 name; read/write | **Yes** |
| `Local`/`Node` | inherited/node `Label` ??`Text.Text` | Displayed local-variable text; fallback only | **No** from `Diagram.Nodes[]` |

`PropertyNode` is therefore called **`Property`** in `All Types[]`; `PropItem` represents an individual row and is not the class containing `Linked Control`. The local-variable class is **`Local`**, not `LocalVariable`.

## Sources

(extract from answer)

## What was done with it

Took the cast-free fallback (Node.Label 6359001 -> Text.Text) and built OpNodeLabels_v0 (plan reviewed in
2026-09-14-opnodelabels-v0-plan.md). Confirmed on the machine: 88/88 implicit Value property nodes of the main VI
returned their bound control's label headless (test_opnodelabels.log). The class names ('Property', 'Local') and
IDs (Linked Control 636F806, Local.Control 6355403, Control Name 6355400) are recorded in docs/NAMES.md for the day
a typed reference exists. Verdict: correct and decisive.
