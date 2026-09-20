---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# opshiftregs-v1-fail1-wrong-index-array

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (17s)
- **why asked:** failed gate in build_opshiftregs_v1.log run 1 (ExecState 0) - explanation: the wrong Index Array (the donor Traverse one) was wired
- **verdict:** unverified

## Question

FAILED PREDICTION check (brief, one paragraph). tools/bench/build_opshiftregs_v1.log (tools/recipes/build_opshiftregs_v1.py): the GATE 'wire the Index Array element into a RightShiftRegister[Left Registers[]] property node -> ExecState 1' came back ExecState 0. MY EXPLANATION (from the log itself): the op has TWO Index Arrays with a wired 'index' input - uid 308 (the donor's Traverse-by-index IA: array wire 600 from Traverse for GObjects, element typed GObject) and uid 657 (v0's register selector: array wire 558 from Loop.Shift Registers[], index from the 'index 2' control) - and my selector ('the IA whose index is wired', last match wins) picked 308, so the RightShiftRegister node was fed a GObject-typed element and broke. The gate therefore tested nothing about the Shift Registers[] element type. FIX: select the IA whose 'array' wire equals the data-terminal wire of the Loop[Shift Registers[]] property node (wire identity, not position/index), then rerun the same gate. ATTACK: (a) agree the log supports 'wrong IA' rather than 'element not RightShiftRegister-typed'? (b) anything else in the log that would keep ExecState 0 even with the right IA (e.g. branching an already-wired element terminal - v0 already branches element to the Class Name node; wire count stayed 46 = branch accepted).

## Answer

Yes?봳he described log evidence supports ?쐗rong Index Array selected??more strongly than ?쏶hift Registers[] element is not RightShiftRegister-typed?? UID 308 receives the Traverse-for-GObjects output, so wiring its GObject-typed element into `Left Registers[]` plausibly explains `ExecState 0` without testing UID 657?셲 type. Your wire-identity fix is the right discriminator. Nothing else you report independently predicts failure with UID 657: the unchanged wire count of 46 is consistent with adding a branch to an existing wire rather than creating a new wire, so the existing Class Name branch is not evidence that the element terminal rejected another branch. One caveat: the rerun should verify the selected IA?셲 array terminal is connected by the exact wire UID from `Loop[Shift Registers[]]`, and verify the new branch actually has endpoints at UID 657?셲 element terminal and `Left Registers[]`; otherwise `ExecState 1` alone could again be a weak gate. No external claims used.

## Sources

(extract from answer)

## What was done with it

Selector rewritten to wire identity (the IA whose `array` wire == the `ShiftRegs[]` data wire, 558 → IA 657); rerun
(build_opshiftregs_v1.log 17:27): the RightShiftRegister[Left Registers[]] node accepted the element, ExecState 1 -
the static type of `Loop.Shift Registers[]` IS RightShiftRegister[] as the earlier review predicted, no seed needed;
the whole left-side chain built and saved. Verdict: correct.
