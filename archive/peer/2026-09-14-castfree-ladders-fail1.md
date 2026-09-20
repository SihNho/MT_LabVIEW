---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# castfree-ladders-fail1

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (65s)
- **why asked:** first ladder attempt failed.
- **verdict:** superseded - see castfree-ladders-execstate0 and probe_castfree5.log (both ladders compile).

## Question

ATTACK my diagnosis of two failed predictions (LabVIEW 2026 VI Scripting through erdosmiller Create Property Node, driven over ActiveX). RUN: tools/recipes/probe_castfree_ladders.py. FAILURE 1: created an AbstractDiagram-class property node with property ID 6375802 (documented on labviewwiki as AbstractDiagram.SubVIs[]) - node created, but reading its terminals back shows NO property-specific output terminal at all (only reference/reference out/error in/error out). By contrast the same donor's existing AbstractDiagram.Nodes[] node (6375809) has a 'Nodes[]' terminal. Then wiring the VI.Block Diagram node's 'Diagram' output (ALREADY wired to Nodes[]) into the new node was declined silently (wire count unchanged). FAILURE 2: created a Control-class node with Control.Terminal 6332006 - this DID attach (output terminal reads back as 'Terminal'); wired it from an Index Array 'element' that is ALREADY wired to Control.Label, using our branch=True flag which skips the count check; ExecState went to 0. MY DIAGNOSIS: (i) our wire op cannot BRANCH from an already-wired source (documented: declined silently), so in both cases the new node's required 'reference' input stayed unwired and that alone breaks the VI; fix = feed new nodes from the upstream property node's unwired 'reference out' pass-through instead of branching. (ii) 6375802 did not attach at all, so SubVIs[] is unavailable to this creator - either the ID is wrong for LabVIEW 2026, or it is private/unsupported, or the creator only attaches what 'All Supported Properties' (636F80E) lists for the class. QUESTIONS: (a) is 6375802 really AbstractDiagram.SubVIs[] in LabVIEW 2026, and is it public? Is there an ID list/dump for the 2026 class table? (b) does a Property node's 'reference out' pass the SAME statically-typed reference through (so chaining from Nodes[]-node.reference out gives a Diagram-typed ref, and from Control.Label-node.reference out gives a Control-typed ref)? (c) is 'unwired required reference on a property node' sufficient to break a VI, i.e. would (i) fully explain ExecState 0 in failure 2? (d) alternative for SubVI identity with NO cast if SubVIs[] is dead: does Traverse for GObjects.vi with Class Name='SubVI' return references whose STATIC type is SubVI (it is a typed-array output?), or always GObject? Cite labviewwiki / NI. Do not confirm; find what I am missing.

## Answer

Your diagnosis is plausible for failure 2, but it overreaches on failure 1 and on what the evidence proves.

### (a) `6375802` / `AbstractDiagram.SubVIs[]`

`6375802` is indeed listed as `AbstractDiagram.SubVIs[]`, read-only, returning top-level subVI references. However, the available LabVIEW Wiki table was last edited in 2020; it is not evidence that the property is public or supported in LabVIEW 2026. The table?셲 `RTE: No` means unavailable in the run-time engine?봭ot necessarily private?봞nd the rendered page does not clearly expose the Basic/Scripting/Private permission columns??values. [LabVIEW Wiki: AbstractDiagram class](https://labviewwiki.org/wiki/AbstractDiagram_class)

I found no public NI 2026 property-ID/class-table dump. Consequently, the live 2026 `All Supported Properties` result is stronger evidence than the old wiki, provided you query it on an actual AbstractDiagram-typed node/reference.

But your conclusion ?쏶ubVIs[] is unavailable to this creator??is not yet established. No property-specific terminal proves that the mutation did not attach; it does not tell you why. Competing explanations include:

- `6375802` is absent from the 2026 supported-property table.
- It exists but is private/disabled under the current scripting configuration.
- The setter requires a property-table index/row operation before assigning the ID.
- The donor?셲 property-row metadata was not in a mutable state.
- The creator rejected the assignment because the node had not yet acquired the expected class/type context.
- The ID was supplied with the wrong radix. These wiki IDs are hexadecimal-looking identifiers; verify that the working `6375809` and failing `6375802` take the identical conversion path.

Cheap decisive check: capture `All Supported Properties` from the same newly created AbstractDiagram node and search both the numeric ID and localized long name. If `6375802` is present but assignment still produces no terminal, the fault is your mutation sequence/creator?봭ot availability.

Also, the failed wire into this empty node does not explain why the property terminal is absent. Wiring the reference input cannot retroactively create a rejected property row. Failure 1 therefore contains two independent failures: property attachment and wire creation.

### (b) Does `reference out` preserve the reference and type?

The value is the same reference. NI explicitly says the output refnum exists for wiring convenience and that there is no difference between passing the input or output refnum onward. [NI: Differences Between the Input and Output Refnum Value](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000001Dp7cCAC&l=en-US)

The classic documentation labels it `dup reference`, supporting pass-through rather than a reference returned by the selected property. [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999b.pdf)

For static type, the correct formulation is: the duplicate terminal preserves the property node?셲 reference-terminal datatype. VI Server reference types follow the class hierarchy, and the selected reference class controls which properties are available. [NI employee explanation of VI Server reference typing](https://forums.ni.com/t5/LabVIEW/reference-of-property-node/m-p/2206778)

Thus:

- An explicitly AbstractDiagram/Diagram-typed node should pass that type through.
- A Control-typed node should pass Control through.
- Do not infer the pass-through type merely from a property name such as `Nodes[]` or `Label`; verify the reporter?셲 terminal datatype/class. A generic or broader input remains generic/broad.

Chaining from `reference out` is therefore a sound workaround for your wire operation?셲 inability to fan out. It also imposes dataflow ordering, which ordinary branching does not.

### (c) Is an unwired reference sufficient to make the VI bad?

Yes?봧f this is an explicit, unlinked Property Node whose reference terminal is required. NI?셲 debugging documentation says an unwired required block-diagram terminal is sufficient to break a VI. [NI: LabVIEW Debugging Techniques](https://www.ni.com/en/support/documentation/supplemental/12/debugging-techniques-in-labview.html)

NI also documents a concrete error-list entry, `Property Node: Contains unwired or bad terminal`, in a broken VI. [NI: System Configuration VIs Are Broken](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YRHMCA4&l=en-US)

So this can fully explain failure 2?셲 `ExecState = 0`; zero denotes a bad/non-executable VI. [NI Community: execution-state numeric values](https://forums.ni.com/t5/LabVIEW/How-to-tell-if-VI-is-running/m-p/721963), [NI: execution-state meanings](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YIEJCA4)

But `ExecState = 0` cannot prove it was the only error. You need the Error List/report text after insertion. In particular, verify:

- the `reference` input is actually unwired;
- no malformed or dangling wire was created;
- the `Terminal` property output has a valid terminal/type;
- the new node reports no ?쐀ad terminal??independently of the missing reference.

Your broader statement that ?쐔he wire op cannot branch??describes the scripting operation you use, not LabVIEW?셲 wiring model?봭ative LabVIEW wires routinely branch. The likely defect is that the operation expects an unwired source terminal and silently refuses a terminal already owning a wire.

### (d) Is classic `Traverse for GObjects.vi` cast-free?

No. The classic VI?셲 class-name string is a runtime filter; it does not specialize the output wire?셲 static datatype. The strongest evidence is the NI Community?셲 malleable wrapper: its author says the wrapper accepts a class specifier specifically to eliminate the need to downcast the references returned by the classic traversal VI. [NI Community: Malleable wrapper for Traverse for GObjects](https://forums.ni.com/t5/LabVIEW/Malleable-wrapper-for-Traverse-for-GObjects/td-p/4151358)

That means classic:

```text
Traverse for GObjects.vi
Class Name = "SubVI"
        ??statically GObject[]; runtime objects are SubVI
```

NI likewise documents that when an array/index operation yields a broad Control reference, `To More Specific Class` is required before subclass-specific properties become available. [NI: Accessing Properties and Methods of Array or Cluster Elements](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YH1ACAW&l=en-US)

So classic traversal is not a no-cast replacement. The viable cast-free possibilities are:

- make `SubVIs[]` attach correctly, since its declared output should be `SubVI[]`;
- use/adapt a malleable typed traversal wrapper;
- inspect all `Nodes[]` and identify subVIs using properties available on the common Node type, if identity?봭ot SubVI-specific access?봧s sufficient.

Bottom line: chaining through `reference out` likely fixes failure 2, but it cannot fix failure 1?셲 missing property terminal. Treat failure 1 primarily as a rejected property-assignment problem, and use the 2026 live supported-property list plus the node?셲 error/report metadata to distinguish ?쐏roperty removed/private??from ?쐁reator mutation sequence is wrong.?

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
