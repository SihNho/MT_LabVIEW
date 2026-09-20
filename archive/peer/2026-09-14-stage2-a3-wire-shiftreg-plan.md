---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, stage2, plan]
---

# stage2-a3-wire-shiftreg-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (122s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS PLAN, do not confirm it. LabVIEW 2026 VI Scripting from Python/COM, zero GUI. Read docs/stage2-assembly-step-a3.md (the plan), docs/stage2-assembly-step-a.md, docs/NAMES.md (search "Loop /" and "Shift registers are CREATABLE"), tools/recipes/build_opconnectctl_v0.py and tools/recipes/build_opshiftregs_v1.py in this project directory.

The plan wires a script-created shift register's three terminals with Terminal.Connect Wire (6349C03, invoked on the SINK, Wire Source = source), reaching every terminal through TYPED property chains with no To-More-Specific-Class cast. Attack specifically:
1. Loop.Diagram (6361401) on a WhileLoop-typed reference: does it return the loop's BODY (subdiagram) or the diagram that OWNS the loop? If it returns the body, is AbstractDiagram.Nodes[] on it the right way to enumerate nodes inside the loop, and are structure-border objects (tunnels, shift registers) included in Nodes[] in a way that shifts indices?
2. Connect Wire where the SINK is a shift register's terminal (right INSIDE, left OUTSIDE): are those terminals legal Connect Wire destinations, or must the wire be created from the source side / via a different method for structure terminals? Any documented restriction for LeftShiftRegister/RightShiftRegister terminals?
3. Connect Wire where the SOURCE is the left register's INSIDE terminal feeding a node input inside the body - legal? Direction sensitivity confirmed?
4. The functional test drives an IMAQ image refnum through the register (IMAQ Create.New Image -> left outside; left inside -> IMAQ Copy.Image Dst; Image Dst Out -> right inside). Is a shift register of image-refnum type going to compile to ExecState 1 with an otherwise empty While loop, and does the VI terminate when the stop control is TRUE? Name anything that would keep ExecState at 0 even with all three wires present.
5. For the LeftOutCtl variant the plan deliberately wires a STRING control into an image-typed register and predicts "a broken wire". Is that prediction right, and can a broken wire be reliably deleted by script afterwards (this project uses VI method 'Remove Bad Wires' 410)?
6. Name the single cheapest discriminating test for question 1, and any better route for reaching a node inside a loop body than Loop.Diagram -> Nodes[].
Cite file paths and documentation URLs you actually read. Read-only, do not open LabVIEW.


## Answer

The plan is not ready to execute unchanged. The weakest point is not `Connect Wire`; it is the unverified assumption that `Loop.Diagram ??Nodes[n]` gives a stable, correctly scoped node reference. The functional test also conflates compile validity, wire creation, runtime behavior, and IMAQ resource validity.

1. `Loop.Diagram`: likely the body, but the plan has not proved it

A structure contains one or more subdiagrams, while the structure itself is a node in its parent diagram. Therefore, a `Diagram` property belonging to `Loop` is most naturally the loop?셲 body subdiagram, not the diagram owning the loop. NI describes structure code as residing in contained subdiagrams, and `AbstractDiagram.Nodes[]` as returning the nodes in that diagram. [NI Nodes[] reference](https://www.ni.com/docs/zh-CN/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/abstractdiagram/nodes.html), [LabVIEW Wiki block-diagram model](https://labviewwiki.org/wiki/Block_diagram)

But I found no NI page explicitly saying ??Loop.Diagram` returns the loop body.??Consequently this remains an inference, not documentation-grade confirmation. That agrees with [docs/NAMES.md](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/NAMES.md), which labels `Loop.Diagram 6361401` ?쐍ot yet verified on this machine.??A short name copied from an NI example proves that the member exists, not what object it returns.

If it is the body, `AbstractDiagram.Nodes[]` is the appropriate collection for ordinary nodes inside that body. The index assumption is still unsafe:

- The project already establishes that `Nodes[]` is creation order and differs from Traverse order in [docs/NAMES.md](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/NAMES.md).
- NI documents only ?쏿ll nodes in the diagram,??not whether loop-owned border objects participate in this collection. [NI Nodes[] reference](https://www.ni.com/docs/zh-CN/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/abstractdiagram/nodes.html)
- Tunnels and shift-register sides are owned by the structure border, not ordinary functions placed in the body. I would expect them not to shift body `Nodes[]` indices, but I did not find an authoritative promise. Treat that as unknown.
- Adding, deleting, or recreating any ordinary body node can still change indices. The recipe should resolve and verify the selected node UID immediately before connecting, not merely ?쐀eforehand.??
2. Shift-register terminals as `Connect Wire` destinations

There is good general evidence that structure terminals are legal wiring endpoints. NI describes shift registers conventionally as:

- outside source ??left register,
- left register ??body node,
- body node ??right register.

[NI shift-register tutorial](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YKYuCAO&l=en-US)

There is also practitioner evidence that `Terminal.Connect Wire` can connect terminals across different diagrams using an automatically routed wire. [NI Community answer by retired NI employee](https://forums.ni.com/t5/LabVIEW-APIs-Discussions/What-is-up-with-the-DeleteJoint-method/m-p/3384955)

I found no documented restriction excluding `LeftShiftRegister` or `RightShiftRegister` terminals. I also found no authoritative page guaranteeing them. Therefore:

- right INSIDE as sink: plausible and consistent with normal shift-register wiring;
- left OUTSIDE as sink: plausible and consistent with initialization;
- ?쐀oth are proven legal endpoints??in [docs/stage2-assembly-step-a.md](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/stage2-assembly-step-a.md) is too strong.

Creating the wire ?쐄rom the source side??should not be necessary. The API contract being used is destination-oriented: invoke on the destination terminal and supply `Wire Source`. The project?셲 existing [build_opconnectctl_v0.py](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_opconnectctl_v0.py) proves this for an ordinary node terminal, but not for a structure-border terminal.

3. Left INSIDE as source

Functionally, yes: the left inside shift-register terminal is the value available to code in the loop body, so it is a source. NI?셲 example explicitly wires the left register into a function input and the function output into the right register. [NI shift-register tutorial](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YKYuCAO&l=en-US)

Calling `Connect Wire` on the body node input with left INSIDE supplied as `Wire Source` is therefore directionally correct. General scripting guidance likewise says to invoke `Connect Wire` on individual terminals, and notes that the resulting wire can still be broken. [NI Community scripting example](https://forums.ni.com/t5/LabVIEW/scripting-create-array-indicator/m-p/3282674/highlight/true)

What is not confirmed externally is whether the specific `Inside Terminals[]` element returned for `LeftShiftRegister` is always the source terminal expected by `Connect Wire`. The project?셲 [build_opshiftregs_v1.py](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_opshiftregs_v1.py) reports `Is Source?`, but it only reads the terminal; it does not prove that `Connect Wire` accepts it.

4. The IMAQ functional test is underspecified

An IMAQ image wire carries a reference/pointer to an internal image object rather than copying the image buffer itself. Passing that reference through a shift register is type-consistent in principle. [NI IMAQ memory model](https://www.ni.com/en/support/documentation/supplemental/18/ni-imaq-memory-allocation.html), [NI IMAQ execution-order note](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P8khSAC)

With Stop-if-True and a TRUE value, a While Loop executes its body once and then terminates because the condition is evaluated after the body. [NI While Loop documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YJYUCA4)

That does not guarantee `ExecState == 1`. Possible reasons it remains zero even with the three intended shift-register wires present include:

- The stop conditional terminal is unwired or wired to the wrong terminal.
- `IMAQ Copy.Image Src` or `Image Dst` is unwired, misindexed, or connected by a broken wire. Required node inputs must be wired for the VI to run. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)
- One ?쐓uccessful??`Connect Wire` silently branched an existing net or connected a different terminal because the body-node or terminal index was stale.
- The register is typed inconsistently because the string test or another connection fixed its type first.
- A broken wire exists elsewhere in the scratch VI.
- A required connector-pane input on some inherited harness node remains unwired.
- A subVI is missing or itself broken.
- The loop condition is configured Continue-if-True rather than Stop-if-True; TRUE then causes it to continue indefinitely. [NI While Loop documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YJYUCA4)

IMAQ runtime validity is a separate issue. IMAQ image buffers use names, and NI documentation says created images require unique names. [NI IMAQ reference material](https://download.ni.com/support/manuals/322598a.pdf) Duplicate or stale image names can produce a runtime error without making the diagram uncompilable. The test must distinguish:

1. wire exists,
2. wire is not broken,
3. VI is executable,
4. VI runs once and returns,
5. IMAQ error output is clean.

The present prediction contract collapses those into one gate.

5. The string mismatch prediction is conditionally correct?봞nd risky

A string and an IMAQ image reference are incompatible types, so once the shift register has been fixed to the image-refnum type, connecting a string control should create a broken wire rather than a coercion. NI says incompatible types create broken wires, while only compatible conversions receive coercion dots. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

The missing condition is ordering. A newly created shift register is initially untyped. If the string wire lands first, the register may become string-typed, and one or more later IMAQ wires?봭ot the string wire?봫ay be the broken connection. Therefore the test must first prove that the three image connections exist and are healthy, then add the string wire.

Broken wires can be removed programmatically in principle; the UI operation removes broken wires, and the project already uses VI method 410. NI confirms that Remove Broken Wires deletes broken wires. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

It is not a reliable deletion mechanism for ?쐔he wire just created.??It removes all currently broken wires in scope, and deleting one bad upstream connection can cause downstream inferred-type wires to disappear too. That cascading behavior is already recorded locally in [docs/NAMES.md](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/NAMES.md). The test needs before/after wire-UID sets and must confirm that only the expected UID disappeared.

6. Cheapest discriminating test and better addressing route

The cheapest test for question 1 is a read-only identity test, with no wiring and no execution:

1. On a scratch loop containing exactly one known body node, obtain `Loop.Diagram`.
2. Read that diagram?셲 UID and Owner UID.
3. Compare it with the independently recorded UID of the body diagram created with the loop.
4. Read `Nodes[]` and verify that it contains the known body-node UID but not the loop UID.
5. Add a shift register and repeat the `Nodes[]` UID list. If unchanged, the register sides do not perturb body-node indices.

That single probe distinguishes body versus owning diagram and simultaneously answers the index-shift concern.

The better production route is to avoid positional identity altogether:

- Preserve the body diagram UID when the loop is created?봳he same pattern `new_loop()` already uses in [build_opshiftregs_v1.py](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_opshiftregs_v1.py).
- Preserve each dropped node?셲 returned UID/reference.
- Resolve the current `Nodes[]` index from that UID immediately before calling the wiring op.
- Inside the op, verify the selected node?셲 UID before selecting `Terminals[t]`.
- Prefer terminal name plus direction where names are unique; use terminal index only when duplicate or empty names force it.

Verdict: `Connect Wire` is probably viable for all three connections, but A3 currently overstates two unproved facts: the precise semantics of `Loop.Diagram`, and the stability/scope of `Nodes[]` indexing. The string-negative test should also be separated from the positive image-register test because it can alter type inference and let `Remove Bad Wires` erase more than the intended wire.

## Sources

(extract from answer)

## What was done with it

(Annotated retrospectively on 2026-09-15 by the cycle audit, which found this review unused-in-writing.) The plan it
reviewed became step A3 and shipped: the four `OpWireSR_*_v0` ops that wire a script-created shift register's three
sides (`Loop.Shift Registers[] → Left Registers[] → Tunnel.Outside/Inside Terminals[]`, plus the node route through
`Loop.Diagram` 6361401), recorded in `archive/benchmarks/INDEX.md` row 38 and used by every later assembly cycle.
The register ops exist for BOTH loop classes because a WhileLoop-seeded op raises 1055 on a For loop — that fact is
in `docs/NAMES.md`.
