---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# setcommand-signed-fail1-nodes-index-scope

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (21s)
- **why asked:** failed prediction in build_setcommand_signed.log run 1 (connect_terminals returned (0,0) inside the case frame: top-level Nodes[] scope)
- **verdict:** unverified

## Question

FAILED PREDICTION check (brief). tools/bench/build_setcommand_signed.log (tools/recipes/build_setcommand_signed.py): after deleting the two wires inside the driver's read CASE FRAME (Traverse diagram 1), the three connect_terminals calls and the connect_ctl call returned (0, 0) after ~8 s each (our known 'out-of-range Nodes[] index -> 8-s dialog' signature) and error 1055, leaving every target terminal unwired. MY EXPLANATION: OpConnect_v0 / OpConnectCtl_v0 resolve node indices through VI.Block Diagram -> Nodes[] = the TOP-LEVEL diagram only (it holds one node, the case structure), while I passed Nodes[] indices measured on diagram 1 (3, 4, 5, 8) - a tool-scope error, not a LabVIEW refusal. FIX: use gscript.wire() (erdosmiller Wire Inputs: Traverse class 'Function' + index + terminal NAME - proven inside loop bodies) for substring->Hex.string, Hex.number->TypeCast.x, TypeCast.out->Multiply.x, and Wire Indicators (by name) for the 'read buffer 2' indicator. ATTACK: (a) agree? (b) any reason Wire Inputs would refuse a wire whose source and sink are inside the same case frame (it worked inside For-loop bodies); (c) note the deletions already happened on the in-memory copy - the recipe restarts from a fresh copy, so no residue.

## Answer

Yes?봸our explanation fits the evidence.

- The repeated ~8-second failures plus error 1055 strongly support invalid `Nodes[]` lookup scope, especially since every attempted index failed uniformly.
- Wire Inputs should not inherently refuse same-case-frame wiring. The relevant constraint is that both terminals resolve within the same diagram context; a case subdiagram is no less wireable than a For-loop subdiagram.
- Your proposed replacements correctly avoid top-level `Nodes[]` indexing: `gscript.wire()` for the three function-terminal connections and Wire Indicators for `read buffer 2`.
- Restarting from a fresh source copy eliminates residue from the already-deleted in-memory wires.

One caveat: confirm the terminal names (`string`, `number`, `x`, `out`) match the primitives??reporter output exactly. Otherwise the new method could fail for terminal-name resolution while the underlying scope diagnosis remains correct.

## Sources

(extract from answer)

## What was done with it

Confirmed: wire() by Traverse class + name wired all three connections inside the frame (run 2). Verdict: correct.
