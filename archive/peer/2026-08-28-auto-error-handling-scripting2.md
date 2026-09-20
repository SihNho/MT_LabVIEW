---
type: peer-review
status: historical
date: 2026-08-28
tags: [peer-review]
---

# auto-error-handling-scripting2

- **agent:** codex
- **date:** 2026-08-28
- **outcome:** ANSWERED (53s)
- **why asked:** Can 'Enable automatic error handling' be turned off programmatically, to stop unwired error-out dialogs from wedging COM automation?
- **verdict:** adopted

## Question

LabVIEW VI Server / VI Scripting question. When a node's 'error out' terminal is unwired and the VI's 'Enable automatic error handling' option (VI Properties > Execution) is ON, runtime errors pop a modal dialog. Questions: (1) Is there a VI Server property, settable programmatically via a Property Node on a VI refnum, to turn OFF 'Enable automatic error handling' for a specific VI? Exact property name and class? (2) Is it reachable from an external ActiveX/COM client driving LabVIEW.Application / VirtualInstrument (e.g. SetVIProperty)? (3) Is there a labview.ini token or Tools>Options setting that disables automatic error handling dialogs globally for all VIs? Search NI documentation and forums; cite URLs for every claim.

## Answer

1. Yes. Use the Boolean VI Server property:

- Property: `Automatic Error Handling`
- VI Server class: `VI` / `Virtual Instrument`
- Access: read/write
- Set it to `FALSE` on the target VI reference.
- It cannot be changed while that VI is running.

NI explicitly states that the Execution-page option can be controlled programmatically using the `Automatic Error Handling` property. [NI: Execution Page?봙I Properties](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html)

The property metadata lists its long name as `Automatic Error Handling`, short name as `Auto Err Handling`, internal data name as `Def Err Handling`, owning class as `VI Class`, and type as Boolean. [LabVIEW Wiki property metadata](https://labviewwiki.org/wiki/VI_class/Automatic_Error_Handling_property)

This is a normal VI Server property, not a VI Scripting-only property.

2. No?봭ot directly through the standard external `VirtualInstrument` ActiveX/COM interface.

The ActiveX `VirtualInstrument` object exposes a fixed subset of VI properties. Its documented property list includes properties such as `AllowDebugging`, `RunOnOpen`, `SuspendOnCall`, and `PreferredExecSystem`, but does not expose `AutomaticErrorHandling` or a generic `SetVIProperty` method. [VirtualInstrument ActiveX property list](https://documentation.help/NI-ActiveX-LabView/VirtualInstrument_Class.html) [VirtualInstrument ActiveX method list](https://documentation.help/NI-ActiveX-LabView/VI_Class_Method.html)

Therefore:

- `vi.AutomaticErrorHandling = False` is not part of the documented COM interface.
- A generic `VirtualInstrument.SetVIProperty(...)` is also not part of that interface.
- `SetControlValue` only writes a front-panel control; it does not write arbitrary VI Server properties. [VirtualInstrument ActiveX method list](https://documentation.help/NI-ActiveX-LabView/VI_Class_Method.html)

An external client can still invoke a helper VI through ActiveX; that helper VI can receive/open the target VI reference and write `VI class ??Automatic Error Handling = FALSE` internally. LabVIEW documents that external automation clients obtain `VirtualInstrument` objects through `Application.GetVIReference`, but clients are limited to properties and methods exported by that COM type library. [NI: ActiveX and LabVIEW](https://www.ni.com/en/shop/labview/activex-and-labview.html)

3. Yes, but there are two distinct global settings:

- `defaultErrorHandlingForNewVIs = False`  
  Disables the per-VI option only for newly created VIs. It does not retrofit existing VIs.

- `EnableAutomaticErrorHandling = False`  
  Disables automatic-error-handling dialogs globally in the development environment, including for existing VIs whose individual `Automatic Error Handling` property remains enabled.

NI documents both INI tokens. [NI: Prevent LabVIEW Error Dialog Box](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019SFfSAM&l=en-US)

The corresponding Tools 쨩 Options 쨩 Block Diagram checkboxes are:

- `Enable automatic error handling in new VIs`
- `Enable automatic error handling dialogs`

NI lists both settings separately. [NI instrument-driver configuration guidance](https://www.ni.com/en/support/downloads/instrument-drivers/tools-resources/instrument-driver-guidelines/before-you-develop-your-driver.html)

An NI forum discussion confirms the important distinction: the ?쐍ew VIs??setting only determines the saved property of newly created VIs, while the ?쐂ialogs??setting controls whether dialogs actually appear. [NI Community discussion](https://forums.ni.com/t5/LabVIEW/suppress-pop-up-dialog-boxes-on-error/td-p/2177798/page/2)

Bottom line: for an ActiveX-driven workflow, the least invasive global safeguard is `EnableAutomaticErrorHandling=False`. To permanently change a particular VI?셲 saved execution property, call a helper VI that writes `VI class ??Automatic Error Handling=False`, then save that target VI.

## Sources

(extract from answer)

## What was done with it

Key facts adopted: VI-class property 'Automatic Error Handling' is G-writable but NOT reachable from external COM; labview.ini EnableAutomaticErrorHandling=False kills the dialogs globally (deferred - global config change needs the user's decision). The chosen fix instead: OpWire_v1's internal error chain into Clear Errors sinks, which removes the dialogs without any config change.
