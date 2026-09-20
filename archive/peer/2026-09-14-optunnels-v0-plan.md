---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, plan]
---

# optunnels-v0-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (137s)
- **why asked:** plan review + API facts before building OpTunnels_v0 (loop tunnels' outer/inner terminals, to resolve the frame loop's 83 half-edges).
- **verdict:** ACTED ON: IDs taken (Inside Terminals[] 6356000, Outside Terminal 6356001 = 'Outer Term' on this machine, IndexMode 6356C00, GObject.UID 632A813); per-property nodes with own error chains; tunnel identity persisted by tunnel UID (Traverse index = access only); shift registers (LeftShiftRegister/RightShiftRegister, siblings of LoopTunnel) recorded as NOT covered by v0 - the donor's cast targets LoopTunnel - a v1 via Loop.Shift Registers[] is the open item; 'wire uid unique per VI' noted.

## Question

PLAN REVIEW + API facts (attack; cite labviewwiki/NI pages; be concrete). GOAL: OpTunnels_v0 - for the -th LoopTunnel of a target VI (Traverse class 'LoopTunnel' by index, the front half of OpSetIndexMode_v0 / OpTunnelInd_v0: Traverse -> Index Array -> To More Specific Class(LoopTunnel), proven) return: OUTER terminal (Tunnel.'Outer Term' 6356001 -> Terminal[Name, Is Source?, Connected Wire -> GObject.UID]) and INNER terminal(s) (which property? LoopTunnel 'Inner Term' / Tunnel 'Inner Terms[]' / 'Inside Terminal' - give the exact property NAME, SHORT name and Unique ID for LabVIEW 2020+), plus the tunnel's own GObject.UID and its IndexMode (already readable in the donor). PURPOSE: docs/frame-loop-wire-graph.md has 83 of 156 wires of the frame loop (diagram 43) as unresolved half-edges because the WhileLoop's own tunnels/shift registers are not in AbstractDiagram.Nodes[]; with outer/inner wire uids per tunnel we stitch parent-diagram wires to child-diagram wires (wire uids are unique per VI) and name the loop's inputs/outputs - and assign each tunnel to its loop by the wire match, avoiding an Owner cast. QUESTIONS: (1) exact properties/IDs for LoopTunnel: Outer Term, inner terminal(s), Index Mode, and for the Tunnel base class 'Inner Terms[]' (case structures: one inner terminal per frame) - can a LoopTunnel-typed ref also expose the Tunnel base 'Inner Terms[]'? (2) shift registers: are LeftShiftRegister / RightShiftRegister separate Traverse classes or LoopTunnel subclasses, and does Traverse('LoopTunnel') include them? (3) does Traverse over the whole VI list every LoopTunnel of every loop (nested loops too) in a stable order, and how many LoopTunnels would you expect in a 170-diagram VI with 3 While loops and 17 For loops (cost estimate at ~1 s per op run on this 473 KB VI)? (4) the i / N loop terminals: are they LoopTunnels, Terminals of the loop node, or separate classes? (5) any cast-free way to get the loop's UID from the tunnel (Tunnel.Owner is Generic) - or is wire matching the only route? Failure scenarios + cheapest checks.

## Answer

Verdict: the core graph-stitching idea is sound, but `Traverse("LoopTunnel") -> index` is too fragile as the long-term identity contract. Build `OpTunnels_v0` as a batched census if possible: return every tunnel and both terminal-side wire UIDs in one run, then sort externally by tunnel UID. Treat Traverse index only as an access mechanism, never as persistent identity.

## 1. Exact properties

For a `LoopTunnel` reference, use the two inherited `Tunnel` properties plus `LoopTunnel.IndexMode`:

| Class | Unique ID | Data name | Short name | Long name | Type |
|---|---:|---|---|---|---|
| `Tunnel` | `6356000` | `InsideTerms[]` | `InsideTerms[]` | `Inside Terminals[]` | `InnerTerminal refnum[]` |
| `Tunnel` | `6356001` | likely `OutsideTerm`* | likely `OutsideTerm`* | `Outside Terminal` | `OuterTerminal refnum` |
| `LoopTunnel` | `6356C00` | `IndexMode` | `IndexMode` | `Index Mode` | `U32`, 0 regular / 1 auto-index |
| `GObject` | `632A813` | `UID` | `UID` | `UID` | `I32` |

The authoritative public entry explicitly gives `InsideTerms[]`, `InsideTerms[]`, `Inside Terminals[]`, and ID `6356000`. It returns one inner-terminal reference for each structure frame. For an ordinary For/While loop that means an array of length one; for a Case structure it means one element per case. [LabVIEW Wiki: Inside Terminals[]](https://labviewwiki.org/wiki/Tunnel_class/Inside_Terminals%28%29_property)

The Tunnel class table confirms `6356001 = Outside Terminal` and that both properties are inherited by `LoopTunnel`. [LabVIEW Wiki: Tunnel class](https://labviewwiki.org/wiki/Tunnel_class)

`IndexMode` is exactly ID `6356C00`, short/data name `IndexMode`, with values 0=`Regular`, 1=`Auto Index`. [LabVIEW Wiki: Index Mode](https://labviewwiki.org/wiki/LoopTunnel_class/Index_Mode_property), [NI: Index Mode](https://www.ni.com/docs/ko-KR/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/tunnel/looptunnel/indexmode.html)

\* I could not find a separately indexed public page exposing the data/short name for `6356001`. Do not freeze `OutsideTerm` from inference alone. The cheapest authoritative check is `All Supported Properties` on a Tunnel-typed property node; that API returns Unique ID, data name, localized short name, and localized long name, and NI/LabVIEW Wiki state that Unique IDs are stable across versions/locales. [LabVIEW Wiki: All Supported Properties](https://labviewwiki.org/wiki/Property_class/All_Supported_Properties_property)

A `LoopTunnel`-typed Property Node can expose `Inside Terminals[]` and `Outside Terminal`: `LoopTunnel` inherits from `Tunnel`, and LabVIEW property nodes expose inherited properties. [LabVIEW Wiki: LoopTunnel class](https://labviewwiki.org/wiki/LoopTunnel_class), [LabVIEW Wiki: control-reference inheritance](https://labviewwiki.org/wiki/Control_References)

There is no separate LoopTunnel ?쏧nner Term??property in the documented hierarchy. Use inherited `Inside Terminals[]`; do not use the unrelated `FlatSequenceOuterTunnel.Inner Terminal`, ID `3195B801`. [LabVIEW Wiki: FlatSequence outer-tunnel property](https://labviewwiki.org/wiki/FlatSequenceOuterTunnel_class/Inner_Terminal_property)

For each returned terminal:

- `Name`: `634A004`
- `Is Source?`: `634A003`
- `Connected Wire`: `634A000`, data/short name `Wire`
- connected wire `GObject.UID`: `632A813`

These IDs and meanings are listed on the Terminal class page. An unwired terminal should be represented explicitly as ?쐍o wire/error 1055?? not UID zero silently. [LabVIEW Wiki: Terminal class](https://labviewwiki.org/wiki/Terminal_class), [LabVIEW Wiki: UID](https://labviewwiki.org/wiki/GObject_class/UID_property)

One correction to the purpose statement: wire UIDs are unique only within the same VI, not globally. [LabVIEW Wiki: UID](https://labviewwiki.org/wiki/GObject_class/UID_property)

## 2. Shift registers

`LeftShiftRegister` and `RightShiftRegister` are separate sibling subclasses of `Tunnel`, not subclasses of `LoopTunnel`:

```text
Tunnel
?쒋?? LeftShiftRegister
?쒋?? LoopTunnel
?붴?? RightShiftRegister
```

Therefore a strict class filter for `LoopTunnel` should not include shift registers. [LabVIEW Wiki: VI Server hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy), [LabVIEW Wiki: Tunnel class](https://labviewwiki.org/wiki/Tunnel_class)

Do not assume the two halves of a shift register will be discovered as one object. The hierarchy models left and right separately, while `Loop.Shift Registers[]` is the purpose-built property for obtaining a loop?셲 shift registers. [LabVIEW Wiki: Loop class](https://www.labviewwiki.org/wiki/Loop_class)

Consequently, `OpTunnels_v0` will not close every frame-loop half-edge unless you either:

- add separate traversals for `LeftShiftRegister` and `RightShiftRegister`, or
- build a second loop-centric reader using `Loop.Shift Registers[]`.

This is the largest hole in the current plan.

## 3. Traverse coverage, order, and cost

Traverse is recursive, so starting from the VI should find matching objects inside nested diagrams as well as top-level objects. Community examples use it specifically as a recursive object-tree walk. [NI Community: recursive Traverse for GObjects](https://forums.ni.com/t5/LabVIEW/controls-within-several-level-of-tab-controls/m-p/4315034)

I found no NI contract guaranteeing output order. There is evidence that its order is independent of panel tab order and differs from other object-array orderings. Therefore:

- Expect all nested `LoopTunnel` objects.
- Do not call the order stable across edits, recompiles, saves, or LabVIEW versions.
- An index is acceptable only for selecting a row during that same census.
- Persist `(tunnel UID, class name)`, not Traverse index. UID remains attached to the object across saves, though deleted-object UIDs can later be reused. [NI Community: Traverse ordering discussion](https://forums.ni.com/t5/LabVIEW/String-reference/m-p/4430231), [LabVIEW Wiki: UID](https://labviewwiki.org/wiki/GObject_class/UID_property)

There is no meaningful tunnel-count estimate from ?? While + 17 For loops.??Each loop can have zero or arbitrarily many ordinary tunnels. The count could therefore be zero, dozens, or hundreds. The 83 unresolved half-edges are a better bound, but not an exact tunnel count because:

- a tunnel can contribute an outer and an inner half-edge;
- either side can be unwired;
- shift registers are excluded from `LoopTunnel`;
- `i`, `N`, and conditional terminals are not LoopTunnels.

At one op run per tunnel, runtime is approximately `T seconds`, plus traversal/open overhead. If the 83 unresolved entries represent mostly one missing endpoint per actual tunnel, budget roughly 1?? minutes. If each tunnel accounts for two unresolved records, perhaps ~40??0 seconds. Neither estimate is defensible until a one-run class census returns `T`.

Strong recommendation: traverse once and process the entire reference array inside the Op. Re-running a whole-VI Traverse for every index turns the job into repeated full-tree walks and makes the result sensitive to any ordering change between calls.

## 4. `i`, `N`, and loop-end terminals

They are not LoopTunnels.

- `i` is the loop?셲 iteration/counter terminal, returned by inherited `Loop.Loop Counter`, ID `6361400`.
- For a For Loop, `N` is returned by `ForLoop.Loop Count`, ID `6362000`.
- The While/conditional-end terminal is returned by the loop class?셲 `Loop End Ref` property.
- The documented class hierarchy has dedicated `Terminal` subclasses, whereas LoopTunnel is a separate `Tunnel` branch. [LabVIEW Wiki: Loop class](https://www.labviewwiki.org/wiki/Loop_class), [LabVIEW Wiki: ForLoop class](https://labviewwiki.org/wiki/ForLoop_class), [LabVIEW Wiki: WhileLoop class](https://labviewwiki.org/wiki/WhileLoop_class), [LabVIEW Wiki: VI Server hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)

NI also describes `N` as an input terminal and `i` as an output terminal, consistent with ordinary loop terminals rather than border tunnels. [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999e.pdf)

Thus a complete loop wiring graph needs separate rows for `i`, `N`, loop-end/conditional, dynamic-parallelism and chunk-size terminals where applicable. The latter two even have dedicated ForLoop properties and should not be presumed to appear in ordinary `LoopTunnel` traversal. [LabVIEW Wiki: ForLoop class](https://labviewwiki.org/wiki/ForLoop_class)

## 5. Getting the owning loop UID

Wire matching is not the only possible route, but it is probably the best route for this graph.

`Generic.Owner`, ID `6327806`, returns a Generic reference. It should identify the tunnel?셲 owning object, but because its output type is Generic it does not provide a cast-free typed path to `GObject.UID`. [LabVIEW Wiki: Owner](https://labviewwiki.org/wiki/Generic_class/Owner_property)

Alternatives:

1. **Your wire-match method:** match outer-wire UID against parent-diagram wires and inner-wire UID against child-diagram wires. This directly solves the graph problem and avoids assuming Owner semantics.

2. **Structure-centric reverse lookup:** enumerate each known loop, read inherited `Structure.Tunnels[]` (`6360801`), then compare each returned tunnel?셲 UID with the Traverse census. This assigns tunnels to loops without following `Tunnel.Owner`, although obtaining each loop and its UID still requires the existing loop-class path. [LabVIEW Wiki: Structure.Tunnels[]](https://www.labviewwiki.org/wiki/Structure_class/Tunnels%28%29_property)

3. **Owner plus cast:** read `Tunnel.Owner`, verify `Class Name`/`Class ID`, cast to `GObject` or `Loop`, then read UID. This is simpler conceptually but violates the cast-free constraint.

I would retain wire matching as the primary mapping and use structure-centric `Tunnels[]` as the verification oracle. If they disagree, fail closed.

## Failure scenarios and cheapest checks

- **Wrong property name:** `Inner Term`, `Inner Terms[]`, and `Inside Terminal` are plausible but wrong guesses. Cheap check: build the property row by ID `6356000` and confirm its output terminal short name is `InsideTerms[]`.

- **Inherited property unexpectedly unavailable in the builder:** query `All Supported Properties` on a LoopTunnel property node and require IDs `6356000`, `6356001`, and `6356C00` before building.

- **Shift-register gaps mistaken for ordinary tunnels:** run one class-count census for `LoopTunnel`, `LeftShiftRegister`, and `RightShiftRegister`; verify the classes are disjoint.

- **Traverse index drift:** run the read-only census twice and compare the UID sequence. Equal sequences are useful machine evidence, but still not a documented stability guarantee. Store results keyed by UID.

- **Unwired tunnel side:** expose a separate wire-error column for every outer and inner terminal. Do not coerce invalid wire references to UID 0 without the error.

- **Unexpected `InsideTerms[]` cardinality:** for LoopTunnel require exactly one inner terminal. Log and reject zero or greater than one; greater than one would indicate either a wrong class or an invalid assumption.

- **Wire direction inversion:** record `Is Source?` on both sides. For an input tunnel, the outer terminal should be the sink and inner terminal the source; output tunnels reverse that relationship. Verify this on one tiny input/output-loop fixture.

- **Duplicate wire UID interpretation:** the same wire UID appearing at multiple terminals is expected for branches. Stitch by wire UID to a wire record, not by assuming one wire UID maps to exactly two terminals.

- **Incomplete reconstruction:** after adding tunnels and shift registers, recompute unresolved half-edges. The acceptance test should be a quantified decrease from 83, with every remaining row classified as `i/N/end`, shift register, deliberately unwired, or unsupported structure?봭ot merely ?쐔he Op ran without error.??
Overall: approve the property ladder, but revise the deliverable to a single-run UID-keyed census and explicitly add shift-register handling. The current LoopTunnel-only plan cannot by itself promise closure of the 83 unresolved edges.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
