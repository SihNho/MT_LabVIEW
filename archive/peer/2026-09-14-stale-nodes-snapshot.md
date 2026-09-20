---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# stale-nodes-snapshot

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (38s)
- **why asked:** the walker did not see nodes created by another op.
- **verdict:** RESOLVED: same cause as castfree-reader-nondeterministic (walker junk); superseded.

## Question

ATTACK this (LabVIEW 2026 VI Scripting; two separate op VIs driven over ActiveX against the same target VI path, target front panel opened via OpenFrontPanel). MEASURED, deterministic: op A (erdosmiller Create Property Node) creates two Property nodes on Traverse('Diagram')[0] of the target; a class traversal (Traverse for GObjects, class 'Property') immediately sees both new uids. Op B - Open VI Reference(path) -> Traverse('Diagram') -> Index Array[0] -> To More Specific Class(Diagram) -> AbstractDiagram.Nodes[] -> Index Array[n] -> Node.UID - run for n=0..13 BEFORE and AFTER the creation returns IDENTICAL uid sequences: the 8 real donor nodes at 0..7, then at 8..13 six uids (306,307,309...) that belong to op B's OWN diagram objects (its Index Array default ref bleeding into downstream reads), never the two new uids. Traverse('Diagram') returns exactly 1 diagram. In earlier sessions the same op B DID report freshly created nodes - but only in flows where 'Block Diagram:Remove Bad Wires' (VI method 410) or a Connect Wire had run on the target after the creation. One probe today saw the FIRST created node but not a second created a moment later. HYPOTHESIS: Nodes[] as read by op B is a stale snapshot relative to edits made by another VI-Server client until something forces the target's diagram to refresh/recompile (Remove Bad Wires, a wire connect, closing and reopening the reference). QUESTIONS: (a) is AbstractDiagram.Nodes[] ever cached per reference/session, or is it always a live query - any NI/community evidence of scripting edits from one reference not being visible through another already-open reference to the same VI? (b) does 'Open VI Reference' by path from two different op VIs return the same in-memory instance, and can 'options' (e.g. prepare for reentrant run 0x08) or the target being open in the editor cause two instances? (c) which is the documented/cheapest 'commit' - closing the reference, a Remove Bad Wires call, VI method 'Compile'/'Save', or nothing (i.e. am I misreading and the new nodes are on a sub-diagram not enumerated)? (d) note Index Array past the end returns a default (invalid) refnum: could Nodes[] be returned with length 8 because op B is walking a DIFFERENT Diagram object (e.g. a cached ref from the first run of the op, before the target was replaced by a fresh file copy of the same path)? That last one worries me most: the target file is deleted and recopied between probes while op B stays loaded. Short, cited answer.

## Answer

The ?쐓tale `Nodes[]` cache??hypothesis is weaker than the ?쐓tale in-memory VI/diagram identity??hypothesis. Deleting and recopying the target while op B remains loaded is the largest red flag.

**(a) `AbstractDiagram.Nodes[]` caching**

I found no NI documentation or credible community evidence stating that `AbstractDiagram.Nodes[]` is cached per VI reference or requires an explicit commit after scripting edits. Your immediate class traversal seeing both UIDs also proves that the target?셲 live object graph contains them. Therefore, the safest current conclusion is not a documented `Nodes[]` cache, but that op B is holding or obtaining a different/stale diagram reference.

The fact that wiring or Remove Bad Wires appears to ?쐒efresh??the result is correlation, not proof of a documented commit operation. NI documents Remove Bad Wires simply as deleting broken wires, not as committing or synchronizing scripted edits ([NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999b.pdf)).

**(b) Same path and instances**

Ordinary Open VI Reference calls in the same application instance normally refer to the already-loaded VI rather than independently loading the file again. NI describes it as either returning a reference to a VI already in memory or loading it from disk ([NI Community discussion](https://forums.ni.com/t5/LabVIEW/Open-VI-reference-from-bytestream/td-p/4392441)). Different application instances?봲uch as project and main application contexts?봠an contain separate loaded VIs ([NI Community example](https://forums.ni.com/t5/LabVIEW/How-to-call-a-VI-by-reference-that-is-already-loaded-in-a/td-p/3778527)).

`0x08` is an exception for execution identity: it means ?쐏repare for reentrant run??and can return a reentrant clone reference, not merely another reference to the editable source VI ([NI options documentation](https://www.ni.com/docs/sw-UG/csh?context=lvcore_lvhowto_combining_options), [community clarification](https://forums.ni.com/t5/LabVIEW/open-vi-reference-reentrant-vi-state/td-p/3198467)). Do not use `0x08`, `0x80`, or `0x100` for a scripting/editor reference; community evidence says those flags create individual reentrant objects when applicable ([NI Community](https://forums.ni.com/t5/LabVIEW/VI-Refererence-behaviour/m-p/4209136)).

`OpenFrontPanel` itself should not create another instance.

**(c) Cheapest ?쐁ommit??*

There is no supported evidence that any commit is needed before reading `Nodes[]`. The cheapest correct operation should be **nothing**: the new nodes should already be visible through another reference to the same diagram object.

Do not use Remove Bad Wires as a commit?봧t is destructive and officially means deleting broken wires. Compile/Save is also unjustified for visibility and adds side effects. Closing and reopening is useful only as an **identity/reset diagnostic**, not as a semantic commit. Closing the last reference still does not guarantee immediate unloading; NI says disposal can occur asynchronously and recommends checking `All VIs in Memory` ([NI reference-lifetime documentation](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)).

**(d) File replacement is probably the cause**

Yes?봳his is the strongest explanation. Replacing the disk file does not replace an already-loaded VI object. LabVIEW?셲 links and scripting references address in-memory objects; disk replacement affects a later load only after the old VI actually leaves memory. NI explicitly distinguishes making a disk copy from replacing the open in-memory original ([NI Community summary of Save options](https://forums.ni.com/t5/LabVIEW/Save-Options-a-Bit-Confusing/m-p/761949)), and users see ?쏺I in memory ??cannot be replaced??when references keep the old object loaded ([NI Community](https://forums.ni.com/t5/LabVIEW/Close-vi-reference-not-working-on-reentrant-vi/m-p/1693418)).

So op B can remain bound to the eight-node in-memory generation while the same pathname now names a fresh disk file. Re-running Open VI Reference by that path is not proof of reloading.

Cheapest decisive checks:

1. Before replacing the file, close **every** target, diagram, node and traversal-produced reference in both ops.
2. Close the target?셲 front panel.
3. Verify the target disappears from `Application.All VIs in Memory`.
4. Only then replace the file and reopen it.
5. Compare target VI refnums and diagram refnums from A and B using LabVIEW?셲 reference equality, and record VI name/path plus diagram owner.
6. Read the `Nodes[]` array length directly before indexing.

If the array length is 8, the values at indices 8??3 are merely default invalid references followed by op-B dataflow contamination; they say nothing about hidden target nodes. If A and B truly have equal target and diagram references, no reentrant flags, and a direct `Nodes[]` length still differs from traversal, then you have a compact LabVIEW 2026 reproducer worth escalating to NI?봟ut current evidence points first to retained in-memory identity, not a `Nodes[]` cache.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
