---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, producer-consumer]
---

# queue-fail1-errno22-move-target-loaded

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (43s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS DIAGNOSIS briefly (Windows 10, Python 3.10 shutil, LabVIEW 2026 with VIs loaded over ActiveX). Log: tools/bench/build_track_v6_queue.log run 1: the recipe's first phase build_pathtostr() -> gscript.copy_by_index(donor, 'Function', i, target=PathToStr.vi, ...) raised "[Errno 22] Invalid argument: '...\NIScriptingExamples\Moving Objects\Test - Moving Objects Target.vi'" within 1 s (before any COM Move ran; the EMPTY copy for PathToStr.vi had been created; on disk afterwards Source.vi = 15849 B (the donor's size, mtime 03:16) and Target.vi = 4300 B (the pristine size, mtime 03:16)). copy_by_index (tools/gscript.py) does: close_panel(MOVE_SRC/MOVE_DST) [COM]; restore_move_fixtures() = shutil.copyfile(ORIG.bak -> MOVE_DST); shutil.copyfile(donor -> MOVE_SRC); shutil.copyfile(target -> MOVE_DST); revert() [COM]; ... The same routine succeeded at 00:3x on a FRESH LabVIEW instance (StrToPath.vi). Since then LabVIEW has kept running and 'Test - Moving Objects Target.vi' has been LOADED in memory (its panel closed) - the exact situation the earlier review (archive/peer/2026-09-15-strtopath-fail4-gui-save-of-broken-target.md) warned about.
MY DIAGNOSIS: Python 3.10's shutil.copyfile on Windows uses the CopyFile2 fast path; when the destination file is held by another process in a state that makes CopyFile2 fail with ERROR_INVALID_PARAMETER, Python maps it to EINVAL/Errno 22 - here the destination is a .vi that LabVIEW currently has loaded (possibly with the file mapped or opened with restrictive sharing while loaded). The remedy: never byte-substitute a VI file that LabVIEW has loaded - restart LabVIEW (permitted) before any copy_by_index session, and make copy_by_index refuse/recover if the substitution copy fails.
Attack: (1) does LabVIEW keep a VI's file open/mapped while the VI is loaded in memory (panel closed)? cite; if not, what else yields Errno 22 from shutil.copyfile on Windows (destination attributes, path length, a directory, an open handle with FILE_SHARE_NONE...)? (2) which copy call in that sequence is the likely one (restore of ORIG -> Target, or target -> Target), given Target.vi's mtime moved to 03:16 and size is the pristine 4300 B? (3) safest protocol: restart LabVIEW before copy_by_index vs. unloading the two example VIs over VI Server (a 'close VI reference with unload' - is there an ActiveX/VI Server way to UNLOAD a VI so its file is free? cite) vs. copying via a Python open()/write loop that bypasses CopyFile2? (4) cheapest discriminating test. Read-only; cite what you read.


## Answer

The diagnosis is probably wrong in mechanism, though the restart workaround remains sensible.

1. **Python 3.10 does not use `CopyFile2` here.** On Windows, Python 3.10 `shutil.copyfile()` opens the destination with `open(dst, "wb")` and copies through a 1 MiB `memoryview` buffer. Python?셲 own 3.10 documentation says Windows uses this buffered implementation; `CopyFile2` acceleration arrived later. [Python 3.10 shutil docs](https://docs.python.org/3.10/library/shutil.html#platform-dependent-efficient-copy-operations), [CPython issue tracking the later `CopyFile2` addition](https://github.com/python/cpython/issues/88745)

2. **A restrictive LabVIEW file handle is not the natural explanation for `Errno 22`.** Windows reports an incompatible open handle as `ERROR_SHARING_VIOLATION` (32), whereas `ERROR_INVALID_PARAMETER` is 87. Python normally exposes the former as a sharing/permission error, not `EINVAL`. Directory destination, read-only attributes, malformed/overlong paths, and same-file copying likewise normally have distinguishable exceptions or Windows codes. [Microsoft system error codes](https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-499-)

   NI documentation establishes that a VI can remain **in memory** after its panel closes, and that closing references may unload it asynchronously. It does **not** establish that LabVIEW continuously holds the `.vi` disk file open or memory-mapped while loaded. Thus ?쐋oaded in LabVIEW??and ?쏻indows handle blocks overwrite??must not be treated as equivalent. [NI: Closing References in LabVIEW](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)

3. **The failing call was almost certainly `target -> MOVE_DST`, not the restore.** The observed state is a transaction trace:

   - `MOVE_SRC` equals the donor: donor ??source succeeded.
   - `MOVE_DST` equals pristine 4300-byte content, with the new run timestamp: restore ??destination succeeded.
   - The next operation naming `MOVE_DST` then failed before replacing that content.

   That evidence actively weakens the ?쏬abVIEW prevents overwriting this loaded destination??hypothesis: the same destination had just been overwritten successfully. Something specific to the third call?봢specially its source path/object, source/destination aliasing, a malformed path-like value, or an error during buffered reading/writing?봡eserves priority.

4. **Protocol recommendation:** restart LabVIEW before a session as a conservative state reset, but do not describe it as a proven file-lock remedy. VI Server can unload a VI by closing every owning VI reference, provided nothing else?봠aller, project/library, implicit reference, or leaked ActiveX reference?봩eeps it resident. Disposal may be asynchronous; verify disappearance with `All VIs in Memory` before copying. [NI reference lifecycle](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html), [NI example stating reference closure unloads a VI](https://knowledge.ni.com/KnowledgeArticleDetails?OpenDocument=&id=kA00Z0000019SItSAM)

   A manual `open()/write` loop is **not a bypass**: that is effectively what Python 3.10 `copyfile()` already does, and it cannot bypass Windows sharing restrictions.

5. **Cheapest discriminating test:** capture the complete exception fields at each individually labelled copy: `type`, `repr(src)`, `repr(dst)`, `errno`, `winerror`, `filename`, and `filename2`, plus sizes before/after. Also assert resolved source and destination are different. Separately, while LabVIEW retains the VI, use Microsoft Sysinternals Handle or Process Explorer to search for the exact destination pathname; this directly tests whether LabVIEW owns a disk handle without modifying anything. [Microsoft Sysinternals Handle](https://learn.microsoft.com/en-us/sysinternals/downloads/handle)

Bottom line: retain ?쐒estart before fixture substitution??as defensive policy, but reject the claimed `CopyFile2 ??ERROR_INVALID_PARAMETER ??loaded-VI lock` chain. The supplied filesystem state instead points to the **third copy and its arguments**, while the actual `winerror` is the single most valuable missing datum.

## Sources

(extract from answer)

## What was done with it

Mechanism claim withdrawn (Python 3.10 `copyfile` is a buffered open/write; a foreign handle would be a sharing
violation, not EINVAL). The reviewer's pointer — the third copy (`target → MOVE_DST`) and the missing `winerror` —
is acted on: `gscript.copy_by_index` now labels each substitution copy and re-raises with type/errno/winerror/
src/dst/sizes, plus a same-file guard. The LabVIEW restart before a `copy_by_index` session is KEPT as a
defensive state reset only (recipe `fresh_labview()`), not described as a lock remedy. Rerun:
`tools/bench/build_track_v6_queue.log` (run 2) — if Errno 22 recurs, the log now says which copy and why.
