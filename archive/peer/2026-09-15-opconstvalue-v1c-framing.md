---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opconstvalue-v1c-framing

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (93s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS (LabVIEW 2026 flattened-variant layout). tools/recipes/build_opconstvalue_v1c.py run 1 (log tools/bench/build_opconstvalue_v1c.log): the BYTE ROUTE PASSED every measurement gate - the U8 SAFEARRAY and the lowercase hex string agree byte-for-byte (53 bytes), Unflatten's remainder is empty, identity (UID/class/# of Refs) matches, the main VI is untouched. The one FAILED PREDICTION is the framing hypothesis A of my parser (as planned: it was to be validated on the documented StringConstant[7] before any numeric result is trusted). The full 53 bytes of Flatten To String on the Constant.Value variant of the string constant 'img%05d.tif' (label 'format string'):
26 00 80 00 | 00 00 00 01 | 00 16 40 30 ff ff ff ff 0d 66 6f 72 6d 61 74 20 73 74 72 69 6e 67 00 | 00 01 | 00 00 | 00 00 00 0b 69 6d 67 25 30 35 64 2e 74 69 66 | 00 00 00 00
MY READING: version 0x26008000 (LV 2026); I32 #type-descriptors = 1; TD: I16 total length 0x16=22, I16 code 0x4030 (0x30 string with flag 0x40 = 'has label'), I32 size -1 (unlimited), Pascal label 0x0d 'format string', 1 pad byte to even length; then I16 count of top-level type indices = 1, I16 index 0; then the data: I32 length 11 + 'img%05d.tif'; then I32 attribute count 0. Total 4+4+22+2+2+15+4 = 53. New parser: after the TD list read I16 nidx, nidx I16 indices, top-level TD = TDs[idx[0]], code = low byte, data follows, trailing I32 attrs must be 0, data must be consumed exactly.
Questions: (1) Is this reading consistent with NI's documented flattened-variant format (version, type descriptor(s), data, attributes) and with the known LabVIEW type-descriptor encoding (I16 length, I16 code with 0x40 label flag, string size I32 -1, Pascal label, padding)? Cite. (2) The two I16s between the TDs and the data - are they the 'number of top-level types' + 'type index' fields (the usual 'types used' list of a flattened-variant), or something else (e.g. part of the last TD)? What would DIFFER for a DBL constant: TD 00 04 00 0A with no label -> 4 bytes, or 00 xx 40 0A + label? Any element-count I32 for scalars? (3) For DigitalNumericConstant the representation may be I32/DBL/U8 etc.: list the numeric TD codes (I8..EXT) so the parser's table can be checked (mine: 01 I8, 02 I16, 03 I32, 04 I64, 05 U8, 06 U16, 07 U32, 08 U64, 09 SGL, 0A DBL, 0B EXT); does EXT flatten as 16 bytes in LV 2026 on x64 Windows? (4) Anything that would let a WRONG framing decode a DBL to a plausible finite value (e.g. an offset error of 2 or 4 bytes) - what extra gate would catch it (my current gates: exact consumption of the body, attrs==0, finite)? Read-only; cite what you read.


## Answer

Your revised framing is essentially correct, but there is one byte-boundary error in the annotation: the string TD has no padding byte after `format string`. The `00` following the final `67` is the first byte of `nTypesUsed = 00 01`.

1. Overall interpretation

The documented post?밚abVIEW 8 flattened-variant structure is:

```text
U32 LabVIEW version
U32 nTDs
TD[nTDs]
varint nTypesUsed
varint TypesUsed[nTypesUsed]
flattened value
I32 attribute count
attributes...
```

NI documents the outer sequence as version, type descriptor, flattened value, and signed 32-bit attribute count; all integers are big-endian. The detailed type-descriptor documentation expands ?쐔ype descriptor??into `nTDs`, the TD list, `nTypesUsed`, and the `TypesUsed` indices. [NI: flattened variant format](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGQrCAO&l=en-US), [NI-derived type-descriptor documentation](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/Type_Descriptors.html)

Your 53 bytes therefore segment as:

```text
26 00 80 00                         version

00 00 00 01                         nTDs = 1

00 16                               TD length = 22
40 30                               named string TD
ff ff ff ff                         variable-sized string
0d                                  label length = 13
66 6f 72 6d 61 74 20 73
74 72 69 6e 67                      "format string"

00 01                               nTypesUsed = 1
00 00                               TypesUsed[0] = TD index 0

00 00 00 0b                         data string length = 11
69 6d 67 25 30 35 64 2e
74 69 66                            "img%05d.tif"

00 00 00 00                         attribute count = 0
```

The TD length is exactly:

```text
4-byte TD header
+ 4-byte string dimension
+ 1-byte Pascal length
+ 13-byte label
= 22 bytes
```

There is therefore no TD padding here: `1 + 13 = 14`, already even. NI specifies that a name is a Pascal string and increases the TD size by its Pascal-string length rounded to an even number of bytes. [Type Descriptors](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/Type_Descriptors.html)

The string data itself is correctly `I32 length + bytes`, with no element count beyond that length. [NI Flattened Data, ?쏶trings and Paths??(https://www.ni.com/docs/en-US/bundle/labview/page/flattened-data.html)

One caution: treating `0x26008000` as ?쏿 LabVIEW 2026 version field??is supported by your direct LabVIEW-2026 observation, but NI warns that variant representation can change by release. The parser should accept or explicitly whitelist observed versions, not infer a permanently stable subfield interpretation from this one value. [NI flattened-variant article](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGQrCAO&l=en-US)

2. The two I16 values and the DBL case

Yes:

```text
00 01  = nTypesUsed
00 00  = first zero-based TD index
```

They are not part of the string TD. A TD consumes exactly the number of bytes declared by its initial I16 length; here that boundary occurs immediately after the final `67`. NI describes both fields as variable-width integers: values below 32768 occupy 16 bits, while larger values use a four-byte representation with the high bit set. [Type Descriptors](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/Type_Descriptors.html)

For an unnamed scalar DBL, expect:

```text
00 00 00 01        nTDs
00 04 00 0a        TD: size 4, DBL
00 01              nTypesUsed
00 00              index 0
<8-byte DBL>
00 00 00 00        zero attributes
```

For a named DBL:

```text
00 nn 40 0a <Pascal label> [even padding if required]
```

The `0x40` high-byte convention is demonstrated by NI?셲 named-enum example, while NI also cautions that the entire high byte is reserved/internal and should be ignored when comparing type identity. Thus, parse the base type as the low byte, but do not generalize every high-byte bit as a permanently documented flag. [Type Descriptors](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/Type_Descriptors.html)

Whether `Constant.Value` supplies a name for a particular numeric constant is an empirical property of that returned variant. Your string result strongly suggests the object label is included, but the parser must support both named and unnamed DBL TDs.

There is no scalar element-count I32. A DBL body is exactly eight big-endian bytes. Counts precede variable-size strings and each array dimension, not scalar numerics. [NI Flattened Data](https://www.ni.com/docs/en-US/bundle/labview/page/flattened-data.html)

3. Numeric TD table

Your table is correct:

| Code | Type | Flattened bytes |
|---:|---|---:|
| `01` | I8 | 1 |
| `02` | I16 | 2 |
| `03` | I32 | 4 |
| `04` | I64 | 8 |
| `05` | U8 | 1 |
| `06` | U16 | 2 |
| `07` | U32 | 4 |
| `08` | U64 | 8 |
| `09` | SGL | 4 |
| `0A` | DBL | 8 |
| `0B` | EXT | 16 |

The official flattened-data documentation explicitly says flattened numerics are big-endian, shows an eight-byte DBL example, and specifies that EXT is always stored as a 16-byte, 128-bit extended-precision quantity. That normalized flattened representation applies across platforms, including LabVIEW 2026 on x64 Windows; it is not the host compiler?셲 native `long double` layout. [NI Flattened Data](https://www.ni.com/docs/en-US/bundle/labview/page/flattened-data.html)

The numeric TD-code list is documented here: [Type Descriptors](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/Type_Descriptors.html).

4. How a wrong DBL framing can pass your gates

Yes, `finite + exact consumption + attrs==0` is insufficient. Eight arbitrary bytes frequently decode as a finite IEEE-754 number. A two- or four-byte displacement can therefore produce a plausible-looking finite value, particularly when adjacent framing bytes are mostly zero.

Add these gates:

- Require every TD to end exactly at its declared length.
- Require `nTypesUsed >= 1`, every index `< nTDs`, and resolve the value type through `TypesUsed[0]`.
- Require the resolved TD?셲 low-byte code to equal the expected type.
- Derive body length exclusively from that TD: exactly 8 for DBL.
- Require the attribute-count field to begin exactly at `data_start + 8`, not merely that some trailing four bytes decode as zero.
- Compare the decoded value against an independent LabVIEW-side value representation, not just `finite`.
- Validate with several deliberately chosen sentinels whose big-endian bytes are recognizable, for example `0.25` ??`3f d0 00 00 00 00 00 00`, which NI publishes directly. [NI Flattened Data](https://www.ni.com/docs/en-US/bundle/labview/page/flattened-data.html)
- Include at least `+0`, `-0`, a non-integer finite value, and a large-normal value. Comparing raw expected bytes catches endian and offset mistakes that ordinary numeric equality?봢specially for signed zero?봠an miss.
- Best gate: take the body slice selected by the parser, unflatten it explicitly as DBL in LabVIEW, and require equality with `Variant To Data(DBL)` from the original variant. This tests the parser-selected boundary independently of Python?셲 IEEE decoding. NI states that `Unflatten From String` requires a wired type to decode otherwise untyped flattened data. [NI Flattened Data](https://www.ni.com/docs/en-US/bundle/labview/page/flattened-data.html)

Bottom line: hypothesis A failed because it omitted the documented `nTypesUsed/TypesUsed` save-buffer suffix. Your replacement framing matches the documentation and the 53-byte specimen, after correcting the nonexistent padding byte after the label.

## Sources

(extract from answer)

## What was done with it

Framing accepted as documented (`version · nTDs · TDs · nTypesUsed · TypesUsed[] · value · attrs`); the padding
byte in my annotation was a mis-segmentation (the parser itself walks TDs by their declared length, so it was
never affected). The parser resolves the value type through `TypesUsed[0]`, takes the base type from the low byte,
derives the body length only from that TD, requires exact consumption and attrs == 0, and whitelists the observed
version. Limitation recorded honestly: the numeric decode is validated against the documented layout and the
53-byte string specimen, NOT yet against an independent LabVIEW-side value (Variant To Data / sentinel constants);
the reseed constants read next (10850/10312/9806/10142) will be sanity-checked against their documented roles, and
an independent sentinel check stays on the list. Rerun: `tools/bench/build_opconstvalue_v1c.log` (`--test-only`).
