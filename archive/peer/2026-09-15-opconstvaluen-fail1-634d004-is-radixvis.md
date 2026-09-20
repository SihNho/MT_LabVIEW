---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opconstvaluen-fail1-634d004-is-radixvis

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (93s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS (LabVIEW 2026 VI Scripting property IDs). tools/recipes/build_opconstvaluen_v0.py run 1 (log tools/bench/build_opconstvaluen_v0.log): build_property on class VI Server:DigitalNumericConstant with property unique ID 634D004 (labviewwiki table: Numeric Text) attached a property whose terminal is named RadixVis (Radix Visible?) - so the wiki ID list for DigitalNumericConstant (634D001 Display Format, 634D002 Display Format:Format, 634D003 Precision, 634D004 Numeric Text, 634D006 Format String, 634D007 Radix Visible?, 634D008 Unit Label) does NOT match LabVIEW 2026 (634D004 = Radix Visible? here). FAILED PREDICTION: wiki IDs are the unique IDs LabVIEW uses. My explanation: the wiki list is stale or mis-numbered for this class; the unique IDs are stable across versions in general (634AC00 Constant.Value and 632D800 Text.Text worked) but this table is wrong. PLAN: a scripted census on a scratch VI - build a property node for EACH id 634D000..634D00F on class DigitalNumericConstant and record the terminal name each produces (the fleet reads terminal names; it cannot read IDs back), then use the id whose terminal is named Numeric Text / NumText. Questions: (1) is there a documented or reliably derived unique ID for DigitalNumericConstant.Numeric Text (NI vi.lib scripting examples, the LabVIEW Help property page URL slug, the labviewwiki page for that single property rather than the class table)? cite. (2) Are property unique IDs of a class strictly 634Dxxx contiguous, so a 16-id sweep must hit it, or can Numeric Text live under the NumericConstant (5DCFCxx) or a different prefix? (3) Any risk in sweeping unknown IDs on a scratch VI (crash, private-member hang)? The fleet already survived probing private members (error 1058-like declines). (4) Alternative: does the fleet-style Property Node builder accept the NAME Numeric Text when AllowAlternateNames is TRUE (Set Properties[] semantics) - cite. Read-only; cite what you read.

## Answer

Your diagnosis is probably one slot off, but the proposed 16-ID census is the wrong primary test. LabVIEW already exposes a supported census API: `Property Node ??All Supported Properties`. Use that on `VI Server:DigitalNumericConstant`, then select the record whose long name is `Numeric Text` and consume its returned Unique ID.

1. Exact ID

I found no NI documentation or installed-example reference publicly asserting a literal ID for `DigitalNumericConstant.Numeric Text`.

The strongest available sources establish:

- `DigitalNumericConstant` really has separate `Numeric Text` and `Radix Visible?` properties ([LabVIEW Wiki category](https://labviewwiki.org/wiki/Category%3AVI_Scripting_Property)).
- The individual `Unit Label Visible?` page reports `634D005`, demonstrating that the class?셲 list contains at least one entry omitted from your quoted sequence ([property page](https://labviewwiki.org/wiki/DigitalNumericConstant_class/Unit_Label_Visible%3F_property)).
- LabVIEW?셲 `All Supported Properties` result includes Unique ID, data name, short name, and long name, and says Unique IDs are stable across versions/locales ([API description](https://labviewwiki.org/wiki/Property_class/All_Supported_Properties_property)).

That substantially weakens ?쐔he IDs changed in 2026.??Your observation that `634D004 ??RadixVis`, together with `634D005 ??UnitLblVis`, instead suggests the copied table is shifted/omitted an entry. `Numeric Text = 634D003` is therefore a strong hypothesis, but I cannot call it documented ground truth from the sources retrieved.

Also distinguish two things:

- `DigitalNumericConstant.Numeric Text` returns the child `NumericText` reference.
- Properties of that returned object use the separate `NumericText` prefix `632E4xx`; for example, its display properties are `632E400..632E403` ([NumericText class](https://labviewwiki.org/wiki/NumericText_class)).
- Its inherited actual text property is on the `Text` class, consistent with your working `632D800` ([Text class](https://labviewwiki.org/wiki/Text_class)).

2. Contiguity

No, a `634D000..634D00F` sweep is not guaranteed to enumerate everything usable from the node.

Properties can be inherited from other class prefixes:

- `DigitalNumericConstant` inherits `NumericConstant`; that parent owns `5DCFCxx` properties ([NumericConstant class](https://labviewwiki.org/wiki/NumericConstant_class)).
- It also inherits `Constant`, whose properties include `634AC00 Value` ([Constant class](https://labviewwiki.org/wiki/Constant_class)).
- `Numeric Text` is a child-object-returning property; subsequent operations belong to `NumericText`/`Text`, under `632E4xx` and `632D8xx` ([NumericText class](https://labviewwiki.org/wiki/NumericText_class), [Text class](https://labviewwiki.org/wiki/Text_class)).

A 16-ID sweep might find the direct `DigitalNumericConstant.Numeric Text` accessor, but it cannot establish completeness. Dotted/nested properties are a known complication: `All Supported Properties` may list a reference-returning property without flattening every property of the returned object ([NI Community discussion](https://forums.ni.com/t5/LabVIEW/VI-Scripting-Can-t-get-or-set-all-available-properties/td-p/4030544)).

3. Sweep risk

There is no documented guarantee that arbitrary unknown/private IDs merely return a clean error. NI says internal/private properties ?쐓hould be used with caution??([NI knowledge article](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU0000006kEf0AI&l=en-US)), and experienced scripting users describe private ?쐒usty nails??as unsupported and historically crash-prone ([LAVA history](https://lavag.org/topic/20653-scripting-and-rusty-nails-history/)). One private property-method discussion even reports a repeatable LabVIEW crash for an oversized input array, demonstrating that malformed private-method calls are not necessarily safely rejected ([LAVA discussion](https://lavag.org/topic/13378-get-property-and-set-property-private-methods/)).

Thus:

- Scratch VI limits file damage.
- One ID per invocation/process limits accumulated corruption.
- It does not eliminate editor-process crashes or hangs.
- There is no hardware risk inherent in an unexecuted scratch diagram, but that conclusion depends on the fleet not running generated code or touching project/hardware VIs.

Given `All Supported Properties`, brute-force probing is unnecessary.

4. Name lookup with `Allow Alternate Names = TRUE`

Yes. `PropertyItem.Set Property` explicitly says that when `Allow Alternate Names?` is true, `ID String` may match any of:

- Unique ID
- data name
- localized short name
- localized long name

([Set Property documentation](https://labviewwiki.org/wiki/PropertyItem_class/Set_Property_method)).

Therefore `"Numeric Text"` should be accepted as the long name in an English LabVIEW installation. `Set Properties[]` exposes the same `ID Strings[]` plus `Allow Alternate Names?` inputs ([Set Properties[] documentation](https://labviewwiki.org/wiki/Property_class/Set_Properties%28%29_method)), although its page does not repeat the detailed matching semantics.

Recommended cheapest check:

1. Set node class to `VI Server:DigitalNumericConstant`.
2. Read `All Supported Properties`.
3. Record every entry whose long/data/short name contains `Numeric`, `Radix`, or `Unit`.
4. Try `"Numeric Text"` through `Set Properties[]` with alternate names enabled.
5. Only if that fails, test the returned Unique ID?봭ot a guessed range.

Bottom line: do not conclude that 2026 reassigned stable IDs. Current evidence fits an incomplete or shifted wiki class table better, and LabVIEW provides a direct runtime authority that avoids the sweep entirely.

## Sources

(extract from answer)

## What was done with it

Accepted: "IDs changed in 2026" is withdrawn — the wiki class table is shifted/incomplete (634D005 = Unit Label
Visible? confirms it). The blind 16-ID sweep is dropped; the census is narrowed to the class's eight documented
public members 634D001..634D008 (no unknown/private IDs), recording the terminal name each attaches, with 634D003
as the leading candidate for `Numeric Text`. `All Supported Properties` (636F80E) is noted as the runtime
authority to build as a reader op if the narrowed census is ambiguous; the fleet's `build_property` uses unique IDs
only (`AllowAlternateNames = FALSE`), so the long-name route needs a builder change and is deferred.
