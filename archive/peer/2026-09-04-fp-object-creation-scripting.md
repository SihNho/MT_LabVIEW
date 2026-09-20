---
type: peer-review
status: historical
date: 2026-09-04
tags: [peer-review]
disposition: legacy
---

# fp-object-creation-scripting

- **agent:** codex
- **date:** 2026-09-04
- **outcome:** ANSWERED (77s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW VI Scripting factual question, need web sources (labviewwiki.org, forums.ni.com, NI docs). Goal: create FRONT-PANEL controls/indicators programmatically (e.g. a 2D numeric array indicator, a numeric control) on a target VI, and position them, from a scripting VI driven over ActiveX. Questions: (1) With New VI Object, what exactly is the owner refnum for a front-panel object - the VI's Front Panel (Panel) refnum, or the panel's root pane? Which i object class (Control subclass?) and which style-ring entries (e.g. 'Array (classic)', 'Numeric Indicator (classic)') create an ARRAY INDICATOR whose element is a numeric? How is the array element type set after creation - a nested New VI Object into the array's element, or a property? (2) Is there a scripting METHOD on a block-diagram Terminal (or Node) that creates a constant/control/indicator wired to it in one step, like the right-click 'Create > Indicator' - exact class and method name if it exists (I believe something like 'Create Constant, Control or Indicator' exists on the Terminal class). (3) Which properties set an FP object's position and size - is GObject.Position writable for FP controls, is Bounds writable or read-only, and is there a Control.Indicator boolean to flip a control into an indicator? (4) Does NI's shipped example 'Create Control From Reference.vi' (examples\\Application Control\\VI Scripting\\Creating Objects) create FP controls by typing them from an existing reference - what does it take as input? Cite URLs. Context: LabVIEW 2026; we already confirmed RingConstant.Strings And Values[] gives the style codes. Already ruled out: erdosmiller lv-scripting has no Create-Control VI (its Create Constant.vi is block-diagram only).

## Answer

## Findings

### 1. Creating a front-panel numeric array

For `New VI Object`, use the target VI?셲 **Front Panel (`Panel`) reference as `owner refnum`**, not its root-pane reference. NI forum examples explicitly describe the owner as ?쐔he panel of the control,??and the `Panel` is the top-level front-panel object; `Panel.Panes[]` is primarily how you inspect the pane hierarchy. ([NI forum](https://forums.ni.com/t5/LabVIEW-APIs-Discussions/copy-a-queue-ref-control-to-a-typedef-control/m-p/3436493/highlight/true), [Panel class](https://labviewwiki.org/wiki/Panel_class), [Panel owner semantics](https://labviewwiki.org/wiki/Generic_class/Owner_property))

For the array shell:

- `vi object class`: `Generic ??GObject ??Control ??Array`
- `style`: `Array (classic)` for the classic shell
- `owner refnum`: target VI?셲 `Front Panel`/`Panel` reference

`Array` really is a subclass of `Control`; it is not a pane or decoration. ([Array class hierarchy](https://labviewwiki.org/wiki/Array_class))

An array shell does not acquire its element datatype from an ordinary property. The published `Array` API exposes display/layout properties such as rows, columns, indexes, and scrollbars, but no public ?쐃lement datatype??setter. ([Array properties](https://labviewwiki.org/wiki/Array_class))

The traditional scripting construction is therefore:

1. Create the array shell.
2. Call `New VI Object` again to insert the element into that shell.
3. Use the returned **array reference as the nested object?셲 owner**.
4. Create a numeric object, such as class `Numeric` with style `Numeric Control (classic)` or the exact numeric style present in your 2026 style ring.
5. Set the resulting top-level array?셲 `Control.Indicator = TRUE`.

That nested-owner pattern is consistent with published scripting examples which show a separate `New VI Object` operation to create elements inside aggregate containers. ([ICALEPCS scripting example, especially Figure 8](https://epaper.kek.jp/icalepcs2011/papers/wepks015.pdf))

Important correction: I would not rely on a style named `Numeric Indicator (classic)` being necessary. The public scripting model generally creates a control and then changes its direction through `Control.Indicator`; NI?셲 datatype-creation documentation expressly says objects are initially controls even when an indicator style is requested. ([VI `Create from Data Type`](https://labviewwiki.org/wiki/VI_class), [Indicator property](https://labviewwiki.org/wiki/Control_class/Indicator_property))

For a **2D** array, the cleanest supported route is usually not shell construction at all: obtain a 2D numeric datatype from an existing typed terminal/reference and use the VI method `Create from Data Type` or `Create from Reference`, then set `Indicator = TRUE`. That avoids uncertain manipulation of array dimensionality. NI documents `Create from Reference` as creating a control or constant using an existing control/constant reference as its template. ([VI class methods](https://labviewwiki.org/wiki/VI_class), [NI forum example](https://forums.ni.com/t5/LabVIEW/Create-Control-From-Reference/td-p/1539816))

### 2. Terminal method equivalent to ?쏞reate ??Indicator??
Yes. These are three separate methods on the **Terminal class**, not one combined method:

- `Terminal.Create Constant`
- `Terminal.Create Control`
- `Terminal.Create Indicator`

`Create Indicator` is method ID `6349C02`; it creates a correctly typed indicator for that terminal and returns its control reference. `Create Control` is `6349C01`, and `Create Constant` is `6349C00`. ([Terminal class method table](https://labviewwiki.org/wiki/Terminal_class), [Create Constant details](https://labviewwiki.org/wiki/Terminal_class/Create_Constant_method))

This is the closest programmatic equivalent of right-clicking a terminal and choosing `Create ??Indicator`. The interactive operation itself is also documented as acting on a node/function terminal. ([LabVIEW Wiki block-diagram guidance](https://labviewwiki.org/wiki/Block_Diagram))

Thus, if you already have an output `Terminal` reference, `Create Indicator` is preferable to manually constructing an FP array: it derives the complete datatype?봧ncluding element type and array rank?봣rom the terminal.

### 3. Position, size, and control/indicator direction

- `GObject.Position` is **read/write** and applies to front-panel controls. It specifies the upper-left of the complete visible bounding rectangle, including a visible label. ([`GObject.Position`](https://labviewwiki.org/wiki/GObject_class/Position_property))
- `GObject.Bounds` is **read-only**. It reports width and height of the maximum visible bounding area and cannot resize the object. ([`GObject.Bounds`](https://labviewwiki.org/wiki/GObject_class/Bounds_property))
- `Control.Indicator` is **read/write in the development environment**. `TRUE` makes the FP object an indicator; `FALSE` makes it a control. It is not settable while the edited VI is running. ([`Control.Indicator`](https://labviewwiki.org/wiki/Control_class/Indicator_property))

For initial sizing, use the `bounds` input of `New VI Object`; NI?셲 scripting tutorial demonstrates supplying both `location` and `bounds` while creating an object. After creation, resizing is class-specific because generic `Bounds` cannot be written. ([NI-derived New VI Object tutorial](https://rajsite.github.io/unofficial-lvdocs/lvhowto/scripting_creating_new_VI_objects.html))

Arrays additionally expose writable `Number of Rows` and `Number of Columns`, but those control the number of **visible cells**, not the array?셲 datatype rank. ([Array class](https://labviewwiki.org/wiki/Array_class))

### 4. `Create Control From Reference.vi`

Yes?봳he shipped example is illustrating the same principle as the VI-class `Create from Reference` method: create a new FP object by using an existing typed control reference as the template. The method preserves substantially more than merely extracting a runtime value; NI forum users report it reproducing the control?셲 datatype and presentation, including aggregate controls such as clusters. ([NI forum: Create Control From Reference](https://forums.ni.com/t5/LabVIEW/Create-Control-From-Reference/td-p/1539816), [NI forum: copying a cluster](https://forums.ni.com/t5/LabVIEW/Using-scripting-to-copy-a-cluster-from-one-vi-to-another/td-p/1087076))

The essential inputs to the underlying method are:

- the **destination VI reference** as the Invoke Node?셲 object;
- a **source control reference** used as the template;
- creation options such as style/location exposed by the method version.

I could not find a current NI web page exposing the exact connector-pane labels of the shipped `Create Control From Reference.vi` wrapper. To state those labels confidently, I would need reporter output for that example VI. The public documentation does establish that the underlying `VI.Create from Reference` method accepts a control/constant reference as its template. ([VI class method listing](https://labviewwiki.org/wiki/VI_class))

Recommended route for your case: obtain the typed output terminal and call `Terminal.Create Indicator`. It constructs the 2D numeric array indicator and its diagram terminal in one operation, without needing to discover array-shell or numeric-element style codes.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
