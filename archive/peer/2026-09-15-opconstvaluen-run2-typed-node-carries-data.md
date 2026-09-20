---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opconstvaluen-run2-typed-node-carries-data

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (111s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS (LabVIEW 2026 VI Scripting). tools/recipes/build_opconstvaluen_v0.py run 2 (log tools/bench/build_opconstvaluen_v0.log): OpConstValueN_v0 built and saved (all gates PASS). DECISIVE MEASUREMENT: with the property node generated for class VI Server:DigitalNumericConstant (typed control on its reference feeding the To More Specific Class target), Constant.Value 634AC00 now CARRIES DATA for all six numeric constants: flattened variants of 31/43/37/41/31/31 bytes with labelled TDs 400a (DBL), 4007 (U32), 4003 (I32) - while the SAME property ID on the SAME objects through a VI Server:Constant-typed node returned the 20-byte void variant (and Boolean constants void too). Numeric Text 634D007 -> Text.Text gives 1,0,1,0,0,1; Representation 5DCFC00 gives 1,6,3,3,3,3 (raw ints). Negative control: a StringConstant through the numeric cast gives error 1055 on the typed property nodes (their separate error indicators), op error out clear. TWO FAILED PREDICTIONS of mine: (a) my parser gated TD lengths to be EVEN (your earlier answer: label Pascal string rounded to even) - measured TD lengths 7, 23, 17, 21, 11 are ODD and the totals 8 + ln + 4 + data + 4 equal the blob length EXACTLY with NO pad byte (e.g. 31 = 8+7+4+8+4 for the DBL); (b) I expected 1057 (wrong class) from the TMSC; got 1055 (invalid reference) on the property nodes. My explanations: (1) the static class of a scripted property node decides how Value is materialised - the base Constant node yields void for fixed-size scalars, the subclass node yields the value (an NI defect or by-design specialisation); (2) TD lengths are the raw byte count, not padded, in this flattened-variant form; (3) the TMSC output in error is an invalid refnum that the downstream nodes report as 1055 while TMSC error itself is not wired into the op error chain. Questions: (A) rank/attack (1) - is there any NI statement that Constant.Value depends on the node class, or that Value must be read on the most-specific class? (B) confirm or refute (2): in the flattened-variant / type-descriptor format is the TD length field the unpadded byte count with padding applied only in some contexts (e.g. saved VI heaps)? cite. (C) what representation enum order does 1=?, 3=?, 6=? correspond to (NumericConstant.Representation, LabVIEW 2026): documented? If DBL=1, I32=3, U32=6 matches the TDs, say so. (D) anything that would make a wrong-TD decode still pass: my gates are exact body consumption (8 B for DBL, 4 B for I32/U32), attrs==0, finite; plus the value must equal the parsed Numeric Text (1/0). Read-only; cite what you read.

## Answer

Your measurements are strong, but explanation (1) should be narrowed. Explanation (2) is correct for this specific modern flattened-variant representation, not as a universal TD rule.

### A. `Constant.Value` versus property-node class

My ranking:

1. **LabVIEW 2026 defect or undocumented implementation specialization ??most likely.**
2. **Some hidden construction metadata differs between the two generated property nodes ??plausible.**
3. **Documented requirement to access `Value` through the most-specific class ??unsupported and unlikely.**

NI documents property `634AC00` on the base `Constant` class: it ?쐏rovides the value of the constant??as an LV Variant. It gives no subtype restriction, no exception for fixed-size scalars, and no instruction to downcast first. [NI Constant.Value](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/constant/value.html)

The class hierarchy likewise puts `Value` on `Constant`, inherited by `NumericConstant` and `DigitalNumericConstant`; the subclass adds properties such as `Representation`, rather than redefining `Value`. [Constant class hierarchy](https://labviewwiki.org/wiki/Constant_class), [NumericConstant class](https://labviewwiki.org/wiki/NumericConstant_class)

NI does recommend casting references to a specific class when you need properties exposed only by that subclass?봣or example, casting a generic control to `Digital` to access format/precision. That does **not** imply inherited properties change meaning after the cast. [NI employee explanation](https://forums.ni.com/t5/LabVIEW/Change-properties-of-multiple-controls/m-p/532481)

Therefore:

- ?쏷he static class changes how this inherited Variant-valued property is materialized??fits the measurement.
- ?쏺alue must be read on the most-specific class??does **not** have documentary support.
- Since the identical property ID behaves differently, I would call it an **undocumented LabVIEW 2026 behavior, probably a defect**, until NI confirms otherwise.

One remaining attack: confirm that both nodes report exactly property ID `634AC00`, read direction, and only differ in `Property Node Class Name`. If so, the ?쐆idden recipe difference??alternative becomes very weak.

Your 1055 explanation is credible but should remain empirical. A failed cast producing an invalid output refnum, followed by a property operation that reports invalid reference, is normal dataflow behavior when the cast?셲 error output is not chained downstream. NI explicitly describes invalid or failed casts as producing unusable/default references in related TMSC cases. [NI TMSC cast requirements](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000gNoVCAU&l=en-US), [NI Community discussion of invalid TMSC outputs](https://forums.ni.com/t5/LabVIEW/To-more-specific-class-works-on-IDE-but-not-on-EXE-on-target/td-p/4398467)

### B. Odd TD lengths and padding

**Confirmed for the LabVIEW 8+ type-descriptor save-buffer representation used inside `Flatten To String(variant)`. Do not generalize it to every TD serialization.**

The crucial distinction is:

- `Flatten To String` on a variant produces a TD **save buffer**.
- `Variant To Flattened String` exposes a different descriptor form.
- LabVIEW 7.x conversion uses yet another 16-bit representation.

The documented format explicitly distinguishes these encodings. It even gives a scalar save-buffer descriptor:

```text
0005 000A 00
```

That descriptor?셲 declared length is **5 bytes**, proving that an odd TD length is valid in the modern save-buffer form. [Type Descriptors, especially ?쏰bservable Formats??and the scalar save-buffer example](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/Type_Descriptors.html)

The even-rounding statement applies to a Pascal name appended in the `Variant To Flattened String` descriptor form: there the name contribution is rounded to a multiple of two. It is not a safe parser invariant for your `Flatten To String(variant)` blob. [Same type-descriptor documentation](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/Type_Descriptors.html)

NI?셲 current KB confirms the outer structure you observed?봵ersion, type descriptor, data, and attribute count?봞nd explicitly warns that the variant encoding can change between LabVIEW releases. [NI flattened-variant format](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGQrCAO&l=en-US)

So your corrected rule should be:

> In this LabVIEW 2026 `Flatten To String` variant encoding, consume exactly the declared TD byte length; do not independently round it. Alignment rules from `Variant To Flattened String`, 7.x descriptors, in-memory TDs, or VI resource heaps do not automatically apply.

I found no source supporting the more specific claim that padding is ?쏿pplied in saved VI heaps.??Keep that as a separate format-specific proposition.

### C. Representation enum

Yes?봮fficially documented by NI:

- `1` = Double Precision (`DBL`)
- `3` = Long (`I32`)
- `6` = Unsigned Long (`U32`)

[NI NumericConstant.Representation](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/constant/numericconstant/representation.html)

Those values match your TD codes:

- `0x400A` ??underlying type code `0x0A` = DBL
- `0x4003` ??`0x03` = I32
- `0x4007` ??`0x07` = U32

The high byte contains internal/name flags and should be ignored when comparing the underlying TD type code. [Type descriptor codes and reserved high byte](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/Type_Descriptors.html)

### D. Can a wrong decoder still pass?

Yes, principally because all measured values are only `0` and `1`.

Your present gates establish the decoded **value**, but do not fully establish the numeric representation:

- I32 and U32 encode nonnegative `0` and `1` identically. A decoder with the signed/unsigned meanings swapped could pass body length, exact consumption, attributes, finiteness, and text equality.
- Zero is especially weak: many incorrect numeric interpretations of an all-zero body still produce numeric zero.
- DBL `0` and `1` are stronger, but they do not thoroughly test byte order or arbitrary floating-point handling.
- Matching Numeric Text is not an independent representation oracle; it verifies the value shown by LabVIEW, not your TD-code mapping.

Cheap strengthening checks:

- Require the outer LabVIEW version word and `nTDs == 1`.
- Validate the entire declared TD structure, including label/name consumption and type-specific fields?봭ot merely the final `0x0A/03/07`.
- Cross-check TD code against the independently documented `Representation` enum.
- Eventually test a negative I32 to distinguish it from U32.
- Test a non-integral finite DBL such as `1.5`.
- Test a non-palindromic integer such as `0x01020304` to expose endian mistakes.
- If constants cannot be changed, classify the existing result as ?쐖alue decoding validated for 0/1; signedness and general endian handling not independently exercised.??
Bottom line: the six-object result convincingly proves that the subclass-typed node materializes usable values and the base-class node does not. It does **not** justify a general ?쐌ost-specific class required??rule, and the current `0/1` fixtures do not independently prove I32-versus-U32 decoding.

I followed the project?셲 LabVIEW-automation skill only to enforce the read-only evidence workflow and avoid touching LabVIEW or repository binaries.

## Sources

(extract from answer)

## What was done with it

Accepted. NAMES.md now states the finding as "undocumented LabVIEW 2026 behaviour, probably a defect: the same
634AC00 read materialises a void variant through a `Constant`-typed node and the value through a
`DigitalNumericConstant`-typed node" — not as a documented most-specific-class rule. The odd-TD-length rule is
recorded as specific to the `Flatten To String(variant)` save-buffer encoding. The documented Representation enum
(1 DBL, 3 I32, 6 U32) is now a cross-check gate in the reader: the TD low byte must match the enum for every read
(0x0A/0x03/0x07). Limitation kept explicit: values 0/1 validate value decoding only; signedness/endian are not
independently exercised until a negative I32 or a non-palindromic integer is read (the selector constants may
provide one). Both nodes carry exactly 634AC00 read — the recipe builds both from the same `build_property`
call differing only in class name (gate B prints the terminal lists).
