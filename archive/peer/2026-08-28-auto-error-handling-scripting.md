---
type: peer-review
status: historical
date: 2026-08-28
tags: [peer-review]
---

# auto-error-handling-scripting

- **agent:** gemini
- **date:** 2026-08-28
- **outcome:** ANSWERED (44s)
- **why asked:** Can 'Enable automatic error handling' be turned off programmatically? (first attempt, agy)
- **verdict:** rejected

## Question

LabVIEW VI Server / VI Scripting question. When a node's 'error out' terminal is unwired and the VI's 'Enable automatic error handling' option (VI Properties > Execution) is ON, runtime errors pop a modal dialog. Questions: (1) Is there a VI Server property (settable programmatically via a Property Node on a VI refnum, or via ActiveX) to turn OFF 'Enable automatic error handling' for a specific VI? What is the exact property name and which class is it on? (2) Can it be set via the LabVIEW ActiveX automation interface (VirtualInstrument object) from an external COM client, e.g. SetVIProperty or similar? (3) Is there an application-wide or ini-file setting that disables automatic error handling dialogs globally? Search NI documentation and forums; cite URLs.

## Answer

agy.exe : jetski: no output produced ??a tool required the "read_file" permission that headless mode cannot prompt for,
 so it was auto-denied. Add an allow-rule under permissions.allow in settings.json (e.g. read_file(<target>)). Alternat
ively, re-run with --dangerously-skip-permissions to auto-approve all tools.
위치 줄:5 문자:36
+     Get-Content $promptFile -Raw | & $exe @exeArgs 2>&1 | Out-String
+                                    ~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (jetski: no outp...rove all tools.:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 



## Sources

(extract from answer)

## What was done with it

agy produced no answer: headless mode auto-denied its read_file tool. Exposed two bugs - peer.ps1 classified the empty run ANSWERED (fixed: such runs are now ERROR), and agy needs permissions.allow rules to use any tool headless. Question re-asked to codex (see -scripting2).
