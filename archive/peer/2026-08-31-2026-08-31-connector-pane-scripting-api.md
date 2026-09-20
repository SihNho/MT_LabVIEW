---
type: peer-review
status: historical
date: 2026-08-31
tags: [peer-review]
disposition: legacy
---

# 2026-08-31-connector-pane-scripting-api

- **agent:** codex
- **date:** 2026-08-31
- **outcome:** ANSWERED (131s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Web research task, answer with NI/LAVA source URLs. LabVIEW 2026 VI Scripting over ActiveX: I must assign a VI's CONNECTOR PANE by script (set a pattern with >=12 terminals, connect 9 named inputs + 3 named outputs to specific pane terminals, verify by readback, save). Questions: (1) exact VI-class/ConnectorPane-class property and invoke names for setting the pattern (and the numeric pattern IDs for the common 12/14/16-terminal layouts); (2) exact API to connect a CONTROL refnum to a pane terminal (how are terminal indices numbered?); (3) NI ships vi.lib\express\express shared\Wire Connector Pane.vi and ex_Wire Controls to ConPane.vi - document their connector panes/inputs if known, are they usable as library calls; (4) constraints: must the pattern be set before wiring, does changing pattern clear wiring, does it need the front panel open, known errors when the VI is reserved/running; (5) how to READ BACK which control sits on which terminal. Also attack this assumption: 'pane edits cannot break the VI (ExecState stays 1)'.

## Answer

The direct scripting route is:

1. VI class ??`Connector Pane:Reference`
2. ConnectorPane class ??`Pattern` = `4815` or `4833`
3. ConnectorPane class ??`Assign Control To Terminal(Control, Terminal Index)` for each control
4. Read back `Pattern`, `Number of Connection Terminals`, and `Controls[]`
5. Save explicitly
6. Verify the target VI and its callers remain executable

Do not use VI class ??`Connector Pane:Set` for this job; that property copies an entire connector pane from another VI and imposes name/type matching requirements. [LabVIEW Wiki: Connector Pane:Set](https://labviewwiki.org/wiki/VI_class/Connector_Pane.Set_property)

## 1. Exact properties and pattern IDs

On the target VI reference, read:

- VI class property: `Connector Pane:Reference`
- Short name/data name commonly shown as `ConPane.Ref`
- Property ID: `23E`

That returns a ConnectorPane-class reference. [LabVIEW Wiki: VI class property table](https://labviewwiki.org/wiki/VI_class)

On that reference, use:

- ConnectorPane property: `Pattern`
- Read/write `U32`
- Property ID: `239A8400`
- Valid documented range: `4800`??4835`
- ConnectorPane property: `Number of Connection Terminals`
- Read-only; useful immediately after writing `Pattern`

The ConnectorPane API table also lists `Controls[]`, `Terminal Bounds[]`, `WiringRules[]`, `Disconnect Terminal`, and `Disconnect All Terminals`. [LabVIEW Wiki: ConnectorPane class](https://labviewwiki.org/wiki/ConnectorPane_class)

Relevant patterns:

| Terminals | Pattern | ID |
|---:|---|---:|
| 12 | 4-2-2-4 | `4815` |
| 16 | 5-3-3-5 | `4833` |
| 20 | 6-4-4-6 | `4834` |
| 28 | 8-6-6-8 | `4835` |

There is no standard 14-terminal pattern in the published `4800`??4835` table. Thus, if ?쐁ommon 14-terminal layout??came from a design note, it is likely a mistaken count or a customized/add-terminal pane rather than one of the canonical pattern IDs. For nine inputs plus three outputs, `4815` is exactly full; `4833` gives four spare terminals. [LabVIEW Wiki: connector-pane pattern table](https://labviewwiki.org/wiki/Connector_pane_patterns)

NI recommends 4-2-2-4 or 5-3-3-5, and warns that changing connector-pane patterns can require caller rewiring or create incompatibilities. [NI: Icon and Connector Panes](https://www.ni.com/en/support/downloads/instrument-drivers/tools-resources/instrument-driver-guidelines/icon-and-connector-panes.html), [NI: Driver and VI Library Development Guidelines](https://www.ni.com/en/support/documentation/supplemental/21/driver-and-vi-library-development-guidelines.html)

## 2. Connecting a control reference

Use the ConnectorPane-class invoke method:

- Long name: `Assign Control To Terminal`
- Short/data name: `AssignCtrlToTerm`
- Method ID: `239A8000`
- Inputs:
  - `Control`: front-panel Control refnum
  - `Terminal Index`: terminal index
- No return value
- Loads the target front panel into memory
- Remote access allowed
- Not settable while the target VI is running

[LabVIEW Wiki: Assign Control To Terminal](https://labviewwiki.org/wiki/ConnectorPane_class/Assign_Control_To_Terminal_method)

Indices are zero-based array indices. In the default, unrotated orientation, their general traversal is described as right-to-left and bottom-to-top. Rotation or flipping changes the physical position represented by an index. Do not derive production mappings from that sentence alone: use NI?셲 shipped `Connector Pane Pattern Reference.vi`, which displays the exact index at every position for every pattern. [NI Community: pattern-reference example](https://forums.ni.com/t5/LabVIEW/Get-Control-Reference-From-Connector-Pane/m-p/3070203), [NI Community: terminal IDs start at lower right](https://forums.ni.com/t5/LabVIEW/Scripting-Set-connector-pane-error-1-if-source-terminals-are/td-p/3685361)

The safe automation contract is therefore ?쐍amed control ??explicit numeric index from the pattern-reference VI,??not ?쐇nputs go on the left, so calculate indices geometrically.??
## 3. NI?셲 `Wire Connector Pane.vi` and `ex_Wire Controls to ConPane.vi`

The public evidence is thin and old.

The NI Community discussion documents the Express-VI helper usually referred to there as `ex_WireConPane.vi`:

- `VI Refnum`: source/target VI
- `All Controls`: string array with one element per connector terminal
- Array index corresponds to connector-pane terminal index
- Empty strings represent terminals with no associated control
- `Controls to Wire`: names of the subset that should actually be connected
- The order of `Controls to Wire` is not important
- The indexed order of `All Controls` is critical
- The discussed example uses a 16-terminal pane

[NI Community: detailed description of ex_WireConPane.vi](https://forums.ni.com/t5/LabVIEW/Is-there-any-documentation-for-Support-VI-s-in-the-LabVIEW/m-p/163444)

That thread explicitly says these Express support VIs lacked separate documentation and had to be reverse-engineered. It does not establish the exact LabVIEW 2026 connector pane of either filename you listed. [NI Community: Express support-VI documentation discussion](https://forums.ni.com/t5/LabVIEW/Is-there-any-documentation-for-Support-VI-s-in-the-LabVIEW/td-p/163440)

Treat both as internal implementation VIs, not supported public library APIs. They may be callable as ordinary subVIs if unlocked and their dependencies resolve, but I found no NI source promising compatibility or documenting their LabVIEW 2026 interfaces. For durable tooling, wrap the public scripting properties/methods above. To settle their exact 2026 inputs without opening the binaries here, have the manager run the existing plain-text reporter on each VI and capture:

- connector-pane pattern
- terminal index
- control label
- direction/type
- required/recommended/optional setting
- subVI dependencies

## 4. Ordering and edit constraints

Set the pattern before assigning controls. NI?셲 normal documented workflow is explicitly ?쐓elect a sufficient pattern, then assign controls and indicators.??[NI: Assigning Terminals](https://www.ni.com/docs/en-AS/bundle/labview/page/assigning-terminals-to-controls-and-indicators.html)

Changing the pattern should be treated as destructive to existing assignments. At minimum it changes terminal identity/position and can make caller instances incompatible; NI advises leaving spare terminals specifically to avoid later pattern changes and caller rewiring. Before changing it, read and preserve `Controls[]`; after changing it, assign every intended terminal anew. [NI: connector-pane development guidelines](https://www.ni.com/en/support/documentation/supplemental/21/driver-and-vi-library-development-guidelines.html)

The front-panel window need not be visibly open. However, `Assign Control To Terminal` and `Controls[]` load the front panel into memory. The VI?셲 `Connector Pane:Set` property additionally requires the UI thread to be idle. [LabVIEW Wiki: Assign Control To Terminal](https://labviewwiki.org/wiki/ConnectorPane_class/Assign_Control_To_Terminal_method), [LabVIEW Wiki: Connector Pane:Set](https://labviewwiki.org/wiki/VI_class/Connector_Pane.Set_property)

The target must not be running. `Assign Control To Terminal`, `Pattern`, and `Connector Pane:Set` are not settable while it is running. A VI reserved as a dependency of an active top-level VI therefore must be treated as non-editable as well. Check:

- `Execution:State`
- `Context:Is Reserved In This Context`
- `Context:Is Reserved In Other Context`

The latter properties are exposed by the VI class. [LabVIEW Wiki: VI class](https://labviewwiki.org/wiki/VI_class)

I did not find an NI source guaranteeing one stable error code for every running/reserved case. Report the actual error cluster from the scripting VI rather than matching only a presumed numeric code.

Save explicitly after verification. There is community evidence that some scripting changes may not set the modified flag in the way `Save All` expects, so relying on dirty-state detection is unsafe. [NI Community: scripting and explicit save](https://forums.ni.com/t5/LabVIEW-APIs-Discussions/Can-you-change-a-VISA-Reference-control-s-VISA-class-using/td-p/4135114)

## 5. Readback verification

Read ConnectorPane ??`Controls[]`.

It returns one Control refnum per connector terminal, in terminal-index order. Unassigned positions appear as null/invalid refnums; they are not omitted. Thus:

```text
controls = ConPane.Controls[]
for i = 0 .. NumberOfConnectionTerminals-1:
    if controls[i] is valid:
        read controls[i].Label.Text
        record i -> label
    else:
        record i -> unassigned
```

[NI Community: Controls[] ordering and null entries](https://forums.ni.com/t5/LabVIEW/Get-Control-Reference-From-Connector-Pane/td-p/3070203), [LabVIEW Wiki: Controls[] property](https://www.labviewwiki.org/wiki/ConnectorPane_class/Controls%28%29_property)

For stronger verification, also read:

- `Pattern`
- `Number of Connection Terminals`
- `Controls[]`
- `Terminal Bounds[]`
- `WiringRules[]`

`Terminal Bounds[]` lets you associate each index with physical pane coordinates, which avoids ambiguity if someone rotated or flipped the pane. [LabVIEW Wiki: ConnectorPane class](https://labviewwiki.org/wiki/ConnectorPane_class)

Compare control references or stable object identity first; labels are useful diagnostics but can be duplicated or renamed.

## Attack on ?쐏ane edits cannot break the VI because ExecState stays 1??
Reject that assumption.

NI defines `Execution:State` as:

- Bad: VI has errors and cannot execute
- Idle: VI is not running but is in memory
- Run top level
- Running/reserved as a dependency

Therefore, `1` means Idle only if the enum is being marshalled with the expected numeric representation. It is evidence that the queried VI was executable at that instant?봭ot proof that the edit was harmless to callers or remained valid after save/reload. [NI: Programmatically Check If a VI Is Running](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YIEJCA4)

Connector-pane changes can break:

- the target VI, for example through invalid required/dynamic-dispatch connector configuration;
- already loaded callers whose subVI terminals no longer match;
- callers after reload/relink even if the target initially reports Idle;
- API compatibility without making the target itself broken.

NI explicitly warns that changing the pattern may require replacing or rewiring subVI instances. [NI: connector-pane guidelines](https://www.ni.com/en/support/documentation/supplemental/21/driver-and-vi-library-development-guidelines.html)

Minimum defensible verification:

1. Verify the target?셲 `Controls[]` mapping.
2. Save explicitly.
3. Close/reopen the target in the same project context.
4. Check target `Execution:State != Bad`.
5. Enumerate and check every loaded caller.
6. Reopen or compile the intended top-level hierarchy and check it too.
7. If anything is Bad, retrieve LabVIEW?셲 error list; NI identifies the broken run arrow/error list as the authoritative indication of compile errors. [NI: LabVIEW Debugging Techniques](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000001DbgJSAS)

So the corrected claim is: ?쏛 post-edit Idle state is one useful target-VI check, but it does not establish connector-pane compatibility or hierarchy integrity.?

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
