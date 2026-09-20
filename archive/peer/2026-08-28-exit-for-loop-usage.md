---
type: peer-review
status: historical
date: 2026-08-28
tags: [peer-review]
disposition: legacy
---

# exit-for-loop-usage

- **agent:** codex
- **date:** 2026-08-28
- **outcome:** ANSWERED (64s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW VI Scripting, erdosmiller/lv-scripting library (MIT). I am driving 'Exit For Loop.vi' from my own scripting VI and its wires come out BROKEN. Its terminals appear to be: 'Diagram in', 'Diagram out', 'Outputs', 'Indexing', 'error in (no error)', 'error out'. Questions: (1) What EXACT reference type does 'Diagram in' expect - the For Loop's inner/body Diagram reference, an AbstractDiagram, or the TOP-LEVEL diagram that owns the loop? (2) What does 'Outputs' expect - an array of Terminal references from Get Outputs.vi run on a node INSIDE the loop, or something else (an array of a typedef cluster)? What is its exact wire datatype? (3) What is 'Indexing' - a Boolean, or an enum/typedef such as 'Loop Terminal Types'? What value means auto-indexed output tunnel? (4) Show the canonical calling pattern: which library VIs feed Exit For Loop in the shipped examples (Example 8 - For Loops), in order. Cite the repo file paths or forum URLs you rely on.

## Answer

I can?셳 establish the exact connector datatypes from the public web evidence available here. The GitHub repository exposes these as compiled `.vi` files, not textual source, and its README only confirms that the shipped examples are the intended documentation. Guessing would be unsafe. [Repository README](https://github.com/erdosmiller/lv-scripting)

What would settle all four questions cheaply: have the manager produce plain-text reporter output for:

- `Exit For Loop.vi`: connector-pane terminals, terminal datatype strings/type descriptors, typedef paths, and block-diagram object/wire listing.
- `Example 8 - For Loops.vi`: subVI labels plus wire source/destination terminals.
- Any typedef referenced by `Outputs` or `Indexing`.
- `Get Outputs.vi` and the VI that creates/enters the For Loop.

I would specifically test these likely interpretations, but they remain hypotheses?봭ot verified facts:

1. `Diagram in` is probably the loop?셲 body/subdiagram reference, because a tunnel created on a structure boundary must be wired relative to the structure?셲 internal diagram. I cannot confirm whether its declared class is `Diagram`, `AbstractDiagram`, or another reference superclass.

2. `Outputs` is probably not merely arbitrary terminal references from a node. Its plural name and the existence of a dedicated `Get Outputs.vi` suggest that the intended input is that helper?셲 complete output?봯ossibly an array of library-defined output-description clusters. Exact reporter datatype information is required.

3. `Indexing` may be a scalar Boolean or a parallel array matching `Outputs`; I found no reliable public source establishing either. Do not substitute a guessed `Loop Terminal Types` enum value.

4. The canonical sequence must be recovered from `Example 8 - For Loops.vi`; GitHub does not render its compiled diagram. The repository identifies Examples 1??3 as the authoritative learning material, but does not document their internal call graph textually. [README, ?쏬earning to Use LV-Scripting??(https://github.com/erdosmiller/lv-scripting#learning-to-use-lv-scripting)

So the defensible answer is: **the public repository page alone cannot establish the exact types or call order.** A connector/type reporter and diagram listing for those five VIs would settle it without opening or executing LabVIEW here.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
