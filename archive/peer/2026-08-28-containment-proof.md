---
type: peer-review
status: historical
date: 2026-08-28
tags: [peer-review]
---

# containment-proof

- **agent:** codex
- **date:** 2026-08-28
- **outcome:** ANSWERED (51s)
- **why asked:** How to prove a subVI is inside a specific loop, not just owned by some Diagram?
- **verdict:** adopted

## Question

LabVIEW VI Scripting. I need to prove programmatically that a specific subVI node sits INSIDE a specific For Loop's subdiagram (not merely that its owner is of class Diagram). Available: Traverse for GObjects.vi (vi.lib Utility traverseref.llb) and Property Nodes. Questions: (1) On a GObject reference, what is the exact property that returns its owner, what CLASS of reference does it return, and can I read a UID from that returned reference directly - or must I cast (To More Specific Class) to GObject first? Give exact property names. (2) Traverse for GObjects.vi has a 'Traverse Target' enum (TRef TravTarget.ctl) with a value like 'Other' plus an 'Other Refnum' input: does wiring a Diagram reference there restrict traversal to objects inside THAT diagram only? What are the exact terminal names? (3) Is there a Diagram-class property that lists the objects it contains directly (e.g. 'Objects[]' or 'All Objects')? Exact class and property name. Cite URLs (labviewwiki.org, NI forums).

## Answer

1. Owner and UID

- Exact property: `Generic 쨩 Owner`
- Owning property class: `Generic`
- Return type: `Generic Refnum`
- Exact UID property: `GObject 쨩 UID`
- UID type: `I32`

Because `Owner` is statically a `Generic Refnum`, it does not directly expose the GObject-only `UID` property. Cast it with `To More Specific Class` to `GObject`?봮r to `AbstractDiagram`/`Diagram` if that is what you expect?봳hen read `GObject 쨩 UID`. A Diagram inherits from GObject, so its UID is readable after that cast. [`Generic:Owner`](https://labviewwiki.org/wiki/Generic_class/Owner_property), [`GObject:UID`](https://labviewwiki.org/wiki/GObject_class/UID_property), [class hierarchy showing Diagram inherits GObject](https://labviewwiki.org/wiki/TopLevelDiagram_class).

For a subVI node directly inside a For Loop body, the expected chain is:

```text
SubVI node
  ??Generic:Owner
  ??cast to Diagram/GObject
  ??GObject:UID
```

Compare that UID with the UID of the For Loop?셲 body Diagram reference. Equality proves direct ownership by that particular subdiagram. Merely checking the owner?셲 class as `Diagram` does not identify which diagram.

2. `Traverse for GObjects.vi`

Yes. Use these exact terminals:

- `Traverse Target` = `Other`
- `Other Refnum` = the specific Diagram reference
- `Class Name` = the desired VI Server class, such as `SubVI`
- output: `References`
- output: `# of Refs`

Other terminals are `VI Refnum`, `Traverse Generated Code`, `dup VI Refnum`, `error in`, and `error out`.

With `Traverse Target = Other`, `Other Refnum` defines the container at which traversal begins. A Diagram reference is valid because it inherits from GObject. `VI Refnum` is ignored when a specific container is supplied through `Other Refnum`. [Traverse for GObjects documentation mirror](https://rajsite.github.io/unofficial-lvdocs/glang/TRef_Traverse_for_References.html), [NI forum discussion of its `VI Refnum` and `Other Refnum` inputs](https://forums.ni.com/t5/LabVIEW/Malleable-wrapper-for-Traverse-for-GObjects/m-p/4151358).

Important qualification: traversal is recursive. It finds matching objects in that Diagram and in nested containers beneath it. Therefore:

- It proves that the node is somewhere under that diagram.
- It does not by itself prove immediate/direct ownership by that diagram.

For direct membership, compare `node.Owner.UID` with the target Diagram?셲 `UID`, or test membership in the Diagram?셲 nonrecursive `All Objects[]`.

3. Directly contained objects

The exact property is:

- Class: `AbstractDiagram`
- Property: `All Objects[]`
- Internal/data name: `AllObjs[]`
- Return type: array of `GObject Refnum`
- Semantics: all top-level objects in that diagram

`Diagram` inherits this property from `AbstractDiagram`. It is not recursive, making it suitable for proving that a subVI node is directly on that particular loop subdiagram. [`AbstractDiagram:All Objects[]`](https://labviewwiki.org/wiki/AbstractDiagram_class/All_Objects%28%29_property), [NI forum noting that `Diagram:AllObjects[]` returns main/top-level objects rather than recursively nested objects](https://forums.ni.com/t5/LabVIEW/LV-Scripting-how-to-get-all-diagram-object-references/td-p/2742296).

The strongest programmatic proof is therefore either:

```text
cast(SubVI.Owner, GObject).UID == ForLoopBodyDiagram.UID
```

or:

```text
SubVI reference/UID is present in ForLoopBodyDiagram.All Objects[]
```

The first is the clearest direct-owner test.

## Sources

(extract from answer)

## What was done with it

Gave the exact chain (Generic:Owner returns a Generic refnum -> cast to GObject -> GObject:UID) and the better option AbstractDiagram All Objects[] (non-recursive = direct membership), plus the caveat that Traverse Target=Other is recursive. Recorded in STATUS as the identity-level route; the build itself was settled by two cheaper empirical proofs (elimination + offset bijection).
