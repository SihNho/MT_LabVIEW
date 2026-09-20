---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review]
---

# movebyindex-fail1-execstate0

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (76s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS (LabVIEW 2026 VI Scripting over COM, zero GUI). Log: tools/bench/cycle3b_toolkit.log item 1 (tools/recipes/build_opmovebyindex.py). OpMoveByIndex_v0 = copy of OpMoveByLabel_v0 (your plan, archive/peer/2026-09-15-strtopath-fail3-move-by-index-plan.md). Every surgery gate passed with wire uids equal on both ends: OVOR deleted (14 -> 8 wires; Move.reference unwired, Move.owner wire 738 intact); PN_src.'error out' -> PN_tgt.'error in' (149); Traverse for GObjects.vi dropped, 'VI Refnum' <- Revert-VI invoke 'reference out' (946, branch); control on Traverse.'Class Name'; Index Array: 'References' -> 'array' (319); control on IA.'index'; IA.'element' -> Move.'reference' (336) and -> PN GObject[UID].'reference' (336, branch); indicator on UID; control on Move.'duplicate' (label 'Duplicate? (F)'). RESULT: ExecState 0 (broken), predicted 1. Nothing saved.
Candidates: (a) a REQUIRED input of Traverse for GObjects left unwired ('Traverse Target' ring? 'error in'?) - which of its inputs are required per the shipped VI (vi.lib\Utility\traverseref.llb\Traverse for GObjects.vi)? (b) Move's 'reference' (GObject) fed from an Index Array element of a GObject-refnum ARRAY: the Traverse 'References' output type is an array of GObject refnums - should be exactly the Move invoke's class; or is the Invoke node typed to a more specific class in the donor (its OVOR fed it a class chosen by the class-specifier constant - e.g. Node/Control), so a plain GObject wire is a class-conflict broken wire (error 1057 family at compile time)? (c) the deleted OVOR's 'error in' chain: PN_tgt.'error out' (539) -> Move.'error in'; Traverse's own error out unconnected - not an error. (d) an unwired REQUIRED terminal on the branch 'reference out' of the Revert invoke: no. (e) the IA.'index' control creation (I32) fine. (f) two consumers of IA.element (Move + PN): fine.
Rank these; name the single cheapest read-only discriminator the fleet can run (it has: node terminals with wire uids, node labels, class counts, ExecState; no 'VI:Get Errors' reader). If (b): the fix (retype the Invoke's class to GObject? or insert To More Specific Class - the fleet has no class-specifier constants; the typed-seed trick exists for WhileLoop/ForLoop only)? If (a): which input and what constant/control to add (the fleet can create controls from terminals). Cite what you read.


## Answer

Most likely both (a) and (b) are present, with (a) the first thing to fix.

Ranking:

1. **(a) Unwired `Traverse Target` ??very likely.** `Traverse for GObjects.vi` requires selecting what is traversed: `0=FP`, `1=BD`, `2=Other`. Your recipe wires `VI Refnum` and `Class Name` but apparently creates nothing on `Traverse Target`. For this operation it must be **BD (I32/ring value 1)**. `error in` and `Traverse Generated Code` have usable defaults; `Other Refnum` is ignored for FP/BD. The published connector description lists all these inputs and their semantics. [Traverse for GObjects connector documentation](https://rajsite.github.io/unofficial-lvdocs/glang/TRef_Traverse_for_References.html)

2. **(b) Retained specific Invoke-node class ??also highly plausible.** `References` is explicitly an array of **GObject references**, and the documentation says to downcast elements with `To More Specific Class` only when necessary. [Traverse for GObjects connector documentation](https://rajsite.github.io/unofficial-lvdocs/glang/TRef_Traverse_for_References.html) The `Move` method itself belongs to the **GObject class**, so no downcast is logically necessary: a GObject-typed Move Invoke node is the correct consumer. [GObject `Move` method](https://labviewwiki.org/wiki/GObject_class/Move_method) However, if the copied donor Invoke node retained a subclass reference terminal established by the old OVOR output, feeding it a parent GObject wire is a class conflict even though UID 336 appears at both endpoints. NI confirms incompatible endpoint types produce broken wires. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

3. **(c) Error-chain arrangement ??unlikely.** An unconnected `Traverse.error out` cannot break the caller; required status applies to inputs, not outputs. Recommended and optional terminals may remain unwired without breaking execution. [NI required-terminal documentation](https://www.ni.com/docs/ar-IQ/csh?context=lvcore_lvhowto_specifying_required_recomm)

4. **(d) Branched Revert `reference out` ??essentially ruled out.** Outputs need not be consumed, and branching an output is ordinary LabVIEW dataflow. [NI required-terminal documentation](https://www.ni.com/docs/ar-IQ/csh?context=lvcore_lvhowto_specifying_required_recomm)

5. **(e)/(f) Index control and two consumers ??effectively ruled out.** An I32 index is normal for Index Array, and fan-out to multiple consumers is legal unless one consumer demands an incompatible type. The latter collapses back into (b), not a branching defect. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

The single cheapest read-only discriminator is:

> **Report the class counts after construction and ask specifically whether a `BrokenWire` object exists.**

- `BrokenWire > 0` strongly selects **(b)**: UID equality proves connectivity, not type compatibility.
- `BrokenWire = 0` with `ExecState=0` strongly selects **(a)** or another required unwired terminal.
- If class counts cannot distinguish broken from valid wires, the next-cheapest report is simply the Traverse terminal table: verify `Traverse Target.wire_uid != 0`.

Fix order:

1. Create a control/constant from `Traverse Target` and set it to **BD = 1**.
2. Recheck `ExecState`.
3. If still broken, **retype/recreate the Invoke node as `Generic 쨩 GObject 쨩 Move`** and reconnect UID 336. Do not add `To More Specific Class`: the Traverse result and the owning class of `Move` are both GObject. A class-specifier constant is only needed for an actual downcast. [NI class-specifier documentation](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/constants/class-specifier.html)

I would not invest in a typed-seed workaround here. The clean solution for (b) is a GObject-typed Move Invoke node.

## Sources

(extract from answer)

## What was done with it

Both fixes adopted in `tools/recipes/build_opmovebyindex.py`, in the reviewer's order: (a) a control on
`Traverse Target` (the caller sets 1 = BD; `gscript.copy_by_index` does so); the `BrokenWire` class count is
printed as the read-only discriminator; then, ONLY if ExecState is still 0, declared plan B: the donor's Move invoke
is deleted and recreated as a GObject-class `Move` (632A400) with its four feeds rewired from the recorded sources.
No `To More Specific Class` (Traverse elements and `Move`'s owning class are both GObject). Rerun:
`tools/bench/cycle3b_toolkit.log` (run 2).
