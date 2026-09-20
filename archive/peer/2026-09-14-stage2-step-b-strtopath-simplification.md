---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, stage2]
---

# stage2-step-b-strtopath-simplification

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (61s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

SHORT ATTACK on a simplification you caused (LabVIEW 2026 VI Scripting over COM, zero GUI). Read docs/stage2-assembly-step-b.md "REVISED route" (updated) and your review archive/peer/2026-09-14-stage2-step-b-revised-forloop-route.md.
Because no small donor has a one-argument Format Into String (census tools/bench/census_fis_donors.log: 5 and 6 arguments), the plan now drops Format Into String entirely: Python precomputes each frame's FULL path as a string; a 1-D STRING-array control 'Frame Paths' is auto-indexed into the For loop (sets N); each element goes through a one-node sub-VI StrToPath.vi (String To Path primitive copied from save N xyz traces.vi n7, control on 'string', indicator on 'path', connector pane) into IMAQ ReadFile 'File Path'. The string-array control is made by Terminal.Create Control on erdosmiller Get Controls.vi's 'Control Names' terminal (known to yield a String[] control), then deleting that wire and the helper node.
Attack: (1) String To Path with absolute Windows paths containing spaces, and with a UNC path: exact round trip? Any LabVIEW 2026 UTF-8/localisation pitfall for Korean characters in a path (the fixture is under G:\Data\SiHyeong\20260906 Kimlab - 50bp 16X WT 90Hz 1p2 Ramp_Newbatch\test)? (2) SetControlValue of a 10,043-element string array over ActiveX: any documented limit or known slowness? (3) A For loop auto-indexing a String[] input: N = array length - confirm, and confirm an EMPTY array yields zero iterations (so the registers' final values equal the initial controls). (4) After 'create control then delete its wire, then delete the Get Controls node', is the control guaranteed to remain a String 1-D array control (type is fixed at creation, not re-inferred)? (5) Anything cheaper or safer? Name the single cheapest discriminating test. Read-only; cite what you read.


## Answer

Verdict: sound, with one caveat?봌orean characters are not guaranteed safe merely because Python/COM uses Unicode.

1. `String To Path`

- Ordinary absolute paths and spaces should round-trip unchanged.
- Standard UNC `\\server\share\file` is supported. Do **not** use extended Windows paths such as `\\?\UNC\...`; LabVIEW can misinterpret them. [NI Community explanation](https://forums.ni.com/t5/LabVIEW/File-Dialog-fails-to-show-if-start-path-is-a-UNC-path/m-p/3908929)
- LabVIEW 2026 on Windows does **not** use UTF-8. It converts strings according to the OS locale/code page; Korean is safe only when representable under the machine?셲 configured Korean encoding. [NI: Porting VIs among Platforms](https://www.ni.com/docs/ar-SD/csh?context=lvcore_lvconcepts_porting_among_platforms)
- The stated fixture path is entirely ASCII??SiHyeong`, `Kimlab`, spaces?봲o this specific fixture avoids the Korean-character risk.

?쏣xact round trip??should mean String ??Path ??String equality. It does not prove the subsequent file API can open an inaccessible UNC target.

2. 10,043 strings through `SetControlValue`

I found no documented element-count or string-array size limit specific to `Ctrl Val.Set`. NI only requires the control name and datatype to match, otherwise the call fails with an invalid-parameter error. [NI VI Server guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019MoeSAE)

Therefore: no reason to redesign, but latency is unproven. Time the actual 10,043-element call and read back `Array Size`; do not infer success merely from a successful COM return.

3. For-loop semantics

Confirmed:

- One auto-indexed `String[]` input sets the iteration count to its array length and supplies one string per iteration. [NI auto-indexing rules](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG)
- An empty input array produces zero iterations. [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999e.pdf)
- Initialized shift registers then return their initializer unchanged, which is precisely why NI recommends shift registers when a For loop may execute zero times. [NI zero-iteration guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kJNfSAM)
- The auto-indexed `XYZ` output will be an empty 2-D array, independently of the preserved register outputs.

4. Create-control, delete-wire, delete-helper

The datatype is fixed when `Terminal.Create Control` creates the independent control; deleting its wire should not trigger type inference. However, I found no NI guarantee covering this exact scripting/deletion sequence. Keep the proposed gate: same UID survives, control class is Array, rank is 1, element type is String, and terminal has zero wires. The local plan already specifies this correctly: [stage2-assembly-step-b.md](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/stage2-assembly-step-b.md).

5. Cheapest discriminating test

Run only `StrToPath.vi` through the **same Python COM path**, with one `Frame Paths` array containing:

- the real fixture path with spaces,
- `\\server\share\a b.tif`,
- `G:\?뚯뒪???대?吏.tif`.

Return each value through `Path To String` and demand byte-for-byte equality. Then call once with `[]` and verify zero iterations plus unchanged initialized-register outputs. This single tiny harness discriminates COM string marshalling, locale/Korean handling, UNC parsing, auto-indexing, and zero-iteration behavior without image I/O or the kernel.

The simplification is substantially safer than the archived formatter route; its only material unresolved risk is Windows code-page conversion, not `String To Path` itself.

## Sources

(extract from answer)

## What was done with it

Adopted as-is: the route was built (`tools/recipes/cycle3_toolkit.py`, log `tools/bench/cycle3_toolkit.log`).
Caveats carried into the recipes: the 10,043-element `SetControlValue` is TIMED and read back by size (never
inferred from a COM return), the `Frame Paths` control gate (UID survives, rank 1, String, terminal unwired) stays,
and the Korean-code-page risk is noted as not applying to this ASCII fixture path but recorded for any future
fixture (NAMES.md). The zero-iteration behaviour (initialised registers return their initialisers, `XYZ` empty)
is used as a cheap sanity check in the assembly test.
