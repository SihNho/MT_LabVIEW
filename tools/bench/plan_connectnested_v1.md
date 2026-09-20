# PLAN under review: `OpConnectNested_v1` (cross-diagram wire creator) + `OpTunnelSource_v0` (tunnel-source reader)

Context: `docs/d1-build-plan.md` §11p is the user's decision — ONE last attempt at route A for D1. Two artifacts
are authorised, nothing else.

## Artifact 1 — `OpConnectNested_v1.vi`

**Duty.** Wire a SOURCE terminal on nested diagram P into a SINK terminal on a DIFFERENT nested diagram Q, both
ends addressed purely by INDEX (`Diagram[i].Nodes[j].Terminals[k]`), because the terminals have no usable name.
`Terminal.Connect Wire` 6349C03 is the writer.

**What exists today.** `OpConnectNested_v0.vi` (built 2026-09-17, `tools/recipes/build_opconnectnested_v0.py`,
`docs/toolkit-capabilities.md` row 55) does this with BOTH ends constrained to the SAME nested diagram: it keeps
`OpConnect2_v0`'s sink ladder `Traverse('Diagram')[index] -> To More Specific Class -> AbstractDiagram.Nodes[]
6375809 -> IndexArray -> Node.Terms[] 6359000 -> IndexArray` and BRANCHES that one TMSC's `specific class
reference` into the source `Nodes[]` property node. Row 56 of the same file records the measured limit and its
claimed cause.

**Why v0 is limited, as recorded.** `build_opconnectnested_v0_run1.log:45` — ROUTE A (a second `Index Array` on
`Traverse for GObjects.vi`'s `References` array feeding the source `Nodes[]` node directly) measured
`ExecState 0`: `References` is `GObject[]`, the property node is `Diagram`-class, and GObject -> Diagram is a
downcast. `docs/toolkit-capabilities.md:56` then states: *"A second TMSC has no creator: `New VI Object` makes no
primitive, and `copy_by_index` would land it with an unwirable `target class` (a class-specifier `Constant` is a
GObject, not a Node)"*, and `docs/d1-build-plan.md` §11n item 2 repeats it as **MEASURED "cannot be built"**.

**The plan, and the two claims it rests on.**

1. That "no creator" statement appears to be wrong on our own record, in two independent places:
   - `tools/recipes/build_opconstvalue_v1.py:171-199` **copies a `To More Specific Class` node** out of the NI
     example `Navigating Nodes and Wires.vi` with `copy_by_index(EX, "Function", i_tmsc, OP, ...)` and then feeds
     its `target class` from a **typed refnum CONTROL seed** created with `create_control` on the copied property
     node's `reference` (`wire_control(dst, [seed], "Function", i_tmsc, ["target class"])`, gate F2). So the
     `target class` input is NOT wired from a class-specifier Constant at all, and `docs/toolkit-capabilities.md:72`
     states the rule: *"`To More Specific Class`'s `target class` accepts ANY wire of the target type"*.
   - `C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting\` contains
     **`Create To More Specific Class.vi`** (listed 2026-09-17, 84 VIs). Every writer op in this fleet is a wrapper
     of a VI from that folder.

2. Therefore v1 = v0 + a SECOND cast, built additively:
   - copy a second `To More Specific Class` into the op (`copy_by_index`, the proven route);
   - feed its `target class` by BRANCHING the wire that already feeds the first TMSC's `target class` in
     `OpConnectNested_v0` (same target type on both sides — both are diagrams), or from the same seed control;
   - feed its `reference` from a second `Index Array` on the same Traverse `References` array, with its own
     front-panel index control (`create_control`);
   - its `specific class reference` -> the SOURCE `Nodes[]` property node's `reference` (replacing the branch
     from the first TMSC).
   - Gate: `ExecState 1`, then a functional test on a scratch: body(loop A) -> body(loop B), ExecState 1, same
     wire uid on both ends; and into an unnamed tunnel of a CaseStructure nested inside A.

3. Codex's API answer (`archive/peer/2026-09-17-nested-diagram-terminals.md`, `-Kind fact`, ANSWERED) says the
   downcast `GObject -> AbstractDiagram` is ONE cast, that `Nodes[]` is owned by `AbstractDiagram` (6375809, an ID
   already in `docs/vi-server-ids.json`), and lists five CODE-GENERATION causes for an ExecState 0 after adding a
   second ladder: wrong class-specifier configuration, wrong terminal index on the TMSC, a property node
   configured for another class, an alternate/localized property name, and the Index Array output wired past the
   downcast. The build rules each out by measurement (reading back the TMSC's class, its terminal names, the
   property node's data-terminal name, and the wire uid on both ends of every connection).

## Artifact 2 — `OpTunnelSource_v0.vi`

**Duty.** For a `LoopTunnel`/`Tunnel` given by index or UID, return what feeds it from OUTSIDE:
`Tunnel.Outside Terminal` 6356001 -> `Terminal.Connected Wire` 634A000 -> `Wire.Terminals[]` 6371003 ->
per terminal `Terminal.Is Source?` 634A003 + `Generic.Owner` 6327806, plus `ControlTerminal.Control` 6353000
when the owner is a diagram (a ControlTerminal's Owner is its diagram, not a node).

**Why.** `docs/d1-build-plan.md` §11L: of 66 re-wire rows in run 7, 24 had NO ROUTE and 17 of those are
`from-tunnel` rows; §11n item 3 says **16 of the 17 print `outer_source (none)`** — a source-RESOLUTION gap.
`tools/bench/d1_rewire_sources.json` is the map, `tools/bench/d1_step0_census.json` the oracle for 3 known rows.

**What exists today.** `tunnels(target, index)` / `OpTunnels_v0` (row 24) already returns the outer terminal's
name / is-source? / wire. `OpWireSource_v5` (row 48) resolves "which object drives a wire" from a wire UID and is
recorded as returning **error 1055 for every wire** in one control (`diag_d1_full_route` T6, STATUS OPEN 28c).
`OpOwnerChain_v1` (row 49) gives owner class + owner UID from any UID. The plan is an ADDITIVE build on
`OpTunnels_v0`/`OpWireSource_v5` rather than a new family.

## What the review is asked to check

Only "has this already been done here": whether either artifact already exists under another name, whether either
has already been attempted and failed (and whether this plan repeats that cause), whether the "no TMSC creator"
claim in `toolkit-capabilities.md:56` / §11n is contradicted or corroborated elsewhere in our files, whether
`OpWireSource_v5`'s 1055 has a recorded cause that this plan would walk into, and which existing document should
obviously have been read for this direction.
