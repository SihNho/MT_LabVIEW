---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# cast-route-research

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (93s)
- **why asked:** research: any scriptable route to a retargetable To More Specific Class?
- **verdict:** ClassSpecifierConstant.Set Type 566EF800 / Class Name 566EFC02 exist, but a typed reference to the constant needs one seed cast -> ONE manually prepared donor (GUI, one act) documented in docs/toolkit-capabilities.md; deferred to a session with the user.

## Question

API RESEARCH (cite labviewwiki / NI pages; be concrete; no code needed). PROBLEM: our scripted op fleet can only build property nodes on references that are ALREADY statically typed (Nodes[] -> Node, SubVIs[] -> SubVI, Controls[] -> Control, Inside Terminals[] -> Terminal ...). Anything reachable only through Traverse for GObjects (GObject-typed refs) needs a To More Specific Class (TMSC) whose target class is fixed by a class-specifier constant; we have exactly two donors (TMSC->LoopTunnel in OpSetIndexMode_v0, TMSC->Diagram in OpNetInfo_v1) and erdosmiller's creators cannot make a TMSC or a class specifier constant with a chosen class (New VI Object style ring has no such entry as far as we know; error 1054 on primitives). STILL BLOCKED BY THIS: LeftShiftRegister/RightShiftRegister (Tunnel subclasses: Outside Terminal / Inside Terminals[] to read the frame loop's state carriers), Loop.Shift Registers[] and ForLoop 'Number of Parallel Instances' (need Loop/ForLoop-typed refs), Structure.Tunnels[], the implicit PropertyNode's linked object, Constant.Value 634AC00. QUESTIONS: (1) Is the class of a VI Server class-specifier constant settable by VI Scripting - which class is the constant (e.g. 'ClassSpecifierConstant' / 'VI Server Refnum Constant'), and which property/method sets its class (name + Unique ID)? If yes, the TMSC in a COPY of a donor op could be retargeted by script (copy -> set the constant's class -> the rest of the chain re-types). (2) Can New VI Object create a To More Specific Class primitive - what is its style ring entry / style value, and can it create a class specifier constant ('VI Server Class Constant'?) with a given class? (3) Alternative cast-free routes: VI method 'Get VI Object Reference'/'Open VI Object Reference'-style calls that return a typed ref from a class name + UID or name; Application/VI-class methods taking a class STRING; the 'Traverse for GObjects' output arrays typed by the class constant on ITS input (is Traverse's 'References' output typed as the requested class or as GObject?); LabVIEW's 'Variant to Data' with a typed refnum constant as the type input (does a GObject ref -> To Variant -> Variant To Data with a LeftShiftRegister refnum constant perform the downcast? and can the fleet create such a typed refnum constant?). (4) For each viable route: the exact scripting objects involved and what a minimal proof-of-concept would look like with OUR primitives (build_property / build_invoke on typed refs, drop_subvi of vi.lib VIs, wire by terminal name, create_indicator). Rank by feasibility.

## Answer

The strongest route is to retarget the class-specifier constant already present in a copied donor. LabVIEW exposes exactly the scripting API needed:

- Object class: `ClassSpecifierConstant`
- Class ID: `16452` (`0x4044`)
- Property `Class Name`: Unique ID `566EFC02`, read/write
- Method `Set Type`: Unique ID `566EF800`
- Deprecated property `Type`: Unique ID `566EFC00`, read/write
- Current property `Type`: Unique ID `566EFC06`, but read-only despite its somewhat contradictory description

These identifiers are documented by the [LabVIEW Wiki ClassSpecifierConstant class page](https://labviewwiki.org/wiki/ClassSpecifierConstant_class). NI?셲 own documentation confirms that this constant selects the output reference class and is the type input for `To More Specific Class`/`To More Generic Class` ([NI: Class Specifier Constant](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/constants/class-specifier.html)).

## 1. Retargeting a copied class-specifier constant

Yes?봳his is viable and should be your first experiment.

Use either:

1. `Class Name` property, UID `566EFC02`, writing the VI Server class name string; or
2. `Set Type` method, UID `566EF800`.

I would test `Set Type` first because its declared purpose is unambiguous: ?쏶ets the type of the referenced class specifier constant.??The `Class Name` property is the simpler fallback and is explicitly read/write.

The relevant class hierarchy is:

```text
Generic
?붴? GObject
   ?붴? Constant
      ?붴? RefNumConstant
         ?붴? ClassSpecifierConstant
```

The target strings should be the VI Server class names shown by the Class Browser / `All Types[]`, not necessarily the English display names of palette objects. Use the constant?셲 `All Types[]` property, UID `566EFC05`, as the authoritative runtime vocabulary rather than guessing strings such as `"For Loop"` versus `"ForLoop"`.

### Minimal proof of concept

Make a disposable copy of `OpSetIndexMode_v0`, whose TMSC already targets `LoopTunnel`.

Inside the donor infrastructure, obtain a statically typed `ClassSpecifierConstant` reference to that existing constant. Then:

1. Read `Class Name` and record the initial result.
2. Read `All Types[]` and locate the exact target entry, initially something easy and visibly different such as `Diagram`.
3. Invoke `Set Type` with that string.
4. Read `Class Name` again.
5. Inspect the TMSC output terminal?셲 type or try creating a property node valid only for the new target class.
6. Save only the disposable copy.

With your primitives, the essential operation is:

```text
typed ClassSpecifierConstant ref
  -> build_invoke("Set Type", UID 566EF800)
  -> string constant containing exact class name
```

or:

```text
typed ClassSpecifierConstant ref
  -> build_property("Class Name", UID 566EFC02, write)
```

The important remaining bootstrap issue is obtaining the typed constant reference. If your generic reporter returns it only as `GObject`, merely knowing `566EFC02` does not solve that compile-time typing problem. The cleanest donor design is therefore to modify/freeze one manually prepared donor once so that it exposes its class-specifier constant through a statically typed reference or already contains the `Class Name`/`Set Type` node. Thereafter copies can be retargeted using only strings.

An especially useful donor would contain:

```text
ClassSpecifierConstant reference
  -> Set Type invoke node
     type name exposed as a string control
```

That turns the donor into a general-purpose TMSC factory without ever creating a new TMSC or class-specifier constant.

## 2. Can `New VI Object` create TMSC or the constant?

I found no documented `New VI Object` style for either:

- `To More Specific Class`
- `Class Specifier Constant`

The public VI Scripting palette documentation merely identifies `New VI Object`; it does not publish a comprehensive style table ([LabVIEW Wiki: VI Scripting palette](https://labviewwiki.org/wiki/Functions_Palette/Programming/Application_Control/VI_Scripting)). NI?셲 guidance says that `New VI Object` creates objects represented by its style ring, or controls/classes supplied by path; it does not claim arbitrary primitives can be created ([NI: Create Class Control Using VI Scripting](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU000000CWCD0A4&l=en-US)).

The scripting community?셲 established recommendation for objects missing from the style ring is to copy a prepared instance. It specifically notes that probing undocumented style values is risky and may crash LabVIEW ([NI Community: New VI Object style input](https://forums.ni.com/t5/LabVIEW/VI-Scripting-Input-for-style-in-quot-New-VI-Object-quot-function/m-p/3267356)).

There is also relevant evidence that not every scripting object has a `New VI Object` style: an attempted `LoopTunnel` creation failed because that class does not expose the applicable style mechanism; the successful workaround created wiring that caused LabVIEW to generate a tunnel and then traversed/cast it ([NI Community: change tunnel mode using VI scripting](https://forums.ni.com/t5/LabVIEW/How-to-change-tunnel-mode-using-vi-scripting/m-p/3969401)).

Therefore:

- TMSC via `New VI Object`: **not publicly documented; treat as unavailable**.
- Class-specifier constant via `New VI Object`: **not publicly documented; treat as unavailable**.
- Your error 1054 when trying primitive styles is consistent with this conclusion.
- Copying a donor is the supported practical pattern.

For reference, `New VI Object` itself is internal function ID `371`, but that does not provide an object-style value for TMSC ([LabVIEW Wiki function-ID listing](https://labviewwiki.org/wiki/Application_class/Help_Image.Get_Function_Context_Help_Image_method)).

## 3. Alternative cast-free routes

### A. `Open VI Object Reference`: viable when you have a suitable typed class input

`Open VI Object Reference` can return a specifically typed object reference because its `VI Object Class` input establishes the requested type. An NI employee?셲 example describes supplying:

- an owner reference,
- the object?셲 name,
- a class-specifier input such as `Case Selector`,

and receiving the corresponding typed reference ([NI Community: programmatically change case structure range](https://forums.ni.com/t5/LabVIEW/programmatically-change-case-structure-range/m-p/941268)).

It works especially well for uniquely named objects and nested traversal where you can successively open each named structure, obtain its diagram, and continue inward. It is not a class-name-string API: the type is supplied through the typed `VI Object Class` terminal. Consequently, it moves the bootstrap problem?봧t still requires a class-specifier constant or another correctly typed refnum source.

It can be useful after donor retargeting:

```text
retargetable class-specifier donor
  -> Open VI Object Reference.VI Object Class
owner Diagram/Structure ref
  -> Open VI Object Reference.Owner
object name
  -> Open VI Object Reference.Name
```

This may avoid `Traverse for GObjects` entirely for labeled loops, nodes, and selectors. It is weaker for anonymous tunnels, shift registers, and implicit nodes.

The function is specifically for objects inside a VI, not projects or arbitrary external objects ([NI Community: Open VI Object Reference problem](https://forums.ni.com/t5/LabVIEW/open-VI-object-reference-problem/m-p/1749796/highlight/true)).

### B. Class name + UID method: no documented general API found

I found no documented Application- or VI-class method that accepts:

```text
class-name string + object UID/name -> typed VI Server reference
```

`Open VI Object Reference` accepts an owner, object name/path, and typed class input. It does not synthesize the compile-time output type from a runtime class-name string.

UIDs identify properties/methods reliably across localization and LabVIEW revisions; they do not serve as object-casting tokens. NI describes ID strings as stable identifiers for selecting property/invoke-node members, not as a way to change a wire?셲 VI Server type ([NI Community: LabVIEW 2010 Scripting Changes](https://forums.ni.com/t5/LabVIEW-APIs-Documents/LabVIEW-2010-Scripting-Changes/ta-p/3521934)).

### C. `Traverse for GObjects`: useful, but not a way around the type token

The standard traversal infrastructure is designed to search by class. Public examples describe traversing specifically for event structures or other classes, which indicates that the class input controls what is found ([NI Community: add event cases using scripting](https://forums.ni.com/t5/LabVIEW/add-event-cases-to-an-event-structure-using-scripting/m-p/3098814)).

However, I did not find an authoritative NI connector-pane description proving that its `References` output preserves the requested subclass rather than returning `GObject[]`. Your observed compiled behavior??GObject[]`?봲hould be treated as ground truth for your installed `Traverse for GObjects.vi`.

Even if another overload or wrapper adapts its output type, it would still require a typed class constant on the input. Thus it cannot bootstrap a new class on its own.

A custom wrapper could accept a class-specifier constant and internally preserve/adapt the result, but creating that input constant remains the same problem.

### D. Variant round-trip: not viable for downcasting VI Server refs

`GObject ref -> To Variant -> Variant To Data`, with a more-specific refnum wired as the type, does **not** perform VI Server downcasting.

A focused test reported that `Variant To Data` fails when a specific VI Server reference is first upcast to `GObject` and then requested back as `Control`, even though the underlying referenced object really is a control. The conclusion was that `Variant To Data` does not implement the equivalent of `To More Specific Class` for VI Server refnums ([NI Community: Variant To Data Cannot Downcast VI Server Refnum](https://forums.ni.com/t5/LabVIEW/Variant-To-Data-Cannot-Downcast-VI-Server-Refnum/td-p/3917665)).

NI documents error 91 when the stored variant type is incompatible with the requested output type ([NI: Error 91 from Variant To Data](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000015AWGSA2&l=en-US)). Variant conversion can preserve or convert compatible representations, but it cannot replace TMSC?셲 runtime hierarchy check.

So this route is ruled out for:

```text
GObject -> LeftShiftRegister
GObject -> ForLoop
GObject -> Constant
```

It also would require creating the desired typed refnum constant, so it has two blockers rather than one.

## 4. Ranked routes

### 1. Retarget the constant inside a copied TMSC donor ??highest feasibility

Objects:

- Existing TMSC
- Existing `ClassSpecifierConstant`
- `ClassSpecifierConstant:Set Type`, UID `566EF800`
- Alternatively `Class Name`, UID `566EFC02`

POC:

- Copy `OpSetIndexMode_v0`.
- Set its constant from `LoopTunnel` to `Diagram`.
- Verify the TMSC output wire changes type and can feed a Diagram-only property.
- Generalize the donor so target class is supplied as a string.

This directly unlocks every target represented in `All Types[]`, subject to class availability/private-class restrictions.

### 2. Prepared typed-cast donor per target family ??very high feasibility

If dynamic `Set Type` causes broken wires or LabVIEW refuses to propagate the new type reliably, create frozen donor variants manually:

- TMSC?묹oop
- TMSC?묯orLoop
- TMSC?뭆tructure
- TMSC?뭈unnel
- TMSC?묹eftShiftRegister
- TMSC?뭃ightShiftRegister
- TMSC?묬onstant
- TMSC?뭁ropertyNode, if needed

This is less elegant but aligns with the established ?쐁opy a working object??scripting practice.

### 3. Retargetable class token + `Open VI Object Reference` ??medium/high feasibility

Best for labeled objects:

- frame For Loop
- named structures
- named nodes
- selectors

Objects:

- Retargeted class-specifier constant
- `Open VI Object Reference`
- typed owner reference
- object name/path

It is probably poor for implicit nodes and anonymous shift-register/tunnel components.

### 4. Induce LabVIEW to create the object, then cast it ??medium feasibility

For tunnels and shift-register components:

- create/wire through the loop or structure,
- let LabVIEW generate the tunnel/shift-register object,
- locate it through structure properties or traversal,
- pass its generic reference through the retargeted TMSC donor.

The tunnel example is known to work as a general technique ([NI Community example](https://forums.ni.com/t5/LabVIEW/How-to-change-tunnel-mode-using-vi-scripting/m-p/3969401)).

### 5. Typed `Traverse for GObjects` wrapper ??uncertain/medium-low

Worth one cheap connector-pane experiment after you have a retargetable constant. Determine whether replacing its class input changes the compile-time type of `References[]`. Public documentation does not settle this, and your current observation says the result is `GObject[]`.

### 6. `New VI Object` for TMSC/class constant ??low

No documented style entry or value. Continue using donors.

### 7. Variant round-trip ??nonviable

It does not downcast VI Server references.

## Practical implication for your blocked properties

A retargetable TMSC donor should cover:

- `Loop.Shift Registers[]`: cast frame loop to `Loop`.
- `Number of Parallel Instances`: cast to `ForLoop`.
- `Structure.Tunnels[]`: cast to `Structure`.
- left/right shift-register objects: cast from the returned tunnel/GObject reference to their exact classes.
- implicit PropertyNode: cast to the appropriate node subclass, then follow its linked-object property if that property is exposed.
- `Constant.Value` `634AC00`: cast to `Constant`, then build the property node by UID.

The one result I would validate before expanding anything is whether `Set Type` automatically retypes the existing TMSC output and repairs/recompiles downstream wires. The API clearly permits changing the constant?셲 selected class; public documentation does not explicitly promise how already-wired downstream nodes respond. A disposable `LoopTunnel ??Diagram` donor copy is the cheapest decisive test.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
