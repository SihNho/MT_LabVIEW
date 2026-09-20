---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# opshiftregs-v0-elements-are-right-registers

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (85s)
- **why asked:** failed prediction in test_opshiftregs.log (all 14 elements are RightShiftRegister, not Left) and the v1 plan (Left Registers[])
- **verdict:** unverified

## Question

FAILED PREDICTION review (attack; one paragraph + IDs). tools/bench/test_opshiftregs.log (OpShiftRegs_v0 built by tools/recipes/build_opshiftregs_v0.py, donor OpWhileCast_v0): the Tunnel-only census on the main VI's frame loop (WhileLoop uid 637) ran clean on all 14 elements of Loop.Shift Registers[] 6361402: GObject.Class Name = 'RightShiftRegister' for ALL 14 (your inference was 14 LeftShiftRegisters - refuted), each with exactly one Inside Terminal (sink, wired; names = 'total data array out', 'error out', 'LastBufferNumber', 'pos in cal image out', 'Bead is good? array out', 'F-x out', 'Value' x2, 'System no.', 2 unnamed, ...) and an Outside Terminal (source; only 4 of 14 wired = final values consumed after the loop). So Loop.Shift Registers[] enumerates the RIGHT registers (one per pair), which already names 14 per-frame state carriers and their body-side feed wires. Is Source? semantics matched your reading for the right side (inside sink, outside source). NEXT (v1): from each right register reach its LEFT register(s): outside terminal (initial value, sink; 0 = uninitialised) and inside terminal (source into the body) to close the frame loop's remaining half-edges; stacked lefts give several. QUESTIONS: (1) which property on RightShiftRegister returns the left register(s) - LabVIEW Wiki RightShiftRegister class: 'Left Shift Registers[]' ? give the ID and whether it is an array (stacked) ; (2) is LeftShiftRegister 6374C00 'Right Shift Register' the inverse (yes per earlier review) - so pairing from the right side is the natural direction here; (3) the seed question: a RightShiftRegister-class property node needs a RightShiftRegister-typed reference: the Index Array element of Loop.Shift Registers[] is typed how (generic Tunnel? ShiftRegister? the Tunnel-class property node compiled on it, GObject.Class Name reads RightShiftRegister at run time) - will a 'VI Server:RightShiftRegister' property node compile directly on that element, or do we need a typed seed (NI example with a RightShiftRegister property node? none found in the Structures examples) - what is the cheapest test; (4) anything else the census result changes in the plan (e.g. 'Value' x2 and two unnamed registers: the name is the inside terminal's name = the wire's label?).

## Answer

The failed prediction changes v1 in your favor: traverse **right ??left**, using `RightShiftRegister.Left Registers[]` **ID `6357800`**, a **1-D array of `LeftShiftRegister` references**?봧ncluding every stacked history element; `LeftShiftRegister.Right Shift Register` **ID `6374C00`** is the scalar inverse, so starting from the one right register returned by `Loop.Shift Registers[]` avoids duplicate pairing ([LabVIEW structure anatomy](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/anatomy.html), [inverse property](https://www.labviewwiki.org/wiki/LeftShiftRegister_class/Right_Shift_Register_property)). The most likely static type of `Loop.Shift Registers[]` **ID `6361402`** is therefore `RightShiftRegister[]`, not generic `Tunnel[]`: Index Array preserves its array element type, while successful wiring to a `Tunnel` node proves only legal upcasting because `RightShiftRegister` inherits `Tunnel`; runtime `Class Name` cannot settle the wire type. Consequently, first try wiring the existing Index Array element directly to a `VI Server:RightShiftRegister` node containing only `Left Registers[] 6357800`; the cheapest decisive gate is simply **wire accepted + `ExecState == 1`**, then run one register and require a nonempty left-ref array whose elements report `LeftShiftRegister`, followed by Tunnel properties `Inside Terminals[] 6356000` and `Outside Terminal 6356001`. If the wire breaks with class conflict, then a typed seed/TMSC is required; derive it from `Create Control` on the `reference` input of a donor RightShiftRegister property node, not from runtime class inspection?봏I?셲 documented pattern for generic arrays is to cast their indexed element before using subclass properties ([NI VI Server casting example](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YHhtCAG)). Finally, preserve terminal UID and wire UID: the two `Value` names and two blanks are not stable carrier identities, and `Terminal.Name` is **not evidence that the wire owns that label**?봶ire labels are separate owned labels?봲o use the name only as annotation and stitch by UIDs ([NI wire-label documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)). **IDs:** RightShiftRegister class `16399`; `Left Registers[] 6357800`; `Is An Error Register 6357801`; LeftShiftRegister class `16442`; `Right Shift Register 6374C00`; inherited Tunnel `Inside Terminals[] 6356000`, `Outside Terminal 6356001`; Loop `Shift Registers[] 6361402`.

## Sources

(extract from answer)

## What was done with it

Built OpShiftRegs_v1 exactly as advised: the Index Array element wired straight into a RightShiftRegister[Left
Registers[] 6357800] node compiled (static type RightShiftRegister[], as predicted) once the RIGHT Index Array was
selected by wire identity (run 1 had picked the donor's Traverse IA — separate review); test_opshiftregs_v1.log 8/8:
14 lefts, all LeftShiftRegister, no stacking, 13 initialised. UIDs, not names, are the stitch keys in
docs/frame-loop-wire-graph.md as the reviewer required. Verdict: correct and decisive.
