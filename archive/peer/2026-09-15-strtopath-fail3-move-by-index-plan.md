---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, plan]
---

# strtopath-fail3-move-by-index-plan

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (89s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS PLAN and the diagnosis behind it (LabVIEW 2026 VI Scripting over COM, zero GUI). Failure: tools/bench/build_strtopath.log run 3 (tools/recipes/build_strtopath.py): with the donor's panel open and the label 'STP' verified on uid 194 ('String To Path' primitive), OpMoveByLabel_v0 raised error 1054 (object not found) BOTH when looking the object up as 'STP' (label) and as 'String To Path' (the primitive's own name). Read your two prior answers archive/peer/2026-09-14-strtopath-fail1-move-by-label-1054.md and archive/peer/2026-09-15-strtopath-fail2-label-present-still-1054.md.
DIAGNOSIS: the name index behind Open VI Object Reference does not resolve this built-in primitive by either string; the label route is exhausted for primitives (it works for controls and for a Call Library node, whose name IS its label).
PLAN (your own 'robust route'): OpMoveByIndex_v0 = a copy of OpMoveByLabel_v0 (which holds STATIC VI refs to NI's 'Test - Moving Objects Source/Target.vi' - byte-substituted by the fleet's copy_into protocol - and a GObject.Move invoke with owner = the Target's diagram and Duplicate? = TRUE), with the Open VI Object Reference node DELETED and replaced by: vi.lib\Utility\traverseref.llb\Traverse for GObjects.vi (VI Refnum <- the Source static ref, Class Name <- a string control, e.g. 'Function') -> References[] -> Index Array (index <- an I32 control) -> element -> Move.'reference'. Python computes the index from report(donor, 'Function') (Traverse order) so uid 194 is selected. Then copy_into gains a by-index twin (copy_by_index(donor, cls, index, target)).
Attack: (1) Does GObject.Move (632A400) with Duplicate?=TRUE and an owner in ANOTHER VI accept a reference obtained from Traverse for GObjects (a GObject refnum from the References[] array) - any class/typing pitfall vs the reference Open VI Object Reference returned? (2) Traverse for GObjects' 'Class Name' for a built-in function: 'Function'? Is the traversal order stable between two calls on the same loaded VI (Python's report() vs the op's own Traverse), so the index maps to the same object? Name the failure mode if not, and the guard (e.g. read the selected element's GObject.UID inside the op and export it - the fleet can build that PN). (3) Is deleting the Open VI Object Reference node and its wires by script safe in this op (any typed wire the Move needs that came only from that node, e.g. the class specifier)? (4) Alternative you may prefer: instead of touching the Move op, use Traverse + Move directly in a fresh op built on OpMove_v0 (already has Traverse(class,index)->Move, owner unwired) - what would supply the TARGET diagram reference there without a second Open VI Reference primitive (which the fleet cannot place)? (5) Cheapest discriminating test. Read-only; do not open LabVIEW; cite what you read.


## Answer

Verdict: the direction is sound, but the plan is not yet robust. `Traverse ??ordinal index ??Move` replaces a failed name lookup with a potentially silent wrong-object lookup. The op must accept an expected UID and refuse to call `Move` unless the selected reference?셲 `GObject.UID` matches it.

1. `Traverse` reference into cross-VI `Move`

This should type-check without a cast:

- `Traverse for GObjects.vi` returns an array statically typed as `GObject`, regardless of the requested class. The project has already measured that this output needs a cast only when the consumer requires a subclass such as `Node`; see [vi-scripting.md](</G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/.agents/skills/labview-automation/references/vi-scripting.md>).
- `Move` is a `GObject` method, so its `reference` input wants exactly that base type. No `To More Specific Class` should be necessary.
- Cross-VI duplication is a real supported behavior: an NI employee explicitly describes `Move` with either `Duplicate? = TRUE` or an owner belonging to another VI as producing a duplicated object. The limitation is that `reference out` remains the source reference, not the new copy. [NI discussion](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Scripting-method-Move-add-quot-Moved-Object-Reference/idc-p/2687099)

The existing project evidence is stronger than documentation here: `OpMoveByLabel_v0` already uses precisely cross-VI `GObject.Move`, and `moveout_chain.log` shows another assembled `Traverse/Index Array ??Move.reference` route compiling. Therefore, the origin of the reference??Open VI Object Reference` versus `Traverse`?봲hould not matter once both wires are statically `GObject`.

Remaining pitfall: do not interpret `Move.reference out` as the duplicate. Discover the copy through the existing target before/after UID census. This behavior is independently reported here: [NI Community](https://forums.ni.com/t5/LabVIEW/VI-Scripting-get-reference-of-the-duplicate-element/td-p/1882509).

2. Class string and order

`"Function"` is the right first candidate for `String To Path`. The repository?셲 own reporter already calls `report(..., "Function")` successfully, and `moveout_chain.log` reports the Open-VI-reference primitive itself under class `Function`. Traversal class strings are exact and sometimes unintuitive?봏I?셲 own discussion shows, for example, that block-diagram controls require `"ControlTerminal"`, not `"Control"`. [NI Community](https://forums.ni.com/t5/LabVIEW/Traverse-for-Refs-Broken-in-2017/td-p/3743956)

I found no NI guarantee that `Traverse for GObjects` preserves array order across separate calls. More importantly, even if it is deterministic today, the Python call and op call are separated by loading, preparation, and possibly diagram mutation. Any reorder causes the classic failure mode:

> index still valid ??wrong `Function` selected ??wrong primitive duplicated successfully.

That is worse than error 1054 because it can produce a plausible but incorrect target.

The proposed UID indicator is necessary but not sufficient if it is merely logged after `Move`. The guard should be inside the op:

```text
Traverse("Function") ??Index Array
                         ?쒋넂 GObject.UID ??equal?(Expected UID)
                         ?붴넂 Move only in TRUE case
FALSE ??explicit error / Copied? = FALSE
```

Inputs should therefore be `Class Name`, `index`, and `Expected UID`. Outputs should include `Selected UID` and preferably `Copied?` or an explicit error. Python should supply UID 194 and reject anything else before target mutation.

If introducing a Case structure is too expensive, a two-phase probe is acceptable for this one build: first run with `Move` disconnected/disabled and verify repeated `Selected UID == 194`; only then enable the move. It is not a robust general `copy_by_index()` API.

3. Deleting `Open VI Object Reference`

Do not assume ?쐂elete node, then remove bad wires??is sufficient. Request reporter output for the current op and account for every terminal before deletion.

Likely consequences are:

- The old object-reference output wire to `Move.reference` is intentionally replaced by `Index Array.element`.
- Any class-specifier constant used only by `Open VI Object Reference` becomes dead and can be removed.
- The Open-VI-object node may participate in the error chain. Deleting it can leave the `Move` error input unwired or leave broken wire fragments.
- The target-owner path must remain untouched: the target static VI reference/diagram reference feeding `Move.owner` is the valuable part of this op.

There is no typing dependency from the deleted class specifier that `Move` needs: the `Move` invoke is already a `GObject` invoke, and the traversal array is already `GObject`-typed. But require these post-surgery gates before saving:

- `Move.reference` wire source is the new `Index Array.element`.
- `Move.owner` still comes from the target diagram reference.
- `Duplicate?` remains `TRUE`.
- error-chain endpoints are accounted for.
- op `ExecState == runnable`.
- no broken wires remain.

4. Fresh `OpMove_v0` alternative

`OpMove_v0` cannot solve the two-VI problem by itself. Its current traversal and owner-unwired design operates on one opened VI. A cross-VI copy needs two independent roots:

```text
source VI reference ??Traverse ??selected GObject
target VI reference ??VI.Block Diagram ??Move.owner
```

A single Open VI Reference primitive cannot simultaneously supply both source and target. Without placing a second one, the options are:

- retain the two static VI references already present in `OpMoveByLabel_v0`; this is the cheapest route,
- copy an existing Open VI Reference node into `OpMove_v0`,
- or statically reference one side and byte-substitute it through the existing protocol.

Thus, building from `OpMoveByLabel_v0` is preferable. Its name-lookup node is the defective selection mechanism, but its dual-source/target topology is exactly what is needed.

5. Cheapest discriminating test

Before building the complete copier:

1. On the unchanged substituted donor, call the existing reporter for `"Function"` twice and require identical ordered UID arrays, including UID 194 at the proposed index.
2. Build/instrument only `Traverse ??Index Array ??GObject.UID indicator`; leave `Move` unable to execute.
3. Run it repeatedly with the same class/index and require `Selected UID == 194`.
4. Then connect/enable `Move`, copy once into an empty scratch target, and require:

   - source still contains UID 194,
   - target gains exactly one top-level `Function`,
   - the added object has the expected class/style,
   - target changes by exactly the expected UID delta.

The repeated reporter comparison is the absolute cheapest order test. The UID-only op probe is the cheapest test that actually discriminates whether Python and the new op share the same traversal ordering.

Finally, narrow the diagnosis. The evidence proves:

> `Open VI Object Reference` in this particular op does not resolve this `String To Path` instance by either tested string.

It does not prove that the label route is exhausted for all primitives. NI explicitly states that named functions such as For Loops and Compound Arithmetic nodes can be obtained through `Open VI Object Reference`. [NI employee discussion](https://forums.ni.com/t5/LabVIEW-APIs-Discussions/Feedback-Request-Open-VI-Object-Reference/m-p/3401796)

So proceed with the traversal route, but call it `copy_by_index_checked(...)`, require the expected UID, and prevent mutation on mismatch.

## Sources

(extract from answer)

## What was done with it

Adopted: build `OpMoveByIndex_v0` from `OpMoveByLabel_v0` (keep its two static roots; delete only the
`Open VI Object Reference` selection; `Move.owner` untouched, `Duplicate?` TRUE), select by
`Traverse for GObjects(Class Name)` → Index Array(index), and add the reviewer's **UID guard**: a `GObject.UID`
property on the selected element exported as `Selected UID`. A Case structure is not built; instead the
two-phase equivalent: every call's `Selected UID` is compared by Python with the expected uid (194) and the target
— always a fresh scratch — is discarded if they differ, so a wrong-object copy can never be used. Post-surgery
gates as listed (reference source = IA.element, owner source unchanged, error chain accounted, ExecState 1).
`Move.reference out` is never treated as the duplicate; the copy is found by UID census on the target.
Census of the donor op: `tools/bench/diag_opmovebylabel.log`; recipe `tools/recipes/build_opmovebyindex.py`.
