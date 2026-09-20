---
type: peer-review
status: historical
date: 2026-09-12
tags: [peer-review]
disposition: legacy
---

# read-constant-value-scripting

- **agent:** codex
- **date:** 2026-09-12
- **outcome:** ANSWERED (57s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PURE API FACT QUESTION about LabVIEW VI Scripting (LabVIEW 2026, VI Server over ActiveX/COM driven from Python, plus the erdosmiller lv-scripting library). Short, concrete, with source URLs.

GOAL: read the VALUE of a numeric constant that sits on a block diagram, without opening the VI in the editor and without a human looking at it. Concretely: a `Wait (ms)` primitive has an I32 constant wired to its `milliseconds to wait` terminal, inside a case frame of a subVI. I want that number.

WHAT I CAN ALREADY DO: traverse a diagram and get every object's VI Server class, UID, position and owning structure class; get each node's terminal names and which wire UID each terminal touches; create Property Nodes and Invoke Nodes by script (class name + property/method ID as strings) inside an "op VI" that takes plain data and does the refnum work in LabVIEW.

QUESTIONS:
1. Which VI Server class does a numeric diagram constant have in LabVIEW scripting (e.g. `Constant`, `NumericConstant`, something else)? Give the exact class string usable with `To More Specific Class` / `Traverse for GObjects`.
2. Is there a readable PROPERTY or a METHOD that returns that constant's VALUE? Name it exactly, and give its Unique/Property ID if you can find one (I register IDs like "VI.Connector Pane:Reference" = 23E in a local table). If the value is only reachable as a variant or a flattened string, say so and name the property.
3. If no direct property exists, what is the cheapest SCRIPTED alternative that does not involve a human reading the diagram? Candidates I can evaluate: reading the constant's terminal and following the wire; `GObject.Get Image` (rendering the constant and OCRing it) - which I consider a last resort; copying the constant into a scratch VI and wiring it to an indicator, then running that VI to read the value back.
4. Same question for a STRING constant and for an ENUM/RING constant, if the answer differs.

Please cite NI documentation, the LabVIEW help for VI Scripting properties, or forum posts with URLs. If the answer is "not exposed", say that plainly and cite what you checked - I need to be able to record a negative result with evidence, not a guess.

## Answer

1. **Class**

An ordinary I32 diagram constant is concretely `DigitalNumericConstant` (class ID `16390`). Its parent is `NumericConstant` (`16389`), whose parent is `Constant` (`16386`). Therefore:

- Use `DigitalNumericConstant` for the exact concrete class.
- Traverse/downcast to `NumericConstant` if you want all ordinary numeric constants.
- Downcast merely to `Constant` if you only need the inherited value property.

The unlocalized class strings have no spaces. [VI Server class hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy), [NumericConstant class](https://labviewwiki.org/wiki/NumericConstant_class)

2. **Direct readable value**

Yes. Use the inherited property:

```text
Class: Constant
Property: Value
Property ID: 634AC00
Output type: LV Variant
Access: Read/Write, VI Scripting
```

`Constant.Value` directly returns the stored constant value as an LV Variant. For your I32 constant, read `Value`, then use `Variant To Data` with an I32 type input inside the op VI. No execution, wire-following, rendering, or OCR is required. [Constant class/property table](https://labviewwiki.org/wiki/Constant_class)

Because `All Objects[]` produces statically generic references, downcast the reference with `To More Specific Class` before connecting it to the `Constant.Value` Property Node. [Measured explanation of generic references and required downcasting](https://github.com/Zuehlke/labview-mcp/blob/main/docs/vi-server-reference.md#reaching-a-classs-private-data-control-and-the-write-primitives-on-it)

3. **Cheapest approach**

The cheapest scripted path is:

```text
diagram object ref
??To More Specific Class {LV.Constant}
??Constant.Value
??LV Variant
??Variant To Data (I32)
??return I32 through op-VI connector pane
```

The target VI must be loaded sufficiently for scripting access, but its diagram window does not need to be shown to a human. VI Scripting properties are specifically enabled through LabVIEW?셲 VI Server settings. [NI: Enabling VI Scripting](https://www.ni.com/docs/en-IE/csh?context=lvcore_lvhowto_enabling_vi_scripting)

Following the wire is unnecessary: the wire carries type/connectivity, while the value belongs to the constant itself. Copying to a scratch VI and executing it is only a fallback if `Constant.Value` unexpectedly fails for a special constant subclass. `GObject.Get Image` plus OCR should not be used here.

The erdosmiller library does not change this API; it is a convenience wrapper around VI Scripting. [erdosmiller/lv-scripting](https://github.com/erdosmiller/lv-scripting)

4. **String, enum and ring**

All inherit the same `Constant.Value` property:

| Constant | Exact class | Returned value |
|---|---|---|
| String | `StringConstant` (`16392`) | LV Variant containing the actual string |
| Enum | `EnumConstant` (`16425`) | LV Variant containing the typed enum |
| Ring | `RingConstant` (`16424`) | LV Variant containing the selected numeric value |

Sources: [StringConstant](https://labviewwiki.org/wiki/StringConstant_class), [class hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy), [RingConstant](https://labviewwiki.org/wiki/RingConstant_class).

For enums/rings, `Value` gives the selected typed/numeric value, not necessarily its displayed label. If you also need the label mapping:

- Enum: value is the zero-based item index; retrieve the item strings from the named-numeric string-list property.
- Ring: use `Strings And Values []`, property ID `634E801`, because ring numeric values need not be sequential. [Named numeric string semantics](https://labviewwiki.org/wiki/NamedNumeric_class/Strings_%28%29_property), [RingConstant properties](https://labviewwiki.org/wiki/RingConstant_class)

So the direct answer is: **downcast to `Constant`, read `Value` (`634AC00`), and decode the returned LV Variant inside LabVIEW.**

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
