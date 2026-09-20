---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# addshiftreg-fail1-branch-or-decline

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (91s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS DIAGNOSIS. Do not confirm it. A prediction failed during LabVIEW VI-Scripting work and I must not act on my own explanation without it being challenged.

WHAT WAS BUILT. OpAddShiftReg_v0.vi = a copy of OpWhileCast_v0.vi (an op VI that holds a WhileLoop-TYPED reference produced by a To More Specific Class node, uid 683, output terminal "specific class reference"). I added an Invoke node configured as class "VI Server:Loop", method ID 6361000 (Loop.Add Shift Register), then tried to wire the TMSC output into the Invoke's "reference" input with branch=True (the TMSC output already feeds two Property nodes).

PREDICTED: Wire count +1 and ExecState 1.
OBSERVED (tools/bench/build_opaddshiftreg_v0.log): Invoke created with terminals ['reference','reference out','error in (no error)','error out','Add Shift Register','Add Shift Register','Y Position','Y Position'] - so the METHOD ATTACHED (not a private-member failure). After the wire call: Wire count unchanged at 16, ExecState 0. The recipe treated that as "the WhileLoop reference is not accepted by a Loop-class invoke" and stopped.

MY EXPLANATION, which you must try to refute:
(a) the branch actually SUCCEEDED - this project's own skill states "a successful BRANCH adds no Wire object", so an unchanged wire count is the expected signature of a branch, not of a decline;
(b) ExecState 0 is fully explained by the Invoke's required "Y Position" input still being unwired at the moment of the check (the recipe creates that control only AFTER the gate), not by any type mismatch;
(c) a WhileLoop reference is legally accepted by an Invoke node configured for the parent class Loop (upcast), so no TMSC retarget to a WhileLoop-class invoke is needed.

ATTACK ALL THREE. Specifically:
1. Is "Y Position" a REQUIRED input of Loop.Add Shift Register, or recommended/optional with a default? If it is optional, my explanation (b) collapses and the ExecState 0 means something else - what?
2. Can a LabVIEW scripting Invoke node configured for class Loop accept a WhileLoop reference without a cast, or does LabVIEW require the invoke's class to match exactly? Is there a known failure mode where such a wire is silently refused?
3. The terminal list shows DUPLICATE names ('Add Shift Register' twice, 'Y Position' twice). What does a duplicated terminal name on a scripting Invoke node mean, and can it make a wire-by-NAME call land on the wrong (output) terminal and be silently declined? This project hit exactly that trap before (archive/peer/2026-09-14-opqueue-fail1-duplicate-error-out.md, archive/peer/2026-09-14-opexitwhile-fail1-duplicate-terminal-names.md - read them).
4. Name the single cheapest DISCRIMINATING test that separates "the branch landed" from "the branch was declined", using only read-only reporter calls on the already-open VI.
5. Is there a better route entirely: should the invoke be configured as class WhileLoop instead of Loop, and does method 6361000 appear on WhileLoop?

Read docs/stage2-assembly-step-a.md, docs/NAMES.md (line ~234 for the Loop class IDs) and tools/bench/build_opaddshiftreg_v0.log in this project directory. Cite file paths and documentation URLs you actually read. Read-only: change nothing, do not open LabVIEW.


## Answer

The diagnosis is not safe to act on yet. Parts (b) and (c) are plausible, but the failed gate proves neither. Part (a) is especially vulnerable because `branch=True` disables verification; it does not establish that a branch landed.

1. `Y Position` is required?봟ut that does not exonerate the reference wire

The method catalogue identifies `Loop.Add Shift Register` as method `6361000`, owned by `Loop` class `16405`. It has:

- required input: `Y Position`
- required return value: `RightShiftRegister` reference

See [LabVIEW Wiki: Loop.Add Shift Register](https://labviewwiki.org/wiki/Loop_class/Add_Shift_Register_method). This agrees with the local registry in [docs/NAMES.md](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/NAMES.md) and the recipe?셲 own description in [build_opaddshiftreg_v0.py](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_opaddshiftreg_v0.py:9).

Therefore, immediately after creating the Invoke node, before wiring `Y Position`, `ExecState 0` is expected.

But your stronger claim?붴쏣xecState 0 is fully explained by Y Position?앪봡oes not follow. A required unwired `Y Position` masks every other possible fault:

```text
reference landed, Y unwired       ??ExecState 0
reference declined, Y unwired     ??ExecState 0
reference landed on bad terminal  ??ExecState 0
broken reference wire, Y unwired  ??ExecState 0
```

So the A1b `ExecState` gate was intrinsically non-discriminating. The recipe should not have interpreted it as a class rejection, but neither can it be interpreted as evidence that the branch succeeded.

2. `branch=True` is not evidence of success

The local implementation is decisive here. In [tools/gscript.py](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:975), `branch=True` merely skips the expected wire-count increase. It does not select a special branch-capable connection operation.

Worse, the same function documents that its underlying name-based wiring operation can silently decline a connection from an already-wired source. The automation reference also says:

> branching from an already-wired source terminal is declined silently

That is in [.agents/skills/labview-automation/references/vi-scripting.md](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/.agents/skills/labview-automation/references/vi-scripting.md).

Thus:

- unchanged wire count is compatible with a successful branch;
- unchanged wire count is equally compatible with a silent decline;
- `branch=True` suppresses the only check that would otherwise complain;
- `ExecState 0` cannot resolve the ambiguity because `Y Position` is required and unwired.

This directly attacks (a): the observation does not show success.

There is also an internal inconsistency worth fixing. `gscript.wire()` says its library-backed operation may decline an already-wired source, while `connect_terminals()` documents native `Terminal.Connect Wire` as successfully branching an already-wired source. Those are different operations and should not share the same inferred semantics.

3. A WhileLoop reference should be legal on a Loop-class Invoke?봟ut this run did not test that cleanly

NI describes VI Server as an object-oriented class hierarchy in which subclasses inherit the properties and methods of higher-level classes. `WhileLoop` is a subclass of `Loop`; therefore a WhileLoop reference should be usable where a Loop reference is required. [NI: What Is the VI Server?](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019MTCSA2&l=en-US)

NI also explains the general LabVIEW inheritance rule that a child object is valid on a parent-typed wire. [NI: LabVIEW OOP design and inheritance](https://www.ni.com/en/support/documentation/supplemental/06/labview-object-oriented-programming--the-decisions-behind-the-de.html)

I found no NI documentation saying an Invoke node requires an exact VI Server class match. Exact matching would largely defeat inherited VI Server methods.

Nevertheless, (c) remains unproved experimentally because the connection mechanism itself may have declined the already-wired source. The present result cannot distinguish:

- legal upcast plus successful branch;
- legal upcast plus branch API decline;
- actual class conflict;
- wrong terminal resolution.

If there were a real class conflict, the expected diagram evidence would be a broken wire/class-conflict report, not merely no new Wire object. The local scripting guide documents precisely that behavior for GObject-to-Node mismatches.

4. Duplicate terminal names are real, but probably did not select the wrong `reference` terminal

The duplicate names almost certainly represent opposite-direction terminals associated with the method parameters:

- one `Add Shift Register` is the method?셲 returned `RightShiftRegister` reference;
- the other is the corresponding opposite-side/name representation exposed by `Node.Terminals[]`;
- similarly, the two `Y Position` entries must be separated by `is_source`, not by name.

LabVIEW?셲 method-node representation permits parameters to have input, output, or both terminals. [NI patent description of method-node terminals](https://patentimages.storage.googleapis.com/ae/81/9e/c6d256c004507d/US7937665.pdf) The independently generated VI Server catalogue also records that LabVIEW exports some Invoke methods with duplicated terminal names, so this is not necessarily a reporter duplication bug. [Zuehlke LabVIEW MCP VI Server reference](https://github.com/Zuehlke/labview-mcp/blob/main/docs/vi-server-reference.md)

The two authorized prior incidents demonstrate exactly why name-only addressing is unsafe:

- [duplicate error-out incident](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/archive/peer/2026-09-14-opqueue-fail1-duplicate-error-out.md)
- [duplicate Outputs/Shift Registers incident](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/archive/peer/2026-09-14-opexitwhile-fail1-duplicate-terminal-names.md)

However, A1b targeted `"reference"`, which appears only once in the reported list. Therefore duplicate method-parameter names are not the leading explanation for that particular attempted connection.

They will break later recipe steps unless direction/index is used:

- select `Y Position` where `is_source == False`;
- select the returned shift-register reference where `is_source == True`;
- never pass the duplicate name back into `g.wire()` and assume it will choose the intended side.

The recipe partially recognizes this when finding terminal indices at lines 163??74, but then throws the index away and later wires the return by its ambiguous name at line 182. That is unsafe.

5. Cheapest discriminating test

Make one read-only `node_terms` reporter call for the new Invoke node and inspect its unique `reference` input:

```text
Invoke.reference wire UID == 0
    ??branch was declined / never landed

Invoke.reference wire UID != 0
    ??branch landed, or a broken wire object landed
```

Then compare that UID with the TMSC output?셲 existing connected-wire UID:

```text
Invoke.reference UID == TMSC.specific-class-reference UID
    ??successful branch onto the existing net

Invoke.reference UID == 0
    ??silent decline

Invoke.reference UID != 0 but differs
    ??separate/broken/rerouted connection; inspect error fields
```

Because a successful branch shares the existing Wire object, equality of the two terminal-reported wire UIDs is the discriminator that raw wire count lacks. The reporter already returns `name`, `is_source`, `wire`, and connection/wire error codes, as documented in [tools/gscript.py](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:586).

6. Do not retarget the Invoke to WhileLoop

`6361000` is owned by `Loop`, not `WhileLoop`. The WhileLoop class inherits it, but the catalogue does not show a separate WhileLoop-owned copy of method `6361000`. [LabVIEW Wiki: Loop.Add Shift Register](https://labviewwiki.org/wiki/Loop_class/Add_Shift_Register_method)

Configuring the node as `WhileLoop` might expose the inherited method in the editor, but it is not a better first repair. It would conceal the actual uncertainty: whether this name-based branch operation can branch from an already-wired source.

The cleaner next test is:

1. Read the Invoke `reference` terminal?셲 wire UID.
2. If zero, use the already-verified index-based native `Terminal.Connect Wire` route, which this project says supports branching.
3. Wire required `Y Position` by terminal index/direction.
4. Wire the returned reference by terminal index/direction.
5. Only then use `ExecState`.

Bottom line: reject the original recipe?셲 ?쏬oop rejects WhileLoop??conclusion, but also reject your ?쐔he branch succeeded??conclusion. The existing evidence establishes neither. The single Invoke-terminal wire-UID report settles the central question cheaply.

## Sources

(extract from answer)

## What was done with it

**The review was right to refuse both conclusions, and the measurement then settled the question.**
`tools/bench/diag_addsr_fail1.py` (the reviewer's own cheapest discriminator — compare the wire UID reported on the
two terminal ends, which raw wire count cannot give) ran at 22:33, `tools/bench/diag_addsr_fail1.log`:

- TMSC `specific class reference` (source) = wire **366**; Invoke `reference` (sink) = wire **366** → **the branch
  landed**. A `Loop`-class Invoke node DOES accept a `WhileLoop` reference (inheritance upcast), so the stopped
  recipe's message "the WhileLoop reference is not accepted by a Loop-class invoke" was simply wrong.
- `ExecState 0` at that moment was the required-and-unwired `Y Position`, as suspected — but the reviewer's point
  stands: that gate could not have told the difference, and my "the branch succeeded" was not established by the
  evidence I had when I wrote it.
- Duplicate terminal names measured, both directions present: `Y Position` 6 = sink / 7 = source;
  `Add Shift Register` 4 = sink / 5 = source (the return).

Recipe repairs adopted from the review (`tools/recipes/build_opaddshiftreg_v0.py`): the A1b gate is now the wire-UID
equality, not `ExecState`; `ExecState` is checked only at the end, after every required input is wired; the return
reference is wired **by index** with `connect_terminals`, not by its duplicated name (the reviewer caught that the
recipe computed the indices and then threw them away); and the op's panel is closed on every exit path, which run 1
failed to do and which cost a LabVIEW restart. Rerun as a NEW batch: `build_opaddshiftreg_v0_run2.log`.

Not adopted: retargeting the Invoke to class `WhileLoop` — `6361000` is owned by `Loop` and the upcast is now
measured to work.
