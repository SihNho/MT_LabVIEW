---
type: peer-review
status: historical
date: 2026-08-28
tags: [peer-review]
disposition: legacy
---

# copy-nodes-between-vis

- **agent:** codex
- **date:** 2026-08-28
- **outcome:** ANSWERED (92s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW VI Scripting question. NI forums advise: to place a node type that New VI Object cannot create, 'create a VI with the function you want and copy it from that VI'. What is the actual programmatic mechanism to COPY an existing node/object (e.g. a Property Node, an indicator with its terminal, or any Function) from one VI's block diagram to another VI's diagram via VI Scripting? Candidates to verify: (1) a GObject or Diagram method named Copy / Copy Objects / Duplicate; (2) selection-based clipboard operations (setting Selected on objects then invoking an Edit>Copy / Edit>Paste equivalent App or VI method) - what are the exact method names and classes; (3) the Move method with a different owner (does Move support re-owning to another diagram?); (4) VI snippet PNG import via scripting. For each: exact class/method names, LabVIEW version availability, and known gotchas (e.g. does paste position land predictably, are wires/linked front-panel terminals carried along when copying a control terminal or subVI). Search NI forums, LAVA, and labviewwiki.org; cite URLs for every claim.

## Answer

The actual general-purpose mechanism is `GObject.Move`, with a destination `owner` and `Duplicate? = TRUE`. For copying several connected objects, use `TopLevelDiagram.Make Selection` followed by `TopLevelDiagram.Move Selected Objects`, or the clipboard sequence `Copy Selection` ??destination `AbstractDiagram.Paste`.

## 1. Direct object copy: `GObject.Move`

Exact API:

- Class: `GObject`
- Method: `Move`
- Inputs:
  - `position`
  - `owner`
  - `Duplicate?` (default `FALSE`)
- Scope: VI Scripting
- Not available in the run-time engine
- The method does not return a reference to the newly created copy. [LabVIEW Wiki: GObject.Move](https://labviewwiki.org/wiki/GObject_class/Move_method)

For a cross-VI copy:

1. Obtain a reference to the source `GObject`.
2. Obtain a reference to the destination diagram or other valid owner.
3. Invoke `Move` on the source object, wiring the destination as `owner`.
4. Wire the desired destination-relative `position`.
5. Set `Duplicate? = TRUE`.

If the supplied owner belongs to another VI, LabVIEW automatically treats the operation as duplication even if `Duplicate?` is false. Thus `Move` really does support re-owning/copying across diagrams; it is not limited to moving within the original diagram. [LabVIEW Wiki: GObject.Move](https://labviewwiki.org/wiki/GObject_class/Move_method), [NI forum confirmation that Move works across VIs](https://forums.ni.com/t5/LabVIEW/Scripting-Create-Cluster-in-Array-from-existing-cluster/td-p/2703465)

Version: the `Duplicate?` input and documented cross-VI duplication behavior were added in LabVIEW 2010. [NI: LabVIEW 2010 Scripting Changes](https://forums.ni.com/t5/LabVIEW-APIs-Documents/LabVIEW-2010-Scripting-Changes/ta-p/3521934)

Important gotcha: `Move` returns/retains the source reference, not a reference to the duplicate. A common workaround is to assign a unique label and find the copied object beneath the destination owner afterward, or compare destination object lists before and after. [NI discussion of the missing duplicate reference](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Scripting-method-Move-add-quot-Moved-Object-Reference/idi-p/2676263)

This is the strongest answer to ?쐁opy a Property Node or arbitrary Function that `New VI Object` cannot create?? keep the desired object in a template VI and invoke `GObject.Move` with the target diagram as owner and duplication enabled.

For multiple connected objects, copying them one at a time is not equivalent to copying the selected code fragment: wires and relationships need to be part of the same operation. LabVIEW 2010 added a selection-moving method specifically to copy or move a group without using the clipboard. [NI: LabVIEW 2010 Scripting Changes](https://forums.ni.com/t5/LabVIEW-APIs-Documents/LabVIEW-2010-Scripting-Changes/ta-p/3521934)

## 2. Selection and clipboard APIs

### Block diagram source

Exact source methods are on `TopLevelDiagram`:

- `Make Selection`
- `Copy Selection`
- `Cut Selection`
- `Clear Selection`
- `Selection List[]` property
- `Move Selected Objects` ??the method referred to in NI?셲 2010 announcement as ?쏮ove Selection.??[LabVIEW Wiki: TopLevelDiagram class](https://labviewwiki.org/wiki/TopLevelDiagram_class)

The clipboard route is:

```text
source TopLevelDiagram.Make Selection(objects[])
source TopLevelDiagram.Copy Selection
destination AbstractDiagram.Paste(position)
```

The paste method is:

- Class: `AbstractDiagram`
- Method: `Paste`
- Optional input: `Position`
- Scope: VI Scripting
- Description: pastes the clipboard contents at the specified location. [LabVIEW Wiki: AbstractDiagram.Paste](https://labviewwiki.org/wiki/AbstractDiagram_class/Paste_method)

`AbstractDiagram` is the common superclass of ordinary block diagrams and structure subdiagrams, so paste must be invoked on the actual intended subdiagram reference?봭ot merely the top-level diagram. Pasting to the top-level diagram when the intended destination is a case frame creates a ?쐄loating??object rather than an object owned by that frame. [LabVIEW Wiki: AbstractDiagram hierarchy](https://labviewwiki.org/wiki/AbstractDiagram_class), [NI example for pasting into a case-frame diagram](https://forums.ni.com/t5/LabVIEW/LabVIEW-Scripting-Paste-object-from-clipboard-inside-a-structure/td-p/4409455)

There is no need to synthesize `Edit쨩Copy` or send Ctrl+C/Ctrl+V keystrokes. The exact scripting equivalents are `TopLevelDiagram.Copy Selection` and `AbstractDiagram.Paste`.

LabVIEW maintains an internal G-code clipboard separately from the ordinary OS bitmap clipboard. Forum evidence says there is no generic VI Server property exposing that internal clipboard, but the diagram copy/paste methods operate on it. [NI: Access to clipboard in VI scripting](https://forums.ni.com/t5/LabVIEW/Access-to-clipboard-in-VI-scripting/td-p/3767611)

Clipboard copying requires an editable source VI; forum reports specifically say `TopLevelDiagram.Make Selection`/`Copy Selection` cannot copy from a running VI. [NI: Scripting?봀opy control from running VI](https://forums.ni.com/t5/LabVIEW-APIs-Discussions/Scripting-Copy-control-from-running-VI/td-p/3437371)

### Front panel source/destination

Exact front-panel methods:

- Class: `Panel`
  - `Make Selection`
  - `Copy Selection`
  - `Paste Selection`
  - `Clear Selection`
  - `Selection List[]` [LabVIEW Wiki: Panel class](https://labviewwiki.org/wiki/Panel_class)

Modern pane-specific paste:

- Class: `Pane`
- Method: `Paste Selection`
- Inputs include destination coordinates; if no pane is wired, LabVIEW uses the upper-left pane. [LabVIEW Wiki: Pane class](https://labviewwiki.org/wiki/Pane_class)

`Panel.Paste Selection` is marked deprecated in the Wiki; use `Pane.Paste Selection` where pane ownership matters. [LabVIEW Wiki: deprecated Panel.Paste Selection](https://labviewwiki.org/wiki/Panel_class/Paste_Selection_method)

Copying a front-panel control/indicator between panels is the appropriate operation when you want its appearance and attributes. Copying its block-diagram terminal and pasting onto another block diagram can create the corresponding front-panel object, but its front-panel placement can be off-screen or otherwise inconvenient. Pasting a BD terminal directly onto a destination front panel is not supported. [NI Idea Exchange demonstration](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Create-Control-Indicator-on-FP-from-copied-Terminal-Variable-on/idi-p/2820680)

### Position and wiring gotchas

`AbstractDiagram.Paste(Position)` provides an explicit drop point and is therefore preferable to UI Ctrl+V. Interactive paste otherwise uses the last mouse location, which is not a reliable cross-VI coordinate. [LabVIEW Wiki: AbstractDiagram.Paste](https://labviewwiki.org/wiki/AbstractDiagram_class/Paste_method), [NI discussion of interactive paste position](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/X-Y-Copy-Alignment-after-Copy-and-Paste-on-Block-Diagram/idi-p/4214442)

For a connected fragment, select/copy the entire fragment, including the relevant wires. NI?셲 programmatic snippet importer explicitly selects diagram objects including nodes, subVIs, decorations, and wires before copying them. [NI: Import VI Snippet Programmatically](https://forums.ni.com/t5/Example-Code/Import-VI-Snippet-png-Programmatically/ta-p/4003651)

A subVI node can be copied, but it remains a reference to the external subVI; the referenced subVI file itself is not embedded. The same limitation applies to VI snippets. [NI: Using VI Snippets](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019OHSSA2&l=en-US)

I did not find authoritative documentation promising that every implicit linkage?봲uch as a Property Node linked to a particular front-panel control?봲urvives when only the node is copied. The cheap verification is to copy the linked control/terminal, Property Node, and any connecting code as one selection, then inspect the pasted Property Node?셲 linkage. Treat copying the Property Node alone as unverified.

## 3. `Move Selected Objects`

Exact API:

- Class: `TopLevelDiagram`
- Method displayed as `Move Selected Objects`
- It simulates a diagram mouse drag.
- It can move a selection between owners and forces duplicate-drag behavior when the destination is another block diagram.
- It has mouse-drag side effects, including resizing owners and modifying the selection list to include duplicated objects. [LabVIEW Wiki: TopLevelDiagram class](https://labviewwiki.org/wiki/TopLevelDiagram_class)

Version: introduced publicly in LabVIEW 2010. NI?셲 announcement calls it ?쏮ove Selection,??while the current class listing gives the long/display name `Move Selected Objects`. [NI: LabVIEW 2010 Scripting Changes](https://forums.ni.com/t5/LabVIEW-APIs-Documents/LabVIEW-2010-Scripting-Changes/ta-p/3521934), [LabVIEW Wiki: TopLevelDiagram class](https://labviewwiki.org/wiki/TopLevelDiagram_class)

This is likely the best clipboard-free method for copying a wired group. For one arbitrary node, `GObject.Move` is simpler.

## 4. VI snippet PNG import

Native VI snippets were introduced in LabVIEW 2009. A snippet PNG contains an `niVI` PNG chunk holding serialized VI data and can normally be dragged onto a block diagram. [LabVIEW Wiki: Snippet](https://labviewwiki.org/wiki/Snippet), [NI: Using VI Snippets](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019OHSSA2&l=en-US)

I found no documented public method resembling `Diagram.Import VI Snippet`. The published programmatic importer is a workaround:

1. Extract the PNG?셲 `niVI` chunk.
2. Save that chunk as a temporary VI.
3. Open the temporary VI.
4. Select and copy all diagram objects.
5. Invoke `Paste` on the destination diagram.
6. Delete the temporary VI. [NI: Import VI Snippet Programmatically](https://forums.ni.com/t5/Example-Code/Import-VI-Snippet-png-Programmatically/ta-p/4003651)

Therefore snippets do not provide a distinct scripting primitive. They eventually reduce to opening a template VI and using selection copy/paste. They also do not embed referenced subVIs, and ordinary image editing may strip the `niVI` chunk. [NI: Using VI Snippets](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019OHSSA2&l=en-US)

## Recommendation

For your Op-VI pipeline:

- One node/object: `source GObject ??Move(owner = target AbstractDiagram, position, Duplicate? = TRUE)`.
- Several nodes plus wires: `Make Selection ??Move Selected Objects`, or `Copy Selection ??target AbstractDiagram.Paste(position)`.
- Front-panel control plus corresponding terminal: copy the front-panel control with `Panel.Copy Selection` and paste through the destination `Pane`; do not assume copying only the terminal gives predictable front-panel placement.
- VI snippets: useful as storage/transport, but programmatic import is only a wrapper around temporary-VI extraction plus ordinary selection copy/paste.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
