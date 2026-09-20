# fsit-class-properties

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** fact
- **cost:** 
- **date:** 2026-09-18 01:36:36
- **outcome:** ANSWERED (240s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PURE API FACT QUESTION — LabVIEW 2026 VI Scripting, class `FlatSequenceInnerTunnel`.

We are about to attach property items to a scripting Property Node whose class string is
`VI Server:FlatSequenceInnerTunnel`, using property UNIQUE IDs (hex strings, AllowAlternateNames=FALSE).
We need the documented list so the attempt is not a blind ID sweep.

Please give, from labviewwiki.org (and NI docs where relevant), with the source URL beside each item:

1. The exact class string LabVIEW uses for this class in a Property Node's "Class Name" (is it
   `VI Server:FlatSequenceInnerTunnel`, or something else?), and the class's inheritance chain
   (Generic > GObject > ... > FlatSequenceInnerTunnel?), and its class id if listed.
2. EVERY property of the class: full name, **Short Name** (the string that appears on the property
   node's data terminal), hexadecimal **Unique ID**, data type, read/write, and scope
   (public / VI Scripting / private).
3. EVERY method of the class, same columns.
4. Specifically confirm or correct these two, which a previous dispatch reported:
   `Left Terminal` = 1C3A9000 and `Right Terminal` = 1C3A9001, both returning Terminal references.
5. Does `FlatSequenceInnerTunnel` inherit anything from `Tunnel` (e.g. `Outside Terminal` 6356001,
   `Inside Terminals[]` 6356000)? If it does NOT inherit from Tunnel, say what its parent class is and
   which of the parent's properties it therefore does expose.
6. Is there any documented way to obtain a `FlatSequenceInnerTunnel` reference other than
   `Generic.Owner` from one of its terminals — e.g. a `FlatSequenceFrame` or `FlatSequence` property
   that returns the frame's inner tunnels, or whether `Traverse for GObjects.vi` with class name
   "FlatSequenceInnerTunnel" returns them?

Answer as a table. If a column is not documented anywhere, write UNDOCUMENTED rather than guessing.


## Answer

## 1. Class identity

| Item | Documented answer | Source |
|---|---|---|
| Property Node `Class Name` string | **`VI Server:FlatSequenceInnerTunnel`**. This exact combined string is obtained from the documented rule “server class + colon + node class,” together with the documented node-class name `FlatSequenceInnerTunnel`. | [Property Node Class Name](https://labviewwiki.org/wiki/Property_class/Property_Node_Class_Name_property); [FlatSequenceInnerTunnel class](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class) |
| Class name | `FlatSequenceInnerTunnel` | [LabVIEW Wiki](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class) |
| Class ID | `16480` decimal | [LabVIEW Wiki](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class) |
| Scope | VI Scripting | [LabVIEW Wiki](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class) |
| Inheritance | `Generic > GObject > FlatSequenceInnerTunnel` | [LabVIEW Wiki](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class); [class hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy) |
| Parent | `GObject`, **not `Tunnel`** | [Class hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy) |

The full Property Node class string is therefore confirmed as **`VI Server:FlatSequenceInnerTunnel`**. The combined string is a direct application of the documented naming rule; the class page itself displays only the node-class portion.

## 2. Class-specific properties

LabVIEW Wiki documents exactly four properties. It does not provide individual property-detail pages for these four, so the Short Name and exact LabVIEW data-type label are **UNDOCUMENTED**. This matters because Short Names are localized/version-sensitive and should not be reconstructed from Long Names. [All Supported Properties documentation](https://labviewwiki.org/wiki/Property_class/All_Supported_Properties_property)

| Full/Long Name | Short Name | Unique ID | Data type | Access | Scope | Documented meaning | Source |
|---|---|---:|---|---|---|---|---|
| Left Terminal | **UNDOCUMENTED** | `1C3A9000` | **UNDOCUMENTED** | Read Only | VI Scripting | Returns a reference to the left terminal of the inner tunnel. | [LabVIEW Wiki](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class) |
| Right Terminal | **UNDOCUMENTED** | `1C3A9001` | **UNDOCUMENTED** | Read Only | VI Scripting | Returns a reference to the right terminal of the inner tunnel. | [LabVIEW Wiki](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class) |
| Left Frame | **UNDOCUMENTED** | `1C3A9002` | **UNDOCUMENTED** | Read Only | VI Scripting | Returns a reference to the frame on the tunnel’s left side. | [LabVIEW Wiki](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class) |
| Right Frame | **UNDOCUMENTED** | `1C3A9003` | **UNDOCUMENTED** | Read Only | VI Scripting | Returns a reference to the frame on the tunnel’s right side. | [LabVIEW Wiki](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class) |

Thus the previous dispatch was correct about:

| Claim | Verdict | Source |
|---|---|---|
| `Left Terminal = 1C3A9000` | **Confirmed** | [LabVIEW Wiki](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class) |
| `Right Terminal = 1C3A9001` | **Confirmed** | [LabVIEW Wiki](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class) |
| Both return terminal references | **Confirmed semantically** by the property descriptions. The exact refnum data-type name/icon is **UNDOCUMENTED** on this class page. | [LabVIEW Wiki](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class) |

## 3. Class-specific methods

| Full/Long Name | Short Name | Unique ID | Return/data type | Access | Scope | Source |
|---|---|---|---|---|---|---|
| **None** | N/A | N/A | N/A | N/A | N/A | The class page states that the class has no methods of its own; it inherits methods from `GObject`. [LabVIEW Wiki](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class) |

Because its chain includes `GObject > Generic`, references also support the inherited methods listed on the [GObject class](https://labviewwiki.org/wiki/GObject_class) and [Generic class](https://labviewwiki.org/wiki/Generic_class) pages. Those are inherited APIs, not `FlatSequenceInnerTunnel`-owned method IDs.

## 4. No `Tunnel` inheritance

| Question | Answer | Source |
|---|---|---|
| Does it inherit `Tunnel.Inside Terminals[]` (`6356000`)? | **No.** | [`Tunnel` hierarchy](https://labviewwiki.org/wiki/Tunnel_class); [`FlatSequenceInnerTunnel` hierarchy](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class) |
| Does it inherit `Tunnel.Outside Terminal` (`6356001`)? | **No.** | [`Tunnel` class](https://labviewwiki.org/wiki/Tunnel_class); [class hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy) |
| Why? | `Tunnel` and `FlatSequenceInnerTunnel` are separate sibling children of `GObject`. | [Class hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy) |
| Actual inherited API | All applicable `GObject` properties/methods, plus those inherited by `GObject` from `Generic`. | [GObject class](https://labviewwiki.org/wiki/GObject_class) |

The documented inherited properties are:

| Owner | Inherited property IDs and Long Names | Source |
|---|---|---|
| `Generic` | `6327800` Class ID; `6327801` Owner (Deprecated); `6327802` Owning VI; `6327803` Class Name; `6327804` Modified; `6327805` Is On Block Diagram?; `6327806` Owner | [Generic class](https://labviewwiki.org/wiki/Generic_class) |
| `GObject` | `632A800` Position; `632A801` Position:Left; `632A802` Position:Top; `632A803` Bounds; `632A804` Bounds:Area Width; `632A805` Bounds:Area Height; `632A806` Grouped; `632A807` Locked; `632A808` Group Member Refs[]; `632A809` Selected; `632A80A` Total Bounds Rect; `632A80B` Master Bounds Rect; `632A80C` Basic Object Flags; `632A80D` Is Wizard Locked; `632A80F` Resize Info:Can Resize Horizontally; `632A810` Resize Info:Can Resize Vertically; `632A811` Resize Info:Name in Resize Dialog; `632A812` Resize Info:Include In Resize; `632A813` UID; `632A814` Dependencies:Missing Dependency Paths; `632A815` Dependencies:Missing Dependency Names; `632A816` Dependencies:Found Dependency Paths; `632A817` Dependencies:Found Dependency Names | [GObject class](https://labviewwiki.org/wiki/GObject_class) |

## 5. Documented ways to obtain the reference

| Route | Status | Details | Source |
|---|---|---|---|
| Terminal → `Generic.Owner` | Documented | Current `Owner` is `6327806` and returns a `Generic` reference to the owning object. A cast is required afterward. | [Generic.Owner](https://labviewwiki.org/wiki/Generic_class) |
| Flat sequence → frames → inner tunnels | **Documented and preferable** | Use `FlatSequence.Frames[]` (`3578BC07`), then each `FlatSequenceFrame.Left Side Inner Tunnels[]` (`18E76803`) and/or `Right Side Inner Tunnels[]` (`18E76804`). | [FlatSequence class](https://labviewwiki.org/wiki/FlatSequence_class); [FlatSequenceFrame class](https://labviewwiki.org/wiki/FlatSequenceFrame_class) |
| `FlatSequenceFrame` direct inner-tunnel properties | **Yes** | `Left Side Inner Tunnels[]` and `Right Side Inner Tunnels[]` explicitly return arrays of references to inner tunnels. | [FlatSequenceFrame class](https://labviewwiki.org/wiki/FlatSequenceFrame_class) |
| A single `FlatSequence.Inner Tunnels[]` property | **No documented property** | The documented `FlatSequence` property list contains frames and terminals but no inner-tunnel array. | [FlatSequence class](https://labviewwiki.org/wiki/FlatSequence_class) |
| `Traverse for GObjects.vi` with class name `FlatSequenceInnerTunnel` | **UNDOCUMENTED** | NI Community material documents traversal by class-name strings generally, including `GObject`, `SubVI`, `Constant`, and `Control`, but does not specifically confirm that hidden flat-sequence inner-tunnel objects are returned for `FlatSequenceInnerTunnel`. | [NI Community traversal discussion](https://forums.ni.com/t5/LabVIEW/Scripting-Reference-all-objects-traverse/td-p/3811133) |

Bottom line: use the documented path

`FlatSequence.Frames[] → FlatSequenceFrame.Left/Right Side Inner Tunnels[]`

rather than a blind property-ID sweep or an unverified traversal assumption. The four class-specific IDs to attach are exactly `1C3A9000` through `1C3A9003`; their Short Names remain **UNDOCUMENTED**.

## Sources

(extract from answer)

## What was done with it

**USED AS THE BOUNDED CANDIDATE LIST FOR AN ON-MACHINE MEASUREMENT, then CORROBORATED BY IT** (material
session, cycle 19, 2026-09-18). This was a `-Kind fact` dispatch, asked before the sweep so the sweep would not
be blind (the objection raised against `census_dnc_property_ids.py`'s earlier blind sweep).

Measured in `tools/bench/probe_flatseq_walk_run2.log:47-56` on a scratch VI in `user.lib\claudeDev`, created
and deleted in the same run — every documented claim held, and the short names codex could only mark
**UNDOCUMENTED** are now MEASURED:

| id | codex said | machine says |
|---|---|---|
| `1C3A9000` Left Terminal | documented, short name UNDOCUMENTED | **ATTACHES, data terminal `LeftTerm`** |
| `1C3A9001` Right Terminal | documented, short name UNDOCUMENTED | **ATTACHES, `RightTerm`** |
| `1C3A9002` Left Frame | documented, short name UNDOCUMENTED | **ATTACHES, `LeftFrame`** |
| `1C3A9003` Right Frame | documented, short name UNDOCUMENTED | **ATTACHES, `RightFrame`** |
| `1C3A9004`, `1C3A9005` | not documented — the block ends at `…03` | **error 1077** (creator refuses) |
| `6356000` / `6356001` (Tunnel) | NOT inherited; chain is `Generic > GObject > FlatSequenceInnerTunnel` | **error 1077** — no Tunnel inheritance, confirmed |
| class string `VI Server:FlatSequenceInnerTunnel` | derived from the naming rule, not shown on the page | **correct** — control id `632A813` attaches as `UID` |

Its one UNDOCUMENTED answer was also settled on the machine: `Traverse for GObjects.vi` with class name
`FlatSequenceInnerTunnel` **does** return the objects — 518 of them on the V6 working copy
(`probe_flatseq_walk_run2.log:39`).

Not yet used, and recorded for the judgement session: codex's preferred route to an instance,
`FlatSequence.Frames[]` **3578BC07** → `FlatSequenceFrame.Left Side Inner Tunnels[]` **18E76803** /
`Right Side Inner Tunnels[]` **18E76804**. Both ids are UNVERIFIED here. They matter because they would reach
the inner tunnels without a Traverse index, but nothing was built from them this cycle.

(Claude fills in)
