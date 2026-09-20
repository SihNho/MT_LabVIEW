---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opconstvalue-run6-numeric-reads-none

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (56s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS (LabVIEW 2026 VI Scripting over COM, python win32com). New op OpConstValue_v1.vi (built by tools/recipes/build_opconstvalue_v1.py, saved runnable) reads a diagram constant's value: Open VI Reference -> Traverse(class name, BD) -> Index Array -> To More Specific Class (target class from a Constant-typed seed control) -> Property Node Constant.Value 634AC00 (read) -> a VARIANT indicator 'Value'; Python reads it with vi.GetControlValue('Value') after the op runs (log tools/bench/build_opconstvalue_v1.log, run 6, 04:41).
RESULT: for Class Name 'StringConstant' on the 4-MB main VI, all 22 top-level constants came back as typed str with plausible content ('img%05d.tif', 'Bead # %d', 'Save cal cluster file', a multi-line 'Your acquisition lost frames...' message, and 11 empty strings). For 'DigitalNumericConstant' (180 on the top diagram), the first 12 ALL came back as Python None with NO error on the op's 'error out' (status false).
FAILED PREDICTIONS: (a) numeric constants would read as int/float; (b) one string constant would be the VISA resource literal 'COMn'/'ASRL' - now known to sit on FRAME 10 of a sequence structure, and the op traverses only the top diagram (oracle error, not an op error - but say if you disagree).
Candidates for (a): (H1) LabVIEW's ActiveX GetControlValue on a Variant indicator whose payload is a numeric marshals to VT_EMPTY/None (strings marshal fine) - a known marshalling limit? (H2) the Variant holds the number fine but win32com converts the LV variant-of-DBL to None; (H3) DigitalNumericConstant.Value 634AC00 returns an empty variant for numerics (the property is documented as LV Variant); (H4) index mismatch: the reporter's Traverse index and the op's index disagree so the op hits constants with no value (unlikely: no error, and strings matched). Questions: (1) rank; cite anything on GetControlValue + Variant indicators over ActiveX (NI docs/forums). (2) The cheapest scriptable discriminator: I intend (i) read a BooleanConstant class through the same op on the same VI - True/False would show non-string payloads marshal; (ii) read the numeric constants of a small fleet op VI (OpReport_v3.vi) whose constants I can count. Better ideas welcome. (3) The likely fix inside the op: append 'Variant To Flattened String' / 'Flatten To String' or a 'Format Into String' (%g) to the Value output so Python receives a STRING, or use Variant 'Variant To Data' with a DBL type? Which is scriptable with New VI Object (style ring names) and gives an exact, lossless representation for I32/DBL/U8 constants? (4) Anything in this plan that would mask a wrong-class read? Read-only; cite what you read.


## Answer

The leading problem is almost certainly the **LabVIEW-Variant ??COM VARIANT boundary**, but your current observations do not distinguish H1 from H2. I found no NI source documenting numeric payloads of a LabVIEW Variant indicator as supported by `GetControlValue`; therefore ?쐊nown marshalling limitation??would presently be too strong.

### 1. Ranking

1. **H1/H2 jointly ??high probability.** Treat them as one hypothesis until you inspect the value inside LabVIEW. `GetControlValue` demonstrably returns ordinary numeric controls through Python, but that does not establish that a LabVIEW Variant containing a numeric can be represented as an Automation VARIANT. NI?셲 Python/ActiveX article only says controls and indicators can be accessed; it says nothing about nested LabVIEW variants or their supported payload types: [NI: Python `NoneType` errors with LabVIEW ActiveX](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU0000008tNV0AY&l=en-US). A forum example likewise demonstrates only ordinary `GetControlValue` use: [NI Community: win32com GetControlValue](https://forums.ni.com/t5/LabVIEW/win32com-method-to-GET-control-s-value/td-p/3793910).

2. **H3 ??possible, but materially less likely.** The successful StringConstant results show that `Constant.Value` and your cast/wiring work at least for that subclass. NI describes diagram constants as carrying typed fixed values, rather than numeric constants being intrinsically valueless: [NI: Creating and Editing User-Defined Constants](https://www.ni.com/docs/en-GB/bundle/labview/page/creating-and-editing-user-defined-constants.html). Still, the scripting property itself is insufficiently documented publicly, so H3 cannot be dismissed without LabVIEW-side serialization.

3. **H4 ??low, but not eliminated.** String traversal matching proves the general indexing scheme, not that a separately performed numeric traversal has identical options, scope, or ordering. ?쏯o error??is weak evidence unless the post-cast actual class and reference validity are separately reported.

I agree about the VISA literal: if it is in frame 10 and traversal is limited to the owning VI?셲 top-level diagram, its absence is an oracle/scope mistake, not evidence against `OpConstValue`.

### 2. Cheapest discriminator

Before BooleanConstant or the fleet VI, do these two tests:

1. **Read a plain DBL/I32 front-panel indicator directly through `GetControlValue`.** Give it a distinctive value such as `1234.25`. If Python receives a number, ordinary numeric COM marshalling works; only the nested LabVIEW Variant path remains suspect. Existing MATLAB and Python examples show ordinary controls being returned by `GetControlValue`: [MATLAB example](https://forums.ni.com/t5/LabVIEW/matlab-calling-labview-via-activex-passing-parameters/m-p/487497), [Python example](https://forums.ni.com/t5/LabVIEW/win32com-method-to-GET-control-s-value/td-p/3793910).

2. **Inside OpConstValue, feed `Constant.Value` into Variant To Flattened String and return textual hex for both `data string` and `type string`.**  
   - Nonempty type/data: H3 is false; the loss happens at the Variant/COM boundary, leaving H1 versus H2 mostly an implementation-label distinction.
   - Empty output or a LabVIEW-side error: H3 or a wrong reference/cast becomes likely.

BooleanConstant is useful, but weaker: success would prove another nested payload survives; failure would still not say whether LabVIEW supplied an empty value or COM discarded it. Testing OpReport?셲 constants also changes the oracle and target simultaneously, so it is less diagnostic than the two controlled probes above.

### 3. Fix

Use **Variant To Flattened String**, returning:

- type descriptor as hex
- data bytes as hex
- optionally the LabVIEW version
- actual class name and object identity/index

That is the only proposed route that preserves both the original numeric representation and its type. NI says Variant To Flattened String emits the contained variant?셲 data plus its type description; NI also gives a DBL example whose type code is `0x0A`: [NI Community example](https://forums.ni.com/t5/LabVIEW/How-to-get-a-variant-s-value-as-a-string/td-p/1898883). NI documents flattened variant content as including type information and flattened data, with big-endian integers: [NI: Understanding Flattened Variant Data](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGQrCAO&l=en-US).

Hex-encode the binary strings before COM. That avoids making success depend on how embedded NULs and arbitrary bytes are transported as automation strings.

Do **not** use `%g` as the canonical result. It is display formatting, can discard original representation/type, and its notation depends on exponent and precision: [NI format guidance](https://www.ni.com/en/support/downloads/instrument-drivers/tools-resources/instrument-driver-guidelines/block-diagrams.html). It also collapses distinctions such as I32 `1`, U8 `1`, and DBL `1.0`.

Do **not** use Variant To Data with a DBL seed as the general solution. It deliberately requests DBL, so even where numeric conversion succeeds it cannot preserve whether the source was I32, U8, SGL, DBL, enum, fixed-point, or another numeric representation. NI also warns that flattened types are not freely coercible and type mismatches can fail: [NI: Handling Variant Data](https://www.ni.com/docs/ar-IQ/bundle/labview/page/handling-variant-data.html).

I could not verify a documented `New VI Object` style-ring string for Variant To Flattened String. Do not guess that identifier. The cheap scriptable approach is to use a known-good seed containing that primitive/subVI and copy it, or have the manager query the style list through the existing reporter pipeline.

### 4. What could mask a wrong-class read

Your current design can mask one in several ways:

- The reported index may identify the *nth reporter result*, while the op indexes a separately generated traversal array.
- `To More Specific Class` proves compatibility with the requested scripting class, not that the object is the reporter entry you intended.
- An empty Variant is ambiguous if you return neither the runtime class nor a type descriptor.
- Repeating traversal for every index assumes stable ordering; matching string contents does not prove stability for another class query.
- A default-initialized output can hide failure if error flow does not force an unmistakable failure sentinel.

Return, alongside the value:

- array length and requested index
- pre-cast and post-cast `Class Name`
- reference-valid flag
- object UID or another stable scripting identity if exposed
- owner/diagram identity
- flattened type descriptor
- explicit `ValueReadOK`, separate from the ordinary error cluster

The decisive next experiment is therefore not Boolean: it is **numeric `Constant.Value` ??Variant To Flattened String ??hex string** in the same op and at the same failing index.

## Sources

(extract from answer)

## What was done with it

Accepted: the Boolean/OpReport probes are dropped (weaker, two variables at once); the reviewer's probe 1 (plain
numeric indicator over GetControlValue) is already established by every op's `# of Refs` read. The fix and the
decisive experiment coincide: OpConstValue gets `Variant To Flattened String` on the Value output and exports the
type descriptor and data as HEX strings (lossless; `%g` and Variant-To-Data-DBL rejected as type-collapsing, as
argued). The style-ring identifier is not guessed — it is resolved from the fleet's verified style-name registry or by
copy_by_index from a VI that contains the primitive. Wrong-class masking: the op will also export the post-cast
class name and the array length, and the recipe gates the string oracles again after the change.
