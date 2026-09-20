# load-vs-editmode-23c-retry

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-16
- **outcome:** TIMEOUT (180s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this, measured in tools/bench/diag_load_vs_editmode.log (LabVIEW 2026, VI Scripting over ActiveX). Do not agree first; cite NI or labviewwiki.

MEASURED, each arm a FRESH copy of a small op VI (4 Property objects), identical op (Open VI Reference -> Traverse for GObjects 'Property' -> Index Array -> Invoke Generic.Delete 6327400), index 0, same process:
  A0 nothing first                                              4 -> 4  NOTHING deleted, error cluster (False,0,'')
  A2 read VI 'Block Diagram' (23C) first, no window, then delete 4 -> 4  NOTHING deleted
  A3 VI.OpenFrontPanel(activate=False) first, then delete        4 -> 3  deleted uid 115
  A4 same 23C-loaded panel-less copy, GObject.Move instead: (853,300) -> (853,300) DID NOT MOVE
  A Win32 window census confirms A2 opened no window, A3 opened one.
The 23C read was performed by RUNNING a separate op VI whose dataflow is Open VI Reference(path) -> Property Node VI.Block Diagram 23C -> AbstractDiagram.Nodes[] -> Index Array -> node reads; that op then RETURNS and its refnums go out of scope.

CLAIM 1 to attack: because a documented diagram load (23C: 'Loads the block diagram into memory: Yes') was performed and BOTH delete and move were still silently declined, while OpenFrontPanel makes both work, diagram RESIDENCY is not the variable - panel/edit-mode/UI context is. The hole to attack hardest: I could NOT read Metrics:Block Diagram Loaded (292) in this run, so I have not proved the diagram was loaded at delete time. Is a block diagram loaded through 23C guaranteed to STAY in memory after the refnum that loaded it is closed and the loading VI stops running, or is it unloaded again? If it does not stay, what holds it - an open diagram refnum, VI.'Block Diagram Window:Open' (237), an Open VI Reference option flag - and how could that be held across a SEPARATE later op-VI run?

CLAIM 2 to attack: the flag reader failed to build. In a COPY of an op (Open VI Reference -> Traverse -> For loop) I created a Property Node of class 'VI Server:VI' with items 291 and 292 (they ATTACHED: terminals came back named PanelLoaded and DiagramLoaded), then wired its 'reference' input by BRANCHING the Open VI Reference node's 'vi reference' output with Terminal.Connect Wire 6349C03. Result: wire-count delta 0 and ExecState 0 (BROKEN). My explanations: (a) the branch silently did not happen, leaving 'reference' bare; (b) the node was created at (60,900), possibly inside the donor's For Loop while owned by the top-level diagram. Does a VI-class Property Node reject a reference from an Open VI Reference with no type specifier? Do 291/292 carry a requirement I am missing? Is a wire delta of 0 consistent with a successful BRANCH, or does a branch always add a Wire object? What else breaks a VI in exactly this shape?

ALREADY RULED OUT: wrong method ID (6327400 confirmed); the op VI broken (ExecState 1); target running/reserved (idle fresh copy); error reporting (Generic.Delete has no semantic return value; the cluster read (False,0,'') even in the SUCCESSFUL A3).

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

(no answer within 180s — job stopped)

## Sources

(extract from answer)

## What was done with it

(Claude fills in)

**NON-RESULT.** This dispatch told us nothing (CLAUDE.md: a call that failed, timed out or hit quota is not a review) and is kept only so the audit can count it. The review that actually answered is `archive/peer/2026-09-16-load-vs-editmode-23c-r2.md` (codex, ANSWERED 69s, -TimeoutSec 420).
