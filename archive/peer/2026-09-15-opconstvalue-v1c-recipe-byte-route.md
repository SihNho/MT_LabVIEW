---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opconstvalue-v1c-recipe-byte-route

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (99s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRE-BUILD REVIEW (read-only; LabVIEW 2026 VI Scripting over COM, python win32com, Korean Windows cp949). Attack tools/recipes/build_opconstvalue_v1c.py before it runs. It implements the byte route you recommended in archive/peer/2026-09-15-opconstvalue-v1b-bstr-codepage.md, with these MEASURED facts (tools/bench/census_hexstring_vi.log, census_unflatten_terms.log): (a) the Erdos Miller creator library has NO 'String To Byte Array' creator; (b) the stock vi.lib\Bit Manipulation\Bytes to Lowercase Hex String.vi has terminals `bytes` (sink; a string wire attaches but breaks the VI -> U8[]) and `hex string` (source); (c) the fleet's Unflatten From String creator node exposes `binary string`, `type`, `data includes array or string size? (T)`, `byte order (0:big-endian, network order)`, `error in (no error)` -> `value`, `rest of the binary string`, `error out`.
Design: Flatten.data string --branch--> Unflatten.binary string; Unflatten.type <- a U8[] CONTROL obtained by Terminal.Create Control on the hex VI's `bytes` input and then cutting that wire (the fleet's proven 'typed control from a subVI terminal' trick); a Boolean control on `data includes array or string size?` that Python sets FALSE before every run (so the whole string becomes the U8 array = String To Byte Array); Unflatten.value -> hex VI.bytes; indicators on hex VI.`hex string` (ASCII) and Unflatten.`value` (U8[] -> SAFEARRAY VT_UI1 -> tuple of ints); the test requires the two readbacks to be byte-identical, the documented StringConstant[7] bytes to contain 'img%05d.tif', and 6 numeric constants to decode from numeric TDs with exact consumption; per-read identity (UID / Class Name 2 vs the reporter), poisoned indicators, MAIN md5+mtime gates.
Attack: (1) Unflatten From String with type = 1-D U8 array and `data includes array or string size?` = FALSE: does it consume the ENTIRE binary string as bytes (cite NI's function doc), or only up to some limit / leave a remainder in `rest of the binary string`? Is a control (not a constant) legal on the `type` input? Any coercion dot or byte-order effect on U8 (byte order should be irrelevant for 1-byte elements - confirm)? (2) A Boolean CONTROL on `data includes array or string size?` set via SetControlValue(False) before each run - any reason the value would not be read on that run (e.g. the op is non-reentrant and runs via Run VI with defaults)? Safer alternative that is still scriptable: Terminal.Create Constant on that input plus Constant.Value write 634AC00 - is writing a Boolean constant's Value by script documented? (3) `hex string` from Bytes to Lowercase Hex String.vi: is it exactly 2 lowercase hex chars per byte with no separators/prefix (so bytes.fromhex is exact)? cite the vi.lib VI's doc if you can find it; if not, say unknown - the test's hex==u8 equality is the measurement. (4) The U8[] indicator over GetControlValue: any pywin32 pitfall (tuple of ints vs bytes vs memoryview; empty array -> None)? (5) Anything that could let a WRONG object be read while passing the identity + equality gates? (6) Any step that risks the original main VI (it is only opened by reference inside the op; never saved). Cite what you read.


## Answer

Verdict: **do not run unchanged**. The byte route itself is supported by NI, but the recipe needs several acceptance-test hardenings. No repository files were modified or executed.

1. Unflatten behavior

The proposed conversion is valid. NI explicitly says that when `data includes array or string size?` is FALSE, LabVIEW derives the top-level array size from the memory size of `binary string`. For U8 elements, every input byte is one complete element, so the expected remainder is empty. NI also says `rest of the binary string` contains bytes not converted when the input length is not a multiple of the element size. [NI: Unflatten From String](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/unflatten-from-string.html)

A normal U8-array control is legal on `type`: NI describes `type` as a ?쐍ormally constructed LabVIEW type,??not a special type descriptor. Its runtime contents do not specify the array length in this mode; the wire?셲 datatype specializes the output. [NI: Unflatten From String](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/unflatten-from-string.html)

Byte order cannot change individual U8 elements because endian selection only changes byte ordering within multibyte representations. That conclusion follows from NI?셲 endian definition; it is not stated as a U8-specific sentence. [NI: Unflatten From String](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/unflatten-from-string.html)

However, add an indicator on `rest of the binary string` and require `rest == ""` on every read. Presently both hex and U8 outputs originate from the same Unflatten output, so their equality cannot detect a shared truncation. They are independent COM encodings, not independent extraction paths.

2. Runtime Boolean control

Setting the Boolean immediately before synchronous `Run` is a sound design. NI?셲 documented VI Server sequence is set control values first, then invoke Run; non-reentrancy does not cause Run to restore defaults. [NI: Passing Data Using VI Server](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019MoeSAE)

Still, verify the write:

```python
vi.SetControlValue(labels["size"], False)
must("size control readback is False",
     vi.GetControlValue(labels["size"]) is False)
```

This matters because weakly typed COM writes can fail through type mismatch, and NI requires the control name and datatype to match. [NI: Passing Data Using VI Server](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019MoeSAE)

A scripted constant would be structurally safer after construction, but I found no NI documentation establishing that scripting property `634AC00` writes a Boolean constant?셲 value. NI only documents creating a typed constant and editing its value interactively. Therefore, do not replace the measured control route with an unmeasured `Constant.Value` write before this build. [NI: Creating and Editing User-Defined Constants](https://www.ni.com/docs/en-GB/bundle/labview/page/creating-and-editing-user-defined-constants.html)

3. Lowercase hex output

Unknown from public NI documentation. I could not find a public connector/help page for `Bytes to Lowercase Hex String.vi` establishing exactly two lowercase digits per byte with no decoration.

The test should explicitly require:

```python
len(hx) == 2 * len(b_u8)
and hx == hx.lower()
and all(c in "0123456789abcdef" for c in hx)
and bytes.fromhex(hx) == b_u8
```

The current equality proves decodability and equivalence but does not establish lowercase; `bytes.fromhex` accepts uppercase and whitespace.

4. SAFEARRAY/pywin32

Do not assume a tuple. Current pywin32 deliberately maps `SAFEARRAY(VT_UI1)` to a buffer-like Python value for performance; its changelog warns that code expecting a tuple of integers can break. [pywin32 changelog](https://github.com/mhammond/pywin32/blob/main/CHANGES.md#notable-changes-in-this-transition)

The current iterable conversion happens to accept `bytes`, `bytearray`, `memoryview`, and tuples, but it has two weaknesses:

- A non-iterable unexpected value raises during `all(...)`.
- An empty valid result becomes false in `if b_u8`, although the selected fixtures are nonempty.

Use a guarded normalization:

```python
def normalize_u8(v):
    if v is None or isinstance(v, str):
        return None
    try:
        return bytes(v)
    except (TypeError, ValueError):
        try:
            return bytes(int(x) for x in v)
        except (TypeError, ValueError, OverflowError):
            return None
```

I found no authoritative promise that LabVIEW returns an empty U8 array as `None`; treat its exact empty representation as unknown and measure it separately.

5. Wrong-object false positives

The UID plus class comparison is strong provided UIDs are unique within this VI, but I found no external NI page guaranteeing that property?셲 uniqueness or lifetime.

Add these cheap gates:

- Restore the v1b `# of Refs == len(manifest)` check for each class.
- Require `0 <= i < len(manifest)` before running.
- Require the returned reporter index, if available, to equal `i`.
- Poison and verify `# of Refs`, UID, class, hex, U8, value, data, and the new remainder.
- Verify the size-control readback before each Run.
- Add a deliberately invalid/out-of-range index test and require an error or unmistakably poisoned outputs.

The two byte outputs do not protect object identity because both are derived from the same selected reference.

Correction to my interim observation: `decode_flat` does enforce exact numeric-body consumption, zero attributes, and finite floats internally. The final `val is not None` gate therefore inherits those checks. The wording is accurate.

6. Risk to the original main VI

The constructed `Constant.Value` node is a read property: the recipe verifies that `Value` is a source terminal. Thus the intended dataflow only reads the selected constant.

The disk MD5/mtime gate is useful but insufficient by itself:

- It runs only after every test succeeds. An exception before the last line skips the audit.
- It detects saving, not an unsaved in-memory dirty original.
- The code does not explicitly close the main-VI reference obtained inside the op.

Put the MD5/mtime audit in `finally`, and ideally also report the original VI?셲 modification/dirty state before and after if the reporter exposes it. NI recommends closing VI references to avoid unexpected behavior. [NI: Passing Data Using VI Server](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019MoeSAE)

Required pre-run changes:

- Add and assert an empty remainder indicator.
- Read back `size == False` before every Run.
- Accept buffer-style U8 results.
- Assert lowercase/no-whitespace/exact hex length.
- Restore `# of Refs` and range gates.
- Move the main-file integrity audit into `finally`.

With those changes, I see no documentation-based objection to the byte route itself.

## Sources

(extract from answer)

## What was done with it

All six required changes applied before the build: indicator on `rest of the binary string` gated `== ""` on every
read; the size control is read back `False` before every run; U8 results normalised buffer-first
(`bytes(v)`, then int-iteration) — never assumed a tuple; hex gated strict (2 × len, lowercase, hex alphabet, and
`fromhex == u8`); `# of Refs == len(manifest)` and index-range gates restored; the MAIN md5/mtime audit moved into a
`finally`; plus the suggested negative control (out-of-range index must error or leave poisoned outputs). The
Constant.Value WRITE route for the Boolean was not adopted (unmeasured), as advised. Log:
`tools/bench/build_opconstvalue_v1c.log`.
