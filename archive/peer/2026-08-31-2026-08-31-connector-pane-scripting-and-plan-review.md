---
type: peer-review
status: historical
date: 2026-08-31
tags: [peer-review, plan]
disposition: legacy
---

# 2026-08-31-connector-pane-scripting-and-plan-review

- **agent:** gemini
- **date:** 2026-08-31
- **outcome:** ERROR (13s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Two jobs: (A) factual API research with NI source URLs, (B) attack a plan.

CONTEXT: LabVIEW 2026, VI Scripting enabled, driving edits over ActiveX from Python through small 'op' VIs (each op runs library scripting VIs against a target VI given by path). The erdosmiller lv-scripting library (84 VIs) and LAVA scripting tools are installed. Target: a saved, legal VI whose front panel has ~13 controls/indicators; I must assign its CONNECTOR PANE by script: choose a pattern with >= 12 terminals and connect 9 named inputs + 3 named outputs to specific pane terminals, then save.

(A) QUESTIONS, each with a source URL:
1. What is the exact VI-Scripting API to set a connector pane pattern? (VI class property/method names - e.g. is it a 'Connector Pane' property returning a ConnectorPane refnum with a 'Pattern' write property? Which numeric pattern IDs correspond to the common 12-terminal (4-2-2-4) and 14/16-terminal patterns?)
2. What is the exact API to CONNECT a control to a pane terminal? (e.g. ConnectorPane 'Wire' / 'Connect Terminal' invoke taking a terminal index + a Control refnum? How are pane terminal indices numbered within a pattern?)
3. Do erdosmiller lv-scripting or the LAVA scripting-tools package ship ready-made VIs for pane pattern + wiring (names, please)? The LAVA package description mentions 'connector-pane refs, pattern selection, and wiring controls to the pane'.
4. Is pane assignment allowed while the VI is in edit mode over VI Server, and does it require the front panel open? Any known errors (e.g. 1000-range) when the VI is running/reserved?
5. How do I READ BACK the pane assignment to verify (which control is on which terminal), so a script can assert success?

(B) PLAN TO ATTACK - find what breaks: 'A Python script opens the target by path, uses an op VI wrapping the LAVA/erdosmiller pane VIs (or raw property/invoke nodes built once in the op) to (i) set pattern to a 12-plus-terminal layout, (ii) connect the 9 inputs and 3 outputs by CONTROL LABEL in a fixed order mirroring another VI's pane, (iii) verify by reading back the pane map, (iv) COM-save the target. Assumption: pane edits mark the VI modified but cannot break it (ExecState stays 1).' What silently fails? Ordering constraints (pattern must be set before wiring? does changing pattern clear existing wiring?)? Label-vs-name pitfalls for controls whose labels contain newlines? Anything about panes of VIs set reentrant/preallocated-clone?

## Answer

agy.exe : jetski: no output produced ??a tool required the "command" permission that headless mode cannot prompt for, s
o it was auto-denied. Add an allow-rule under permissions.allow in settings.json (e.g. command(<target>)). Alternativel
y, re-run with --dangerously-skip-permissions to auto-approve all tools.
위치 줄:5 문자:36
+     Get-Content $promptFile -Raw | & $exe @exeArgs 2>&1 | Out-String
+                                    ~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (jetski: no outp...rove all tools.:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
