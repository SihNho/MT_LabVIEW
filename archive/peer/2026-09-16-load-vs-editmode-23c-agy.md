---
type: peer-review
status: historical
date: 2026-09-16
tags: [peer-review, archive, labview]
disposition: legacy
legacy_note: closed as legacy 2026-09-25 by card chat-L1 (cutoff 2026-09-22; user 2026-09-25 lint order before runner resume)
---

# load-vs-editmode-23c-agy

- **agent:** gemini
- **model:** (agy default, not readable) (agy built-in default)
- **kind:** review
- **cost:** 
- **date:** 2026-09-16
- **outcome:** ERROR (19s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK two claims measured in tools/bench/diag_load_vs_editmode.log (script tools/bench/diag_load_vs_editmode.py; LabVIEW 2026, VI Scripting driven over ActiveX from Python). Do not agree first. Cite NI documentation or labviewwiki where you can.

MEASURED, each arm a FRESH copy of a small op VI (4 Property objects on its block diagram), identical scripting op (Open VI Reference -> Traverse for GObjects 'Property' -> Index Array -> Invoke Generic.Delete 6327400), index 0, same LabVIEW process, alternating:
  A0 nothing done first                                          4 -> 4  NOTHING deleted, error cluster (False,0,'')
  A2 read the VI 'Block Diagram' property (ID 23C) first, no window opened, then delete   4 -> 4  NOTHING deleted
  A3 VI.OpenFrontPanel(activate=False) first, then delete        4 -> 3  deleted uid 115
  A4 same 23C-loaded panel-less copy, GObject.Move instead of Delete: (853,300) -> (853,300)  DID NOT MOVE
  A Win32 window census confirms A2 opened no window and A3 opened exactly one.
The 23C read was done by running an existing op VI whose dataflow is Open VI Reference(path) -> Property Node VI.Block Diagram (23C) -> AbstractDiagram.Nodes[] -> Index Array -> node reads; that op then RETURNS and its refnums go out of scope.

CLAIM 1 to attack: since a documented diagram load (23C is marked 'Loads the block diagram into memory: Yes') was performed and BOTH delete and move were still silently declined, while OpenFrontPanel makes both work, diagram RESIDENCY is not the variable - the variable is panel/edit-mode/UI context. The hole I want attacked hardest: I could not read Metrics:Block Diagram Loaded (property 292) in this run, so I have NOT proved the diagram was loaded at delete time. QUESTION: is a block diagram loaded through the 23C property guaranteed to STAY in memory after the refnum that loaded it is closed and the loading VI stops running, or does LabVIEW unload it again? If it does not stay, what holds it - keeping the diagram refnum open, VI.'Block Diagram Window:Open' (237), an Open VI Reference option flag - and how could that be held across a SEPARATE later op-VI run?

CLAIM 2 to attack: my flag reader failed to build for an identifiable reason. In a COPY of an op (Open VI Reference -> Traverse -> For loop) I created a Property Node of class 'VI Server:VI' with items 291 (Metrics:Front Panel Loaded) and 292 (Metrics:Block Diagram Loaded) - they attached, the node came back with output terminals named PanelLoaded and DiagramLoaded - then wired its 'reference' input by BRANCHING the Open VI Reference node's 'vi reference' output via Terminal.Connect Wire (6349C03). Result: wire-count delta 0 and the VI went to ExecState 0 (BROKEN). My two explanations: (a) the branch silently did not happen, leaving the PN's reference bare (a Property Node with a bare reference is broken); (b) the node was created at diagram coordinates (60,900), possibly INSIDE the donor's For Loop while owned by the top-level diagram. QUESTIONS: does a VI-class Property Node reject a reference from Open VI Reference that has no type specifier? Do the Metrics properties 291/292 (read-only, Run-Time Engine scope) carry a requirement I am missing? Is a wire-count delta of 0 consistent with a successful BRANCH in LabVIEW scripting, or does a branch always create a new Wire object? What else breaks a VI in exactly this shape?

ALREADY RULED OUT: wrong method ID (Generic.Delete 6327400 is confirmed correct); the op VI being broken (ExecState 1); the target running or reserved (idle fresh copy); error reporting (Generic.Delete has no semantic return value and the error cluster read (False,0,'') in every arm, including the SUCCESSFUL A3).

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

agy.exe : jetski: no output produced — a tool required the "command" permission that headless mode cannot prompt for, s
o it was auto-denied. Add an allow-rule under permissions.allow in settings.json (e.g. command(<target>)). Alternativel
y, re-run with --dangerously-skip-permissions to auto-approve all tools.
위치 줄:12 문자:36
+     Get-Content $promptFile -Raw | & $exe @exeArgs 2>&1 | Out-String
+                                    ~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (jetski: no outp...rove all tools.:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 



## Sources

(extract from answer)

## What was done with it

(Claude fills in)

**NON-RESULT.** This dispatch told us nothing (CLAUDE.md: a call that failed, timed out or hit quota is not a review) and is kept only so the audit can count it. The review that actually answered is `archive/peer/2026-09-16-load-vs-editmode-23c-r2.md` (codex, ANSWERED 69s, -TimeoutSec 420).
