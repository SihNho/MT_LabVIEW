---
type: peer-review
status: historical
date: 2026-08-29
tags: [peer-review]
disposition: legacy
---

# decimate-resize

- **agent:** codex
- **date:** 2026-08-29
- **outcome:** ANSWERED (56s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW 2026 VI Scripting question. I need a 'Decimate 1D Array' node with THREE outputs (default is two) and an 'Interleave 1D Arrays' node with THREE inputs, created programmatically or at least reliably by GUI. Q1: Is there any VI Server scripting property or method to set the number of terminals on a resizable primitive node (Decimate 1D Array, Interleave 1D Arrays, Build Array, Index Array)? Something on the Node/Function class controlling terminal count or node bounds? Q2: If not, what is the exact reliable GUI gesture to grow such a node by one terminal, and can it be done by keyboard rather than a drag? ALREADY RULED OUT, do not suggest these: (a) erdosmiller lv-scripting has no Create Decimate / Create Interleave / Create Reshape - I listed all its Create*.vi files; (b) 'New VI Object' cannot create these node types - it fails with error 1054 and that is settled here; (c) brute-forcing the style code ring is banned, NI warns it can crash LabVIEW. Cite NI docs or forum URLs.

## Answer

Q1: No documented VI Server/VI Scripting API appears to control the terminal count of these resizable primitives.

- `GObject.Bounds` is read-only; NI explicitly says it cannot resize an object and that resizing requires a more class-specific property. No corresponding writable size/terminal-count property is documented for the generic Node/Function classes. [NI Community quotation of the Bounds documentation](https://forums.ni.com/t5/LabVIEW/change-the-size-height-and-widht-form-a-XY-graph/m-p/4176233)
- A knowledgeable NI Community explanation confirms that generic GObjects expose only read-only bounds, while writable sizing exists only for object classes that specifically implement it. [NI Community: Modify an object with scripting](https://forums.ni.com/t5/LabVIEW/Modify-an-object-with-scripting/td-p/1970353)
- I found no documented `Terminal Count`, `Add Terminal`, `Resize Node`, or equivalent method for these primitive classes. Consequently, writing coordinates to `Bounds` is not an available workaround.

I would treat any undocumented/private method discovered by introspection as unsupported until NI confirms it, particularly for LabVIEW 2026.

Q2: The reliable editor operation is terminal-specific context-menu insertion, with border dragging as the general fallback.

1. Right-click an existing terminal on the relevant side of the node.
2. Select `Add Input` or `Add Output`.
3. LabVIEW inserts the new terminal immediately after the terminal that was clicked.

NI?셲 user manual explicitly documents this behavior, including that expandable nodes can instead be grown by dragging their top or bottom border with the Positioning tool. [NI LabVIEW User Manual, ?쏛dding Terminals to VIs and Functions??(https://download.ni.com/support/manuals/320999e.pdf)

Therefore:

- `Decimate 1D Array`: right-click an output terminal and choose `Add Output`.
- `Interleave 1D Arrays`: right-click an input terminal and choose `Add Input`.
- `Build Array`: `Add Input` is known to be present and documented in practice. [NI Community example](https://forums.ni.com/t5/LabVIEW/How-do-I-build-a-string-array-of-unknown-length/td-p/69323)
- `Index Array`: do not assume it has the same menu. A longstanding NI Idea Exchange report specifically says some array primitives such as Index Array lack the add/remove context-menu commands. Use border dragging for it. [NI Idea Exchange: Add Element to Index Array](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Add-quot-Add-Element-quot-and-quot-Remove-Element-quot-to-the/idi-p/1008753)

For the drag gesture: switch to or allow automatic selection of the Positioning tool, place it on the node?셲 bottom border until the resize cursor appears, then drag downward by one terminal pitch and release. Growing downward preserves the top terminals and appends one at the bottom. NI separately illustrates the same ?쐓elect node, then drag the bottom blue resize handle??procedure for expandable array functions. [NI: Create a 2D Array in LabVIEW](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019UM9SAM&l=en-US)

Keyboard-only: I found no built-in keyboard command that means ?쐅row selected primitive by one terminal.??The documented operation is a context-menu command or mouse drag. Reports about resize keyboard shortcuts likewise indicate no standard width/height shortcut and point to custom Quick Drop tooling instead. [NI Community: shortcuts for Resize Objects](https://forums.ni.com/t5/LabVIEW/Short-keys-for-Resize-objects-menu-on-front-pannel/td-p/4242856)

For GUI automation, the context-menu command is preferable to pixel dragging when present: right-click the exact terminal, then activate `Add Input`/`Add Output`. For nodes lacking that item, the bottom-border drag is the documented fallback. The cheap verification is to obtain an `OpReport` before and after and confirm that the terminal array increased from 2 to 3.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
