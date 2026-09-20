---
type: peer-review
status: historical
date: 2026-09-07
tags: [peer-review]
disposition: legacy
---

# com-run-hang-opbuildpn-copy

- **agent:** codex
- **date:** 2026-09-07
- **outcome:** ANSWERED (56s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW 2026 (26.3.1f1) VI Server / VI Scripting driven from Python COM (win32com, ActiveX Application/VirtualInstrument). Cite sources (NI forums, labviewwiki, NI docs). ATTACK this diagnosis and propose the cheapest discriminating test.
OBSERVED: an op VI 'OpReport_v3.vi' (uses VI Scripting - Traverse.lvlib:Traverse for GObjects.vi on a target VI given by path; run via VirtualInstrument.Run(True) from COM after SetControlValue) works thousands of times, but SIX times today Run() never returned (60-180 s watchdog; no modal dialog; LabVIEW UI stays responsive to SendMessageTimeout; LabVIEW's window shows the target VI's front panel in edit mode). Common factor of all six: the target was a fresh file COPY of 'OpBuildPN_v0.vi' (a VI whose diagram calls the erdosmiller LV-Scripting library VI 'Create Property Node.vi' and has an array-of-cluster control) opened with OpenFrontPanel(False, 1) just before; in some attempts the hang came at the first Run on that copy, in others after a scripting 'Delete' of the library subVI node on it. Earlier the same sequence (copy OpBuildPN_v0, delete the creator, report) succeeded (build of OpBuildIA_v0). Restarting LabVIEW did not help; after a forced kill LabVIEW showed a small untitled modal at startup (dismissed). Prediction that FAILED: 'report() on the copy returns in <1 s'.
Already ruled out: modal error dialogs (none found by window enumeration), handle exhaustion (37k, baseline 31.5k), a second COM client (no other python processes), LabVIEW UI hang (ping 0 ms).
Questions: (1) Known causes for VirtualInstrument.Run blocking forever without a dialog while the UI stays responsive - e.g. a VI waiting for 'front panel open' state, root loop contention, a VI reserved for execution, a dependency load prompt suppressed, VI Scripting Traverse on a VI whose subVI is in memory under a different path (LV-Scripting.lvlib 'Dependency loaded from new path')? (2) Could copying a VI that calls an lvlib member, then opening it, put LabVIEW in a state where Traverse for GObjects blocks (e.g., waiting on the library's load or on a 'Save changes?' that never shows because the VI was opened from COM)? (3) What is the cheapest test to separate 'the copied VI is the trigger' from 'the reporter/Traverse is the trigger' from 'LabVIEW instance state'? (4) Is there an ActiveX/VI Server way to abort or time out a Run that never returns (Abort VI via a second reference, VI.Abort, App.Kill?) so the client can recover without killing LabVIEW? Answer concisely with verdicts.


## Answer

## Verdicts

1. **The evidence does not specifically implicate copying or library-path resolution.** It implicates executing `OpReport_v3.vi` synchronously while that VI performs a UI-thread-sensitive scripting operation.

`Run(True)` is expected to block until the reporter finishes. Moreover, NI documents that the Run VI method must wait for the UI to be idle, and NI warns that a VI launched through Run VI may execute in the UI execution system unless configured otherwise. Thus a responsive top-level LabVIEW window does **not** prove that the scripting request or the reporter?셲 execution context is making progress. ([LabVIEW Wiki: Run VI](https://www.labviewwiki.org/wiki/VI_class/Run_VI_method), [NI: Run VI versus Call by Reference](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019MqkSAE&l=en-US))

Check these known execution waits first:

- `OpReport_v3.vi` or `Traverse for GObjects.vi` is non-reentrant and already reserved/running. Run VI cannot run a VI reserved by another caller, while non-reentrant calls wait for the existing invocation. ([LabVIEW Wiki: Run VI](https://www.labviewwiki.org/wiki/VI_class/Run_VI_method), [NI execution properties](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html))
- A subVI has **Suspend when called** enabled. That explicitly waits for user interaction and need not look like a conventional modal dialog. ([NI execution properties](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html))
- A node is waiting for front-panel activity with the default `-1` timeout. This is a documented indefinite, non-modal wait. ([NI: Wait For Front Panel Activity](https://www.ni.com/docs/ar-SO/bundle/labview-api-ref/page/functions/wait-for-front-panel-activity.html))
- Traverse or an operation it invokes is waiting for the UI/root loop. VI Server operations that load from disk explicitly wait for UI-idle state, and Run VI itself is marked as UI-idle-dependent. ([NI: Creating a VI Server Application](https://www.ni.com/docs/tr-CY/csh?context=lvcore_lvhowto_vi_server), [LabVIEW Wiki: Run VI](https://www.labviewwiki.org/wiki/VI_class/Run_VI_method))

2. **A copied VI can expose a dependency conflict, but there is no sourced evidence that ?쏡ependency loaded from new path??makes Traverse deadlock.**

LabVIEW VIs remember dependency locations; opening a copy can cause LabVIEW to find an already-loaded dependency elsewhere and record a load warning. That behavior is established. ([NI forum: dependency loaded from new path](https://forums.ni.com/t5/LabVIEW/Warning-List-Dependecy-Loaded-from-new-path-issue/td-p/4309058), [NI forum: Load Warning Summary](https://forums.ni.com/t5/LabVIEW/quot-Load-Warning-Summary-quot-dialog-box-Dependency-loaded-from/td-p/3349081))

But the stronger diagnosis?봪ibrary loading blocks `Traverse for GObjects` indefinitely?봧s unsupported by the sources I found. The facts attack it:

- Restarting LabVIEW did not clear the failure.
- The identical copy/delete/report sequence previously succeeded.
- The front panel being open in edit mode is normal for scripting and does not itself imply a wait.
- The later startup modal after a forced kill could be crash/recovery residue; it does not establish that an invisible prompt caused the original hang.

Treat the copied VI/library dependency as a **trigger candidate**, not yet the cause.

3. **Cheapest discriminating test: one instance, three targets, asynchronous reporter, progress marker.**

Without modifying the targets, have the manager run this sequence in a fresh LabVIEW instance:

1. Report a known-good, already-loaded VI.
2. Report the original `OpBuildPN_v0.vi`.
3. Make/open a fresh copy, then report the copy without deleting anything.
4. Delete the creator node, then report that same copy.
5. Immediately repeat step 1.

For each call, use `Run(False)` and poll the reporter?셲 `Execution.State`; NI documents `Wait Until Done=False` as the way to avoid blocking the caller. ([NI: running VIs simultaneously](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YHyLCAW&l=en-US), [LabVIEW Wiki: Execution State](https://www.labviewwiki.org/wiki/VI_class))

Interpretation:

- Only steps 3/4 hang, while step 5 succeeds ??copied-target state triggers Traverse.
- Steps 3/4 hang and step 5 then hangs ??LabVIEW instance/shared Traverse state is poisoned.
- Reporter reaches ?쐀efore Traverse??but not ?쏿fter Traverse????Traverse is localized.
- Reporter never reaches ?쐀efore Traverse????Run/reservation/execution-system problem, not target traversal.
- A tiny reporter variant that only opens the target reference and reads a simple property succeeds while Traverse hangs ??strongest cheap evidence against dependency loading and for Traverse itself.

The single most valuable artifact is a progress value written immediately before and after `Traverse for GObjects`. It converts ?쏳un hung??into an exact boundary.

4. **Recovery exists in the API, but it is not a reliable watchdog guarantee.**

`VirtualInstrument.Abort()` is the documented ActiveX method and is equivalent to LabVIEW?셲 Abort Execution button. ([NI: ActiveX Abort](https://www.ni.com/docs/fa-AF/bundle/labview-api-ref/page/properties-and-methods/activex/vi/abort.html)) However:

- An NI forum report says ActiveX abort can require the **same VI reference used to start the VI**, so do not assume a newly obtained second reference is equivalent. ([NI forum: stopping an ActiveX-run VI](https://forums.ni.com/t5/LabVIEW/How-can-I-stop-a-VI-that-is-running-via-ActiveX/td-p/127696))
- Abort applies to a running top-level VI and can fail when the VI is part of another VI?셲 calling hierarchy. ([NI forum: aborting a subVI](https://forums.ni.com/t5/LabVIEW/problem-to-open-and-abort-a-subvi-by-invoke-node/td-p/3340140))
- If the blocking call owns the only thread/reference capable of issuing `Abort`, it is unusable. Therefore call `Run(False)`, retain that reference, and let a separate watchdog thread/process call `Abort()` on it.
- If the server?셲 COM/UI dispatch is itself wedged, the abort call may also block. There is no documented per-call timeout on `VirtualInstrument.Run`.
- `Application.Quit()` exists, but it exits LabVIEW and may encounter save handling; it is graceful shutdown, not a dependable replacement for process termination. ([NI ActiveX Application methods](https://www.ni.com/docs/zh-CN/bundle/labview-api-ref/page/properties-and-methods/activex/application-m.html))

**Bottom line:** change the automation pattern to `Run(False) ??poll Execution.State/progress ??Abort on the original reference`. The first test should instrument the boundary around Traverse; presently, blaming copied lvlib dependencies is premature.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
