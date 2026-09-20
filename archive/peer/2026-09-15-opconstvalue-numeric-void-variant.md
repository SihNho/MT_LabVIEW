---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opconstvalue-numeric-void-variant

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (97s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS (LabVIEW 2026 VI Scripting, Constant class). Measured with tools/recipes/build_opconstvalue_v1c.py (log tools/bench/build_opconstvalue_v1c.log, run 2, 05:11) - the op reads Property Node Constant.Value (634AC00, read) on a To-More-Specific-Class(Constant) reference and exports the variant lossless as bytes (Flatten To String -> Unflatten(U8[], size?=F) -> hex + U8 SAFEARRAY, both agree; per-read identity UID/class/# of Refs verified against the reporter; main VI untouched). RESULTS on the main VI's top diagram: StringConstant[7] (label 'format string') -> 53 bytes = version 26008000, nTDs 1, TD 0016 4030 ffffffff 0d 'format string', nTypesUsed 1, idx 0, data 0000000b 'img%05d.tif', attrs 0 -> decodes exactly. EVERY DigitalNumericConstant[0..5] (six DIFFERENT uids 3575/10631/27549/27561/...) -> the SAME 20 bytes: 26008000 00000001 0004 0000 0001 0000 00000000 = nTDs 1, TD length 4 code 0x0000 (VOID), one type used, NO data, 0 attributes: an EMPTY variant, with NO error on the property node.
FAILED PREDICTION: Constant.Value returns the numeric constant's value as a variant (labviewwiki: 'Value - returns the value of the constant as an LV Variant', read/write, VI Scripting). Earlier review (archive/peer/2026-09-15-opconstvalue-run6-numeric-reads-none.md) ranked 'H3: 634AC00 returns an empty variant for numerics' third; it is now the measurement.
Questions (read-only; cite what you read): (1) Is it known/documented that Constant.Value (634AC00) yields a void variant for DigitalNumericConstant (numeric constants) in recent LabVIEW - e.g. because numeric constants keep their value in the terminal/type, or because the property is implemented only for some Constant subclasses (String, Path, Boolean?)? Any NI forum/LAVA thread with 'Constant Value property returns empty variant'? (2) What OTHER scriptable way reads a numeric constant's value: the DigitalNumericConstant / NumericConstant class has its own properties (labviewwiki 'Numeric Constant class' / 'DigitalNumericConstant' - list them with IDs: e.g. a 'Text'/'Value'/'Representation' property?), the Terminal's 'Value'?, GObject 'Label.Text' is the label not the value, or the ONLY route being VI Server on a COPY of the VI (e.g. change to control then read default value - forbidden on the original but allowed on a copy in claudeDev)? (3) Could the void be caused by MY node: the TMSC casts to 'VI Server:Constant'; would casting to 'VI Server:DigitalNumericConstant' (or NumericConstant) make the same property ID return the value (property lookup by class)? Give the exact class names as VI Server spells them. (4) Cheapest discriminator that separates 'property unimplemented for numerics' from 'my cast/class wrong': e.g. read a BooleanConstant and a PathConstant through the same op - which classes should return data if the property is implemented per-subclass? Rank and cite.


## Answer

The measurement is credible, but it does **not** yet prove that numeric constants intrinsically store their value only in the terminal or that `Constant.Value` is intentionally unimplemented for numerics. The strongest external counter-evidence is an NI Community example where a `DigitalNumericConstant` is configured by writing its inherited `Value` property; the accepted solution merely changes execution order so `Representation` is written before `Value`. That means the property has historically accepted numeric data on this class. [NI Community: Decimal rounding while creating a double numeric constant](https://forums.ni.com/t5/LabVIEW/Decimal-rounding-while-creating-a-double-numeric-constant-when/td-p/3177207)

### 1. Is the void result known or documented?

I found no NI Forum, LAVA, or LabVIEW Wiki source documenting ??Constant.Value` returns an empty/void variant for `DigitalNumericConstant`,??including no recent-version statement to that effect.

The published class metadata says the opposite without listing subclass exceptions:

- `Constant.Value`, property ID `634AC00`, is read/write and ?쐏rovides the value of the constant??as an LV Variant. [Constant class](https://labviewwiki.org/wiki/Constant_class)
- `DigitalNumericConstant` inherits through `NumericConstant ??Constant`; it is class ID `16390`, while `NumericConstant` is `16389` and `Constant` is `16386`. [VI Server class hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)
- A historical VI Scripting example demonstrably writes `Value` on a numeric constant. [NI Community example](https://forums.ni.com/t5/LabVIEW/Decimal-rounding-while-creating-a-double-numeric-constant-when/td-p/3177207)

Therefore rank the explanations:

1. **LabVIEW 2026 read-side regression or undocumented defect** ??most consistent with a successful/no-error read returning a canonical void variant while historical numeric writes work.
2. **A value-access quirk depending on the reference/property-node construction** ??still plausible and cheap to test.
3. **Deliberately unimplemented for every numeric constant** ??contradicted by the historical working numeric `Value` write and unsupported by published metadata.
4. **Numeric value lives only in the terminal/type** ??unlikely as a complete explanation. A terminal exposes type information, but its documented properties do not include a stored value. [Terminal class](https://labviewwiki.org/wiki/Terminal_class)

### 2. Other scriptable ways to read the value

There is no numeric-specific binary `Value` property in the documented `NumericConstant` or `DigitalNumericConstant` property sets.

`NumericConstant` properties are:

| ID | Property |
|---|---|
| `5DCFC00` | Representation |
| `5DCFC01` | Fixed-Point Representation:Bits |
| `5DCFC02` | ?쪩its:Signed |
| `5DCFC03` | ?쪩its:Word Length |
| `5DCFC04` | ?쪩its:Integer Word Length |
| `5DCFC05` | ?쪫esired |
| `5DCFC06` | ?쪫esired:Range Min |
| `5DCFC07` | ?쪫esired:Range Max |
| `5DCFC08` | ?쪫esired:Delta |
| `5DCFC09` | ?쪨ctual |
| `5DCFC0A` | ?쪨ctual:Range Min |
| `5DCFC0B` | ?쪨ctual:Range Max |
| `5DCFC0C` | ?쪨ctual:Delta |
| `5DCFC0D` | Adapt To Entered Data |
| `5DCFC0E` | ?쪰nclude Overflow Status? |
| `5DCFC0F` | Fixed-Point Overflow Status Visible? |

None is the numeric datum. [NumericConstant class](https://labviewwiki.org/wiki/NumericConstant_class)

`DigitalNumericConstant` adds display-oriented properties:

- `634D001` ??Display Format
- `634D002` ??Display Format:Format
- `634D003` ??Display Format:Precision
- `634D004` ??Numeric Text
- `634D005` ??Unit Label Visible? (private)
- `634D006` ??Format String
- `634D007` ??Radix Visible?
- `634D008` ??Unit Label

The documented category confirms this property set; individual pages confirm, for example, `634D001`, `634D002`, and `634D006`. [VI Scripting property index](https://labviewwiki.org/wiki/Category%3AVI_Scripting_Property), [Display Format](https://labviewwiki.org/wiki/DigitalNumericConstant_class/Display_Format_property), [Display Format:Format](https://labviewwiki.org/wiki/DigitalNumericConstant_class/Display_Format.Format_property), [Format String](https://labviewwiki.org/wiki/DigitalNumericConstant_class/Format_String_property)

The best non-mutating fallback is consequently:

1. Cast to `DigitalNumericConstant`.
2. Read `Numeric Text` (`634D004`) to obtain a `NumericText` reference.
3. Read inherited `Text.Text` (`632D800`).

`Text.Text` returns the text as displayed, and `NumericText` supplies formatting properties. [Text class](https://labviewwiki.org/wiki/Text_class), [NumericText class](https://labviewwiki.org/wiki/NumericText_class)

That route is **textual, not lossless binary numeric extraction**. Its result is affected by representation, radix, format string, precision, SI notation, date/time formatting, and possibly locale. Preserve at least `Representation` plus `Format String`/display format and parse accordingly. The numeric display format values are documented here: [DigitalNumericConstant Display Format](https://labviewwiki.org/wiki/DigitalNumericConstant_class/Display_Format_property).

The terminal is not an alternative value source. It exposes `Type Descriptor` (`634A001`), `Type Descriptor (Full)` (`634A007`), and `Data Type` (`634A008`), but no value property. [Terminal class](https://labviewwiki.org/wiki/Terminal_class)

For a lossless result, the mutation-on-a-copy route is defensible:

- On a disposable VI copy, invoke `Constant.Change to Control` (`634A802`).
- Read the resulting control?셲 `Default Value` or `Value`.
- Discard the copy.

The documented method changes the constant into a control and invalidates/closes the old constant reference, so reference handling matters. [Constant class methods](https://labviewwiki.org/wiki/Constant_class)

### 3. Could the `Constant` cast cause the void?

Possible as a LabVIEW bug discriminator, but **not the expected VI Server semantics**.

The exact published VI Server class names are:

- `Constant`
- `NumericConstant`
- `DigitalNumericConstant`
- `BooleanConstant`
- `PathConstant`
- `StringConstant`

They appear with those spellings in the VI Server hierarchy. [VI Server class hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)

`634AC00` belongs to `Constant`; `DigitalNumericConstant` inherits it rather than declaring a second numeric `Value` property. [Constant class](https://labviewwiki.org/wiki/Constant_class), [NumericConstant class](https://labviewwiki.org/wiki/NumericConstant_class)

A successful TMSC to `Constant` retains the underlying object as a `DigitalNumericConstant`; it should not turn that object into a base-class instance. Consequently, changing only the wire?셲 static type should still address the same inherited property ID. Nevertheless, generating the property node from a `DigitalNumericConstant`-typed wire is an excellent test for a 2026 editor/property-node specialization bug. If that works, the problem is node construction/static typing, not numeric storage.

### 4. Cheapest discriminators, ranked

1. **Read `DigitalNumericConstant.Numeric Text ??Text.Text` on one known nonzero integer.**  
   If this returns the visible digits while `634AC00` remains void, you have immediately established that the reference and object are valid and that only binary `Constant.Value` readback is failing. [DigitalNumericConstant property index](https://labviewwiki.org/wiki/Category%3AVI_Scripting_Property), [Text.Text](https://labviewwiki.org/wiki/Text_class)

2. **Rebuild only the property node from a `DigitalNumericConstant`-typed reference and select inherited `Value`.**  
   Use class name `DigitalNumericConstant`, not a guessed ?쏡igital Numeric Constant.??If it returns data, your current base-typed node triggers the defect. If it remains void, the cast hypothesis is substantially weakened. [VI Server class hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)

3. **Read a `BooleanConstant` through the unchanged `Constant` op.**  
   Boolean is the cleanest sibling control: it directly inherits `Constant.Value` and has minimal representation complexity. Data here plus void numeric strongly isolates `NumericConstant`/`DigitalNumericConstant`. [Constant children](https://labviewwiki.org/wiki/Constant_class)

4. **Read a `PathConstant` through the unchanged op.**  
   Path is another direct sibling with no separate value property, although empty-path test data can itself look empty, so use an unmistakably nonempty path. [PathConstant class](https://labviewwiki.org/wiki/PathConstant_class)

Interpretation matrix:

| Boolean | Path | Numeric-child-typed node | Best conclusion |
|---|---|---|---|
| data | data | void | Numeric read-side implementation/regression |
| data | data | data | Base-typed property-node construction bug |
| void | void | data/void | Shared op/reference-class problem despite String working |
| data | void | void | Per-subclass support/defect; add Array or Cluster as another sibling |
| void | data | void | Boolean-specific issue; still numeric-specific evidence |

Bottom line: **do not promote ?쐍umeric constants intentionally return void??to a design fact yet**. The published API promises a value, and historical scripting successfully writes numeric `Value`. Your result currently supports ?쏬abVIEW 2026 returns void for this numeric read path,??with either a regression or property-node/static-class specialization defect as the leading explanations.

## Sources

(extract from answer)

## What was done with it

Accepted: "numerics return void" is NOT promoted to a fact; NAMES.md records it as a measurement of this read path
only. Discriminators run in the reviewer's order of cost: (1) `tools/bench/diag_constvalue_siblings.py` — Boolean
and Path constants through the unchanged op (matrix §4); then (2) a property node generated from a
`DigitalNumericConstant`-typed reference (its own `reference` terminal yields the typed seed, as with the
Constant seed) reading the inherited 634AC00, and (3) the textual fallback `Numeric Text` 634D004 → `Text.Text`
632D800 (ASCII digits, BSTR-safe) with `Representation` 5DCFC00 kept alongside. The mutation-on-a-copy route
(`Change to Control` 634A802 on a claudeDev copy of the main VI) is the lossless last resort.
