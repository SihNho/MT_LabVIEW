# flatseq-tunnel-source-addressing-r3

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (87s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW VI Scripting, short question. Attack this claim; do not agree with it.

MEASURED on a real VI (read-only property reads): a value enters a flat-sequence FRAME diagram and then goes into
a While loop through a LoopTunnel. Walking the tunnel's OUTSIDE wire with `Wire.Terminals[]` + `Is Source?` +
`Generic.Owner`, the single SOURCE terminal's owner class comes back as **`FlatSequenceInnerTunnel`** (14 wires)
or **`LeftShiftRegister`** (2 wires).

CLAIM TO REFUTE: "those source terminals cannot be named as the `Wire Source` input of
`Terminal.Connect Wire` (method id 6349C03), because our wire creator addresses both ends only as
`Diagram[d].Nodes[n].Terminals[t]`, and neither a `FlatSequenceInnerTunnel` nor a `LeftShiftRegister` is a Node on
that diagram. So the wire cannot be branched into a second While loop on the same frame diagram by script."

Answer only these, with citations (NI docs, labviewwiki property/method ids, forum threads):
1. Does `Terminal.Connect Wire`'s `Wire Source` accept ANY Terminal reference - e.g. one obtained from
   `Wire.Terminals[]` (6371003) + `Is Source?` (634A003), or from `Tunnel.Inside Terminals[]` /
   `Outside Terminal` (6356001), or from a shift register's terminal accessor - or must it be a node terminal?
2. What accessor, if any, reaches a FlatSequence tunnel's terminals (the class is `FlatSequenceInnerTunnel`, and
   this VI has zero FlatSequence-owned objects of class `Tunnel`)? Give the property name and id.
3. Name the cheapest scripted experiment that would settle 1 and 2 on a scratch VI, in one or two property/method
   calls.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The claim is wrong because it confuses your creator’s **addressing scheme** with the VI Scripting API’s accepted reference types. `Terminal.Connect Wire` (6349C03) accepts a **Terminal reference or Node reference**; it does not require the terminal’s owner to be a Node or the reference to originate from `Node.Terminals[]`. [LabVIEW Wiki: Connect Wire](https://www.labviewwiki.org/wiki/Terminal_class/Connect_Wire_method)

1. **Yes—with one qualification.** Any valid `Terminal` reference is type-correct as `Wire Source`, including one obtained from:

   - `Wire.Terminals[]` (6371003), whose first element is normally the source. [LabVIEW Wiki: Wire.Terminals[]](https://labviewwiki.org/wiki/Wire_class/Terminals%28%29_property)
   - Filtering those references with `Terminal.Is Source?` (634A003). [LabVIEW Wiki: Is Source?](https://labviewwiki.org/wiki/Terminal_class/Is_Source%3F_property)
   - `Tunnel.Inside Terminals[]` (6356000) or `Outside Terminal` (6356001). [LabVIEW Wiki: Tunnel class](https://labviewwiki.org/wiki/Tunnel_class)
   - A shift register’s inherited `Tunnel` terminal properties; `LeftShiftRegister` inherits from `Tunnel`, and additionally exposes `Right Shift Register` (6374C00). [LabVIEW Wiki: LeftShiftRegister](https://www.labviewwiki.org/wiki/LeftShiftRegister_class)

   “Any” does not guarantee that every attempted connection is legal: diagram membership, source/sink direction and data-type compatibility can still make the resulting wire fail. But **Node ownership is not an API precondition**. NI’s documentation also describes one wire as having one source and potentially many consumers, so an already-wired source can conceptually acquire another branch. [NI: Using Wires to Link Block Diagram Objects](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

2. A `FlatSequenceInnerTunnel` has its own accessors:

   - **Left Terminal** — `1C3A9000`
   - **Right Terminal** — `1C3A9001`

   Both return Terminal references. [LabVIEW Wiki: FlatSequenceInnerTunnel](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class)

   The absence of FlatSequence-owned objects of class `Tunnel` is therefore unsurprising: `FlatSequenceInnerTunnel` is a special `GObject` class, not a `Tunnel` subclass. The alternative explanation for your evidence is that Flat Sequence boundaries are represented through this special owner class, while the actual wire endpoints remain ordinary Terminal references. The old NI discussion saying a **FlatSequence object itself** cannot be passed because it is not a Node does not show that a terminal obtained from `FlatSequenceInnerTunnel.Left/Right Terminal` is unusable. [NI forum: Connect a Terminal to a Flat Sequence Structure](https://forums.ni.com/t5/LabVIEW/Scripting-Connect-a-Terminal-to-a-Flat-Sequence-Structure/td-p/2672239)

3. The claim would be falsified by one observation: `Connect Wire` successfully creates a branch when its `Wire Source` is a Terminal reference owned by `FlatSequenceInnerTunnel` or `LeftShiftRegister`, despite that owner not appearing in `Diagram.Nodes[]`.

**Cheapest discriminating test:** on a scratch VI containing an existing Flat Sequence tunnel wire and an unwired compatible sink on the same frame, read `FlatSequenceInnerTunnel.Left Terminal` or `Right Terminal` once, then call the sink terminal’s `Connect Wire` once with that returned reference. A successful branch settles both questions in exactly **one property read plus one method call**.

## Sources

(extract from answer)

## What was done with it

**verdict: REFUTED MY CLAIM — accepted as a HYPOTHESIS, not yet confirmed on the machine.** Dispatched as the
mandatory review of a failed prediction (`tools/bench/diag_tunnelsource_onehop.log`, 7 pass / **2 fail**: the
contract predicted ≥ 3 of the 18 `from-tunnel` rows would resolve to a `(diagram, node, terminal)` triple; **1**
did). Two earlier dispatches told us nothing and are recorded as non-results: codex **TIMEOUT 180 s**
(`2026-09-17-flatseq-tunnel-source-addressing.md`) and gemini **ERROR 22 s** — agy refused a tool permission in
headless mode (`…-r2.md`; the fix is a `permissions.allow` entry or `--dangerously-skip-permissions`, neither
taken by a material session). This third dispatch shortened the task to three questions and came back ANSWERED in
87 s.

What it changes, stated narrowly: my sentence *"those terminals cannot be named as `Wire Source`"* conflated OUR
op's addressing with the API's precondition. The peer's citations say `Terminal.Connect Wire` 6349C03 takes **any
Terminal reference**, including one from `Wire.Terminals[]` 6371003 filtered by `Is Source?` 634A003 — which is
precisely the reference `OpWireSource_v5.vi` already obtains and prints — and that `FlatSequenceInnerTunnel`
carries its own `Left Terminal` **1C3A9000** / `Right Terminal` **1C3A9001**. Consistent with this project's own
measurement that `FlatSequence` sits outside the `Structure`/`Tunnel` branches with its own accessors
(`archive/peer/2026-09-16-flatseq-frame-unreachable.md`: `Diagrams[]` 3578BC00, `Frames[]` 3578BC07, measured
5/0).

**Not confirmed here, and deliberately not built.** The peer's own cheapest test — one property read plus one
`Connect Wire` call on a scratch — needs a WRITER whose `Wire Source` comes from a wire-terminal reference rather
than from `Diagram[].Nodes[].Terminals[]`. That is a new op (a fused `OpWireSource_v5` front half +
`OpConnectNested_v1` back half), and `docs/d1-build-plan.md` §11p ends with *"No further op beyond (1) and (2) is
authorised for A"*, so a material session may not take it (CLAUDE.md §3). The two property ids above are the
peer's, **not** taken on its authority: nothing is written into `docs/NAMES.md` until they are attached and
measured here. Carried to STATUS as the single judgement question of this session.
