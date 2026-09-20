---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# copy-harness-build-run1

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (33s)
- **why asked:** failed prediction: IMAQ Copy not found in the runtime's Basics.llb (error 7).
- **verdict:** explanation accepted (VDM Management.llb); rebuilt in the same session; cold first-copy cost measured (INDEX row 23).

## Question

FAILED PREDICTION check, one paragraph. tools/bench/build_harness_copy.log run 1 (recipe tools/recipes/build_harness_copy.py): drop_subvi of 'C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision\Basics.llb\IMAQ Copy' raised LabVIEW error 7 (file not found) in a modal dialog (dismissed by the watchdog). Explanation: IMAQ Copy is a Vision Development Module VI shipped under LVAddons\nivision\1\vi.lib\vision\Management.llb (string scan: 'IMAQ Copy', 'IMAQ Copy Vision Info', 'IMAQ ImageToImage 2' in that LLB; nivisioncommon's Basics.llb has only Create/Dispose/ImageToArray-type basics). Fix: the Management.llb path. ATTACK: (1) any reason 'IMAQ Copy' from Management.llb is the wrong VI for a pixel copy Image Src -> Image Dst (vs 'IMAQ ImageToImage 2'), and its likely terminal names ('Image Src', 'Image Dst', 'Image Dst Out', error terminals)?; (2) does a dismissed error-7 dialog leave OpSubVI_v1 (the drop op) or the target in a state that needs a LabVIEW restart before the rebuild? Cheapest check.

## Answer

**FAILED PREDICTION confirmed:** `IMAQ Copy` is the correct semantic choice: it copies the source?셲 pixels **and** image specifications, border, calibration, overlays, and pattern-matching information, whereas `IMAQ ImageToImage 2` appears to be an internal/helper VI and is not the documented public replacement; the documented terminals are exactly `Image Src`, `Image Dst`, `Image Dst Out`, `error in (no error)`, and `error out`, with `Image Dst Out` aliasing `Image Dst` when wired ([IMAQ Copy documentation](https://documentation.help/NI-Vision-LabView/IMAQ_Copy.html)). Thus the discovered `nivision\1\vi.lib\vision\Management.llb\IMAQ Copy` is strongly preferable, subject only to confirming that its connector pane matches those five terminals. A dismissed error-7 dialog does not by itself imply corruption or require restarting LabVIEW: automatic error handling suspends execution while showing the dialog, and error 7 ordinarily means the referenced path was absent or inaccessible ([NI automatic-error-handling behavior](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html), [NI error-7 guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019OgmSAE&l=en-GB)). The cheapest check before rebuilding is for the manager to query `OpSubVI_v1`?셲 `Execution:State` and require `Idle`?봏I defines that as loaded but not running ([NI execution-state reference](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YIEJCA4))?봳hen obtain a reporter object count/list for the target and verify that no partial `IMAQ Copy` node was inserted; if idle and unchanged, rerun with the corrected path in the same LabVIEW session, reserving restart only for a non-idle/bad state, an unexpected residual node, or a repeat failure at the valid path.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
