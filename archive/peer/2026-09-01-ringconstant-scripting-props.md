---
type: peer-review
status: historical
date: 2026-09-01
tags: [peer-review]
disposition: legacy
---

# ringconstant-scripting-props

- **agent:** codex
- **date:** 2026-09-01
- **outcome:** ANSWERED (46s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW VI Scripting question, factual, needs web sources (labviewwiki.org, forums.ni.com, NI docs). The scripting class RingConstant (a ring-typed numeric constant on a block diagram): (1) exact property names to READ its item list - is there a 'Strings And Values[]' or 'Strings[]' property on RingConstant or must one go through a different class? (2) exact property/method to SET which item is selected (its value) - name and datatype. (3) Are the New VI Object function's style ring item VALUES equal to their positional index, or sparse style codes? Cite URLs. Context: LabVIEW 2026, driving scripting VIs over ActiveX; we can build property nodes typed to any class (proven with LoopTunnel). Already ruled out: setting the value via SetControlValue (it is a diagram constant, not a FP control); guessing numeric style codes 0-39 on New VI Object (error 1054).

## Answer

1. **Read the item list directly from `RingConstant`.**

Use the VI Scripting property:

- **Property:** `Strings And Values[]`
- **Owning class:** `RingConstant`
- **Datatype:** array of clusters `{String, Value}`
- **Access:** read/write; remote access allowed
- **Property ID:** `0x0634E801`

This is a property of the diagram-side `RingConstant` class itself; no conversion to the front-panel `Ring` class is required. [`RingConstant.Strings And Values[]`](https://www.labviewwiki.org/wiki/RingConstant_class/Strings_And_Values_%28%29_property)

`RingConstant` also exposes `Values[]`, but its documented class table does **not** expose a `Strings[]` property. Therefore, use `Strings And Values[]` when labels are required. [`RingConstant` class property table](https://labviewwiki.org/wiki/RingConstant_class)

Do not confuse this with the front-panel `Ring.Strings[]` / `Ring.Strings And Values[]` properties. Those belong to the separate `Ring` control class. [`Ring.Strings And Values[]`](https://labviewwiki.org/wiki/Ring_class/Strings_And_Values_%28%29_property)

2. **Set the selected item by writing `Constant.Value`.**

`RingConstant` inherits from:

`Constant ??NumericConstant ??NamedNumericConstant ??RingConstant`

The relevant inherited property is:

- **Property:** `Value`
- **Owning class:** `Constant`
- **Datatype:** **LabVIEW Variant**
- **Access:** read/write
- **Property ID:** `0x0634AC00`

Write a variant containing the desired item?셲 **numeric value**, represented using the ring constant?셲 actual numeric representation?봭ot its positional array index. [`Constant.Value`](https://labviewwiki.org/wiki/Constant_class)

For example, if `Strings And Values[]` returns:

```text
"Add"      ??7
"Subtract" ??42
```

select `"Subtract"` by writing numeric value `42` into `Value` as an LV Variant. NI confirms that ring items may have arbitrary numeric values rather than sequential indices. [NI: Changing the Values of an Enum Constant](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000001DeCbSAK)

3. **The New VI Object style entries are style codes, not positional indices.**

Treat each item?셲 value from `Strings And Values[]` as the actual style ID to pass to `New VI Object`. Do **not** use its zero-based position in the displayed list.

Evidence:

- Rings support explicitly assigned, non-sequential numeric values; only rings configured for sequential values happen to use positions `0, 1, 2??. [NI LabVIEW User Manual: Ring Controls](https://download.ni.com/support/manuals/320999e.pdf)
- NI forum guidance identifies an object?셲 scripting `Style ID` as an `I32` and says its meaning can be decoded using the ring attached to `New VI Object.style`. [NI Community: Which control/palette created an FP object?](https://forums.ni.com/t5/LabVIEW/Which-control-of-which-palette-was-used-to-create-a-FP-object/td-p/4366188/page/2)
- Another NI forum thread explicitly discusses the `New VI Object` style input as a ring containing style IDs, including missing/non-obvious styles?봭ot a positional enumeration of every palette object. [NI Community: Input for style in New VI Object](https://forums.ni.com/t5/LabVIEW/VI-Scripting-Input-for-style-in-quot-New-VI-Object-quot-function/td-p/3267356)

So the safe extraction is:

```text
RingConstant reference
    ??Strings And Values[]
    ??find label
    ??take that cluster?셲 Value
    ??wire/pass that numeric style code to New VI Object.style
```

This also explains why probing `0??9` produced error 1054: that range tests list positions, while the accepted identifiers are the ring?셲 stored style values and may be sparse. The exact LabVIEW 2026 mapping should therefore be read from the installed primitive?셲 style-ring constant rather than copied from an older version.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
