---
type: peer-review
status: historical
date: 2026-09-12
tags: [peer-review]
disposition: legacy
---

# scripted-subvi-extraction

- **agent:** codex
- **date:** 2026-09-12
- **outcome:** ANSWERED (155s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FACT QUESTION about LabVIEW VI Scripting (LabVIEW 2026, driven over ActiveX/COM from Python via "op VIs" that take plain data and do the refnum work inside LabVIEW).

GOAL: take an existing region of a block diagram - a set of nodes and the wires among them - and turn it into a subVI, BY SCRIPT, the way Edit >> Create SubVI does interactively. I need to refactor a large main VI (75 nodes on one loop diagram) into subVIs without a human clicking.

What I have found locally in the LabVIEW 2026 install:
  vi.lib\Erdos Miller\LV-Scripting\Create SubVI.vi
  resource\plugins\CreateSubVI\ModifyNewSubVI.vi  and  Move Labels in Created SubVI.vi
  resource\plugins\PopupMenus\edit time panel and diagram\Create SubVI from Selected Wires.llb\CreateSubVIWires_Create SubVI Method.vi
  vi.lib\Utility\CreateSubVISupport\CreateSubVI Parse Plugin Variant.vi

QUESTIONS:
1. Is there a documented VI Server METHOD that creates a subVI from a selection (something like Diagram.Create SubVI, or a BlockDiagram/VI method)? If so give its exact name and its Unique/Property ID if you can find one - I register IDs like "VI.Connector Pane:Reference" = 23E in a local table. If it is a PRIVATE/scripting-only method, say so and say what enables it (ini tokens, etc.).
2. If no such method exists, what is the accepted scripted approach? Options I can evaluate: (a) select objects then invoke an edit-time menu plugin; (b) create a new VI, move/copy the objects into it with VI Server, build its connector pane, and replace the original region with a subVI call; (c) something else entirely.
3. What does erdosmiller's `Create SubVI.vi` actually do - does it wrap a native method, or does it construct the subVI manually? Its repo is https://github.com/erdosmiller/lv-scripting
4. Known limitations and gotchas of scripted subVI creation: what does it do about local variables inside the selection, control references, uninitialised shift registers, Event Structures with latch-action booleans, and error-cluster wires crossing the boundary?
5. Is "Edit >> Create SubVI" itself scriptable via the edit-time plugin framework (the resource\plugins\CreateSubVI path above), and is that a supported route or an internal one that may break?

Cite NI documentation, the LabVIEW help for VI Scripting, labviewwiki, or forum posts with URLs. If the honest answer is "not exposed as a method", say that plainly with what you checked - I need to record a negative result with evidence, not a guess.


## Answer

## Bottom line

LabVIEW does expose the operation you want, but it is a **private VI Scripting method**, not a documented/supported public VI Server API:

- Class: `AbstractDiagram`
- Method: `SubVI From Selection`
- Method ID: `6375405` decimal (`0x6147ED`)
- Owning class ID: `16503`
- Scope: `Private`
- Return value: VI reference to the newly created subVI
- Inputs reported by the scripting metadata:
  - `Clean Up Wires`
  - `SubVI`
  - `Add To Project`
  - `Apply 'Create SubVI' Plugin (True)`

The corresponding LabVIEW Wiki metadata page identifies all of these fields explicitly: [AbstractDiagram: SubVI From Selection](https://labviewwiki.org/wiki/AbstractDiagram_class/SubVI_From_Selection_method).

### 1. Enabling the method

Ordinary VI Scripting enablement is insufficient because the method is private. NI documents normal VI Scripting enablement through:

`Tools 쨩 Options 쨩 VI Server 쨩 Show VI Scripting functions, properties and methods`

[NI: Enabling VI Scripting](https://www.ni.com/docs/en-IE/csh?context=lvcore_lvhowto_enabling_vi_scripting).

For the private method, the reported INI tokens are:

```ini
SuperPrivateScriptingFeatureVisible="True"
SuperPrivateSpecialStuff="True"
SuperSecretPrivateSpecialStuff="True"
```

A 2024 NI Community question specifically about `AbstractDiagramClass/SubVI from Selection` reports those three tokens as the way to expose it: [Creating a subVI from a selection using VI scripting](https://forums.ni.com/t5/LabVIEW/Creating-a-subvi-from-a-selection-using-VI-scripting/td-p/4351091).

These tokens and this method are **private and unsupported**. NI does not document compatibility guarantees for them. In particular, the public VI Scripting checkbox documents only supported scripting exposure; it does not document these ?쏶uperPrivate??settings.

For your registry, I would record:

```text
AbstractDiagram.SubVI From Selection
Owning class ID: 16503
Method ID: 6375405 decimal / 0x6147ED
Scope: Private
```

The Wiki explains how `All Supported Methods` exposes each method?셲 unique ID, data name, short name, and long name: [VI Server Class Hierarchy: programmatic method discovery](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy#Programmatic_Access_to_the_Methods).

## 2. Accepted scripted approach

The closest scripted equivalent to the interactive command is:

1. Obtain the caller VI?셲 block-diagram/`AbstractDiagram` reference.
2. Set the diagram selection to the intended objects.
3. Invoke `SubVI From Selection`.
4. Capture the returned VI refnum.
5. Save/name the new VI.
6. Verify both caller and child compile cleanly.
7. Optionally invoke the shipping Create SubVI post-processing plugin through the method?셲 `Apply 'Create SubVI' Plugin` input.

This delegates the difficult semantic work?봟oundary analysis, generated controls/indicators, connector-pane mapping, replacement node, and rewiring?봳o LabVIEW?셲 own implementation. NI describes the interactive operation as performing exactly those transformations: [NI: Create and Configure a LabVIEW SubVI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YK4VCAW).

Therefore, among your options:

- **Best fidelity:** private `AbstractDiagram.SubVI From Selection`.
- **Most supportable public scripting route:** manual construction, your option **(b)**.
- **Least attractive:** synthesizing a menu invocation. That still depends on private edit-time behavior and introduces window/menu/selection state without improving supportability.

Option (b) is much more work than a normal copy/move. You must classify every crossing wire, preserve datatype and direction, create suitable front-panel terminals, choose and populate a connector pane, move or recreate selected objects and internal wires, place the static subVI node in the caller, and reconnect every boundary wire. NI?셲 public VI Scripting documentation covers creating, arranging, and wiring diagram objects, but does not present a public high-level refactoring operation: [NI VI Scripting tutorial](https://www.ni.com/docs/zh-CN/bundle/labview/page/vi-scripting-tutorial.html).

## 3. What Erdos Miller?셲 `Create SubVI.vi` does

The public repository establishes that the library is a convenience layer over VI Scripting for code generation: [erdosmiller/lv-scripting](https://github.com/erdosmiller/lv-scripting).

However, the repository stores its implementation as compiled LabVIEW VIs, not reviewable textual source. Consequently, I cannot cite textual repository evidence proving the internal diagram of that particular VI.

Given that:

- the exact native private method exists,
- it returns the created VI reference,
- and its operation matches the library VI?셲 name and purpose,

the strong likelihood is that Erdos Miller?셲 VI is a convenience wrapper around `AbstractDiagram.SubVI From Selection`, possibly also handling selection/reference conversion and defaults. I would **not record that as proven** until a reporter listing of `Create SubVI.vi` shows its Invoke Node and selected method ID.

Cheap decisive check: ask the manager for a reporter listing containing Invoke Nodes and their class/method unique IDs. If it contains `6375405` / `SubVI From Selection`, it is a wrapper; if not, inspect its called subVIs before concluding it manually constructs the result.

## 4. Behavioral limitations and gotchas

These mostly apply equally to the interactive command and the private method because the method invokes LabVIEW?셲 native selection refactoring.

- **Local variables inside the selection:** A local belongs to a front-panel object in its owning VI and cannot simply retain that relationship after moving to another VI. Reported Create SubVI behavior converts an included local into a control reference passed through the connector pane plus a `Value` property node in the child. If the local remains outside the selection and only its wire crosses the boundary, the child normally receives plain data through a generated connector terminal. [NI Community example](https://forums.ni.com/t5/LabVIEW/How-to-illiminate-some-local-variables/m-p/3886394/highlight/true).

- **Control references:** These may be passed through the connector pane, but reference typing matters?봢specially strict versus non-strict references and control subclass compatibility. Locals converted to references also introduce synchronous UI/property-node access and change the result from pure dataflow. A community explanation confirms that references can give a subVI access to a caller control, while normal caller values should generally be wired through the connector pane: [SubVI and Global Variable](https://forums.ni.com/t5/LabVIEW/SubVI-and-Global-Variable/m-p/3573564).

- **Latch-action Booleans:** This is a genuine semantic hazard. A latch Boolean?셲 terminal is part of its reset behavior; reading it indirectly through a `Value` property node is not equivalent and is disallowed/problematic. A long-standing NI Community discussion explicitly notes that latch mechanical action cannot be used when reading through a Value property node: [Boolean references and latch action](https://forums.ni.com/t5/LabVIEW/i-created-boolean-references-in-my-main-vi-block-diagram-and/td-p/118698). Do not automatically extract an Event Structure case that consumes a latch Boolean unless the actual terminal and its event semantics remain valid.

- **Event Structures:** Events registered against front-panel controls are tied to control references and the owning UI. Extraction may create reference plumbing, but that does not automatically make the architecture sound. Event Structures, controls, references, and linked property nodes are specifically identified as code that often does not refactor cleanly into subVIs: [NI Community discussion](https://forums.ni.com/t5/LabVIEW/When-to-make-a-sub-Vi/m-p/3329794).

- **Uninitialised shift registers:** A shift register belongs to its loop structure. You cannot select only an interior consumer and expect the register?셲 state boundary to move. If the loop remains in the caller, the register value must cross the new subVI boundary as input/output data. If the entire loop and register move together, the uninitialised register becomes persistent state inside the new subVI; reentrancy and call-site sharing can therefore matter. NI documents that a non-reentrant VI has one data space and preserves state used by its callers, whereas reentrant configurations allocate clone data spaces: [NI: Execution Page](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html).

- **Error-cluster boundary wires:** They are ordinary typed boundary wires, so native Create SubVI normally makes `error in`/`error out` connector terminals and reconnects them. Community documentation reports that the generated 4-2-2-4 connector pane generally places error input/output in the lower corners when the error wire is included: [Create a VI with selected data from another VI](https://forums.ni.com/t5/LabVIEW/Create-a-VI-with-selected-data-from-another-VI/td-p/4186126). Still verify direction, required/recommended status, and that extraction did not introduce unintended serialization.

- **Selection accuracy:** Decorations, labels, polymorphic selector labels, tunnels, and partial structure contents can produce surprising results. NI acknowledged CAR 571520, where selecting a polymorphic VI selector during Create SubVI could remove or break unrelated wires: [NI Community bug report](https://forums.ni.com/t5/LabVIEW/LabVIEW-Bug-Report-Create-VI-from-selection/td-p/3215955).

- **Connector capacity:** A region with too many independent crossing values may exceed the chosen connector pattern or yield an undesirable pane. The Create SubVI plugin?셲 caller-connection mapping exists specifically because changing connector patterns requires remapping old connector indices to new ones: [LabVIEW Wiki: Create SubVI](https://labviewwiki.org/wiki/Create_SubVI).

## 5. Is the edit-time Create SubVI plugin itself callable?

The `resource\plugins\CreateSubVI` mechanism is real, but it is primarily a **hook for modifying the newly created VI**, not the primitive that selects and extracts caller objects.

The documented community description says:

- LabVIEW runs built-in Create SubVI processing first.
- `CreateSubVI_AdditionalActions.vi` can add post-processing.
- The modify-new-subVI hook receives the new VI refnum and caller-connection mapping.
- Setting its failure output causes LabVIEW to fall back to older built-in behavior.

[LabVIEW Wiki: extending/replacing Create SubVI behavior](https://labviewwiki.org/wiki/Create_SubVI).

NI also confirms that corruption of `resource\plugins\lv_modifyNewSubVI.vi` can make Create SubVI malfunction or crash, showing that this file participates in the shipping command: [NI: Create SubVI Function Is Not Working As Expected](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YSCSCA4&l=en-US).

So:

- **Yes**, the private `SubVI From Selection` method can request application of that plugin through `Apply 'Create SubVI' Plugin`.
- **No**, the post-processing plugin should not be treated as a supported standalone API for performing the initial extraction.
- Calling the menu command or invoking shipping plugin VIs directly is an **internal, version-fragile route**.
- For exact interactive fidelity, use the private method with the plugin flag and pin/test it against LabVIEW 2026.
- For an NI-supported long-term implementation, build the refactoring from public VI Scripting primitives and accept the substantially larger implementation and validation burden.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
