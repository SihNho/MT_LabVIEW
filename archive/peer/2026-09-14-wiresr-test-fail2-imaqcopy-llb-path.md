---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# wiresr-test-fail2-imaqcopy-llb-path

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (125s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS DIAGNOSIS briefly. LabVIEW 2026, VI Scripting over COM. Failure: tools/bench/test_opwiresr.log - gscript.drop_subvi(scratch, r"C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision\Basics.llb\IMAQ Copy", body, (300,300)) blocked behind an UNTITLED modal 348x305 while every VI window (including the op OpSubVI_v1.vi whose Block Diagram had been opened) read 'blocked' in the raw window rows logged in that file. The same drop failed identically at 23:04 in tools/bench/build_opwiresr_v0.log.

MY DIAGNOSIS: the LLB path is wrong - 'IMAQ Copy' is a member of Management.llb, not Basics.llb (this project recorded exactly that in an earlier recipe header: grep "Management.llb holds 'IMAQ Copy'" under tools/). Open VI Reference inside OpSubVI_v1 returned error 7 (file not found), and OpSubVI_v1's AUTOMATIC ERROR HANDLING raised its untitled error dialog and opened the op's block diagram to highlight the node - which is why 'OpSubVI_v1.vi Block Diagram' appears among the windows. Fix applied: COPY_VI -> Management.llb. Earlier, at 23:04, I wrongly blamed a watchdog false positive; the watchdog was right both times.

Attack: (1) does LabVIEW's automatic error handling dialog match 'untitled window, all VI windows disabled, the failing VI's block diagram opened'? (2) Verify from the installed files which LLB contains 'IMAQ Copy' (a string scan of the .llb files under C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision\ is allowed - read only). (3) Should the op VIs have automatic error handling disabled (the fleet convention is set_auto_error_handling(False) on new ops) - is OpSubVI_v1 an exception, and what is the risk of leaving it? (4) Name the cheapest test proving the diagnosis on the next run. Read-only; do not open LabVIEW. Cite what you read.


## Answer

The diagnosis is mostly correct, but the applied fix still contains a path error.

1. The window pattern strongly supports automatic error handling. NI says it suspends execution, opens the failing node?셲 block diagram, highlights that node, and displays an error dialog. That matches the enabled 348횞305 untitled window plus every VI window disabled and `OpSubVI_v1.vi Block Diagram` appearing in [test_opwiresr.log](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/test_opwiresr.log:4>). The blank title itself is not specifically guaranteed by NI, but it does not weaken the diagnosis. [NI automatic-error-handling documentation](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html)

2. Crucial correction: the installed files show:

   - `Basics.llb`: `C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision\Basics.llb`
   - `Management.llb`: `C:\Program Files\NI\LVAddons\nivision\1\vi.lib\vision\Management.llb`
   - No `nivisioncommon\1\...\Management.llb` exists.

   Therefore the current `COPY_VI` in [build_opwiresr_v0.py](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_opwiresr_v0.py:54>) is still invalid. It must be:

   ```python
   r"C:\Program Files\NI\LVAddons\nivision\1\vi.lib\vision\Management.llb\IMAQ Copy"
   ```

   The static LLB scan finds `IMAQ Copy` in that `Management.llb`; it does not find it in `Basics.llb`. Error 7 is exactly consistent with a nonexistent or inaccessible path. [NI error-7 guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019OgmSAE&l=en-US)

3. `OpSubVI_v1` should not be an exception to the fleet convention. Disable automatic error handling, because `drop_subvi()` already reads `error out` and raises it at [gscript.py](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/gscript.py:983>). NI likewise recommends disabling automatic handling in reusable API VIs and reporting errors through error clusters. [NI VI guidelines](https://www.ni.com/en/support/downloads/instrument-drivers/tools-resources/instrument-driver-guidelines/vis-names-and-properties.html)

   The risk of merely disabling it is silent error loss if the op?셲 error indicator is not genuinely connected to `Open VI Reference`. Verify that connection/reporting once; otherwise a failed drop could look like a clean no-op.

4. Cheapest proving test: correct both the LLB and package root, then run one isolated `drop_subvi` on a disposable scratch and require:

   - no modal watchdog hit,
   - returned `error out` is clear,
   - SubVI count increases by exactly one,
   - the new node?셲 reported path/name is `IMAQ Copy`.

The two prior identical failures already provide the negative control. No restart or full T1?밫9 batch is needed to establish causality.

## Sources

(extract from answer)

## What was done with it

Diagnosis confirmed (automatic error handling on error 7: untitled dialog + the op's BD opened), and the reviewer
caught that my fix was STILL wrong — `Management.llb` is under `LVAddons\nivision\1`, not `nivisioncommon\1`.
Corrected in `tools/recipes/build_opwiresr_v0.py` and in NAMES.md's "Vision LLB member locations" table. Follow-up
recorded, not done tonight: disable automatic error handling on `OpSubVI_v1` after verifying its `error out` is
genuinely fed from `Open VI Reference` (the reviewer's silent-loss caveat). Rerun: `tools/bench/test_opwiresr.log`.
