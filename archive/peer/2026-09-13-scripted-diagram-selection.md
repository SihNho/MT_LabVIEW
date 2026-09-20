---
type: peer-review
status: historical
date: 2026-09-13
tags: [peer-review]
disposition: legacy
---

# scripted-diagram-selection

- **agent:** codex
- **date:** 2026-09-13
- **outcome:** ANSWERED (129s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FACT QUESTION about LabVIEW VI Scripting (LabVIEW 2026, driven over ActiveX/COM from Python). I need to know whether the diagram SELECTION can be set programmatically, because it is the input to the subVI-extraction method and currently the only reason a mouse would be needed at all.

WHAT I ALREADY ESTABLISHED (confirmed by a previous search):
  AbstractDiagram.SubVI From Selection - method ID 6375405 decimal / 0x6147ED, owning class 16503, scope PRIVATE,
  inputs `Clean Up Wires`, `SubVI`, `Add To Project`, `Apply 'Create SubVI' Plugin`, returns the new VI reference.
  The three private ini tokens (SuperPrivateScriptingFeatureVisible, SuperPrivateSpecialStuff,
  SuperSecretPrivateSpecialStuff) are already set in this install.

QUESTIONS:

1. Is there a VI Server PROPERTY or METHOD that SETS which objects are selected on a block diagram? Candidates I can imagine: a `Selection[]` property on Diagram / AbstractDiagram / Panel, or a `Selected` boolean on GObject. Give exact class + property/method name and its Unique ID if you can find one. State the scope (public VI Scripting, private, super-private).
2. Is there a corresponding READ - can I query what is currently selected?
3. If selection is settable, does `SubVI From Selection` actually act on it when invoked headlessly (no visible block-diagram window)? Or does the operation require the diagram window to be open/frontmost? Any reports either way.
4. If selection is NOT settable, is there any other scripted route to "make these N specific nodes into a subVI" - e.g. move objects into a new VI, or an API that takes an array of object references instead of a selection?
5. Related: can a GObject be moved BETWEEN VIs by script (from one VI's diagram to another's)? I know `GObject.Move` (632A400) moves within a diagram. Is there a cross-VI equivalent, or is copy/paste via the clipboard the only route?

I have working tools for: traversing any class and getting uid/position/owner, reading per-diagram connectivity with terminal names, creating Property and Invoke nodes by class string + ID, wiring by terminal name, deleting objects. What I do NOT have is any way to move a multi-node region into another VI.

Cite labviewwiki, NI documentation, or forum posts with URLs. If the honest answer is "selection is not exposed", say that plainly with what you checked - a documented negative is worth as much to me as a positive.


## Answer

Yes. Diagram selection is programmatically settable; a mouse is not inherently required.

1. Setting the selection

There are two useful APIs.

- `GObject.Selected`
  - Class: `GObject`
  - Class ID: `36`
  - Property ID: `0x632A809`
  - Type: Boolean, read/write
  - Scope: Basic Development Environment
  - Effect: setting it `TRUE` adds that object to the current editor selection; setting it `FALSE` removes it.
  - This is inherited by diagram nodes, wires, structures, terminals, decorations, controls, etc. [LabVIEW Wiki: GObject class](https://labviewwiki.org/wiki/GObject_class)

- `TopLevelDiagram.Make Selection`
  - Class: `TopLevelDiagram`
  - Class ID: `16423`
  - Method ID: `0x6349002`
  - Input: array of `GObject` references
  - Scope: public VI Scripting
  - Effect: selects exactly the supplied objects and deselects all others. [LabVIEW Wiki: TopLevelDiagram class](https://labviewwiki.org/wiki/TopLevelDiagram_class)

The second API is the cleaner choice for your operation:

```text
VI.Block Diagram
    ??TopLevelDiagram.Make Selection(Objects[])
    ??AbstractDiagram.SubVI From Selection(...)
```

Related public VI Scripting methods are:

- `Clear Selection`: `0x6349001`
- `Copy Selection`: `0x6349003`
- `Make Selection From Rect`: `0x6349005`
- `RemoveFromSelection`: `0x634900C`

All belong to `TopLevelDiagram`, class `16423`. [LabVIEW Wiki](https://labviewwiki.org/wiki/TopLevelDiagram_class)

One constraint worth testing: all supplied references should belong to one selectable diagram context. Do not mix objects from different VIs or different simultaneously visible structure frames.

2. Reading the selection

There are two corresponding reads:

- `TopLevelDiagram.Selection List[]`
  - Property ID: `0x6349400`
  - Read-only
  - Returns an array of selected `GObject` references
  - Scope: public VI Scripting. [LabVIEW Wiki](https://labviewwiki.org/wiki/TopLevelDiagram_class)

- `GObject.Selected`
  - Property ID: `0x632A809`
  - Read/write Boolean
  - Suitable for checking one particular object. [LabVIEW Wiki](https://labviewwiki.org/wiki/GObject_class)

Thus you can verify the exact selection before extracting by comparing the returned UIDs with your requested UID set.

3. Headless `SubVI From Selection`

I found strong evidence that selection is model state rather than merely mouse/window decoration, but no source explicitly demonstrating this exact private method with a never-opened block-diagram window.

Relevant evidence:

- `Make Selection` and `Selection List[]` are VI Server APIs, not simulated mouse operations. [LabVIEW Wiki](https://labviewwiki.org/wiki/TopLevelDiagram_class)
- An NI scripting overview explicitly recommends chaining `TopLevelDiagram.MakeSelection`, `CopySelection`, and `PasteSelection` for scripted code manipulation. [NI Community](https://forums.ni.com/t5/LabVIEW-APIs-Documents/LabVIEW-Scripting/ta-p/3535340)
- A shortcut-menu plugin report confirms that `Make Selection` changes the selection even when the visual ?쐌arching ants??are absent or stale. That separates the actual selection list from its window rendering. [NI Community](https://forums.ni.com/t5/LabVIEW-Shortcut-Menu-Plug-Ins/Selected-Items-in-plugin-script-have-no-marching-ants-when/ta-p/4016983)
- These APIs require edit mode; selection/copy does not work on a running target VI. [NI Community](https://forums.ni.com/t5/LabVIEW-APIs-Discussions/Scripting-Copy-control-from-running-VI/td-p/3437371)

My evidence-based expectation is therefore:

> `Make Selection` followed by `SubVI From Selection` should work without the block-diagram window being frontmost, and probably without it being visibly open, provided the VI is in edit mode and its diagram is available in the development environment.

But that last ?쐍ever visibly open??case remains unconfirmed by a published report. The cheapest decisive test is:

1. Open the target VI reference headlessly in edit mode.
2. Obtain its block-diagram reference and two known object references.
3. Call `Make Selection`.
4. Read `Selection List[]` and confirm the exact UIDs.
5. Call `SubVI From Selection`.
6. Confirm a non-null new-VI reference and that the original nodes were replaced.

If step 3?? succeeds but step 5 fails until `Open.BD` is called, then the private extraction operation itself has a UI-window dependency. Nothing I found says it must be frontmost.

4. Other routes to construct a subVI

There are three relevant alternatives.

- `TopLevelDiagram.NewVIFromSelection`
  - Method ID: `0x634900E`
  - Scope: public VI Scripting
  - This is another selection-driven API, so it does not remove the selection requirement, but it deserves testing against the private `AbstractDiagram.SubVI From Selection`. [LabVIEW Wiki](https://labviewwiki.org/wiki/TopLevelDiagram_class)

- Scripted copy/paste:
  - Source: `Make Selection` ??`Copy Selection`
  - Destination: `AbstractDiagram.Paste`
  - `AbstractDiagram.Paste` ID: `0x6375400`
  - Scope: public VI Scripting
  - Input: optional destination position. [LabVIEW Wiki: Paste](https://labviewwiki.org/wiki/AbstractDiagram_class/Paste_method)

  A recent NI forum example confirms that copying a selection and pasting into a diagram in another VI works, including contents of a structure frame. [NI Community](https://forums.ni.com/t5/LabVIEW/VI-Scripting-Copy-contents-of-one-case-structure-frame-to-a-new/m-p/4480508)

  This preserves the selected code as a copied region, but you must independently:
  - create destination controls/indicators,
  - reconnect boundary wires,
  - configure the connector pane,
  - drop the new VI as a subVI,
  - delete the source objects.

- `VI.Create from Reference`
  - VI class ID: `2`
  - Method ID: `0x443`
  - Scope: VI Scripting
  - This duplicates a control or constant from an object reference; it is not a general multi-node cloning operation. [LabVIEW Wiki](https://labviewwiki.org/wiki/VI_class/Create_from_Reference_method)

I found no public method that accepts an arbitrary array of node references and directly creates a wired subVI without first establishing an editor selection. `Make Selection(Objects[])` is effectively that missing array-input front end.

5. Moving objects between VIs

`GObject.Move` (`0x632A400`) is not a cross-VI reparenting method. It changes the position of an object within its existing owner. [LabVIEW Wiki: GObject class](https://labviewwiki.org/wiki/GObject_class)

`TopLevelDiagram.Move Selected Objects` (`0x634900F`) also should not be treated as a clean cross-VI ownership-transfer API. Its documentation says it moves objects within the referenced `TopLevelDiagram` and simulates editor drag behavior; the mention of duplicate-drag into another diagram describes a drag side effect, not a destination-VI/reference parameter. [LabVIEW Wiki](https://labviewwiki.org/wiki/TopLevelDiagram_class)

For reliable cross-VI transfer, the supported route is therefore:

```text
source TopLevelDiagram.Make Selection(objects[])
source TopLevelDiagram.Copy Selection
destination AbstractDiagram.Paste(position)
```

This is genuine VI Scripting, even though it uses LabVIEW?셲 internal clipboard. NI forum examples and NI staff recommendations describe that exact family of operations for copying code between diagrams. [NI scripting overview](https://forums.ni.com/t5/LabVIEW-APIs-Documents/LabVIEW-Scripting/ta-p/3535340), [cross-VI example](https://forums.ni.com/t5/LabVIEW/VI-Scripting-Copy-contents-of-one-case-structure-frame-to-a-new/m-p/4480508)

Bottom line: build `TopLevelDiagram.Make Selection` at `0x6349002`, feed it your exact `GObject Ref[]`, verify via `Selection List[]` at `0x6349400`, then invoke your existing `0x6375405`. That should eliminate the mouse; only the completely hidden-window behavior still needs a small machine-level confirmation.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
