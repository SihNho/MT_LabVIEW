---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, producer-consumer]
---

# queue-fail2-errno22-copy-after-load

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (65s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS (Windows 10, Python 3.10, LabVIEW 2026 over ActiveX). Follow-up to archive/peer/2026-09-15-queue-fail1-errno22-move-target-loaded.md: your instrumentation request was applied. Log tools/bench/build_track_v6_queue.log run 2: LabVIEW was killed and restarted fresh; gscript.copy_by_index then did close_panel(MOVE_SRC) and close_panel(MOVE_DST) FIRST (each = GetVIReference(path) over ActiveX, which LOADS the VI into the fresh instance), then restore_move_fixtures() (copy ORIG.bak -> MOVE_DST: succeeded), then the FIRST labelled copy "donor -> MOVE_SRC" raised: OSError errno=22 winerror=None, src=the donor (15849 B, exists), dst=...\Test - Moving Objects Source.vi (4656 B, exists). In run 1 the failing copy was target -> MOVE_DST (after the same close_panel had loaded MOVE_DST). At 00:3x the identical routine succeeded once (StrToPath.vi) - order then: close_panel (loads), restore, copies - same order, so timing must have differed.
HYPOTHESIS H1: LabVIEW keeps a loaded VI's file memory-mapped (or open with a share mode that forbids write-open); Python's open(dst,'wb') fails at the CRT level, which maps ERROR_USER_MAPPED_FILE (1224) / an unknown Win32 error to EINVAL = errno 22 with winerror None (CRT _wopen path, not a WinAPI OSError). H2: an unrelated cause (path/attributes) - but the same paths work when LabVIEW is not running/has not loaded them.
PLANNED FIX (also the discriminating experiment): reorder copy_by_index so that ALL byte substitutions (restore, donor -> MOVE_SRC, target -> MOVE_DST) happen BEFORE any COM call names those files (on a fresh instance nothing is loaded), and only then revert()/open them. If the copies succeed in that order every time and fail after a load, H1 stands.
Attack: (1) Does the Windows CRT map ERROR_USER_MAPPED_FILE / ERROR_SHARING_VIOLATION to EINVAL (errno 22) for _wopen/CreateFile failures - cite the CRT errno mapping (e.g. _dosmaperr table) - and would Python's open() then report winerror None? (2) Is there evidence LabVIEW memory-maps or holds VI files open while loaded (NI docs, forum reports of "cannot overwrite a VI that is in memory")? (3) Is the reorder sufficient, and should copy_by_index additionally verify with a write-open probe (open(path,'r+b')) before each copy and, on failure, state "file held - restart" instead of retrying? (4) any risk in reverting a VI that was byte-substituted BEFORE it was ever loaded (none expected - revert on an unloaded VI = load)? Read-only; cite what you read.


## Answer

H1 is plausible in broad form?봍abVIEW?셲 loaded VI prevents truncation?봟ut the specific attribution is not established. The evidence actually weakens the `ERROR_SHARING_VIOLATION ??EINVAL` branch.

1. CRT/Python translation

- Modern CRT mappings associate `ERROR_SHARING_VIOLATION` (32) with `EACCES`, not `EINVAL`. A reproduced `_dosmaperr` table shows that mapping explicitly. [CRT-derived mapping table](https://tangled.org/huwcampbell.com/reactos/commit/de7e7074592e1e8d119f1f5b8907c532037bf4ac)
- Older CRTs apparently once omitted code 32 and fell through to `EINVAL`, but that report dates from 2005; it is not persuasive evidence about Python 3.10?셲 UCRT. [PostgreSQL investigation](https://www.postgresql.org/message-id/db4hlo%24sm4%241%40news.hub.org)
- `ERROR_USER_MAPPED_FILE` (1224) is not present in the reproduced normal mapping table, so an unmapped-error fallback to `EINVAL` remains credible. However, I did not find an authoritative current-UCRT source explicitly showing 1224?셲 result.
- Python?셲 Windows `open()` calls `_wopen()`, then constructs the exception with `PyErr_SetFromErrnoWithFilenameObject`, i.e. from CRT `errno`, not from `GetLastError()`. [CPython `_io/fileio.c`](https://github.com/python/cpython/blob/main/Modules/_io/fileio.c)
- Therefore `winerror is None` is expected on this path: Python documents that `winerror` is only populated when a native Windows error is supplied to the exception constructor. [CPython `OSError` documentation](https://github.com/python/cpython/blob/main/Doc/library/exceptions.rst?plain=1)

Verdict: errno 22/no `winerror` is compatible with an unmapped Windows error such as 1224, but is inconsistent with the ordinary current mapping of sharing violation 32, which should normally become errno 13.

2. What the LabVIEW evidence proves

NI clearly documents that a VI can remain in memory while its on-disk file changes, and warns that loading the panel afterward can combine inconsistent in-memory and on-disk portions and corrupt the VI. [NI: ?쏺I Has Changed on Disk??(https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kEssSAE&l=en-US)

NI also says opening a VI reference allocates memory for the referenced VI and that closing references allows LabVIEW to dispose of it from memory. [NI: Closing References](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)

That supports:

- `GetVIReference(path)` loads or retains the VI in memory.
- External replacement while it remains loaded is unsafe.
- Closing the front panel is not necessarily equivalent to unloading the VI or releasing every reference.

It does **not** establish that LabVIEW memory-maps the `.vi`, nor that it keeps a non-share-write file handle open. NI?셲 own changed-on-disk warning demonstrates that at least some external modifications can succeed while a VI is loaded. Thus ?쐋oaded VI prevents overwrite??is probably conditional on LabVIEW state, resource loading, references, antivirus, or timing?봭ot a universal LabVIEW invariant.

3. Reorder and probe

The reorder is the correct operational fix:

1. Start a fresh LabVIEW instance.
2. Perform every restore/substitution before *any* VI Server call can name either fixture.
3. Verify destination bytes/hash.
4. Only then obtain VI references and operate on them.

But the experiment distinguishes only:

> failure depends on something caused by loading the VI

It does not distinguish memory mapping from an incompatible open handle, lingering reference, scanner interaction, or another load-triggered filesystem action. Microsoft documents that incompatible handle sharing causes `CreateFile` to fail with `ERROR_SHARING_VIOLATION`. [Microsoft `CreateFile`](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea)

Do not use `open(path, 'r+b')` as the principal probe:

- It does not truncate the file, whereas `open(..., 'wb')` does.
- A mapped file may permit opening and ordinary writes yet reject shrinking/truncation. CPython?셲 mmap investigation specifically records `SetEndOfFile` failing with `ERROR_USER_MAPPED_FILE` when section references remain. [CPython issue evidence](https://bugs.python.org/msg371050)
- It is also a TOCTOU check; success does not guarantee the following copy succeeds.

Better: let the real copy attempt be the probe, catch the exception once, record `errno`, `winerror`, message, paths, sizes and timestamps, and abort without retrying or making further COM calls. ?쏡estination unavailable after VI load; restart required??is justified. ?쏤ile memory-mapped??is not yet justified.

For a conclusive diagnostic, instrument a native Windows open/truncate path that captures `GetLastError()` immediately. Code 32 supports incompatible sharing; code 1224 supports a mapped-section/truncation conflict. Python?셲 ordinary `open()` has already discarded that distinction.

4. Revert after pre-load substitution

There is no expected filesystem-lock risk from substituting bytes before the first reference. NI explicitly recommends creating an unopened disk copy to avoid loading/cross-linking it in memory. [NI recommendations](https://www.ni.com/en/support/documentation/supplemental/07/recommendations-when-using-multiple-versions-of-labview-and-labv.html)

But ?쐒evert on an unloaded VI = load??is misleading. Obtaining the reference first loads the already-substituted disk image; at that point it is the version LabVIEW last loaded. A subsequent revert is likely redundant, not a mechanism for discovering newer bytes. More importantly, it cannot restore the pre-substitution file, because LabVIEW never loaded those old bytes in that fresh instance.

Bottom line: adopt the reorder, but phrase the finding as ?쐍aming/loading the fixture makes later truncating replacement fail.??Do not promote it to ?쏬abVIEW memory-maps VI files??until native instrumentation captures `GetLastError() == 1224`.

## Sources

(extract from answer)

## What was done with it

Adopted: `gscript.copy_by_index` performs every restore/substitution as pure file operations BEFORE any VI Server
call can name the fixtures (the `close_panel` pre-step is gone; `restore_move_fixtures` no longer reverts), and
only then reverts/opens them; the recipe starts each copy session on a fresh instance. The mechanism is recorded
as "load-dependent" (errno 22 / winerror None = an unmapped Windows error surfaced through the CRT, consistent
with a truncation refused on a mapped file, NOT a sharing violation), not as a proven memory-map. No `r+b` probe
(TOCTOU, and it would not exercise truncation). Rerun: `tools/bench/build_track_v6_queue.log` (run 3).
