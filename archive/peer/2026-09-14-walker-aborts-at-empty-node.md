---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# walker-aborts-at-empty-node

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (67s)
- **why asked:** hypothesis that the walker aborts at the first empty node.
- **verdict:** superseded by the junk-Invoke finding (the walker's own junk, purged since).

## Question

ATTACK this hypothesis (LabVIEW 2026 VI Scripting over ActiveX). OBSERVATION, deterministic over 3 repeated reads: on a scratch VI I created four Property nodes in sequence by script: (1) GObject.Position 632A800, (2) Control.Terminal 6332006, (3) AbstractDiagram.SubVIs[] 6375802, (4) AbstractDiagram.Nodes[] 6375809 - the last one is a KNOWN-GOOD ID used in working ops. A separate reporter (Traverse for GObjects, class 'Property') sees all four uids. My node walker - an op doing AbstractDiagram.Nodes[] -> Index Array by index -> Node.Terminals[] -> Terminal.Name, iterating index 0..N - lists node (1) with its 'Position' row, and lists NONE of (2),(3),(4), not even the known-good (4). HYPOTHESIS: the walker iterates Nodes[] by index and ABORTS (error in the op's dataflow, swallowed) at the first node whose property rows are empty - because Node.Terminals[] or a downstream read on a rows-less Property node errors - so every node after it in Nodes[] order is never visited; (2) and (3) really are empty (their Set Properties[] failed, likely error 1077, and the creator op sinks the error). QUESTIONS: (a) does Node.Terminals[] on a Property node with zero property rows error, return an empty array, or return the four generic terminals? (b) in what order does AbstractDiagram.Nodes[] return nodes - creation order, z-order, or unspecified - i.e. can I rely on 'node created later = later index' for this reasoning? (c) is there a documented behaviour for a Property node whose Set Properties[] failed: is the node left with 0 rows, or with 1 default row (e.g. the class's first property)? (d) what is the cheapest scripted DISCRIMINATING test: I propose creating the known-good (4) BEFORE (2) and (3) - if (4) is then visible and (2),(3) still are not, the walker aborts at empties and (2),(3) are confirmed empty. Any flaw in that test? Cite labviewwiki/NI where possible.

## Answer

The hypothesis is probably wrong at its key step: a zero-row Property node should still expose the four generic terminals. `Node.Terminals[]` itself is therefore unlikely to be the abort source.

### (a) Zero-row Property node terminals

Best available evidence says a Property node has:

- Terminals 0??: reference in, reference out, error in, error out.
- Terminals 4?쫚??: one terminal per property row.

Therefore, a zero-row Property node should return four terminal references?봭ot an empty array and not an error. This is community evidence rather than an explicit NI guarantee, but it directly describes inspection through `Node.Terminals[]`. [NI Community: Scripting?봗erminal Information](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/m-p/4303393)

The formal `Node.Terminals[]` documentation merely says it returns ?쏿n array of references to the terminals of the node?? it documents neither a zero-row exception nor an error case. [LabVIEW Wiki: Node.Terminals[]](https://labviewwiki.org/wiki/Node_class/Terminals%28%29_property)

So if the walker stops at node (2), more plausible failure points are:

- casting the generic Node reference to the wrong subclass;
- reading a terminal property from an invalid/default reference produced by indexing logic;
- assuming a particular terminal count or index;
- error-cluster propagation from an earlier operation;
- filtering/output assembly that discards nodes whose property-item terminal names are absent.

Merely calling `Terminal.Name` on the four valid generic terminal references should not distinguish a zero-row Property node from another Property node by causing an error.

### (b) `AbstractDiagram.Nodes[]` order

Do not rely on creation order.

Both NI and LabVIEW Wiki say only that `Nodes[]` returns references to all nodes. Neither defines creation order, z-order, spatial order, or stability between calls. [NI: AbstractDiagram.Nodes[]](https://www.ni.com/docs/zh-CN/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/abstractdiagram/nodes.html), [LabVIEW Wiki: AbstractDiagram.Nodes[]](https://www.labviewwiki.org/wiki/AbstractDiagram_class/Nodes%28%29_property)

The claim that some front-panel `Controls[]` collections follow creation order does not establish the same contract for `AbstractDiagram.Nodes[]`; they are different collections. [NI Community: Controls[] ordering discussion](https://forums.ni.com/t5/LabVIEW/Way-to-reorder-controls-in-front-panel/m-p/1950859)

Thus, ?쐁reated later ??larger `Nodes[]` index??is unsupported even if it happens deterministically in this scratch VI.

### (c) State after failed `Set Properties[]`

I found no documented postcondition.

The available class documentation says only that `Set Properties[]` sets the Property node?셲 selected properties. It does not state whether failure is atomic, preserves the previous selection, leaves zero rows, or installs a default property. The same class exposes three much better state probes:

- `Property Count`
- `Properties[]`
- `Property Items[]`

[LabVIEW Wiki: Property class](https://labviewwiki.org/wiki/Property_class)

Error 1077 means ?쐇nvalid property value,??but that definition does not describe the receiver?셲 state after the failed write. [NI: Error 1077 example](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P6FSSA0)

Consequently, ??2) and (3) are empty because `Set Properties[]` returned 1077??is plausible but unproved. They could retain whatever initial/default row existed before the failed method call.

### (d) Cheapest discriminating test

Your reorder test is not cleanly discriminating because it depends on undocumented `Nodes[]` ordering. Even if (4) becomes visible, that would only support?봱ather than establish?봳he abort explanation.

A cheaper and stronger test requires no recreation:

1. Use the reporter?셲 traversal result to select each Property reference by UID.
2. For UIDs (1)??4), independently read:
   - `Property Count`
   - `Properties[]`
   - `Property Items[]`
   - `Node.Terminals[]` array size
3. Capture and clear the error separately around every read; do not thread one uncleared error cluster through all four nodes.
4. For every returned terminal, record terminal index, validity, name, and the exact error from `Terminal.Name`.

Expected signatures:

| State | Property Count | Property Items | Terminals |
|---|---:|---:|---:|
| Zero property rows | 0 | 0 | probably 4 |
| One property row | 1 | 1 | probably 5 |
| Walker fails on generic terminals | 0 | 0 | 4, with a recorded downstream error |
| Node absent due to enumeration/filtering | Direct UID probe succeeds, ordinary walker omits it |

`Property Count` is specifically documented as getting the number of properties in the node, while `Property Items[]` returns references to the individual property items. [LabVIEW Wiki: Property class](https://labviewwiki.org/wiki/Property_class)

The decisive attack on the current hypothesis is therefore: **even if (2) and (3) have zero rows, that alone does not predict `Node.Terminals[]` failure.** First measure their `Property Count`, then isolate the exact operation producing the first nonzero error.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
