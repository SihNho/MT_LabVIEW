---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review]
---

# case-frame-reader-property-ids

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (106s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

API FACTS (LabVIEW 2026 VI Scripting property/method unique IDs; read-only). To run the two censuses you required in archive/peer/2026-09-15-reseed-vi-design-cycle7.md I must build a read-only case-structure reader op. The fleet addresses objects BY UID through vi.lib\VIServer\UID to GObject Reference.vi (inputs Owning VI / UID, output GObject) and then casts with To More Specific Class; property nodes are built by unique ID and their terminals carry the SHORT name (e.g. 634A000 Connected Wire shows as Wire, 6359000 Terminals[] shows as Terms[], 6327806 Owner shows as Owner). Known already: AbstractDiagram.Nodes[] 6375809, AbstractDiagram.All Objects[] 6375804, Node.Label 6359001, GObject.UID 632A813, Generic.Class Name 6327803, Generic.Owner 6327806, Wire.Terminals[] 6371003, Terminal.Connected Wire 634A000, Terminal.Is Source? 634A003, Tunnel.Inside Terminals[] 6356000, Tunnel.Outside Terminal 6356001. WHAT I NEED, with the exact VI Server class name the property node must be built for, the unique ID, and the terminal SHORT name it will show (say UNKNOWN rather than guessing): (1) the case/multi-frame structure class - is it CaseStructure or MultiFrameStructure in VI Server spelling - and the property that returns its FRAMES/DIAGRAMS as an array, plus the property that returns the frame LABELS (the case selector strings such as True / False / 0, Default); (2) the property that gives the CURRENTLY VISIBLE frame if any, and any property that tells which frame index corresponds to which label; (3) for a case-structure TUNNEL: the property Default If Unwired? (or its actual name), and confirmation that a case tunnel is the same Tunnel class as a loop tunnel so Inside Terminals[] 6356000 returns one inner terminal PER FRAME (in frame order?); (4) Diagram class - does it expose UID (so I can match a diagram returned by Frames[]/Diagrams[] against the VI-wide Traverse order and then reuse the fleet reader node_terms(target, diagram_index, node_index)), and does it expose Owner (to prove a diagram belongs to a given case); (5) CaseStructure.Selector (the terminal whose wire carries the selector) - ID and short name; (6) anything that lets me read, for one tunnel, WHICH inner terminal belongs to WHICH frame, since that mapping is the whole point of the census. Cite what you read for each; do not guess IDs.

## Answer

The read-only census can be built without assuming that `Inside Terminals[]` is ordered. Use each inner terminal?셲 `Terminal.Diagram` reference to identify its frame.

| Requested item | Property-node class | Unique ID | Short name | Result |
|---|---|---:|---|---|
| Case structure object | `CaseStructure` | Class ID `16408` | ??| This is the concrete VI Server spelling. `MultiFrameStructure` is its parent class, not the concrete case class. [Class hierarchy](https://labviewwiki.org/wiki/CaseStructure_class) |
| Frame diagrams | `MultiFrameStructure` | `6363801` | **UNKNOWN** | Long name `Frames[]`; returns the frame `Diagram` references as an array. [MultiFrameStructure properties](https://labviewwiki.org/wiki/MultiFrameStructure_class) |
| Frame labels | `CaseStructure` | `6365002` | `FrameNames` | `Frame Names`; returns the case selector strings as a string array. [Property record](https://labviewwiki.org/wiki/CaseStructure_class/Frame_Names_property) |
| Visible frame | `MultiFrameStructure` | `6363800` | `VisFrame` | Zero-based index of the currently visible frame. [Property record](https://labviewwiki.org/wiki/MultiFrameStructure_class/Visible_Frame_property) |
| Case selector terminal | `CaseStructure` | `6365000` | **UNKNOWN** | `Selector`; returns the selector-tunnel reference. [CaseStructure properties](https://labviewwiki.org/wiki/CaseStructure_class) |
| Default-if-unwired | `ConditionalTunnel` | `5D251C00` | `UseDefault` | Actual long name `Use Default if Unwired`. [Property record](https://labviewwiki.org/wiki/ConditionalTunnel_class/Use_Default_if_Unwired_property) |
| Inner terminals | `Tunnel` | `6356000` | `InsideTerms[]` | One inner-terminal reference per structure frame. [Property record](https://labviewwiki.org/wiki/Tunnel_class/Inside_Terminals%28%29_property) |
| Inner terminal?셲 frame | `Terminal` | `634A002` | `Diagram` | Returns the terminal?셲 owning diagram. This is the reliable tunnel-terminal?뭚rame mapping. [Property record](https://labviewwiki.org/wiki/Terminal_class/Diagram_property) |
| Diagram UID | inherited from `GObject` | `632A813` | `UID` | Yes: `Diagram ??AbstractDiagram ??GObject`, so a diagram exposes `UID`. [Diagram inheritance](https://labviewwiki.org/wiki/Diagram_class), [UID property](https://labviewwiki.org/wiki/GObject_class/UID_property) |
| Diagram owner | inherited from `Generic` | `6327806` | `Owner` | Yes: the returned owner can be cast to `CaseStructure`, proving membership. [Owner property](https://labviewwiki.org/wiki/Generic_class/Owner_property) |

Important class distinction: a normal case data tunnel is a `ConditionalTunnel`, which inherits `Tunnel`; it is not necessarily reported as the concrete class `Tunnel`. A loop?셲 corresponding concrete object is generally `LoopTunnel`. Both inherit the base `Tunnel` API, which is why `InsideTerms[]` and `Outside Terminal` apply. `SelectorTunnel` is a child of `ConditionalTunnel`. [ConditionalTunnel hierarchy](https://labviewwiki.org/wiki/ConditionalTunnel_class), [Tunnel hierarchy](https://labviewwiki.org/wiki/Tunnel_class)

For index-to-label mapping, the direct pairing is:

```text
Frames[][i]  ?? FrameNames[i]
```

The supporting API also provides `CaseStructure.Get Frame Index`, method ID `6364C04`, short name `GetFrameIndex`, which converts a frame-name string to its frame index. [Method record](https://labviewwiki.org/wiki/CaseStructure_class/Get_Frame_Index_method) The published scripting anatomy explicitly says to use frame names and frame indexes with the diagrams returned by `Frames[]`. [VI-scripting anatomy](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/anatomy.html)

For each tunnel, the safest census algorithm is:

```text
case.Frames[]           ??frame_diagrams
case.FrameNames         ??frame_labels

tunnel.InsideTerms[]    ??inner_terminals
for each inner terminal:
    terminal.Diagram    ??terminal_frame
    match terminal_frame against frame_diagrams
    matched index       ??frame_labels[index]
```

That avoids depending on an undocumented ordering assertion. The public description confirms ?쐎ne reference for each frame,??but does not explicitly promise that `InsideTerms[]` uses frame-array order. Therefore, ?쐇nside-terminal array index equals frame index??is **UNKNOWN**, not established. `Terminal.Diagram` plus reference equality?봮r diagram UID equality?봲ettles it deterministically. An NI Community solution independently describes finding a diagram in `Frames[]` to obtain its frame index and then indexing `FrameNames`; it also notes that a terminal?셲 owner/diagram path can identify the containing frame. [NI Community discussion](https://forums.ni.com/t5/LabVIEW/Access-name-of-case-from-indicator-inside-case-using-VI/m-p/2329972)

One limitation: these public property records predate LabVIEW 2026. NI?셲 property metadata says unique-ID strings are consistent across LabVIEW versions and locales, while displayed short names can vary across versions, locales, and launches. [All Supported Properties documentation](https://labviewwiki.org/wiki/Property_class/All_Supported_Properties_property) Consequently, I have deliberately left `Frames[]` and `Selector` short names as **UNKNOWN** where I could not retrieve their individual metadata records; the fleet?셲 own read-only `All Supported Properties` report in LabVIEW 2026 is the authoritative way to fill those two strings.

## Sources

(extract from answer)

## What was done with it

(annotation below)

Every ID was taken into `docs/NAMES.md` under "Case-structure reading" and drove `OpCaseFrames_v0`: `Frames[]`
6363801 and `Frame Names` 6365002 were CENSUSED at build time rather than trusted (short names `Frames[]` and
`FrameNames` — the answer marked both UNKNOWN, correctly). The warning that `Inside Terminals[]` order is not
documented as frame order shaped `OpTunnelRead_v0`: it maps each inner terminal to its frame through
`Terminal.Diagram` 634A002 instead of assuming index == frame, which is how Census B got its per-frame wires.
`ConditionalTunnel.Use Default if Unwired` 5D251C00 was not needed — the measured tunnels are `SelectorTunnel`.
