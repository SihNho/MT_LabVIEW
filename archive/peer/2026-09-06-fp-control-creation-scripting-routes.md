---
type: peer-review
status: historical
date: 2026-09-06
tags: [peer-review]
---

# fp-control-creation-scripting-routes

- **agent:** codex
- **date:** 2026-09-06
- **outcome:** ANSWERED (115s)
- **why asked:** the keystone op needs an array-of-cluster front-panel control; copy_into (Move-example substitution) crashed LabVIEW with a vi.lib donor; needed the documented scripted routes before deciding on a GUI bootstrap.
- **verdict:** actionable: Terminal.Create Control (input terminals), Constant.Change to Control, Control.Indicator (R/W), VI.Create from Data Type (variant -> Panel Control), VI.Create from Reference (template), New VI Object(path=.ctl). Chosen: build an Invoke keystone (VI-class node, method string) via Create Invoke Node.vi first, then use VI.Create from Data Type for the Properties control. Not yet machine-verified.

## Question

Question about LabVIEW VI Scripting (LabVIEW 2026); answer only with documented facts and URLs; say NOT DOCUMENTED where unsure. I need to create, by script, a FRONT-PANEL CONTROL wired to an INPUT terminal of a subVI node on a block diagram (the subVI is erdosmiller Create Property Node.vi; the input is an array of cluster {ID String, Is Write?}). (1) Terminal class methods: does Terminal have Create Control, Create Indicator, Create Constant? Exact method names and which terminal directions each accepts (input vs output). Does Create Indicator on an INPUT terminal error? (2) Is there a scripting way to convert a constant into a control or an indicator into a control (Constant.Change To Control? Control.Indicator property writable?) - exact names. (3) Can New VI Object create a front-panel control of an ARRAY-OF-CLUSTER type directly from a datatype or from a terminal reference (style names)? (4) Is there any VI Server method that creates a control from a data type or a typedef path? Give the class, method name, parameters, and a source URL for each claim.

## Answer

The shortest documented route is:

> Obtain the subVI input `Terminal` reference ??invoke `Terminal.Create Control`.

Because the terminal already has the required array-of-cluster datatype, this avoids reconstructing `{ID String, Is Write?}` manually.

### 1. `Terminal` methods

The documented `Terminal` scripting methods are:

| Method | Documented purpose | Appropriate direction |
|---|---|---|
| `Create Control` | Creates and returns a front-panel control for the terminal; optional `Value` input. [NI API reference](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/terminal/createcontrol.html) | Input terminal |
| `Create Indicator` | Creates and returns a front-panel indicator for the terminal. [LabVIEW Wiki API listing](https://www.labviewwiki.org/wiki/Terminal_class/Create_Indicator_method) | Output terminal |
| `Create Constant` | Creates and returns a block-diagram constant for the terminal; optional `Value` input. [NI API reference](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/terminal/createconstant.html) | Input terminal |

NI?셲 user documentation explicitly describes creating a constant from an input terminal and an indicator from an output terminal. [NI: Creating and Editing User-Defined Constants](https://www.ni.com/docs/en-AS/bundle/labview/page/creating-and-editing-user-defined-constants.html), [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999b.pdf)

For your input terminal, use exactly:

```text
Terminal.Create Control
```

Whether `Terminal.Create Indicator` on an input terminal returns a particular scripting error, automatically creates something anyway, or has a specific error number is **NOT DOCUMENTED** in the API material I found. The documented semantic pairing is input?뭖ontrol and output?뭝ndicator; do not depend on the wrong-direction case.

### 2. Converting objects

These scripting operations are documented:

- `Constant.Change to Control` ??converts the constant to a front-panel control and returns its reference. [LabVIEW Wiki method index](https://www.labviewwiki.org/wiki/Category%3AVI_Scripting_Method)
- `Constant.Change to Indicator` ??converts the constant to an indicator, returns the indicator reference, and automatically closes the old constant reference. [NI API reference](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/constant/changetoindicator.html)
- `Control.Indicator` ??Boolean, read/write in the development environment: `FALSE` means control and `TRUE` means indicator. It cannot be set while the VI is running. [NI API reference](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/control/indicator.html)

Thus an indicator can be converted to a control by writing:

```text
Control.Indicator = FALSE
```

The exact property name is `Indicator`, not `Control.Indicator?` or `Is Indicator`.

There are also `ControlTerminal.Change To Constant` and `ControlTerminal.Toggle Direction` methods in the scripting API. [LabVIEW Wiki scripting-method index](https://www.labviewwiki.org/wiki/Category%3AVI_Scripting_Method)

### 3. `New VI Object` and array-of-cluster types

`New VI Object` does not have a datatype or terminal-reference input. Its relevant inputs are:

- `vi object class`
- `owner refnum`
- `style`
- `location`
- `path`
- `bounds`

The `style` value selects a native object compatible with the selected class; it does not describe an arbitrary compound datatype. The `location` input may accept an existing-object reference, but that reference controls placement, not datatype. [NI: New VI Object Function](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/new-vi-object.html)

Therefore:

- Creating an `Array` object by class/style does not, by itself, specify that its element is the cluster `{String, Boolean}`.
- There is no documented ?쏿rray-of-this-terminal?셲-datatype??style.
- Exact enum display names for an array-of-cluster style: **NOT DOCUMENTED**, because no such compound-datatype style is documented.

`New VI Object` can instead accept `path` to a pre-existing custom control. NI says `path` is for a subVI or pre-existing custom control. Therefore, if that array-of-cluster is saved as a `.ctl` typedef/custom control, `New VI Object` can instantiate it from the path. [NI: New VI Object Function](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/new-vi-object.html) NI also documents that when a path is supplied for a class/custom control, it overrides the style selection. [NI: Create Class Control Using VI Scripting](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU000000CWCD0A4&l=en-US)

### 4. Methods that create controls from datatype/reference

#### `VI.Create from Data Type`

Class: `VI`  
Method: `Create from Data Type`

Parameters:

| Parameter | Required | Meaning |
|---|---:|---|
| `Data Type` | Yes | Variant carrying the datatype to create |
| `Style` | Yes | `Diagram`, `Panel Control`, `3D Panel Control`, `Dialog Panel Control`, `Panel Indicator`, etc. |
| `Position` | No | New-object position |
| `New Object Reference` | Output | Created object reference |
| `Make Names Unique (F)` | No | Name-uniquing option |

LabVIEW initially creates a control even when `Style` requests an indicator or constant; NI?셲 documented instruction is to use the created control?셲 writable `Indicator` property to change its direction. [LabVIEW Wiki API entry reproducing the method documentation](https://labviewwiki.org/wiki/VI_class/Create_from_Data_Type_method), [NI `Indicator` property](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/control/indicator.html)

This method can represent an array-of-cluster datatype through its `Data Type` variant. It does not take a typedef path.

#### `VI.Create from Reference`

Class: `VI`  
Method: `Create from Reference`

Parameters:

| Parameter | Required | Meaning |
|---|---:|---|
| `Source Object Reference` | Yes | Existing control or constant used as the template |
| `Position` | No | New-object position |
| `New Object Reference` | Output | Created control/constant reference |
| `Make Names Unique (F)` | No | Name-uniquing option |

It creates a control or constant using an existing control or constant as its template. It does not accept a `Terminal` reference directly. [LabVIEW Wiki API entry](https://labviewwiki.org/wiki/VI_class/Create_from_Reference_method)

#### Typedef path

I found no documented `VI`-class method whose parameter is directly ?쐔ypedef path.??For a typedef/custom-control path, the documented API is the `New VI Object` function?셲 `path` input, not a VI Server invoke method. [NI: New VI Object Function](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/new-vi-object.html)

So for this particular input, the clean documented choice is `Terminal.Create Control`; use `VI.Create from Data Type` only if you cannot invoke the terminal method, and use `New VI Object(path=...)` only if you have an appropriate saved `.ctl`.

## Sources

(extract from answer)

## What was done with it

plan v3 in docs/keystone-op-spec.md; tools/recipes/build_keystone_invoke.py written and running.
