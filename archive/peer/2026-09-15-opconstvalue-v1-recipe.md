---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opconstvalue-v1-recipe

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (83s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS RECIPE before it runs (LabVIEW 2026 VI Scripting over COM, zero GUI). Read tools/recipes/build_opconstvalue_v1.py whole, docs/toolkit-capabilities.md ("typed-control seed" section and the table row "reading a diagram constant's value"), tools/recipes/build_opconstvalue.py (the older DRAFT and its unresolved donor problem), tools/bench/census_constant_seed.log, and tools/gscript.py copy_by_index().
Design: OpConstValue_v1 = a copy of OpReport_v3 (Open VI Reference -> Traverse(Class Name) -> refs[] -> Index Array(index)) into which two nodes are copied BY REFERENCE (copy_by_index, verified in row 39/41) from NI's example 'Navigating Nodes and Wires.vi' diagram 3: the Property Node uid 284 (data terminal 'Value') and the To More Specific Class that feeds it. Finish hooks: F1 (after the PN copy) makes the loaded target runnable by Terminal.Create Control on the PN's 'reference' -> a CONSTANT-typed refnum control (the seed); F2 (after the TMSC copy) deletes the seed's wire, wires seed -> TMSC 'target class', IA.element -> TMSC 'reference' (branch), TMSC out -> PN 'reference', and creates a Variant indicator on 'Value'. Test: read the main VI's Constant objects (Traverse class 'Constant') by index and require values for >= 1.
Attack: (1) Is PN 284 in that example really a Constant-class node (NI's example navigates from a wire to a constant and reads Value) - could it be a Control/Terminal 'Value' instead? The census shows its reference comes from a TMSC; what class does that example cast to (cite the example's description or the NI help for 'Navigating Nodes and Wires')? If it is not Constant, the seed would type the TMSC wrongly (silently: Create Control types the control by the terminal). (2) Does Terminal.Create Control on a Property Node's 'reference' input produce a refnum CONTROL of the node's class (the row-28 seed trick used exactly this on a Loop-class PN) - confirm it applies to a Constant-class PN. (3) copy_by_index copies ONE object: does copying a Property Node by reference bring its configured property (Value 634AC00) and class along (the Move method duplicates the node as-is)? Any risk the copied PN arrives with a generic class? (4) Traverse class string for constants: 'Constant'? (NAMES.md: 'Constant' traverse used by report()); numeric constants are DigitalNumericConstant -> NumericConstant -> Constant: does Traverse 'Constant' return all subclasses, and does Constant.Value on the base class return a Variant for every subclass? (5) The Variant over ActiveX: GetControlValue of a Variant indicator - returns the underlying number/string (the draft's design choice) - cite anything on ActiveX marshalling of LV Variants. (6) Gates missing; cheapest scratch test. Read-only; cite what you read.


## Answer

**Verdict: STOP before running.** The design is plausible, but the evidence does not yet establish that PN 284 is Constant-typed, and the functional test can pass without proving correct value or Variant marshalling.

1. **PN 284 is probably Constant-class, but the census does not prove it.**  
   `census_constant_seed.log` establishes only: diagram 3, property `Value`, reference supplied by TMSC. It never identifies the TMSC target class. NI?셲 description of *Navigating Nodes and Wires* discusses navigating from nodes through terminals to wires; it does not identify PN 284?셲 class. [NI?셲 LabVIEW manual](https://nubilight.nubicom.co.kr/upload/datasheet/LabVIEW_Fundamentals_ko.pdf)

   A Control-class `Value` property is therefore not excluded by current evidence. Do not infer the class from the property name.

   Required pre-build gate: report the class encoded by the TMSC `target class` input or create the seed and prove that it compiles when used as the target-class input of a known Constant.Value chain. Merely finding `Value` and a TMSC is insufficient.

2. **Terminal.Create Control is type-preserving, but Constant-specific applicability remains an inference.**  
   An NI engineer states that a terminal?셲 type is the correct source for creating a control, specifically noting that this preserves refnum and class types. [NI Community](https://forums.ni.com/t5/LabVIEW/Create-Control-From-Reference/td-p/1539816) That supports the row-28 technique generically.

   It does not prove that PN 284?셲 terminal is Constant-typed. If PN 284 is actually Control.Value, Create Control will faithfully create the wrong seed?봳he exact silent failure under attack. The typed-seed section itself says each seed casts exactly its class; a wrong seed can still produce a structurally valid-looking build.

3. **Copy-by-reference should preserve the configured Property Node, but add an explicit post-copy gate.**  
   `copy_by_index()` drives Move with `duplicate=True`, and VI Scripting users describe that method as copying arbitrary objects. [NI Community](https://forums.ni.com/t5/LabVIEW/VI-Scripting-get-reference-of-the-duplicate-element/td-p/1882509) This strongly favors the copied node retaining its configured property and class rather than becoming generic.

   However, the current UID guard validates the selected donor object, not the semantic state of the new object. After C1, require:

   - exactly one new Property object;
   - its data terminal is exactly `Value`;
   - its property ID is still `634AC00`, if the fleet can read that metadata;
   - its reference terminal accepts the intended Constant seed and the target becomes runnable.

   Also record the new UID. F1 currently rediscovers ?쏿 Property Node with a source Value terminal,??which could select an existing OpReport property node if one ever matches.

4. **`Constant` is a valid Traverse class locally; subclass coverage is strongly supported but not fully tested.**  
   The requested toolkit table records measured main-VI counts:

   - `Constant`: 301
   - `NumericConstant`: 207
   - `DigitalNumericConstant`: 180
   - `StringConstant`: 22

   Thus `Constant` clearly behaves as a base-class query in this installation; its count exceeds each subtype count. External Traverse examples likewise describe searching by a broad class such as `Control` to return subclasses. [NI Community](https://forums.ni.com/t5/LabVIEW/LV-OOP-for-an-alternative-to-clusters/m-p/3352783)

   What is not established is that `Constant.Value` succeeds for every Constant subclass. Array constants are known to expose their whole value through the array constant?셲 Value property, but that is community evidence, not a universal guarantee. [NI Community](https://forums.ni.com/t5/LabVIEW/Using-VI-Scripting-to-find-value-of-Array-of-String-Constants/td-p/4000163) Class/refnum or unusual universal constants may still error or marshal unexpectedly.

5. **The ActiveX Variant assumption is not confirmed.**  
   NI documents a LabVIEW Variant as a container retaining both value and original type, and recommends Variant data when interoperating with ActiveX. [NI Variant documentation](https://www.ni.com/docs/ar-IQ/bundle/labview/page/handling-variant-data.html) NI also says Variant controls and indicators pass data to and from ActiveX controls. [NI ActiveX documentation](https://www.ni.com/docs/ar-SD/csh?context=lvcore_lvconcepts_using_activex_with_labview)

   Neither source says `VirtualInstrument.GetControlValue` automatically unwraps a LabVIEW Variant indicator to the contained Python scalar. The draft?셲 ?쏱ython gets a plain number or string??remains unverified. A COM Variant could instead contain a LabVIEW-specific Variant representation, an array representation, or a value with coercion.

6. **The current test gate is too weak.**

   `got` increments whenever `_run()` and `GetControlValue()` do not throw. Consequently it accepts:

   - `None`;
   - an empty/default Variant;
   - the wrong constant?셲 value;
   - a wrapper object;
   - a coerced value;
   - identical defaults returned for every index.

   The docstring promises ?쐍umbers or strings,??but the code never checks `isinstance`, expected values, uniqueness, or the known VISA literal. It also tests only the first 40 of 301 constants, so the cited startup VISA constant may not be included.

Additional missing gates:

- Assert the donor TMSC?셲 `target class` input is actually Constant-typed before copying.
- Assert exactly one TMSC was copied and identify it by the added UID, not terminal signature alone.
- Assert the seed wire selected for deletion is nonzero, unique, and absent afterward.
- Assert all four final wires by matching wire UIDs at both endpoints, including both TMSC inputs.
- Assert `labels["seed"]` and `labels["value"]` each contain exactly one newly created label.
- Preserve and verify the NI example?셲 hash as well as `OpReport_v3`; currently only `SRC` is checked.
- Assert no unexpected GObjects were added by either copy operation.
- Check `_run()`?셲 LabVIEW error outputs, not only Python exceptions.
- Test at least numeric, string, Boolean, array/cluster, and unsupported/special constants separately; report failures rather than treating one success as fleet-wide support.

**Cheapest safe scratch test**

Do not use the main VI as the first oracle. Create a disposable VI with three known constants?봢.g. I32 `12345`, DBL `3.25`, and string `hello`?봳hen demand exact type-and-value equality. LabVIEW?셲 Terminal.Create Constant method creates a constant of the terminal?셲 datatype and accepts an optional value, so the claim that the fleet ?쐁annot create constants??is too strong; this is the cleanest headless fixture if that method is already reachable. [NI Terminal.Create Constant](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/terminal/createconstant.html)

Minimum acceptance:

```text
I32    -> Python int/compatible integer, exactly 12345
DBL    -> Python float, exactly 3.25
String -> Python str, exactly "hello"
```

Also read two different constants consecutively and then reread the first, proving the indicator updates rather than returning a stale/default value.

Only after that passes should the manager run a reference-only main-VI sample. The present `got >= 1` gate is not adequate to certify OpConstValue_v1.

## Sources

(extract from answer)

## What was done with it

Gates adopted in `tools/recipes/build_opconstvalue_v1.py` before the first run: copied nodes identified by ADDED
uid (exactly one new Property with data terminal `Value`; exactly one new TMSC), the seed's wire verified unique
and gone after deletion, all four final wires verified by uid at both ends, exactly one new label per created
control/indicator, the NI example's hash checked unchanged. The class question is settled by TEST, not inference:
Traverse `StringConstant` must return `str` values including the VISA resource literal of startup frame 10
(`COM`/`ASRL`), and `DigitalNumericConstant` must return numbers that are not all identical — a Control-class
seed would fail the cast (1055/1057) instead. `Terminal.Create Constant` is recorded as the cleaner headless
oracle for a later, dedicated test; the Variant→COM marshalling claim is what the typed oracles verify.
Run: `tools/bench/build_opconstvalue_v1.log`.
