---
type: peer-review
status: historical
date: 2026-09-16
tags: [peer-review, archive, labview]
disposition: legacy
legacy_note: closed as legacy 2026-09-25 by card chat-L1 (cutoff 2026-09-22; user 2026-09-25 lint order before runner resume)
---

# case-frame-identity-and-contents

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-16
- **outcome:** TIMEOUT (180s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW 2026 VI Scripting. Failure record for the gate: tools/bench/diag_autofocus_panel2.log (a deliberate 2x2 grid whose FAIL rows were PREDICTED by the script's own contract - 'PropertyNode' raises error 1092 while 'Property' returns results; that conclusion was already reviewed and accepted, and I am not re-asking it).

THE NEW QUESTION, and the claim I want attacked. We have a Case Structure on a running experiment VI whose selector is a boolean. We know one of its two frames contains a serial motion call. We currently assert - WITHOUT having read the frames - that when the selector is TRUE the motion call executes, i.e. that 'the case fires' means 'the axis is commanded'. I think that assertion is unsafe: the frame could hold a further conditional, the motion VI could be wired to a zero displacement, or our frame-to-selector-value mapping (which frame is TRUE) could be inverted.

1. In LabVIEW 2026 scripting, how do I read WHICH FRAME corresponds to which selector value? Our notes name 'CaseStructure.Frame Names' (ID 6365002) as the candidate but record it as never used. Is that the right property, what exactly does it return for a boolean selector, and is there anything that gives the frames in a guaranteed order matching Diagram[] indices?
2. Is there a property that gives a Case Structure's DEFAULT frame, and one that gives the currently visible frame? Do either of those tell me the TRUE frame?
3. Given a frame's Diagram reference, what is the cheapest scripting route to list the subVI calls inside it INCLUDING nested structures, without walking every node of a 626-node VI?
4. Attack the premise: is there any way a subVI node can sit on a case frame's diagram and NOT execute when that frame is selected?

Cite NI documentation or LabVIEW Wiki. If a property does not exist in 2026, say so plainly.

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
