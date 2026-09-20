---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opconstvaluen-v0-recipe-numeric-reader

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (77s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRE-BUILD REVIEW (read-only; LabVIEW 2026 VI Scripting over COM). Attack tools/recipes/build_opconstvaluen_v0.py, the discriminators 2+3 you ranked in archive/peer/2026-09-15-opconstvalue-numeric-void-variant.md. NEW MEASUREMENT since (tools/bench/diag_constvalue_siblings.log, unchanged Constant-typed op, byte route, identity verified): BooleanConstant[0..3] (4 uids) -> the same 20-byte VOID variant (TD 0x0000, no data, no error) exactly like DigitalNumericConstant; StringConstant[0] -> 36 bytes with data (TD 4030 labelled String, empty string) and StringConstant[7] -> img%05d.tif; there are 0 PathConstants on the top diagram. So the matrix row is Boolean void / numeric void / String data - per-subclass defect or something strings escape. The recipe copies OpConstValue_v1.vi to OpConstValueN_v0.vi and: (1) build_property(VI Server:DigitalNumericConstant, [Value 634AC00 read, Numeric Text 634D004 read, Representation 5DCFC00 read]) in ONE node; Terminal.Create Control on its reference gives a DigitalNumericConstant-typed control; cut that wire; (2) delete the Constant-seed -> TMSC target class wire and wire the new control there (TMSC output becomes DigitalNumericConstant; it still feeds the old Constant PN by upcast); (3) TMSC output -> new PN reference (branch); (4) rewire Flatten.anything from the old PN Value to the new PN Value (byte route now carries the subclass-typed node = discriminator 2); (5) build_property(VI Server:Text, [Text 632D800 read]) fed by Numeric Text; indicators on Text and Representation (= discriminator 3). Test: 6 numerics must give parsable Numeric Text; report whether the subclass-typed Value is void; if it carries data it must equal the parsed text; a StringConstant through the numeric cast must ERROR (negative control); MAIN md5 in finally. Attack: (a) is 634D004 Numeric Text a read property returning a NumericText reference usable by a Text-class property node (Text.Text 632D800), and does Text.Text need the constant DISPLAYED/panel open to be non-empty? (b) 5DCFC00 Representation returns which type (enum/U16)? name the enum order if documented; (c) three properties in one node: if Numeric Text errors for some constants (e.g. no numeric text object), the error cluster hides Value - should I split nodes or is the error-in chain fine since each read is independent? (d) will TMSC to DigitalNumericConstant on a reference that is actually a DigitalNumericConstant succeed for ALL 180 objects the reporter lists under that class name, or can the reporter class name include subclasses (e.g. fixed-point or enum constants) that would fail the cast? (e) any reason Boolean AND numeric constants would return a void variant while string constants carry data - e.g. Constant.Value implemented via the Terminal type descriptor only for variable-size types? cite anything. (f) risk to the original main VI: none of this saves it - agree? Cite what you read.

## Answer

Verdict: buildable, but revise the recipe before running it. Discriminator 2 is sound; discriminator 3 is useful only as a display-text fallback, not as a lossless value oracle. The new Boolean/numeric/String matrix supports a shared scalar-fixed-size read defect more than a `NumericConstant`-specific defect, but no documentation I found establishes that design.

### (a) `Numeric Text` ??`Text.Text`

`634D004 Numeric Text` is expected to return a `NumericText` reference, and wiring that reference to a `Text`-class Property Node reading `632D800 Text` is the correct inheritance-based construction. NI demonstrates the equivalent `Numeric Text ??Text` property chain for numeric controls. [NI Community](https://forums.ni.com/t5/LabVIEW/Update-Numeric-Value-While-Typing/td-p/162171)

I found no NI documentation saying a diagram numeric constant must be displayed, selected, or have a front panel open for that text to exist. NI?셲 generic `Text.Text` metadata says the property does not load the front panel or block diagram into memory, which argues against a display-window requirement. [NI Text.Text API reference](https://www.ni.com/docs/ko-KR/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/decoration/text/text.html)

Still, reject the proposed assertion ?쏿ll six parse with `int`/`float`??as too strong. Display text can contain:

- hexadecimal/binary/octal notation;
- SI or engineering notation;
- localized decimal/group separators;
- units;
- infinity or NaN;
- fixed-point formatting.

NI explicitly treats a numeric constant?셲 radix as independent display state. [NI numeric-constant guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z00000159ubSAA&l=en-US)

For the discriminator, require `txt != ""`, log it, and parse only rows whose representation/format makes the grammar known. Better: choose six deliberately ordinary decimal constants after inspecting their reported text.

### (b) `Representation`

`5DCFC00` returns a LabVIEW numeric-representation enum, not the numeric datum. Across COM, expect its indicator value to arrive as the enum?셲 underlying integer, although preserving an enum indicator in the op is preferable.

I could not find a current NI page documenting the complete ordinal order. Do not encode a recalled order into the acceptance test. Log both the raw integer and, if possible, the enum display string generated by LabVIEW. Treat any complete enum ordering from an unofficial class table as unverified until measured against known I8/U8/I16/U16/I32/U32/I64/U64/SGL/DBL/EXT/complex/fixed-point seeds.

### (c) Split the three-property node

Yes?봲plit it.

A multi-element Property Node executes top-to-bottom. If one property errors, execution stops at that element and later properties are not read. Therefore the current order:

```text
Value
Numeric Text
Representation
```

means:

- `Value` is still a valid discriminator even if `Numeric Text` fails;
- `Representation` may remain stale/default if `Numeric Text` fails;
- one error cluster cannot establish which successful outputs are fresh unless every output is poisoned or separately gated.

This behavior is explicitly documented by NI. [NI Property Node reference, archived manual](https://download.ni.com/support/manuals/321526b.pdf)

Use three nodes from the same typed reference:

1. `Value` ??flatten route, own error output.
2. `Numeric Text` ??`Text.Text`, own error output.
3. `Representation`, own error output.

That gives discriminator 2 independence from discriminator 3. ?쏧gnore errors inside node??exists, but introduces another configuration assumption and is inferior for this diagnostic. [NI Community discussion](https://forums.ni.com/t5/LabVIEW/guidelines-for-order-of-property-node-elements/td-p/3215744)

Also poison/reset `repr`, `u8`, UID, text, hex, and every error indicator before each run. Presently only text/hex and UID are explicitly reset, so an aborted path can expose retained outputs.

### (d) Will all 180 casts succeed?

Do not assume that from the filter count alone.

A true subclass of `DigitalNumericConstant` will cast successfully to its base class. Fixed-point instances are therefore not intrinsically a problem if their actual VI Server class is `DigitalNumericConstant` or a descendant. A sibling class returned by an unexpectedly broad reporter filter would fail.

Your reporter already returns each object?셲 actual `Class Name 2` in [gscript.py](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:260). Cheap precondition:

```python
classes = sorted({r["class"] for r in man})
must("numeric reporter classes known", classes == ["DigitalNumericConstant"], classes)
```

If subclasses occur, enumerate them and explicitly accept only classes known to inherit from `DigitalNumericConstant`. Also test all 180 casts eventually; testing six cannot justify ?쏛LL 180.??
An enum constant may have a distinct class rather than merely a different numeric representation. The reporter?셲 returned actual class?봭ot its requested filter?봧s the decisive evidence.

### (e) Why Boolean and numeric are VOID while String carries data

There is no evidence yet that this is intentional ?쐖ariable-size types only??behavior.

NI describes constants generally as diagram terminals supplying fixed data values, without distinguishing fixed- and variable-size values. [NI constants documentation](https://www.ni.com/docs/en-GB/bundle/labview/page/creating-and-editing-user-defined-constants.html)

The strongest current interpretations are:

1. `Constant.Value` read-side implementation/defect affecting at least Boolean and digital numeric constants.
2. A shared internal storage/access path for fixed-size scalar constants that this property fails to materialize as a variant.
3. String-specific implementation that correctly materializes its value.
4. Least supported: an intentional documented contract that only variable-size constants return data.

The String result disproves a global failure in identity, flattening, and variant decoding. The Boolean result disproves the narrower ?쏯umericConstant-only??hypothesis. It does not prove the terminal/type-descriptor explanation; that remains an inference with no supporting NI source found.

A useful next sibling would be a fixed-size nonnumeric constant, if one is available, followed by an array/cluster constant. That separates fixed-size versus variable-size better than another numeric subtype.

### (f) Risk to the original main VI

Agree narrowly: the reviewed recipe contains no intentional save or mutation of the main VI. It copies and edits only `OpConstValueN_v0.vi`; main is passed as the target of read operations. The final MD5 plus mtime comparison proves the main file remained unchanged during `_test`. See [build_opconstvaluen_v0.py](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_opconstvaluen_v0.py:140).

I would not state ?쐒isk: none??absolutely:

- The baseline is taken only when `test()` begins, not at the outermost entry point.
- A process termination can prevent `finally` from reporting.
- MD5 proves disk identity, not absence of an unsaved in-memory dirty state.
- The negative test should verify the exact cast error source/code, not merely `bool(err)`; an unrelated failure currently passes T3.

Move the main MD5/mtime baseline to the start of `main()` and retain the outermost possible `finally`. Also assert the expected TMSC error code/source for `StringConstant`, and verify main modification state if the existing read-only reporter exposes it.

Bottom line: proceed only after splitting the property reads, weakening the universal `int/float` parsing assertion, checking actual reporter classes, and tightening stale-output and negative-control handling. Discriminator 2 remains decisive; discriminator 3 establishes readable displayed text, not lossless numeric equality.

## Sources

(extract from answer)

## What was done with it

All four changes applied before the build: the three properties are three separate nodes from the same typed
reference (Value → byte route; Numeric Text → Text.Text; Representation), each with an error-out indicator on the
Value and Text nodes; the universal int/float assertion is replaced by "non-empty display text, grammar logged";
the reporter's actual `Class Name 2` set is gated to exactly `DigitalNumericConstant` before any cast (T0); the
MAIN md5/mtime baseline is taken at import (before anything runs) and re-checked in the outermost `finally`; the
negative control requires the class-cast error 1057 explicitly; every result indicator (u8, repr, text, hex, UID)
is reset before each run. Representation is logged raw, its enum order not assumed. Discriminator 3 is recorded as
"readable display text", not lossless numeric equality. Log: `tools/bench/build_opconstvaluen_v0.log`.
