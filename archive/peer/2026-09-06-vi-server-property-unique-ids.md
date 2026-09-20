---
type: peer-review
status: historical
date: 2026-09-06
tags: [peer-review]
---

# vi-server-property-unique-ids

- **agent:** codex
- **date:** 2026-09-06
- **outcome:** ANSWERED (72s)
- **why asked:** the erdosmiller creators call Set Method / Set Properties[] with AllowAlternateNames=FALSE, so the keystone ops need Unique ID strings; needed a table before building OpBuildPN_v0.
- **verdict:** stored as docs/vi-server-ids.json; 6349C03 (Connect Wire) machine-verified via OpBuildInvoke_v0 t8; the rest unverified until used.

## Question

LabVIEW VI Scripting fact lookup (LabVIEW 2026). The erdosmiller Create Property Node.vi calls Property.Set Properties[] with IDStrings[] and AllowAlternateNames=FALSE, so property Unique ID strings are required (like method IDs 6349C03 = Terminal.Connect Wire). From labviewwiki.org (each property page lists its Unique ID) or NI docs, give the Unique ID strings for these properties, one per line as "<Class>.<Property> = <ID>": GObject.Position, GObject.Bounds, GObject.Label (or Label.Text), Control.Indicator, Control.Value, Invoke.Method Class Name (MethClassName), Invoke.All Supported Methods, Property.Property Node Class Name (PropClassName), Property.All Supported Properties, ClassSpecifierConstant.All Types[], ClassSpecifierConstant.Class Name, Node.Terms[], Terminal.Name, Terminal.Wire, Diagram.Nodes[] (or Diagram.Objects). Also give the Unique IDs of these METHODS: Terminal.Create Control, Terminal.Create Constant, Diagram.Connect Wire (if it exists on Diagram) , Generic.Delete, GObject.Move, Invoke.Set Method, Property.Set Properties[], Property.Add Property Item After. Cite the page URL for each. If a page does not list an ID, say NOT FOUND for that item; do not guess.

## Answer

The IDs explicitly listed by LabVIEW Wiki are:

```text
GObject.Position = 632A800
```
[Source](https://labviewwiki.org/wiki/GObject_class/Position_property)

```text
GObject.Bounds = 632A803
```
[Source](https://labviewwiki.org/wiki/GObject_class/Bounds_property)

```text
GObject.Label = NOT FOUND
```
The GObject class does not define a Label property. For controls, use the following two-step chain: [GObject class](https://labviewwiki.org/wiki/GObject_class)

```text
Control.Label = 6332005
```
[Source](https://labviewwiki.org/wiki/Control_class/Label_property)

```text
Text.Text = 632D800
```
[Source](https://labviewwiki.org/wiki/Text_class/Text_property)

```text
Control.Indicator = 6332007
```
[Source](https://labviewwiki.org/wiki/Control_class/Indicator_property)

```text
Control.Value = 633200D
```
[Source](https://labviewwiki.org/wiki/Control_class/Value_property)

```text
Invoke.Invoke Node Class Name = 6370402
```
Short name: `MethClassName`. [Source](https://labviewwiki.org/wiki/Invoke_class/Invoke_Node_Class_Name_property)

```text
Invoke.All Supported Methods = 637040D
```
[Source](https://labviewwiki.org/wiki/Invoke_class/All_Supported_Methods_property)

```text
Property.Property Node Class Name = 636F804
```
Short name: `PropClassName`. [Source](https://labviewwiki.org/wiki/Property_class/Property_Node_Class_Name_property)

```text
Property.All Supported Properties = 636F80E
```
This is the current cluster-array property, not deprecated `636F801`. [Source](https://labviewwiki.org/wiki/Property_class/All_Supported_Properties_property)

```text
ClassSpecifierConstant.All Types[] = 566EFC05
```
[Source](https://labviewwiki.org/wiki/ClassSpecifierConstant_class/All_Types%28%29_property)

```text
ClassSpecifierConstant.Class Name = 566EFC02
```
[Source](https://labviewwiki.org/wiki/ClassSpecifierConstant_class)

```text
Node.Terminals[] = 6359000
```
Data/short name: `Terms[]`. [Source](https://www.labviewwiki.org/wiki/Node_class/Terminals%28%29_property)

```text
Terminal.Name = 634A004
```
[Source](https://labviewwiki.org/wiki/Terminal_class)

```text
Terminal.Connected Wire = 634A000
```
This is the property corresponding to the requested `Terminal.Wire`. [Source](https://labviewwiki.org/wiki/Terminal_class)

```text
AbstractDiagram.Nodes[] = 6375809
```
`Diagram` inherits this property from `AbstractDiagram`. [Source](https://labviewwiki.org/wiki/AbstractDiagram_class)

Alternative enumeration:

```text
AbstractDiagram.All Objects[] = 6375804
```
[Source](https://labviewwiki.org/wiki/AbstractDiagram_class/All_Objects%28%29_property)

Methods:

```text
Terminal.Create Control = 6349C01
```
[Source](https://labviewwiki.org/wiki/Terminal_class/Create_Control_method)

```text
Terminal.Create Constant = 6349C00
```
[Source](https://labviewwiki.org/wiki/Terminal_class/Create_Constant_method)

```text
Diagram.Connect Wire = NOT FOUND
```
The documented Diagram method table does not contain `Connect Wire`; wiring is exposed through `Terminal.Connect Wire = 6349C03` or `Node.Connect Wires = 6358C00`. [Diagram source](https://labviewwiki.org/wiki/Diagram_class), [Terminal source](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method), [Node source](https://labviewwiki.org/wiki/Node_class)

```text
Generic.Delete = 6327400
```
[Source](https://labviewwiki.org/wiki/Generic_class/Delete_method)

```text
GObject.Move = 632A400
```
[Source](https://labviewwiki.org/wiki/GObject_class/Move_method)

```text
Invoke.Set Method = 6370002
```
[Source](https://labviewwiki.org/wiki/Invoke_class/Set_Method_method)

```text
Property.Set Properties[] = 636F405
```
[Source](https://labviewwiki.org/wiki/Property_class/Set_Properties%28%29_method)

```text
Property.Add Property Item After = 636F401
```
[Source](https://labviewwiki.org/wiki/Property_class)

## Sources

(extract from answer)

## What was done with it

docs/vi-server-ids.json + NAMES.md pointer.
