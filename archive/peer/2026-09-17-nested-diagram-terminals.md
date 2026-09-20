# nested-diagram-terminals

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** fact
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (250s)
- **why asked:** OPEN 33 - `OpConnectNested_v0` can only wire two terminals on the SAME diagram; §11m's 17
  `from-tunnel` rows need two DIFFERENT nested diagrams, and our second ladder measured ExecState 0
  (`tools/bench/build_opconnectnested_v0_run1.log:45`, "W4 ROUTE A wired: ExecState 0"). Pure API fact, `-Kind fact`.
- **verdict:** partly CORROBORATED by our own files (6 of 18 IDs match `docs/vi-server-ids.json` exactly, 0 conflict);
  the rest UNVERIFIED. NOT built on - no op was built from this answer.

## Question

LabVIEW 2026 VI Scripting ??pure API-fact question. Please answer with concrete class names, property/method
UNIQUE ID strings (hex, the form used by `Set Method` / `Set Properties[]` with AllowAlternateNames=FALSE, e.g.
Terminal.Connect Wire = 6349C03), and the exact node-by-node chain, citing NI documentation / LabVIEW Wiki /
forum URLs for each.

CONTEXT (what the op VI must do). We build LabVIEW code by running small "op" VIs over ActiveX. Each op opens a
target VI by path, walks the target's object graph with property/invoke nodes, and mutates it. One op must wire
between two terminals that live on TWO DIFFERENT NESTED DIAGRAMS of the target VI ??e.g. a node inside the body
of WhileLoop A and a node inside the body of WhileLoop B, or a tunnel of a Case Structure nested inside A.

THE QUESTION, in three parts.

(1) In ONE op VI, how do I obtain two Terminal references that sit on two DIFFERENT nested diagrams, so that
    `Terminal.Connect Wire` (6349C03) can wire between them? Give the correct class-specifier chain, node by
    node: which class constant goes into each `To More Specific Class`, which property IDs are read at each hop,
    and what class each hop's output actually is.

(2) Our attempt and why we ask. Working from the VI reference we do:
        `Traverse for GObjects.vi` (Class Name = "Diagram", Traverse Target = the VI) -> `References[]`
        -> `Index Array` [i] -> element is a **GObject** refnum
        -> `To More Specific Class` (target class = a class-specifier constant)
        -> a Property Node reading `Nodes[]`, then `Index Array`, then `Terminals[]` / `Terms[]`, then
           `Index Array` -> the Terminal reference -> `Connect Wire`.
    This ladder works when there is exactly ONE such ladder in the op. Adding a SECOND, independent ladder for
    the second diagram leaves the op at ExecState 0 (broken) ??the measured symptom is that the **GObject**
    element coming out of `Index Array` cannot drive a **Diagram**-class property node, i.e. the downcast is
    what breaks. (In the working single-ladder version the second Terminal comes from `VI.Block Diagram`
    ("Diagram" property) instead, which is already a Diagram-class refnum and needs no cast.)
    So: what is the CORRECT way to turn a Traverse "Diagram"-class GObject element into a reference that a
    Diagram/AbstractDiagram property node accepts? Which class constant exactly ??"Diagram", "AbstractDiagram",
    something else ??and is the LabVIEW class hierarchy here GObject -> Diagram, or GObject -> AbstractDiagram
    -> Diagram (i.e. must the cast be done in two steps)? Does `Nodes[]` live on Diagram or on AbstractDiagram,
    and what are the unique IDs of `AbstractDiagram.Nodes[]` / `Diagram.Nodes[]`?

(3) Is `Loop.Diagram` (we have the ID 6361401 for it, UNVERIFIED) or `Structure.Diagrams[]` the INTENDED route ??    i.e. from a WhileLoop/ForLoop/CaseStructure reference, get the body diagram directly rather than traversing
    all diagrams of the VI and guessing which is which? Give the exact class + property name + unique ID for
    getting a loop's body diagram and for getting a case structure's per-frame diagrams, and say which
    class-specifier constants the casts along that path need.

(4) SEPARATE SUB-QUESTION, same API: given a **LoopTunnel** reference (a tunnel on the border of a While/For
    loop), which property returns the tunnel's OUTER terminal, and from that terminal, the connected **wire**,
    and from that wire its **source terminal** and the source terminal's **owning node**? We need to resolve
    "what feeds this tunnel from outside the loop" programmatically. Give the property chain with unique IDs:
    e.g. LoopTunnel/Tunnel -> (outer terminal?) -> Terminal.Wire -> Wire.Source Terminal? Wire.Wire Source?
    -> Terminal.Owner / Terminal.Owning Node. Name each property's exact name, its class, and its unique ID,
    and say which of them are private (SuperSecretPrivateSpecialStuff) vs public VI Scripting scope.

Please be explicit about which of your IDs you are SURE of (from documentation you can cite) versus inferred.


## Answer

The key point: `Nodes[]` belongs to `AbstractDiagram`, not `Diagram`. A Traverse result can be downcast directly from `GObject` to either `AbstractDiagram` or `Diagram`; you do not cast through both. For your ladder, cast directly to `AbstractDiagram`.

Also, a single physical LabVIEW wire cannot inhabit two diagrams. `Terminal.Connect Wire` can ask LabVIEW to connect endpoints across a structure boundary, in which case LabVIEW may create the required tunnels and per-diagram wire segments. That tunnel-creation behavior is supported by community examples, but it is not specified in the formal `Connect Wire` documentation, so I would verify the resulting topology after the call.

## 1. Exact Traverse → terminal chain

For each of the two endpoints:

```text
Target VI ref
  │
  ├─ Traverse for GObjects.vi
  │    Traverse Target = BD
  │    Class Name      = "Diagram"
  │
  └─ References[]                         static type: GObject[]
       │
       └─ Index Array                     static type: GObject
            │
            └─ To More Specific Class
                 target class constant:
                   Generic
                     → GObject
                       → AbstractDiagram
                 │
                 └─ AbstractDiagram ref
                      │
                      └─ AbstractDiagram.Nodes[]
                           ID: 6375809
                           output: Node[]
                              │
                              └─ Index Array
                                   output: Node
                                      │
                                      └─ Node.Terminals[]
                                           Data Name: Terms[]
                                           ID: 6359000
                                           output: Terminal[]
                                              │
                                              └─ Index Array
                                                   output: Terminal
```

`Traverse for GObjects` deliberately returns `GObject[]`; its documentation explicitly says to use `To More Specific Class` afterward. It also recursively finds objects in nested containers. [Traverse for GObjects documentation](https://rajsite.github.io/unofficial-lvdocs/glang/TRef_Traverse_for_References.html)

The verified property details are:

| Owner class | Property | ID | Scope |
|---|---|---:|---|
| `AbstractDiagram` | `Nodes[]` | `6375809` | VI Scripting |
| `Node` | `Terminals[]`; data/short name `Terms[]` | `6359000` | VI Scripting |
| `Terminal` | `Connect Wire` | `6349C03` | VI Scripting |

Sources: [AbstractDiagram.Nodes[]](https://www.labviewwiki.org/wiki/AbstractDiagram_class/Nodes%28%29_property), [Node.Terminals[]](https://www.labviewwiki.org/wiki/Node_class/Terminals%28%29_property), [Terminal.Connect Wire](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method).

Duplicate that complete ladder independently for endpoint B. Invoke `Connect Wire` on the sink terminal and wire endpoint A’s `Terminal` ref to its `Wire Source` input.

### Alternative legal cast

This is also legal:

```text
GObject
  → To More Specific Class
      target = Generic → GObject → AbstractDiagram → Diagram
  → Diagram ref
  → inherited AbstractDiagram.Nodes[] (6375809)
```

`Diagram` inherits through exactly:

```text
Generic → GObject → AbstractDiagram → Diagram
```

[Diagram class hierarchy](https://labviewwiki.org/wiki/Diagram_class)

But this does **not** imply two downcast nodes. `To More Specific Class` can downcast directly from `GObject` to any compatible descendant. NI’s navigation documentation describes the direct downcast model. [NI: Navigating from a Wire to a Node](https://www.ni.com/docs/en-US/bundle/labview/page/navigating-from-a-wire-to-a-node-using-vi-scripting.html)

### Connecting endpoints on different diagrams

A wire object belongs to one diagram; crossing a loop/case boundary is represented by outer/inner tunnel terminals and separate wire segments. The editor can synthesize tunnels when scripting a connection across a structure boundary—an accepted NI forum answer explicitly says that connecting the two endpoints automatically creates the tunnel—but this is community-observed behavior, not a guarantee stated on the formal `Connect Wire` API page. [NI forum: programmatically creating a tunnel](https://forums.ni.com/t5/LabVIEW/Programmatically-creating-a-tunnel-with-LV-scripting/td-p/1830745)

For sibling loops A and B, the resulting logical path should be:

```text
source node in A body
  → A inside tunnel terminal
  → A outside tunnel terminal
  → top-level wire
  → B outside tunnel terminal
  → B inside tunnel terminal
  → sink node in B body
```

For a Case Structure nested inside A, add another outer/inner tunnel pair at that Case boundary. Case tunnels have one outer terminal and one inner terminal per case. [NI forum: wiring a pass-through tunnel](https://forums.ni.com/t5/LabVIEW/LabvVIEW-Scripting-wiring-a-pass-through-tunnel-inside-a-case/m-p/3945608)

For production code I would verify afterward that:

- `Terminal.Diagram`, `634A002`, gives the expected diagram for each endpoint.
- The relevant structures’ `Tunnels[]`, `6360801`, gained the expected tunnel.
- Each created wire’s `Terminals[]`, `6371003`, contains endpoints on only its own diagram.

[Terminal properties](https://labviewwiki.org/wiki/Terminal_class), [Structure properties](https://labviewwiki.org/wiki/Structure_class), [Wire properties](https://labviewwiki.org/wiki/Wire_class).

## 2. What is wrong with the second ladder?

The authoritative hierarchy is:

```text
Generic
  → GObject
    → AbstractDiagram
      → Diagram
        → TopLevelDiagram
```

[AbstractDiagram hierarchy](https://labviewwiki.org/wiki/AbstractDiagram_class), [Diagram hierarchy](https://labviewwiki.org/wiki/Diagram_class), [TopLevelDiagram hierarchy](https://www.labviewwiki.org/wiki/TopLevelDiagram_class).

Therefore:

- A runtime `Diagram` object may be downcast directly from `GObject` to `AbstractDiagram`.
- It may also be downcast directly from `GObject` to `Diagram`.
- Two-stage `GObject → AbstractDiagram → Diagram` is unnecessary.
- If your Property Node is explicitly configured as `AbstractDiagram.Nodes[]`, use an `AbstractDiagram` class-specifier constant.
- If it is statically configured as `Diagram`, use a `Diagram` constant; the property remains inherited from `AbstractDiagram`.

There is no separate `Diagram.Nodes[]` ID. The single property is:

```text
AbstractDiagram.Nodes[] = 6375809
Owning Class ID          = 16503
Owning Class Name        = AbstractDiagram
```

[AbstractDiagram.Nodes[] metadata](https://www.labviewwiki.org/wiki/AbstractDiagram_class/Nodes%28%29_property)

Thus the fact that the op becomes broken only after adding the second ladder is not explained by VI Server class hierarchy. A correctly generated second copy of the above ladder is statically valid. The most likely code-generation-level possibilities are:

- The second class-specifier constant is not actually configured as `AbstractDiagram`/`Diagram`.
- The second `To More Specific Class` has its terminals wired by the wrong terminal index.
- The Property Node was configured for another class despite displaying a similar property name.
- `Set Properties[]` selected an alternate/localized name or the wrong inherited property.
- The second `Index Array` output was wired directly to the Property Node, bypassing the downcast output.

Those are diagnoses, not documented API facts. Reporter output showing the two `To More Specific Class` terminals, both class-specifier constants’ class names, and the broken-wire error text would distinguish them cheaply.

## 3. Preferred structure-owned route

Yes: when you already possess the loop or Case Structure reference, the structure-owned properties are the cleaner and less ambiguous route.

### While/For loop body

```text
GObject loop result
  → To More Specific Class
      target constant:
        Generic → GObject → Node → Structure → Loop
  → Loop.Diagram
      ID: 6361401
  → Diagram ref
  → AbstractDiagram.Nodes[]
      ID: 6375809
  → Node[]
```

`Loop.Diagram`, `6361401`, is verified and returns the loop’s diagram. [Loop class](https://labviewwiki.org/wiki/Loop_class)

You may instead cast directly to the concrete class:

```text
Generic → GObject → Node → Structure → Loop → WhileLoop
Generic → GObject → Node → Structure → Loop → ForLoop
```

Both inherit `Loop.Diagram`; no intermediate casts are required. [WhileLoop hierarchy](https://labviewwiki.org/wiki/WhileLoop_class), [ForLoop hierarchy](https://labviewwiki.org/wiki/ForLoop_class)

### Case Structure diagrams

```text
GObject case result
  → To More Specific Class
      target constant:
        Generic → GObject → Node → Structure
  → Structure.Diagrams[]
      ID: 6360803
  → Diagram[]
  → Index Array
  → selected Diagram
  → AbstractDiagram.Nodes[]
      ID: 6375809
```

`Structure.Diagrams[]`, `6360803`, returns all subdiagrams of the structure. [Structure.Diagrams[]](https://labviewwiki.org/wiki/Structure_class/Diagrams%28%29_property)

Casting directly to this concrete class is also valid:

```text
Generic
  → GObject
    → Node
      → Structure
        → MultiFrameStructure
          → CaseStructure
```

[CaseStructure hierarchy](https://labviewwiki.org/wiki/CaseStructure_class)

Again, this is one `To More Specific Class`, not a cast at every inheritance level.

If you need a case by name rather than relying on array position:

```text
CaseStructure.Get Frame Index
ID: 6364C04
Frame Name → index
index + Structure.Diagrams[] → selected diagram
```

[CaseStructure methods](https://labviewwiki.org/wiki/CaseStructure_class)

### Which route is intended?

Use:

- `Loop.Diagram`, `6361401`, for a known While/For loop.
- `Structure.Diagrams[]`, `6360803`, for Case/Event/other structures.
- Traverse `"Diagram"` only when you genuinely need every diagram or do not yet know the owning structure.

This avoids guessing which globally traversed diagram belongs to which structure.

## 4. LoopTunnel → outside source chain

The public chain is:

```text
LoopTunnel ref
  │
  └─ inherited Tunnel.Outside Terminal
       ID: 6356001
       output: OuterTerminal
          │
          └─ inherited Terminal.Connected Wire
               ID: 634A000
               output: Wire
                  │
                  └─ Wire.Terminals[]
                       ID: 6371003
                       output: Terminal[]
                          │
                          ├─ index 0 for a valid ordinary wire
                          │    output: source Terminal
                          │
                          └─ or inspect every element with:
                               Terminal.Is Source?
                               ID: 634A003
                          │
                          └─ source Terminal
                               │
                               └─ Generic.Owner
                                    ID: 6327806
                                    output: Generic ref
                                       │
                                       └─ To More Specific Class
                                            target = Generic → GObject → Node
                                            output: Node
```

Verified IDs and scope:

| Owner class | Exact property | ID | Scope |
|---|---|---:|---|
| `Tunnel` | `Outside Terminal` | `6356001` | VI Scripting |
| `Tunnel` | `Inside Terminals[]`; data name `InsideTerms[]` | `6356000` | VI Scripting |
| `Terminal` | `Connected Wire` | `634A000` | VI Scripting |
| `Wire` | `Terminals[]` | `6371003` | VI Scripting |
| `Terminal` | `Is Source?`; data name `IsSource` | `634A003` | VI Scripting |
| `Generic` | `Owner` | `6327806` | Basic Development Environment |

Sources: [Tunnel class](https://labviewwiki.org/wiki/Tunnel_class), [Tunnel.Inside Terminals[]](https://labviewwiki.org/wiki/Tunnel_class/Inside_Terminals%28%29_property), [Terminal class](https://labviewwiki.org/wiki/Terminal_class), [Terminal.Is Source?](https://labviewwiki.org/wiki/Terminal_class/Is_Source%3F_property), [Wire class](https://labviewwiki.org/wiki/Wire_class), [Generic.Owner](https://labviewwiki.org/wiki/Generic_class/Owner_property).

NI’s current documentation states that, for a valid wire, element zero of `Wire.Terminals[]` is the source terminal, then directs you through `Terminal.Owner` and an optional downcast to the actual node class. [NI: Navigating from a Wire to a Node](https://www.ni.com/docs/en-US/bundle/labview/page/navigating-from-a-wire-to-a-node-using-vi-scripting.html)

Using `Is Source?` is safer if you may encounter malformed/broken wires; community reports note that index zero is not necessarily a source when no valid source exists or when a broken wire has multiple sources. [LAVA: Traverse wire to source](https://lavag.org/topic/10734-traverse-wire-to-source/)

There is no public `Wire.Source Terminal` or `Wire.Wire Source` property in the documented `Wire` class. The public route is `Wire.Terminals[]` followed by index zero or `Terminal.Is Source?`. [Wire class property table](https://labviewwiki.org/wiki/Wire_class)

### Owner caveat

For ordinary node terminals, `Terminal.Owner` leads to the node. For a `ControlTerminal`, LabVIEW instead reports the containing diagram as owner; NI forum confirmation explains this distinction. [NI forum: Terms[] and Owner behavior](https://forums.ni.com/t5/LabVIEW/Vi-Scripting-inconsistent-behaviour-of-terms-of-a-wire-owner/td-p/3309055)

If the source terminal is a `ControlTerminal`, use:

```text
Terminal
  → To More Specific Class
      Generic → GObject → Terminal → ControlTerminal
  → ControlTerminal.Control
      ID: 6353000
  → Control ref
```

[ControlTerminal class](https://labviewwiki.org/wiki/ControlTerminal_class)

If the source terminal itself is an `OuterTerminal` and you want to continue through another structure:

```text
Terminal
  → To More Specific Class
      Generic → GObject → Terminal → OuterTerminal
  → OuterTerminal.Tunnel
      ID: 7CC75C00
  → Tunnel
  → Tunnel.Inside Terminals[]
      ID: 6356000
  → continue recursively
```

[OuterTerminal.Tunnel](https://labviewwiki.org/wiki/OuterTerminal_class), [LAVA recursive source traversal](https://lavag.org/topic/10734-traverse-wire-to-source/).

None of the properties in the recommended chain require `SuperSecretPrivateSpecialStuff`; they are either public VI Scripting scope or, for `Generic.Owner`, Basic Development Environment scope. I found no documented public or private unique ID for a separate `Wire.Source Terminal` property, so I would not generate one by inferred naming.

## Sources

(extract from answer)

## What was done with it

**NOTHING WAS BUILT FROM IT** (the brief forbade it; the decision is judgement's). What was done is the one
thing a material session can do with a peer answer: check every ID it gave against our own measured file.

1. **ID VERIFICATION against `docs/vi-server-ids.json`** (`IN` = present AND identical; `ABSENT` = not on file
   here, so UNVERIFIED by us). **Six match exactly, none conflicts:**
   - IN  `AbstractDiagram.Nodes[]` **6375809** · `Node.Terminals[]` **6359000** · `Terminal.Connect Wire`
     **6349C03** · `Wire.Terminals[]` **6371003** · `Terminal.Connected Wire` **634A000** · `Generic.Owner`
     **6327806**.
   - ABSENT/UNVERIFIED `Loop.Diagram` 6361401 · `Structure.Diagrams[]` 6360803 · `Structure.Tunnels[]` 6360801 ·
     `Terminal.Diagram` 634A002 · `Tunnel.Outside Terminal` 6356001 · `Tunnel.Inside Terminals[]` 6356000 ·
     `Terminal.Is Source?` 634A003 · `ControlTerminal.Control` 6353000 · `OuterTerminal.Tunnel` 7CC75C00 ·
     `CaseStructure.Get Frame Index` 6364C04.
   - Two independent corroborations worth recording: `AbstractDiagram` class id **16503** matches the one our
     file already carries for `AbstractDiagram.SubVI From Selection`, and `Wire.Terminals[] 6371003` sits one
     below `Wire.Is Broken? 6371004`, already on file.
   - They are added to `docs/vi-server-ids.json` under `nested-diagram route (codex 2026-09-17)` with their
     verification state written next to each one.

2. **PRIOR ART WE ALREADY HAD AND MISSED.** `AbstractDiagram.Nodes[] = 6375809` was **already in
   `docs/vi-server-ids.json`** before this dispatch. The measured failure in
   `build_opconnectnested_v0_run1.log:45` was a **Diagram**-class property node fed a Traverse GObject; the ID on
   our own file says `Nodes[]` is owned by **AbstractDiagram**, not Diagram. That is the answer's core claim and
   we could have read it locally.

3. **The claim that matters, stated as a claim, not a fact:** the ExecState 0 is **not** explained by the class
   hierarchy - a second identical ladder is statically valid, one `To More Specific Class` suffices
   (`GObject -> AbstractDiagram` directly), and the peer lists five code-generation causes instead. It also
   states the structure-owned route (`Loop.Diagram` 6361401 / `Structure.Diagrams[]` 6360803) is the intended
   one, i.e. "get the loop's own body diagram" rather than traversing all diagrams and guessing.
   **NONE of this is verified on our machine.** Deciding whether to build that route is OPEN 33 = judgement.

4. **For the 17 `from-tunnel` rows** the answer gives a complete public chain (no private scope needed):
   `Tunnel.Outside Terminal 6356001 -> Terminal.Connected Wire 634A000 -> Wire.Terminals[] 6371003 ->
   Terminal.Is Source? 634A003 (safer than index 0) -> Generic.Owner 6327806 -> cast to Node`, with the caveat
   that a `ControlTerminal`'s Owner is the DIAGRAM, not a node. It also says there is **no** `Wire.Source
   Terminal` property, public or private - so do not go looking for one.
