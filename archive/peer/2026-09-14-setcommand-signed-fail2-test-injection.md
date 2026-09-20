---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# setcommand-signed-fail2-test-injection

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (33s)
- **why asked:** failed prediction in build_setcommand_signed.log run 2 (create_control inside the case frame produced nothing: top-level Nodes[] scope) and the copy_into injection plan
- **verdict:** unverified

## Question

FAILED PREDICTION check (brief). tools/bench/build_setcommand_signed.log run 2 (tools/recipes/build_setcommand_signed.py): the deliverable SetCommand_signed.vi built and saved (wire-by-name inside the case frame worked: Hex.number -> Type Cast.x -> Multiply.x, ExecState 1). The TEST copy step failed: create_control on String Subset.string returned no control after ~8 s - the SAME top-level Nodes[] scope limitation as run 1 (Terminal.Create Control op resolves VI.Block Diagram -> Nodes[]; the node is inside the case frame). FIX (plan change): inject the reply through an EXISTING string control moved in by our object mover: copy_into(OpSetLabel_v0.vi, 'Text', SetCommand_signed_TEST.vi) (front-panel objects move by label - proven for indicators), then delete the VISA Read -> String Subset.string wire and wire_control(['Text'] -> Function[String Subset].'string') (erdosmiller Wire Inputs from a control terminal into a node inside a structure auto-creates the tunnel - measured 2026-09-09 on a Case structure). ATTACK: (a) agree the failure is tool scope, not a LabVIEW refusal; (b) any risk that a control terminal wired into ONE case frame leaves the tunnel 'unwired in other cases' - for an INPUT tunnel LabVIEW allows unused inputs in other cases, so ExecState should stay 1 - correct?; (c) the moved control keeps the label 'Text' - fine for SetControlValue; anything about copy_into on a VI whose diagram is a case structure.

## Answer

Prediction is sound, with one caveat.

- **(a) Agree.** The repeat failure is consistent with the operation searching only the top-level block diagram: NI defines `All Objects[]` as returning only top-level objects, while the target terminal is owned by the case subdiagram. The successful in-frame wiring also argues against a LabVIEW refusal. Still, classify this as ?쐓trongly demonstrated tool traversal limitation,??not a universal limitation of `Create Control`. [NI VI Server documentation](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/abstractdiagram/allobjects.html)

- **(b) Correct.** This creates an **input tunnel**. The input is available to every case, but cases do not have to consume it. The all-cases wiring requirement applies to **output tunnels**, so an unused input in other frames should not break the VI or prevent `ExecState == 1`. [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999e.pdf)

- **(c) Mostly safe.** A copied front-panel string control brings a corresponding block-diagram terminal; wiring that top-level terminal to the node inside the case can create the input tunnel. [NI front-panel documentation](https://www.ni.com/en/support/documentation/supplemental/08/labview-front-panel-explained.html) A case structure as the diagram?셲 top-level node is not itself a special obstacle.

Cheap checks before trusting the test:

1. Confirm the destination has exactly one owned label `Text`; LabVIEW uses owned labels to associate diagram objects with controls. [NI local-variable documentation](https://www.ni.com/docs/en-GB/bundle/labview/page/local-variables.html)
2. Confirm `Text` is a **string control**, not an indicator.
3. After deleting the VISA wire and adding the new wire, verify one new input tunnel, `String Subset.string` has exactly one source, and `ExecState == 1`.

Main residual risk: `copy_into` may preserve the label but place/rename it due to a collision. That is a copier/name-resolution risk, not a case-structure restriction.

## Sources

(extract from answer)

## What was done with it

Confirmed: copy_into + wire_control injected the string control into the frame (run 5, +2 wires = tunnel crossing). Verdict: correct.
