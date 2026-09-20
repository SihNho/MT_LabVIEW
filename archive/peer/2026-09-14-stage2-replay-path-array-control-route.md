---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, stage2]
---

# stage2-replay-path-array-control-route

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (116s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RESEARCH QUESTION with an adversarial stance (refute weak options). LabVIEW 2026 VI Scripting over COM, ZERO GUI, using the Erdos Miller LV-Scripting library (C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting - list its VIs) plus NI VI Server.

GOAL: in a new top-level VI, get a FRONT-PANEL CONTROL of type 1-D ARRAY OF PATH (so Python can set ~10,000 TIFF paths via SetControlValue), auto-indexed into a While/For loop so iteration i reads path[i] into IMAQ ReadFile's 'File Path' (a Path input). Alternatively any zero-GUI construction that yields "path of frame i" inside a loop.

This project can already: drop subVIs by path; create While/For loops with input tunnels from EXISTING controls by name (Create While Loop.vi 'Inputs'); create Index Array (Create Index Array.vi); create controls/indicators ONLY from an existing node terminal (Terminal.Create Control / Create Indicator - the new control takes the terminal's type); build Property/Invoke nodes; wire by name (Wire Inputs.vi) and by Terminal.Connect Wire; set a tunnel's IndexMode; it has ops around 'Create Unflatten from String.vi' and 'Create Flatten to String.vi' (OpBuildUnflatten_v0, OpBuildFlatten_v0). It CANNOT place arbitrary primitives (New VI Object style ring; Build Path / String To Path / Format Into String have no creator in the list). No donor VI with a path-array control is known.

CANDIDATES to evaluate and rank, each with the concrete API calls and what is unverified:
(a) 'Create Constant.vi' + 'String to Type.vi' (what type-name syntax does String to Type accept - e.g. "Array of Path"? read the library VIs' documentation/strings) to make a path-array CONSTANT, then the Constant class method 'Change to Control' (does such a scripting method exist in VI Server? ID? documented on labviewwiki?) to turn it into a control;
(b) Terminal.Create Control on a terminal that is already typed array-of-path: e.g. wire a path constant (Create Constant) into 'Create Build Array.vi''s node, then Create Control on the Build Array OUTPUT? (Create Control on an output makes an indicator - so which terminal would be typed 1-D path AND be an INPUT? Index Array's 'array' input is typed by its own input only... is Terminal.Create Control legal on an UNWIRED input whose type is inferred from a sibling?);
(c) Unflatten From String with a type wire: inside the loop Unflatten(string[i], type=Path) - needs a STRING array control (this project can make one from Get Controls.vi's 'Control Names' terminal) plus a Path-typed wire for 'type' (from Create Constant of type Path?) -> element path -> IMAQ ReadFile. Does Unflatten From String accept a scalar Path type and does Python's flattened-string format for a LabVIEW Path have a simple documented encoding?
(d) IMAQ ReadFile's 'File Path' accepting a STRING via a path/string polymorphism - does LabVIEW auto-coerce string to path on a subVI input (I believe NOT - confirm)?
(e) NI's own 'New VI Object' with a control style from the ring: is there a documented style string for an Array control, and can its element be set to Path by script (e.g. 'Array' then drop a Path element inside via New VI Object with the array as owner)? Cite NI 'Adding Objects.vi' example if relevant.
(f) any other route you find (e.g. VI.Front Panel 'Import' of a control from a .ctl typedef file via 'Create Typedef Constant.vi' + a .ctl the manager creates... note .ctl files cannot be authored without GUI either - unless LabVIEW can save a control from a running VI).
Rank by fewest unverified steps, and name for the top candidate the single cheapest test on a scratch VI. Cite the exact files/URLs you read. Read-only: do not open LabVIEW.


## Answer

Conclusion: rank **(e) first**. Native `New VI Object` is the only route that constructs the requested control directly without depending on undocumented datatype-name grammar, polymorphic type propagation, or Python-generated flattened Path bytes.

## Ranking

### 1. (e) `New VI Object`: array shell, then Path element

Recommended construction:

1. Obtain the new VI?셲 `Front Panel`/`Panel` reference.
2. Call `New VI Object` with:

   - `owner refnum` = Panel reference
   - `style` = the ring item for an Array control, probably `Array` or `Array (classic)` depending on the shipped ring
   - `position` or `bounds` = desired panel location
   - matching control/GObject class

3. Call `New VI Object` again with:

   - `owner refnum` = the returned Array reference
   - `style` = the ring item for a Path control
   - matching Path/control class

4. Set the resulting control label, for example `Frame Paths`.
5. Use its diagram terminal as `Create For Loop.vi` input with `Inputs Indexing? = TRUE`, or connect it across the loop boundary and set the tunnel `IndexMode` to indexing.
6. Wire the tunnel?셲 scalar Path output directly to `IMAQ ReadFile.File Path`.

NI documents the underlying composition rule: an array control is an array shell containing an element control, and Path is an allowed element type. [NI array documentation](https://www.ni.com/en/support/documentation/supplemental/08/labview-arrays-and-clusters-explained.html), [NI LabVIEW User Manual PDF](https://download.ni.com/support/manuals/320999e.pdf). NI also says `New VI Object` creates front-panel controls by changing its style input. [NI: Create Class Control Using VI Scripting](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU000000CWCD0A4&l=en-US).

What remains unverified:

- The exact LabVIEW 2026 ring-item spelling for Array and Path.
- Whether the second call accepts the returned Array reference directly as its owner in this version.
- The precise concrete class constants required by the two styles.

Those are narrowly testable construction details, not datatype-format questions.

**Cheapest test:** on an empty scratch VI, make only the two `New VI Object` calls?볾rray owned by Panel, Path owned by Array?봳hen verify through a reporter that exactly one FP object exists whose terminal type is rank-1 array with Path element. Do not build the loop or IMAQ call until this passes.

### 2. (a) `Create Constant.vi` ??`Change to Control`

The second half is real: Constant class method **`Change to Control`, method ID `634A802`**, returns a control reference and closes the original constant reference. [LabVIEW Wiki method entry](https://labviewwiki.org/wiki/Constant_class/Change_to_Control_method).

The weak point is `String to Type.vi`. I found no public documentation establishing that it accepts a recursive text such as `Array of Path`, `Path[]`, or another stable grammar. The Erdos Miller repository recommends learning from its examples but does not document this grammar in its README. [Erdos Miller LV-Scripting repository](https://github.com/erdosmiller/lv-scripting).

Therefore:

```text
String to Type("Array of Path"?)
??Create Constant(type)
??Constant.Change to Control [634A802]
```

is attractive but presently has one foundational unverified step: whether any accepted string denotes a 1-D Path array. I did not inspect `String to Type.vi` internally because it is a compiled VI and the repository instructions expressly prohibit opening it.

If the manager can run a reporter, the cheap discovery test is to feed known type names through `String to Type.vi`, then round-trip them through `Type to String.vi`. Start with `Path`, then test array spellings derived from `Type to String` applied to any known array type.

### 3. (b) infer array-of-Path on a node terminal, then `Terminal.Create Control`

`Terminal.Create Control` is documented in the VI Server catalog as **method ID `6349C01`**. It creates a control with the terminal?셲 datatype and optionally accepts a value. [LabVIEW Wiki method entry](https://labviewwiki.org/wiki/Terminal_class/Create_Control_method). An NI employee also recommends using terminal type information when creating an exactly typed control. [NI Community: Create Control From Reference](https://forums.ni.com/t5/LabVIEW/Create-Control-From-Reference/td-p/1539816).

However, the proposed Build Array sequence does not yet provide a clean eligible terminal:

- Build Array?셲 array output is an **output**, so normal create-from-terminal semantics yield an indicator.
- Index Array?셲 `array` terminal is an input, but before type propagation it is polymorphic/unresolved.
- After wiring Build Array into it, the terminal is typed but already wired.
- It is unverified whether `Create Control` on that already-wired input replaces the existing source, rejects the call, or creates a second/broken connection.
- It is also unverified whether the type remains array-of-Path after removing the type-establishing wire.

NI?셲 standard behavior is ?쏞reate Control??on an input and ?쏞reate Indicator??on an output. [NI Quick Drop scripting example](https://forums.ni.com/t5/LabVIEW-APIs-Documents/Quick-Drop-Keyboard-Shortcut-Create-Object-from-Terminal/ta-p/3508433).

This route may work, but it has more inferred compiler behavior than (e).

### 4. (c) string array plus `Unflatten From String(type=Path)`

This can produce a Path scalar: `Unflatten From String` determines its output type from the wired `type` input. NI explicitly describes wiring an object of the required type to that input. [NI compatibility article](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000015CmaSAE&l=en-US).

But it is a poor interface for this goal:

- Python must emit **LabVIEW?셲 binary flattened Path representation**, not an ordinary filesystem string.
- The format is documented, but it includes the `PTH0` header, byte count, path type, component count, Pascal-style path components, and alignment. [NI flattened-data discussion quoting the official format](https://forums.ni.com/t5/LabVIEW/type-component-in-flattened-data-context/td-p/4414048).
- Flattened data is type-exact; LabVIEW does not generally coerce mismatched flattened representations. [NI variant/data handling](https://www.ni.com/docs/ar-IQ/bundle/labview/page/handling-variant-data.html).
- You still need a Path-typed seed for `type`, although that can probably be created from the IMAQ input terminal.
- Windows roots, UNC paths, relative paths, Unicode, and LabVIEW 2026 UTF-8 behavior increase the interoperability test surface.

This is technically possible but needlessly moves LabVIEW?셲 private-ish binary representation into Python.

A materially safer version would be a **string-array control followed by a real `String To Path` primitive**, but your creator inventory contains no way to drop that primitive and no donor is known.

### 5. (f) generate or import a typedef/control

`Create Typedef Constant.vi` can consume an existing `.ctl`, but that only moves the hard part: someone must first create a valid array-of-Path control file. NI documents that custom controls are authored in the Control Editor and then saved as `.ctl`. [NI custom-control documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/creating-custom-controls-and-indicators-using-the-new-dialog-box.html).

Possible zero-GUI bootstrap:

1. Create the control using (e) or another successful method.
2. Invoke the relevant save-as-control/typedef operation on that control.
3. Reuse the resulting `.ctl` through `Create Typedef Constant.vi`.

But this cannot be the initial solution unless the exact ?쐓ave control as `.ctl`??scripting method is first identified and verified. It is more useful as a way to freeze a working result for future builds.

### 6. (d) wire string directly to `IMAQ ReadFile.File Path`

Reject this. A LabVIEW String and a LabVIEW Path are distinct datatypes; NI supplies explicit `String To Path` and `Path To String` conversion functions. [NI Function and VI Reference](https://download.ni.com/support/manuals/321526b.pdf). NI?셲 variant documentation likewise distinguishes data originally typed as string from data typed as path. [NI: Handling Variant Data](https://www.ni.com/docs/ar-IQ/bundle/labview/page/handling-variant-data.html).

The general existence of coercion dots does not establish this particular conversion. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html). Treat direct String ??Path wiring as illegal unless an actual LabVIEW 2026 compile test proves otherwise.

## Important additional route

Before committing to elaborate type synthesis, search the installed NI libraries for a **subVI whose input connector is already `Path[]`**. Dropping that subVI and invoking `Terminal.Create Control [6349C01]` on its Path-array input would outrank everything except a proven (e), because it derives the exact datatype directly from a concrete terminal. Filename searching alone cannot establish connector types, so this requires the manager?셲 reporter?봭ot binary inspection.

## Installed Erdos Miller VI inventory

Read-only filename enumeration found exactly **84 `.vi` files** under:

`C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting`

```text
Case Next Frame.vi
Conditionally Connect Wire.vi
Construct Control Event.vi
Construct Dynamic Event.vi
Construct Static Event.vi
Create Add.vi
Create And Array Elements.vi
Create Array Size.vi
Create Array Subset.vi
Create Build Array.vi
Create Bundle by Name.vi
Create Bundle.vi
Create Case Structure (Boolean).vi
Create Case Structure (Error).vi
Create Case Structure.vi
Create Close Reference.vi
Create Constant.vi
Create Create User Event.vi
Create Delete DVR.vi
Create Dequeue Element.vi
Create Destroy User Event.vi
Create Enqueue Element.vi
Create Equal.vi
Create Event Structure.vi
Create Flatten to String.vi
Create For Loop.vi
Create Generate User Event.vi
Create In Place Element Array.vi
Create In Place Element Cluster.vi
Create In Place Element DVR.vi
Create Index Array.vi
Create Invoke Node.vi
Create Merge Errors.vi
Create New DVR.vi
Create Obtain Queue.vi
Create Open VI Reference.vi
Create Or Array Elements.vi
Create Property Node.vi
Create Register for Events.vi
Create Release Queue.vi
Create Replace Array Subset.vi
Create Sequence.vi
Create Start Asynchronous Call.vi
Create Static VI Reference.vi
Create SubVI.vi
Create To More Specific Class.vi
Create To Variant.vi
Create Typedef Constant.vi
Create Unbundle by Name.vi
Create Unbundle.vi
Create Unflatten from String.vi
Create Unregister for Events.vi
Create Variant to Data.vi
Create Wait on Asynchronous Call.vi
Create While Loop.vi
Event Next Frame.vi
Exit Event Structure.vi
Exit For Loop.vi
Exit In Place Element Array.vi
Exit In Place Element Cluster.vi
Exit In Place Element DVR.vi
Exit Loop.vi
Exit Multi Frame Structure.vi
Exit Structure.vi
Exit While Loop.vi
Get Cluster Element Names.vi
Get Cluster Element Type.vi
Get Controls.vi
Get Event Data In.vi
Get LV Class Path by Name.vi
Get Outputs.vi
Get Tagged Union Info.vi
Get Term Type.vi
Is Tagged Union.vi
Set Name.vi
Set Tagged Union Info.vi
String to Type.vi
Type to String.vi
Typedef Default Value.vi
Unflatten Name.vi
Update Typedef.vi
Wire Event Data Out.vi
Wire Indicators.vi
Wire Inputs.vi
```

Local text files read: `STATUS.md`, `.claude/skills/labview-automation/SKILL.md`, and `.claude/skills/labview-automation/references/vi-scripting.md`. No `.vi`, `.ctl`, `.lvlib`, or `.lvproj` was opened or parsed.

## Sources

(extract from answer)

## What was done with it

Adopted the ranking: route (e) `New VI Object` ×2 (Array shell owned by the Panel, element owned by the array) is
the cycle-3 construction, with NI's shipped example `Creating Objects\Drop Digital Numeric Inside Cluster.vi` as the
donor (a container as `owner refnum`); (d) string→Path wiring rejected as illegal; (c) Unflatten rejected (Python
would emit LabVIEW's binary Path format); (a) kept as fallback pending the `String to Type` grammar
(`Constant.Change to Control` = 634A802 recorded). The "subVI with a `Path[]` INPUT" route is noted for a later
census. Plan: `docs/stage2-assembly-step-b.md`; its own review: `…-stage2-step-b-replay-core-plan.md`.
