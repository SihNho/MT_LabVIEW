---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review]
---

# constant-vs-wire-source-uid-contradiction

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (96s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS CONTRADICTION (LabVIEW 2026 VI Scripting, read-only; it decides a number that goes into a behaviour-preserving rebuild). Two independent measurements of the SAME edge disagree about which object feeds wire 10850 (the y input of Less? #10950 on diagram 43 of the main VI - the lost-bead threshold). (1) tools/bench/opconstvaluen_scan.log (op OpConstValueN_v1, 180 DigitalNumericConstants, per-read identity gate uid == reporter uid, all passed): constant uid 10739 at scan index 70 reports Constant.Terminal 634AC04 -> Terminal.Connected Wire 634A000 -> GObject.UID 632A813 = wire 10850, with no error, and its Constant.Value read through a DigitalNumericConstant-typed node decodes as I32 0 (Representation 3, flattened TD 0x03, cross-checked against Numeric Text = 0). (2) tools/bench/build_opwiresource_v2.log run 2 (op OpWireSource_v2): wire 10850 is looked up BY UID through vi.lib\VIServer\UID to GObject Reference.vi (readback UID = 10850, Generic.ClassName = Wire), then Wire.Terminals[] 6371003 -> Index Array element 0 -> Generic.Owner 6327806 -> To More Specific Class(GObject) -> GObject.UID = **3628**, class DigitalNumericConstant, no error on any node. Both ops keep the main VI byte-identical and both passed their structural gates. So: which constant really feeds wire 10850, 10739 or 3628? Candidates: (H1) Wire.Terminals[] element 0 is NOT the source in this case (your earlier answer said the first element is the source when one exists, but that the order is not otherwise guaranteed) - so I may be reading a SINK terminal whose owner happens to be another numeric constant; (H2) Constant.Terminal returns something other than the constant own diagram terminal in some situation, so the scan mis-attributed the wire; (H3) one of the two chains reads a STALE indicator (both ops poison their outputs before each run and both showed no error, which weakens this); (H4) the wire is a branched net and I am comparing different segments - but a net has a single source, so this would only matter if the two ops resolve different Wire objects, which the readback UID contradicts. QUESTIONS: (1) rank these and name the single cheapest discriminating measurement I can run read-only with the ops I already have (I intend: ask OpConstValueN_v1 for the fed wire of constant 3628 - if it also answers 10850, then two constants claim the same wire and the constant-side chain is the broken one; and separately read Terminal.Is Source? 634A003 for the terminal I pick as Terms[0], which should be TRUE for a source); (2) is there a documented way to ask a Wire for its source terminal explicitly rather than trusting element 0 - e.g. a Wire property or a method on the wire class; (3) if Terms[] really can put a sink first, what is the correct algorithm - filter by Is Source? TRUE and require exactly one; (4) does Constant.Terminal have any documented failure mode (a constant inside a structure, a constant feeding a tunnel, a constant with no terminal) that would make it report a wrong or another object wire. Cite what you read.

## Answer

The evidence does not yet justify choosing 10739 or 3628. The strongest omitted hypothesis is:

**H5: both constants are sources on the same broken, multi-source wire.**

That exactly reconciles both successful reciprocal-looking chains. ?쏯o error??means the property reads succeeded; it does not prove the diagram or wire is valid. NI states that a normal wire has one source and potentially many sinks; therefore two source terminals imply a broken wire/net. [NI: Using Wires to Link Block Diagram Objects](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

### 1. Ranking and cheapest discriminator

My ranking is:

1. **H5 ??wire 10850 contains two source terminals and is broken.**
2. **H2 ??the constant-side result is mis-associated**, although I found no documentation that `Constant.Terminal` itself returns another constant?셲 terminal.
3. **H1 ??`Terms[0]` is not the source**, possible on a source-less broken wire, but implausible here because a `DigitalNumericConstant` normally supplies data rather than consuming it. NI describes constants as diagram terminals that supply fixed values. [NI: Creating and Editing User-Defined Constants](https://www.ni.com/docs/en-GB/bundle/labview/page/creating-and-editing-user-defined-constants.html)
4. **H3 ??stale output**, weakened substantially by poisoning, UID gates, and successful error chains.
5. **H4 ??different branch/segment objects**, weakest because both operations independently identify UID 10850.

The single best measurement is not merely `Terms[0].Is Source?`. Read **every element of `wire 10850.Terminals[]`** and report, for each:

- terminal identity/reference or UID if available;
- `Terminal.Is Source?`;
- owner UID and class;
- `Terminal.Connected Wire` UID.

Then require:

```text
count(Is Source? == TRUE) == 1
```

Interpretation:

- Exactly one source, owner 3628 ??3628 wins; investigate the 10739 constant-side chain.
- Exactly one source, owner 10739 ??array ordering/owner traversal was misleading.
- Two sources, owners 10739 and 3628 ??both measurements were correct and wire 10850 is broken.
- Zero sources ??source-less broken wire; `Terms[0]` is merely a sink.

A long-standing VI Scripting discussion specifically reports that `Terms[0]` is normally the source, **except source-less broken wires**, and that additional sources on a multi-source broken wire may appear elsewhere in the array. This is community evidence, not an NI API contract. [LAVA: Traverse wire to source](https://lavag.org/topic/10734-traverse-wire-to-source/)

If your existing op can inspect only element 0, your proposed `Terms[0].Is Source?` is the cheapest first probe. But it cannot exclude a second source elsewhere. Querying constant 3628?셲 connected-wire UID is useful reciprocity evidence, but it likewise cannot distinguish a valid wire from a two-source broken wire.

### 2. Explicit Wire source accessor

I found **no documented Wire property or method that directly returns ?쐔he source terminal.??* The published/community procedures use `Wire.Terminals[]` followed by terminal inspection. NI community guidance recommends using `Is Source?` to determine terminal direction rather than relying on ambiguous terminal indices. [NI Community: Scripting?봗erminal Information](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)

Accordingly, I would not treat ?쐃lement zero is the source??as a documented LabVIEW 2026 contract. It is an observed convention with known broken-wire exceptions.

### 3. Correct algorithm

Yes. The robust read-only algorithm is:

1. Resolve the Wire by UID and verify its readback UID/class.
2. Read the complete `Wire.Terminals[]`.
3. For every terminal, read `Is Source?`, owner UID/class, and its connected-wire UID.
4. Retain terminals where:
   - `Is Source? == TRUE`, and
   - `Connected Wire.UID == requested wire UID`.
5. Require exactly one retained terminal.
6. Treat zero or multiple sources as invalid/broken/ambiguous; do not silently select element 0.

NI?셲 dataflow documentation supplies the invariant?봮ne source, multiple possible readers?봞nd the terminal property is the appropriate directional discriminator. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html), [NI Community terminal inspection](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)

For a behaviour-preserving rebuild, also require that the selected source terminal?셲 reciprocal `Connected Wire` resolves back to UID 10850.

### 4. `Constant.Terminal` failure modes

The available reference says only that `Constant.Terminal` is a read-only VI Scripting property that ?쐒eturns a reference to the terminal.??It documents no exception for constants inside structures, constants feeding tunnels, or unwired constants, and no condition under which it legitimately returns another object?셲 terminal. [LabVIEW Wiki property catalogue: Constant.Terminal](https://labviewwiki.org/wiki/Constant_class/Terminal_property)

An unwired constant should still have its own terminal; what would be absent is a connected wire. Constants inside structures still own source terminals on their containing diagram. Feeding a tunnel changes what must be traversed beyond the structure boundary, not which terminal belongs to the constant. The recursive tunnel traversal requirement is described in the VI Scripting discussion, but this is community knowledge rather than formal NI documentation. [LAVA: Traverse wire to source](https://lavag.org/topic/10734-traverse-wire-to-source/)

Therefore, I found **no documented semantic failure mode supporting H2**. If 10739?셲 returned terminal is genuinely its own terminal and that terminal genuinely reports connected wire UID 10850, then the cleanest explanation is not ?쐗rong terminal?? it is that wire 10850 has multiple sources. Enumerating all terminals and their `Is Source?` values settles that in one measurement.

## Sources

(extract from answer)

## What was done with it

(annotation below)

The H5 the answer added (two sources on one broken wire) is exactly what my op could not see, so `OpWireSource_v3`
was built to the prescribed algorithm: read EVERY terminal of the wire, with `Is Source?` 634A003 and the reciprocal
`Connected Wire`, and require exactly one source pointing back at the wire. **Result: H5 rejected** — wire 10850 has
one source (a `DigitalNumericConstant`) and one sink (`Comparison` 10950 = `Less?`). The contradiction turned out to
be instrumentation: the UID branch was reading the wrong `Owner` node. After that repair both measurements agree on
constant 10739 (I32 0), and `docs/stage2-assembly-step-e.md` records the threshold as settled.
