---
type: peer-review
status: historical
date: 2026-09-05
tags: [peer-review, plan]
---

# keystone-build-plan-attack

- **agent:** codex
- **date:** 2026-09-05
- **outcome:** ANSWERED (114s)
- **why asked:** plan review (work cycle step 1) of Build plan v1 in docs/keystone-op-spec.md before construction.
- **verdict:** accepted: (1) the created node's class follows the referenced OBJECT (Term ref -> Term node; only a Control refnum gives Ctl) so 'node class as a string via the creator' is impossible -> plan v2 obtains class by referencing an existing object of that class (Traverse) or by the scripting properties Property Node Class Name / Invoke Node Class Name (R/W) + Set Properties[] / Set Method; (2) copy_into count-only check insufficient -> wire-to-connector + datatype check; (3) Class Name not on pane, outputs unconfirmed -> reporter first; (4) delete-before-rewire is destructive -> record topology, wire replacement, delete last; (5) generic New VI Object route is the better architecture.

## Question

REFUTE this build plan; find what will break, do not confirm. Read docs/keystone-op-spec.md in the project dir (all sections, especially Build plan v1) and docs/NAMES.md. Context: LabVIEW 2026, VI Scripting via the erdosmiller lv-scripting library (Create Property Node.vi, Create Invoke Node.vi, Get Outputs.vi, Wire Inputs.vi), op VIs driven from Python over ActiveX by setting plain front-panel controls and Run; refnums never leave LabVIEW. The plan copies an existing op (Traverse -> Get Outputs -> Wire Inputs) and swaps Wire Inputs for Create Property Node.vi, feeding Diagram in from a Traverse of class Diagram and reference from a terminal refnum picked out of Get Outputs. Attack: (1) does Create Property Node.vi take the node class from the wire TYPE of its reference input or from the referenced object at runtime - i.e. will a generic Terminal refnum (from Get Outputs) give a Control-class Property Node, or an Application-class one, or error 1077? What reference does it actually need (the OBJECT whose properties you want, or any refnum wire on the diagram)? (2) can an array-of-cluster front-panel control be copied between VIs with the VI Server Move/copy method and keep its type, or must it be created (New VI Object with which style)? (3) wiring by terminal NAME into these library VIs: which terminals of Create Property Node.vi are on the connector pane (NI/erdosmiller source), and is Class Name really not on the pane? (4) after deleting a subVI node, do the dangling wires break the VI in a way Remove Bad Wires cannot fix (e.g. tunnels, error clusters)? (5) is there a simpler route: a single generic op that takes (class name, property names, write flags, location) and creates the node WITHOUT a reference wire by using New VI Object style Property Node + PropertyNode.Class Name / Add Property, or an Invoke Node via New VI Object + InvokeNode.Method? Cite the VI Server properties/methods (names) that exist for Property Node and Invoke Node classes and say which are writable. Give concrete failure scenarios and the cheapest discriminating test for each, with sources (NI docs/forums URLs).

## Answer

Build plan v1 should not proceed as written. Its reference-typing premise is wrong, its connector-pane assumptions contradict `NAMES.md`, and its deletion strategy can destroy wiring that `Remove Bad Wires` cannot reconstruct.

## 1. The `reference` must be the object being operated on

`Create Property Node.vi` does not accept ?쏿ny diagram refnum wire??merely as class context. The reference wire represents the actual run-time object whose properties the generated node will access. A wired Property Node is an explicit-reference node: the object reference determines both the VI Server class and the eventual target object. [NI describes creating a Property Node from the reference output of the object concerned](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YQdlCAG).

Therefore:

- A `ControlTerminal` reference from `Get Outputs` should create a **Terminal-class** node, not a Control-class node.
- It will not magically dereference `Terminal ??Control`.
- A generic `Terminal`-typed connector does not become Control merely because the terminal happens to belong to a front-panel control.
- An Application-class result would only be plausible if the creator?셲 connector itself were statically Application-typed and the implementation ignored/rejected the supplied subtype. Your machine-confirmed `Term ??Create Indicator ??Ctl` chain already disproves that for the working path.

The confirmed `OpFP_v0` is the counterexample that kills Build plan v1: the terminal reference types the Invoke Node as `Term`; only the `Create Indicator` return reference types the following node as `Ctl`.

Error 1077 is not the important failure here. The more dangerous outcome is successful creation of the **wrong class** followed by failure when selecting `Position`, because `Position` was intended for `Control`, not the terminal object.

Cheapest discriminating test:

1. Feed the same known `ControlTerminal` reference to `Create Property Node.vi`.
2. Request a Terminal-specific property first, then `Position`.
3. Report the created node?셲 `Property Node Class Name` and `All Supported Properties`.
4. Do not infer class from error status.

`Property Node Class Name` is explicitly read/write, and `All Supported Properties` reports the properties available for the current class. The required class-name syntax is the full server and node class, for example `VI Server:Generic`. [Property Node Class Name](https://labviewwiki.org/wiki/Property_class/Property_Node_Class_Name_property), [All Supported Properties](https://labviewwiki.org/wiki/Property_class/All_Supported_Properties_property).

If the desired object is a Control, obtain an actual **Control refnum**?봣or example from `Terminal.Create Indicator`, `Terminal.Control`, or another documented conversion path?봭ot the terminal refnum merely because its wire is convenient.

## 2. Copying the array-of-cluster control is plausible, but the plan?셲 verification is insufficient

The VI Server `GObject.Move` method explicitly copies an object when its new owner belongs to another VI; cross-VI ownership implies duplication. That argues that copying the complete `Properties` array control should preserve its contained cluster and element types. [GObject.Move documentation](https://labviewwiki.org/wiki/GObject_class/Move_method).

But there are two traps:

- The Move method?셲 returned/reference output has historically referred to the **source**, not reliably to the duplicate. Locating or wiring the new control by the returned reference can therefore operate on the donor. [NI forum report](https://forums.ni.com/t5/LabVIEW/VI-Scripting-get-reference-of-the-duplicate-element/m-p/1883433/highlight/true).
- A count increase proves only that an object appeared. It does not prove that the copied terminal has the exact array-of-cluster datatype required by the subVI connector.

The cheapest test is to copy the donor control into a blank scratch VI, locate the new object independently by before/after UID enumeration, then wire its terminal directly to `Create Property Node.vi.Properties`. A nonbroken wire plus exact datatype reporter output is the acceptance condition.

Creating it from scratch is much harder than the spec suggests. LabVIEW arrays are containers: an array shell must receive an element, and here that element must itself be a cluster containing the correctly typed and ordered `ID String` and `Is Write?` elements. [NI array/cluster construction documentation](https://www.ni.com/en/support/documentation/supplemental/08/labview-arrays-and-clusters-explained.html). There is no single generic ?쏿rray of this cluster??style. You would need an Array control, a Cluster element, then String and Boolean elements owned by that cluster, with correct order and control direction. Copying the known donor is cheaper and safer.

## 3. `Class Name` cannot be wired into the library VI

`NAMES.md` is decisive for the installed version:

> `Create Property Node.vi`: `Diagram in`, `Properties`, `reference`, `error in`; `Class Name` NOT on pane.

An exported front-panel string proves that a front-panel object exists; it does not prove connector-pane exposure. Thus the keystone front-panel `node class` input has no path into `Create Property Node.vi`.

The planned terminal list also overclaims outputs. `keystone-op-spec.md` says `Outputs`, `Inputs`, and `reference out`, but `NAMES.md` confirms only the inputs above. Those names require reporter confirmation before any wiring plan can rely on them. The upstream repository identifies LV-Scripting as a code-generation library and points users to its examples, but its checked-in VIs are binary LabVIEW sources, so GitHub cannot establish the installed connector pane textually. [erdosmiller/lv-scripting](https://github.com/erdosmiller/lv-scripting).

Cheapest test: have the manager run the existing plain-text connector-pane reporter on the installed `Create Property Node.vi` and `Create Invoke Node.vi`, including pane index, terminal direction, label and datatype. Do not use `ExportVIStrings` for this question.

Until that report exists, the only defensible Create Property Node inputs are those recorded in `NAMES.md`; `Class Name` is not one of them.

## 4. Deleting `Wire Inputs` before preserving topology is destructive

`Block Diagram:Remove Bad Wires` does exactly one thing: it removes broken wires. It does not reconnect endpoints, recreate branches, regenerate tunnels, or splice an error/reference chain. [VI scripting method documentation](https://labviewwiki.org/wiki/VI_class/Block_Diagram.Remove_Bad_Wires_method). NI?셲 keyboard documentation likewise describes Ctrl-B as deletion of broken wires, not repair. [NI keyboard shortcuts](https://www.ni.com/docs/en-AS/bundle/labview/page/keyboard-shortcuts.html).

Concrete failures:

- A source ??`Wire Inputs` ??sink chain becomes two loose fragments. Removing bad wires deletes both; it does not produce source ??sink.
- A branched error wire can lose the entire affected branch.
- If a wire crosses a structure boundary, deleting the wire can leave an unused tunnel or remove the only connection through that tunnel. `Remove Bad Wires` cannot infer the intended tunnel connection.
- If an existing wire supplies multiple sinks, deleting it wholesale loses all branches unless their source/sink references were recorded and rewired. NI forum guidance for deliberately disconnecting one sink is to record the source and remaining sinks, delete the wire, then reconstruct the desired branches. [NI forum](https://forums.ni.com/t5/LabVIEW/Disconnect-wire-through-VI-scripting/m-p/3047457).

Cheapest test: on a disposable skeleton, record every terminal and wire UID attached to `Wire Inputs`, including all branch sinks and structure tunnels; delete only the node; report the remaining wire endpoints before calling Remove Bad Wires. If any intended source/sink pairing is no longer represented, the plan needs explicit rewiring.

The safe order is: record topology ??install and wire replacement ??verify all intended endpoints ??delete obsolete node/wire branches ??only then remove residual broken wires.

## 5. The simpler generic op exists?봟ut not through the erdosmiller connector pane

A reference-free generic creator is technically the better architecture:

1. Create a bare Property Node or Invoke Node using `New VI Object`.
2. Set its explicit class by scripting.
3. Configure its property rows or method.
4. Optionally wire a real object reference afterward.

The styles are reported as `Property Node` and `Invoke Node`; the commonly published style list gives Invoke Node style `3900`, but the manager should read the style-ring value on LabVIEW 2026 instead of freezing historical numeric IDs. [LAVA New VI Object style list](https://lavag.org/topic/14519-new-vi-object-style-list/).

Relevant supported scripting surface:

| Node | Member | Access |
|---|---|---|
| Property | `Property Node Class Name` | Read/write |
| Property | `Property Count` | Read/write |
| Property | `Properties[]` | Read-only current configuration |
| Property | `Property Items[]` | Read-only refs |
| Property | `All Supported Properties` | Read-only |
| Property | `Set Properties[]` | Method; sets selected properties |
| Property | `Add Property Item After` | Method |
| PropertyItem | `Set Property` | Method |
| Invoke | `Invoke Node Class Name` | Read/write |
| Invoke | `Method` | Read-only in the current API |
| Invoke | `All Supported Methods` | Read-only |
| Invoke | `Input Terminals[]` / `Output Terminals[]` | Read-only |
| Invoke | `Set Method` | Method |

Sources: [Property class members](https://labviewwiki.org/wiki/Property_class), [Set Properties[]](https://labviewwiki.org/wiki/Property_class/Set_Properties%28%29_method), [PropertyItem.Set Property](https://labviewwiki.org/wiki/PropertyItem_class/Set_Property_method), [Invoke class members](https://labviewwiki.org/wiki/Invoke_class), [Invoke.Set Method](https://labviewwiki.org/wiki/Invoke_class/Set_Method_method).

Two corrections to the proposed shorthand:

- It is not simply `PropertyNode.Class Name`; the documented writable name is **`Property Node Class Name`**.
- ?쏛dd Property??is not the principal bulk API. The supported methods are **`Set Properties[]`** or **`Add Property Item After`**, followed as necessary by `PropertyItem.Set Property`.
- `InvokeNode.Method` is read-only in the current API; changing it requires **`Set Method`**. [Method property](https://labviewwiki.org/wiki/Invoke_class/Method_property).

Property write direction still needs a separate verified mechanism. `Set Properties[]` selects property IDs but does not, from its documented parameters, accept per-row write flags. The erdosmiller `Properties` cluster evidently handles this internally, but a home-grown generic op must identify the writable PropertyItem direction member/method on LabVIEW 2026. Do not assume the cluster?셲 `Is Write?` field maps to a public property with the same name.

## Verdict

Build plan v1 fails its stated goal of a class-name-driven generic keystone:

- It cannot pass `node class` to `Create Property Node.vi`.
- Its reference source is a terminal object, so it creates a Terminal-class node, not a Control-class node.
- Its success checks do not verify the created node?셲 actual class or copied control datatype.
- Its delete-then-clean sequence can irreversibly erase topology.
- `Create Invoke Node.vi` remains connector-pane-unverified.

The cheapest next move is not construction. Run three reporter-only discriminators on scratch VIs:

1. Installed connector-pane reports for both creator VIs.
2. Create PN from a known `ControlTerminal`, then report `Property Node Class Name`.
3. Create bare PN/Invoke nodes with `New VI Object`, set `VI Server:<class>`, then exercise `Set Properties[]`/`Set Method`.

If test 3 succeeds, replace Build plan v1 with a small native generic scripting op and use the erdosmiller VIs only where their fixed connector panes actually match the task.

## Sources

(extract from answer)

## What was done with it

Build plan v1 withdrawn; v2 written in the spec (reference = existing object of the wanted class via Traverse; delete last; reporter-confirmed pane names).
