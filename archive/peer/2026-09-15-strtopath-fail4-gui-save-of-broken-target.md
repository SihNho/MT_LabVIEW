---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, gui]
---

# strtopath-fail4-gui-save-of-broken-target

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (83s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS (LabVIEW 2026, VI Scripting over COM + minimal keystroke save). Log: tools/bench/cycle3b_toolkit.log run 2 (00:13-00:19), scripts tools/recipes/build_strtopath.py and gscript.copy_by_index / gui_save in tools/gscript.py.
GOOD NEWS: OpMoveByIndex_v0 built (13/13, ExecState 1 after wiring 'Traverse Target'=BD; your plan B was not needed). Then copy_by_index(donor 'save N xyz traces.vi', class 'Function', index 4 -> uid 194 'String To Path', target = a fresh copy of EMPTY_v0) ran: the op returned without error, the UID guard passed (no mismatch raised), new GObjects appeared on the substituted Test-Target - and then gscript.save(MOVE_DST, allow_broken=True) -> gui_save raised: "file mtime did not move after Ctrl+S on every candidate window. Check dialogs - a modal dialog blocks the save". lv_gui -Action dialogs right after: NO modal; windows: 'Test - Moving Objects Target.vi Front Panel *' (dirty, 1000x704), 'Test - Moving Objects Source.vi Front Panel' (MAXIMISED, -8,-8,1928,1048), OpFPLabels_v0 FP+BD. The copy_by_index finally-block then restored the two example files ON DISK from backups while the Target stayed loaded and dirty in memory.
CONTEXT: copy_into uses gui_save (editor File>Save via Ctrl+S) because a VI holding a freshly copied primitive with unwired required inputs is BROKEN and the COM save refuses it; gui_save worked for the CLFN copy earlier (2026-09-08). NI: a broken VI CAN be saved from the editor.
Questions: (1) Why would Ctrl+S on the dirty Target's front-panel window not save it - candidates: keystrokes landed on the maximised Source window (focus/foreground); the Target window not activated; a save-as/"changed on disk" prompt appearing briefly and closed; LabVIEW refusing to save a broken VI silently? Cite what NI documents about saving broken VIs and about Save when the file on disk differs. (2) Is there a NON-GUI way to save a BROKEN VI over VI Server/ActiveX (VI.Save.Instrument method 'Save.Instrument' - does it refuse broken VIs? 'Save.For Previous'? Application-level methods?) - cite; if 'Save.Instrument' works on broken VIs the fleet should build that invoke and drop the keystroke save. (3) Given the Target is now loaded+dirty while its disk bytes were restored, what is the safe recovery (LabVIEW restart is permitted) and what must the protocol do differently so a failed save cannot leave this state? (4) Alternative that avoids saving a broken VI at all: copy the primitive into a target VI that already contains its required feeds? (a String To Path's only required input is 'string' - could copy_by_index copy into a target where a string control is wired by a subsequent op BEFORE any save, i.e. keep the Target in memory, run wire ops on it, then COM-save once it is runnable)? Is a VI with a broken node saveable by COM once the node is fully wired (yes?) - cite. (5) Cheapest discriminating test. Read-only; cite what you read.


## Answer

The strongest explanation is not ?쏬abVIEW silently refuses to save broken VIs.??The evidence fits a focus/keystroke failure or a hidden/short-lived file-conflict prompt much better. More importantly, the cleanup protocol has created an unsafe split-brain state: the loaded dirty VI and the restored disk file now represent different programs.

1. Why Ctrl+S probably failed

Ranked hypotheses:

1. **Foreground/focus failure ??most likely.**  
   `gui_save()` trusts the text returned by `lv_gui focus`; it never verifies the actual foreground HWND immediately before `^s`. The maximized Source window makes misdelivery plausible. The dirty `*` remaining on Target supports ?쏷arget never received a successful Save.??
2. **A prompt appeared and was erased by the unconditional Esc ??plausible.**  
   After every Ctrl+S, `gui_save()` sends Esc. Therefore ?쐍o modal afterward??does not prove no modal appeared. Esc could cancel a ?쐁hanged on disk,??Save As, or warning dialog before the later dialog census.

3. **mtime produced a false negative ??possible.**  
   mtime alone is weak proof: filesystem timestamp granularity/caching can hide a rewrite. Check file hash, size, dirty flag, and LabVIEW?셲 saved-state indication, not only `mtime > before`.

4. **LabVIEW silently refuses editor Save solely because the VI is broken ??weakest.**  
   NI defines a broken VI as non-executable, commonly because a required terminal is unwired; that documentation says it cannot *run*, not that it cannot be saved. [NI: LabVIEW Debugging Techniques](https://www.ni.com/en/support/documentation/supplemental/12/debugging-techniques-in-labview.html). NI?셲 own historical bug notes explicitly discuss saving broken VIs, which is strong evidence that broken VIs are valid saved artifacts. [NI: LabVIEW 8.2.1 Bug Fixes](https://www.ni.com/en/support/documentation/bugs/17/archived--labview-8-2-1-bug-fixes.html).

LabVIEW 2026 makes the disk-conflict hypothesis especially relevant: 2026 Q1 added an ?쏣xternally Changed Files List??precisely to warn when open files are changed on disk and LabVIEW is in a bad file-conflict state. [NI: LabVIEW New Features and Changes](https://www.ni.com/docs/ar-LB/bundle/labview/page/labview-changes.html). NI?셲 prescribed response to the older changed-on-disk warning is Revert; Cancel cancels loading, because mixing disk and in-memory parts can produce an inconsistent/corrupt VI. [NI: VI Has Changed on Disk](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kEssSAE&l=en-US).

One nuance: if the disk restoration happened only after all Ctrl+S attempts, that restoration did not cause the original save failure. But any earlier byte substitution while the destination was already loaded could have established the conflict beforehand.

2. Does `Save.Instrument` support broken VIs?

**Not established by the NI documentation I found. Do not yet replace GUI Save based on documentation alone.**

NI documents and demonstrates `Save.Instrument` as the programmatic way to persist scripted VI changes; an NI engineer specifically recommended it after VI Scripting edits. [NI Community: VI reference and scripting?봘nlock method](https://forums.ni.com/t5/LabVIEW/VI-reference-and-scripting-Unlock-method/m-p/3610818). However, that case does not say the edited VI was broken.

I found no NI API statement saying `Save.Instrument` refuses broken VIs. Conversely, I found no current NI statement guaranteeing it works on them. Thus the comment in `gscript.py`?붴쏶aveInstrument blocks forever on a broken VI?앪봧s a local empirical observation, not a documented LabVIEW restriction. A hang could instead be a synchronous method waiting for an unseen UI/file-conflict condition; that is particularly plausible because the current setup mutates backing files while VIs remain loaded.

`Save.For Previous` is not a substitute for ordinary saving. NI describes it as saving a separate copy for an earlier LabVIEW version, with an explicit destination and warnings; it is conversion/export functionality. [NI: Save for Previous Version](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGiHCAW&l=en-US). Application/project `SaveForPrevious` likewise saves a project copy readable by an earlier version. [NI API: SaveForPrevious](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/project/saveforprevious.html).

Verdict: build a `Save.Instrument` op only after the isolated test below proves it on a deliberately broken scratch VI in LabVIEW 2026.

3. Safe recovery now

Because restart is permitted:

1. Preserve the on-disk restored file and its backup/hash.
2. Exit/restart LabVIEW while explicitly declining to save the dirty Test-Target.
3. Do not try another save from the conflicted in-memory instance.
4. After restart, verify Test-Source and Test-Target disk hashes against their pristine originals.
5. Only then reopen/revert them as needed.

NI warns that loading components from a disk version that differs from the already-loaded VI can create an inconsistent/corrupt VI, and recommends reverting the loaded state. [NI: VI Has Changed on Disk](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kEssSAE&l=en-US).

The protocol must change:

- Never restore or overwrite a VI?셲 backing file while that VI may remain loaded.
- On success: save ??verify hash/size and dirty flag ??close/revert/unload reference ??only then restore fixtures.
- On failure: do **not** restore disk bytes in `finally`; mark the session contaminated, close without saving or restart, confirm unloaded, then restore.
- Prefer unique per-operation scratch paths over byte-substituting fixed filenames.
- Verify foreground HWND/title/process immediately before SendKeys.
- Capture dialogs/screenshots before sending Esc.
- Verify save by content hash plus disappearance of `*`, not mtime alone.

The current unconditional disk restore in `finally` should be treated as the primary protocol defect.

4. Avoid saving the intermediate broken VI

Yes?봳his is the better design.

Keep Test-Target loaded, copy `String To Path`, immediately add/wire the string source, verify the resulting VI is executable, and call `Save.Instrument` only once. NI says an unwired required terminal is a cause of a broken VI; once that required input is correctly wired, that particular reason for breakage is removed. [NI: LabVIEW Debugging Techniques](https://www.ni.com/en/support/documentation/supplemental/12/debugging-techniques-in-labview.html).

Caveat: ?쐓tring wired??does not automatically prove the whole VI is runnable. Gate on the final `ExecState`, absence of bad wires, and expected wire UID at both ends. If `ExecState != 0`, the existing COM save path should apply. `Save.Instrument` is an established scripting persistence mechanism. [NI engineer example](https://forums.ni.com/t5/LabVIEW/VI-reference-and-scripting-Unlock-method/m-p/3610818).

This also removes the need to serialize an intentionally broken intermediate artifact.

5. Cheapest discriminating test

Run one isolated, disposable scratch test after restarting LabVIEW:

1. Start from a fresh uniquely named scratch VI.
2. Make it intentionally broken in one controlled way.
3. Invoke `Save.Instrument` directly with a short external watchdog.
4. Record return/error, elapsed time, dialog/window census, disk hash/size/mtime, and dirty flag.
5. Restart and reopen the saved path to verify whether the edit persisted.

Outcomes:

- **Returns and hash changes:** delete the GUI save route; use `Save.Instrument`.
- **Returns an explicit error:** broken-VI refusal is real and diagnosable.
- **Hangs with a prompt/window:** the earlier ?쐀roken VI makes COM hang??conclusion was misattributed to UI/file conflict.
- **Hangs with no prompt on a pristine unique path:** likely a genuine LabVIEW 2026 `Save.Instrument` limitation/bug; then use the wire-before-save architecture.

A second tiny focus test?봪ogging foreground HWND before and after title-bar activation and immediately before `^s`?봶ill discriminate the existing GUI failure, but the direct `Save.Instrument` scratch test has greater architectural value.

## Sources

(extract from answer)

## What was done with it

Adopted §3 and §4 in full. LabVIEW was restarted (dirty Target vs restored disk = the split-brain the reviewer
named; nothing of value unsaved). `gscript.copy_by_index` rewritten: fixtures are restored to pristine bytes at the
START (nothing loaded), never in a `finally`; after the Move the substituted Target stays loaded and the caller's
`finish(dst)` hook wires the copied primitive's required input and adds its indicator; the VI is then COM-saved ONCE
only if `ExecState == 1` — no keystroke save of a broken intermediate; on failure nothing is restored and the next
run cleans up with nothing loaded. `gui_save` also gained the Ctrl+E-to-Block-Diagram step (the 2026-08-30
finding) for the cases that still need it. `Save.Instrument` on a broken VI stays unverified and unused.
Rerun: `tools/bench/build_strtopath.log` (run 5).
