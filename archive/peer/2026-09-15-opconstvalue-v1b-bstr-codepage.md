---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opconstvalue-v1b-bstr-codepage

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (83s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS (LabVIEW 2026 ActiveX server, python win32com, Korean Windows 10 - system ANSI code page 949). Recipe tools/recipes/build_opconstvalue_v1b.py, log tools/bench/build_opconstvalue_v1b.log: the build PASSED (Flatten To String on the Constant.Value variant, indicators 'data string' / 'type string (7.x only)', ExecState 1, saved). The TEST then failed inside my parser: vi.GetControlValue('data string') returned a Python str in which characters at positions 12-15 are > U+00FF ('latin-1' can't encode), i.e. the flattened-variant bytes (version + TD + 'img%05d.tif' data) were converted by LabVIEW's ActiveX string marshalling through the ANSI code page (cp949 multi-byte) into a Unicode BSTR, not passed as raw 8-bit bytes. PREDICTION THAT FAILED (from your archive/peer/2026-09-15-opconstvalue-v1b-recipe-flatten.md 짠2 and mine): a LabVIEW string with arbitrary bytes crosses GetControlValue byte-preserving; only NUL truncation was considered.
Questions: (1) Is 'LabVIEW string -> BSTR = MultiByteToWideChar(CP_ACP)' the documented/known behaviour of LabVIEW's ActiveX server (cite)? If so, is str.encode('mbcs') in Python an EXACT inverse for all byte sequences, or lossy for byte pairs that are invalid in cp949 (lead byte without a valid trail byte, e.g. a DBL's 0x81 0x00) - which would make numeric blobs unrecoverable in general even if this one string case round-trips? (2) The lossless alternative: convert the string to a U8 array inside the op ('String To Byte Array' primitive) so GetControlValue returns a SAFEARRAY of bytes -> Python tuple of ints. Is the U8-array indicator path over ActiveX byte-exact (cite any NI doc/forum on array indicators via GetControlValue)? Is 'String To Byte Array' reachable by VI Scripting - its New VI Object style-ring name (do NOT guess; say if unknown) - or which NI example VI under LabVIEW 2026\examples contains one to copy from? (3) Alternatively 'Number To Hexadecimal String' after 'String To Byte Array' + 'Array To Spreadsheet String' to yield a pure-ASCII hex string - more nodes; any simpler pure-ASCII route (e.g. Flatten To String's own output cannot be made ASCII)? (4) For the immediate discriminator I intend: encode('mbcs', errors='strict') and gate on exact structural consumption of the blob for the string AND for the 6 numerics; a strict-encode failure or a length mismatch on any numeric = lossy = build the U8 route. Anything that would let a lossy path PASS that gate? Read-only; cite what you read.


## Answer

The failed prediction should be retired. A LabVIEW binary string is not a safe ActiveX transport on a DBCS machine.

1. BSTR conversion and reversibility

NI documents only the type mapping?봍abVIEW string ??ActiveX `BSTR`?봭ot the internal conversion routine or flags. I found no NI documentation proving that LabVIEW?셲 ActiveX server specifically calls `MultiByteToWideChar(CP_ACP, ??`. [NI?셲 ActiveX type-mapping table](https://www.ni.com/docs/ar-SD/csh?context=lvcore_lvconcepts_using_activex_with_labview)

There is strong corroborating NI Community evidence: an experienced contributor describes LabVIEW strings as 8-bit, system-code-page strings and says conversion to a `BSTR` requires `MultiByteToWideChar` before `SysAllocString`. That is credible implementation guidance, but not an official guarantee about `GetControlValue`. [NI Community discussion](https://forums.ni.com/t5/LabVIEW/initializing-an-outdated-dll-for-TCP-IP-connection/td-p/4021962)

Your observation?봘nicode characters above U+00FF exactly where binary bytes occur?봯roves that the path is not byte-preserving and is consistent with CP949 decoding. It does not by itself identify the precise Windows API or flags.

`str.encode("mbcs", errors="strict")` is not an inverse for all arbitrary byte sequences:

- Python defines `mbcs` as the current Windows ANSI code page, `CP_ACP`; `strict` detects characters that cannot be encoded. [Python codec documentation](https://docs.python.org/3.12/library/codecs.html)
- Microsoft explicitly classifies a DBCS lead byte without a valid trail byte as invalid. Without `MB_ERR_INVALID_CHARS`, Windows Vista and later replace invalid sequences with U+FFFD. [Microsoft `MultiByteToWideChar`](https://learn.microsoft.com/en-us/windows/win32/api/stringapiset/nf-stringapiset-multibytetowidechar)
- Thus `81 00` is not safely representable as ?쐀yte 0x81 followed by byte 0.??It can become replacement-plus-NUL, or encounter different behavior if the caller treats NUL as termination. Microsoft specifically warns that code-page conversion of random non-text binary data can fail. [Microsoft documentation](https://learn.microsoft.com/en-us/windows/win32/api/stringapiset/nf-stringapiset-multibytetowidechar)

Crucially, strict encoding happens after LabVIEW?셲 decode. It cannot detect every loss that already occurred.

2. U8 array route

Yes: this is the correct lossless design.

NI explicitly recommends converting binary-capable LabVIEW strings to U8 arrays where NUL values are possible. [NI knowledge article](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YILoCAO)

There is unusually direct evidence for the precise VI Server path: an NI Community example uses ActiveX VI Server to read a U8-array front-panel value and reports the returned variant as `VT_ARRAY | VT_UI1`. [ActiveX VI Server U8-array example](https://forums.ni.com/t5/LabVIEW/How-can-I-extract-data-from-an-OLE-variant/m-p/256157)

`VT_ARRAY | VT_UI1` is a SAFEARRAY whose elements are unsigned 8-bit values; it avoids all character-set conversion. The expected pywin32 result is therefore an integer sequence, commonly a tuple, which should be normalized with:

```python
blob = bytes(value)
```

Reject elements outside `0..255` and reject an unexpected returned type. The COM element type?봭ot merely seeing ?쐓ome iterable?앪봧s the important discriminator.

NI documents that String To Byte Array converts each string byte to a U8 element. [NI function reference](https://download.ni.com/support/manuals/321526a.pdf) NI also publishes exactly the pipeline you need: Flatten To String ??String To Byte Array. [NI knowledge article](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000004B2BSAU)

I could not find a defensible source for either:

- the `New VI Object` style-ring string for String To Byte Array; or
- a stock LabVIEW 2026 `examples` VI containing it.

Do not guess the style name. The public sources identify it as a function and place it in the Conversion / Path-Array-String Conversion palettes, but do not expose the scripting style identifier. [LabVIEW Wiki object entry](https://labviewwiki.org/wiki/String_To_Byte_Array_function) The exact identifier requires reporter output or a manager-run scripting query. The downloadable NI example ?쏶tring to U8 Numbers Function Comparison??is a known donor, but it is not evidence of a stock `LabVIEW 2026\examples` path. [NI example](https://forums.ni.com/t5/Example-Code/String-to-U8-Numbers-Function-Comparison-using-LabVIEW/ta-p/3528866)

3. Pure-ASCII alternative

Flatten To String itself cannot be made ASCII while retaining the same flattened representation: NI describes it as producing a binary string. [NI binary-flattening description](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kHquSAE)

The simplest native-looking ASCII route is probably:

```text
Flatten To String
    ??String To Byte Array
    ??Array To Spreadsheet String
         format: %02x
         delimiter: empty
```

LabVIEW?셲 formatting documentation confirms hexadecimal numeric formatting with `%x`, and that Array To Spreadsheet String applies one format specifier across the numeric array. [NI formatting reference](https://download.ni.com/support/manuals/320999e.pdf)

That is simpler than mapping Number To Hexadecimal String over the array and concatenating. Verify that an empty delimiter really produces no terminator in your selected node/version; otherwise strip the known final delimiter. Hex doubles payload size but is robust ASCII.

I would not assume a built-in Base64 primitive: NI?셲 current support article demonstrates Base64 using a third-party add-on, so it is not a safer dependency for this recipe. [NI Base64 article](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q0000019gOWCAY)

4. Attack on the proposed discriminator

Yes?봞 lossy path can pass your proposed gate.

Structural consumption proves only that the recovered bytes form a syntactically valid flattened object. It does not prove they are the original bytes. Failure modes that can pass include:

- A source sequence maps to another encodable character or default character; strict re-encoding succeeds.
- Corruption occurs inside payload data while length fields and type descriptors remain intact.
- A corrupted numeric bit pattern is still a perfectly valid numeric bit pattern?봢specially DBL, where essentially every 64-bit pattern is structurally consumable.
- Equal encoded length does not imply equal bytes.
- Even `decoded.encode("mbcs").decode("mbcs") == decoded` proves only stability of the already-converted Unicode string, not equality with the original LabVIEW bytes.

Microsoft warns that ACP conversions can cause irreversible corruption and that invalid sequences may be replaced. [Microsoft documentation](https://learn.microsoft.com/en-us/windows/win32/api/stringapiset/nf-stringapiset-multibytetowidechar)

Therefore:

- A strict-encode failure or structural/length failure conclusively rejects the string route.
- Passing those checks does not establish losslessness.
- Only comparison against independently known original bytes, or a checksum computed inside LabVIEW before ActiveX conversion, can validate the string route.
- Given that arbitrary numeric blobs must be supported, the U8 SAFEARRAY route should be the default fix, not merely the fallback after this gate.

## Sources

(extract from answer)

## What was done with it

Accepted: the `mbcs` re-encode + structural gate cannot prove losslessness (a corrupted DBL is still a valid DBL), so
it is demoted to a diagnostic and the U8 SAFEARRAY route becomes the fix: Flatten To String → String To Byte Array →
U8-array indicator, read as `VT_ARRAY|VT_UI1` → `bytes(tuple)` with element-range and type checks. The style-ring
identifier for String To Byte Array is not guessed — it is resolved from the fleet's own creator mechanism (how
OpBuildFlatten_v0 placed `FlattenString`) or by a scripted enumeration/negative search recorded in NAMES.md.
