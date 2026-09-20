---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opconstvalue-v1b-recipe-flatten

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (62s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRE-BUILD REVIEW (read-only; LabVIEW 2026 VI Scripting over COM). Attack tools/recipes/build_opconstvalue_v1b.py before it runs. It applies your recommendation from archive/peer/2026-09-15-opconstvalue-run6-numeric-reads-none.md: on the saved OpConstValue_v1.vi it adds a Flatten To String (via the proven creator OpBuildFlatten_v0, class FlattenString; docs/NAMES.md: inputs `anything`, outputs `data string`, `type string (7.x only)`), branches PN Constant.Value -> Flatten.anything, creates indicators on both outputs, gates ExecState 1, saves once, then TESTS on the main VI: StringConstant[7] must decode from the flattened variant (TD 0x30) to 'img%05d.tif' and DigitalNumericConstant[0..5] must decode from numeric TDs (0x01-0x0B). decode_flat() parses: version I32, #TDs I32, TDs (I16 length, I16 code), data, trailing attribute-count I32.
Deviation from your answer: Flatten To String on a VARIANT input (not 'Variant To Flattened String') - I rely on NI's statement that flattening a variant yields the LabVIEW-version + type descriptors + data blob (the same content VTFS splits). Attack points: (1) is that true, or does Flatten To String on a variant input flatten only the *variant type* (TD 0x53) with the payload nested differently - which would make my parser read the wrong TD and fail the numeric gate for a parser reason, not a marshalling reason? (2) The `data string` reaches Python as a BSTR via GetControlValue - I did NOT hex-encode (no String-To-Byte-Array step); embedded NUL bytes (DBL 0.0, I32 small values) - are they preserved by LabVIEW's ActiveX string marshalling, or truncated? If truncated, the discriminating symptom is data length < expected; cite. (3) The recipe wires by name 'Value' -> 'anything' with branch=True on an already-wired source and gates by wire-uid equality on both ends - any reason a branch onto a Variant terminal would be declined silently? (4) The gate '>=3 of 6 numerics decode and not all identical' - could it pass with a wrong-class read? (5) Anything that would put the original main VI at risk (it is opened read-only through Open VI Reference in the op; never saved). Cite what you read.


## Answer

Verdict: do not run this recipe unchanged. The overall approach is sound, but `decode_flat()` is not yet justified by NI?셲 documented flattened-variant layout, and its current bounds handling can misdiagnose malformed or truncated data as a marshalling failure.

1. Flattening the variant

Your deviation is valid: `Flatten To String` on a LabVIEW variant does not merely emit TD `0x53` followed by an opaque nested payload. NI explicitly says it flattens ?쐔he variant and all its contents, including attributes,??while `Variant To Flattened String` extracts only the contained value and discards attributes. [NI: Handling Variant Data](https://www.ni.com/docs/ar-IQ/bundle/labview/page/handling-variant-data.html), [NI: Differences Between Flatten to String and Variant To Flattened String](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019RPPSA2&l=en-US)

Therefore the `data string` should contain:

- LabVIEW version
- contained-value type descriptor
- contained value
- attribute count
- attributes, if any

NI?셲 current description says exactly that and specifies big-endian integers. [NI: Understanding Flattened Variant Data Format](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGQrCAO&l=en-US)

The problem is the parser?셲 assumed framing:

```python
ver, ntd = struct.unpack(">ii", b[:8])
```

NI describes the second component as ?쏿 type descriptor,??not an I32 count of descriptors. Older detailed descriptions show individual TDs beginning with an I16 byte length and I16 type code, plus a compact ?쐔ypes used??list whose count is not necessarily an I32 in that location. [Unofficial LabVIEW type-descriptor documentation](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/Type_Descriptors.html), [NI Community annotated flattened-variant format](https://forums.ni.com/t5/LabVIEW/Format-of-the-variant-in-binary-file/td-p/2114958/page/2)

So attack point 1 resolves as:

- `Flatten To String` is the correct primitive.
- The expected outer TD is the contained type, not merely `0x53`.
- But the exact `version + I32 #TDs + repeated TDs` parser is insufficiently supported and may be wrong for LabVIEW 2026.

Cheap pre-build fix: validate `decode_flat()` against one known flattened string and one known numeric produced by an isolated scratch fixture, or use `Variant To Flattened String` if the creator is available. That function exists specifically to return the contained value?셲 `data string` and `type string`, avoiding manual parsing of the variant wrapper. [NI: Flattened String To Variant](https://www.ni.com/docs/gd-GB/bundle/labview-api-ref/page/functions/flattened-string-to-variant.html)

At minimum, harden the parser before interpreting failures:

- Treat version as unsigned `>I`.
- Bounds-check before every TD header and `p += ln`.
- Reject `ln < 4`, odd lengths, excessive descriptor counts, and `p > len(b)-4`.
- Verify the final attribute count is actually zero; `b[p:-4]` is valid only in that case.
- Require the decoded data length to match the TD exactly.
- Log `repr(d)`, `len(d)`, and the complete initial bytes when parsing fails.

2. Embedded NULs over ActiveX

A BSTR can preserve embedded NUL characters: its length is stored separately, and Microsoft explicitly notes that `SysStringLen` can differ from `strlen` when a BSTR contains embedded NULs. [Microsoft: SysStringLen](https://learn.microsoft.com/en-us/windows/win32/api/oleauto/nf-oleauto-sysstringlen)

NI maps an ActiveX `BSTR` to a LabVIEW string. [NI: Using ActiveX with LabVIEW](https://www.ni.com/docs/ar-SD/csh?context=lvcore_lvconcepts_using_activex_with_labview)

Thus truncation is not inherent to either BSTR or LabVIEW?셲 documented type mapping. I found no NI source guaranteeing the complete LabVIEW-server ??pywin32 `GetControlValue` path for embedded NULs, however. The safe conclusion is: preservation is expected, but must be measured.

Your proposed symptom is correct: truncation at the first NUL produces `len(d)` shorter than the structural minimum or than the length implied by the TD. Add one decisive scratch test containing `b"A\x00B\x00C"` before trusting numeric results. Do not infer truncation merely from `decode_flat()` failing, because the parser framing is independently suspect.

3. Branch wiring

The gate is as strong as this fleet can make it:

```python
a and a == b == w_val
```

The project?셲 `.claude/skills/labview-automation/references/vi-scripting.md` and `docs/NAMES.md` record that illegal name-based connections may be declined silently and that branches do not add a new Wire object. Reading the same existing wire UID at the original source and the new `anything` sink is good evidence that the branch landed.

There is no type reason to reject it: `anything` is polymorphic and accepts variant data. NI documents `Flatten To String` as accepting arbitrary data. [NI archived Function Reference](https://download.ni.com/support/manuals/321526a.pdf)

One caveat: the recipe assumes `walk()` reports the same logical Wire UID for all branches. That has already been locally established for this toolkit, so I would not block on it.

4. The numeric acceptance gate is too weak

Yes, this could pass with a wrong-class read. The gate proves only that at least three returned blobs parse as numeric and contain at least two values. It does not prove that calls requested `DigitalNumericConstant[0..5]`, nor that each result belongs to the expected object.

Possible false-pass cases include:

- `Class Name` or `index` silently retaining a previous value.
- The op repeatedly selecting another set of diverse numeric objects.
- A parser offset accidentally landing on plausible numeric TD bytes.
- Stale front-panel outputs after a failed op run, especially because `_err(...) or ""` cannot distinguish every stale-output scenario.

Strengthen the gate by returning identity from the op?봞t least selected object UID and actual class name?봞nd assert both for every request. Also clear or poison all result indicators before each run and require them to change. Best of all, compare all six results with independently known values or a reporter-generated UID/class/value manifest rather than merely ?쐔hree diverse numbers.??
Also reject non-finite floats and implausible descriptor counts. A wrong offset can decode arbitrary eight bytes as a valid DBL.

5. Risk to the original main VI

The recipe does not explicitly save `MAIN`; its only `g.save()` targets `OP`, and all diagram mutation calls target `OP`. A `Value` property read and flattening occur in the op, so the intended path does not modify or execute the main VI.

Residual risks are operational rather than disk writes:

- Opening the main VI can load its dependency hierarchy.
- An incorrectly wired property node could perform a write only if its `Value` terminal direction were wrong; the recipe verifies it as a source before modification.
- A bug inside the pre-existing op could target or save the wrong VI, but this recipe itself contains no `save(MAIN)`.
- The main VI may remain loaded after repeated tests if the op does not close its reference. The skill explicitly warns that references must be closed; inspect the reporter output for a `Close Reference` chain before running.

I would add before/after `MAIN` checksum and modification-time gates. They do not prevent damage, but they make the ?쐎riginal unchanged??claim auditable. NI?셲 VI Server documentation distinguishes obtaining a reference from running the referenced VI; merely opening a VI reference does not execute its block diagram. [NI: Open VI Reference](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/open-vi-reference.html)

Bottom line: approve the node addition and wire-UID gate, but reject the current functional test until the flattened-variant framing is empirically established and object identity is included in the numeric gate.

## Sources

(extract from answer)

## What was done with it

Not run unchanged. Kept: Flatten To String (confirmed as flattening the variant's contents), the branch wire-uid gate.
Changed before the build: (1) `decode_flat` is labelled HYPOTHESIS A (U32 version, I32 #TDs, I16/I16 TDs), fully
bounds-checked, requires exact consumption and attribute count 0, rejects non-finite floats, and prints raw bytes on
every failure; it is validated empirically on the documented StringConstant[7] — with a framing-independent gate
(the literal bytes `img%05d.tif` inside the blob) separating a parser error from a marshalling error — before any
numeric result is trusted. (2) NUL survival is measured: every numeric blob must be structurally complete (≥ 12 B)
rather than inferred from a decode failure. (3) Identity per read: the op inherited OpReport_v3's `UID` / `Class
Name 2` / `# of Refs` outputs, so every read asserts the reporter's uid and class for that index, and all result
indicators are poisoned before each run. (4) MAIN md5 + mtime gated before/after the reads. Log:
`tools/bench/build_opconstvalue_v1b.log`.
