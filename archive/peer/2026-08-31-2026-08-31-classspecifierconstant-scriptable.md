---
type: peer-review
status: historical
date: 2026-08-31
tags: [peer-review]
disposition: legacy
---

# 2026-08-31-classspecifierconstant-scriptable

- **agent:** codex
- **date:** 2026-08-31
- **outcome:** ANSWERED (46s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Short factual VI-Scripting question, LabVIEW 2026, cite sources (labviewwiki.org class pages are ideal).

(1) The block-diagram object class 'ClassSpecifierConstant' (the VI Server Class constant you normally retype via its left-click picker menu): does VI Scripting expose a WRITABLE property to change WHICH class it specifies - e.g. a 'VI Server Class' / 'Class' / 'VIServerClass' property on ClassSpecifierConstant, settable at edit time from a string or a class-ID? List the class's actual properties/methods from the wiki page if it exists. (2) If not directly settable, is there any scripted route to obtain a 'To More Specific Class' node whose class specifier is LoopTunnel - e.g. does any Create *.vi in erdosmiller lv-scripting or any NI-shipped scripting VI create class-specifier constants of a given class? (3) Separately: the GObject 'Label' - is Label.Text WRITABLE by scripting on block-diagram NODES (functions/primitives), so a script can label a primitive for later find-by-label operations? Which classes allow it (the wiki's Label class / GObject.Label property pages)? Answer tersely with URLs.

## Answer

1. **Yes?봡irectly settable.** `ClassSpecifierConstant` exposes:

   - `Class Name` (`566EFC02`) ??**Read/Write**; accepts the selected class name.
   - `Set Type` method (`566EF800`) ??accepts the class?셲 unique **ID String**; obtain IDs from `All Types[]`.
   - Other properties: `Type (Deprecated)` R/W, `Terminal` RO, `Is Scripting Class Selected` RO, `Is Private Class Selected` RO, `All Types[]` RO, and `Type` RO despite its description saying ?쐅ets or sets.?? 
   
   Full table: [ClassSpecifierConstant class](https://labviewwiki.org/wiki/ClassSpecifierConstant_class). ID-based setter details: [Set Type method](https://labviewwiki.org/wiki/ClassSpecifierConstant_class/Set_Type_method).

2. Therefore no special ?쏞reate??VI is necessary. Create/place the ordinary `To More Specific Class` function and its class-specifier constant, then either:

   - write `Class Name = "LoopTunnel"`, or
   - call `Set Type` with LoopTunnel?셲 ID from `All Types[]`.

   `LoopTunnel` is a scripting class in the hierarchy, and `To More Specific Class` supports VI Server refnum hierarchies: [VI Server Class Hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy), [To More Specific Class](https://labviewwiki.org/wiki/To_More_Specific_Class_function).

3. **Yes for block-diagram nodes, including primitives?봟ut through `Node.Label`, not a universal `GObject.Label`.** `Function`/primitive nodes inherit `Node`; `Node.Label` is a read-only **reference** to the label, while the referenced object?셲 `Text` property is **Read/Write**. The wiki warns that the node label must have been displayed at least once before `Node.Label` can return its text/reference reliably. [Node class](https://labviewwiki.org/wiki/Node_class), [Text.Text property](https://labviewwiki.org/wiki/Text_class/Text_property).

So the practical sequence is: ensure/show the node label, obtain `Node.Label`, then write `Label.Text`. This applies to `Node` descendants?봣unctions, growable functions, structures, subVIs, etc.?봭ot every arbitrary `GObject`.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
