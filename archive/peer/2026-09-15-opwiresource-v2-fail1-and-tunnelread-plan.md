---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting, plan]
---

# opwiresource-v2-fail1-and-tunnelread-plan

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (91s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK TWO THINGS (LabVIEW 2026 VI Scripting, read-only analysis of my own recipes). (A) THE FAILURE: tools/recipes/build_opwiresource_v2.py run 1 (log tools/bench/build_opwiresource_v2.log) wanted to add a second To More Specific Class so that a wire source object (Generic.Owner output) could reach GObject.UID. Sequence: copy OpWireSource_v1.vi, create a spare GObject.UID property node (its reference UNWIRED, so the VI is BROKEN), create_control on that reference to get a GObject-typed seed, cut the wire, then close the panel WITHOUT saving (a broken VI cannot be saved - our gscript.save refuses it) and call copy_by_index to bring in the cast. The finish hook then found NO new To More Specific Class among the added uids and the run stopped. MY DIAGNOSIS: copy_by_index loads the TARGET FROM DISK, and because the edits were never saved, the loaded target was the plain v1 copy - my fn_before set came from the edited in-memory version, and after the reload the copied node very likely reused a uid that was already in that set (LabVIEW reuses uids of deleted/never-saved objects), so the added-uid filter returned nothing. The real mistake is structural: edits that must survive a copy_by_index have to be SAVED first, which means the VI must be runnable at that moment - but the seed trick needs an unwired (hence broken) node. (B) THE PLAN CHANGE that avoids the whole problem, please attack it: do not build v2 at all. Instead build OpTunnelRead_v0 from the same donor (OpWireSource_v1, which already has Open VI Reference -> UID to GObject Reference.vi -> To More Specific Class), by (1) retargeting the EXISTING cast from Wire to Tunnel - create a Tunnel-class property node, create_control on its reference, cut that wire, delete the old Wire-typed seed wire and wire the Tunnel seed to target class; (2) deleting the Wire.Terms[] chain; (3) adding only UPCASTS, which need no further cast: Tunnel.Outside Terminal 6356001 -> Terminal.Connected Wire 634A000 (short name Wire) -> GObject.UID 632A813 (Wire inherits GObject); Tunnel.Inside Terminals[] 6356000 -> Index Array[index control] -> Terminal.Connected Wire -> UID, and the same inner terminal -> Terminal.Diagram 634A002 -> GObject.UID (Diagram inherits GObject) to identify the FRAME; plus ConditionalTunnel.Use Default if Unwired 5D251C00 if the cast target is ConditionalTunnel. Used first in a scan to find which tunnel object carries outer wire 5975 / 5637 (the two outputs of Case #5540), then per index to read each frame inner wire - after which the existing OpWireSource_v1 resolves each inner wire to its source. QUESTIONS: (1) is my diagnosis of (A) right, in particular that LabVIEW REUSES object uids so an added-uid filter is unsafe across a reload - and what is the safe identity for objects created by a copy across a save/reload boundary (count delta plus class plus position? the copy op reports the new uid itself?); (2) in (B), can one To More Specific Class be retargeted simply by replacing the wire on its target class input, or does the node cache the class at creation; (3) if the concrete class of a case output tunnel is ConditionalTunnel, will a cast whose target class is the PARENT Tunnel still let me read Inside Terminals[] and Outside Terminal (upcast on the property node is fine) - and will Use Default if Unwired (a ConditionalTunnel property) then be unreachable, requiring the target to be ConditionalTunnel instead; (4) any cheaper route to find WHICH tunnel carries a known outer wire uid than scanning every tunnel object - e.g. from the wire side, since OpWireSource_v1 already tells me the source terminal owner CLASS but not its uid. Read-only; cite what you read.

## Answer

Your diagnosis is half right: the reload explains the failure; UID reuse does not need to be invoked and is not established by this run.

1. Failure A

`copy_by_index()` definitely did not operate on the edited in-memory `OP`.

Its implementation does this before running the copy operation:

```python
_copy("target -> MOVE_DST", target, MOVE_DST)
before = uids(MOVE_DST, "GObject")
...
added = new_since(MOVE_DST, "GObject", before)
...
finish(MOVE_DST)
```

Because `target` had been closed without saving, the file copied into `MOVE_DST` was plain v1. Therefore `finish()` inspected:

- the disk-state v1 objects,
- plus the newly copied TMSC,
- without `pnU2`, `pnO`?셲 current identity, or the seed created in the discarded editing session.

The recipe?셲 `fn_before`, however, came from the discarded edited instance. That makes this cross-instance set subtraction invalid.

But the specific claim ?쏬abVIEW probably reused the deleted/unsaved TMSC UID??is unsupported. The empty result could equally mean that the copied TMSC received any UID that happened to occur among the extra objects in the discarded edit. The two object universes are different; equality of their numeric UIDs has no identity meaning. NI?셲 public documentation I found does not promise that `GObject.UID` is globally unique, monotonic, or stable across unload/reload/edit history.

The important structural correction is therefore:

> Never compare UID sets obtained from different loaded/file states.

You already have the safe identity available. `copy_by_index()` computes `added` from `MOVE_DST` immediately before and after the copy in the same loaded object universe. That is authoritative. Pass that result into the finish hook, for example conceptually:

```python
finish(MOVE_DST, added, sel)
```

Then require exactly one `Function` in `added` whose terminals match TMSC. The existing `sel` is the donor object?셲 UID guard, not the destination copy?셲 UID.

Ranking possible fallbacks:

1. `added` produced inside `copy_by_index()` ??best.
2. A reference or copied-object UID returned directly by the move/copy Op ??equally good if the underlying operation can expose it.
3. Same-session before/after UID delta, restricted to `Function`, followed by terminal/class verification.
4. Count delta + class + position ??usable only as a recovery heuristic; copying can offset position, and pre-existing objects can share class/nearby bounds.
5. A UID remembered across unload/reload ??unsafe unless you separately demonstrate persistence for this operation.

Also, the claim ?쏿 broken VI cannot be saved??is too broad. LabVIEW permits broken VIs generally?봏I explicitly describes VIs as broken when required terminals are unwired?봟ut your `gscript.save` policy correctly refuses to save them. [NI?셲 wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

2. Retargeting the existing TMSC

Yes: replacing the target-class wire should retarget the existing TMSC. The target-class input determines the compile-time type of its output; it is not merely an initialization hint cached when the node is created.

NI describes the Class Specifier Constant as selecting the class of the output and explicitly says it is used with To More Specific Class. [NI Class Specifier Constant](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/constants/class-specifier.html)

So the proposed sequence is sound:

- disconnect/delete the Wire-typed target seed,
- connect the Tunnel-typed seed,
- verify that `specific class reference` now has Tunnel type,
- only then connect it to Tunnel property nodes,
- gate on `ExecState`.

I would still treat ?쐒etarget succeeded??as a measured condition, because your seed is a generated refnum control rather than an ordinary class-specifier constant. The cheapest gate is that the existing output connects successfully to `Tunnel.Outside Terminal`, plus the VI returns to runnable state.

3. Parent Tunnel versus ConditionalTunnel

A concrete `ConditionalTunnel` reference can be cast to its parent `Tunnel`. At runtime, NI says the reference may be either the target type itself or a child of that target type. [NI?셲 TMSC runtime criteria](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000gNoVCAU&l=en-US)

Consequently:

- TMSC targeted as `Tunnel` can accept a runtime `ConditionalTunnel`.
- You can read properties declared by `Tunnel`, including `Outside Terminal` and `Inside Terminals[]`.
- You cannot access a property declared only by `ConditionalTunnel` from a wire whose compile-time type is merely `Tunnel`.

That last point follows from how LabVIEW uses the wire?셲 compile-time class to determine available members; changing the wire type does not change the underlying runtime object. NI summarizes this as TMSC controlling the wire type. [NI explanation of TMSC/TMGC](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU00000069mz0AA&l=en-US)

Therefore, if `Use Default if Unwired` is genuinely declared only on `ConditionalTunnel`, you need a `ConditionalTunnel`-typed cast to reach it. Sensible designs are:

- target `ConditionalTunnel` if this Op is specifically for conditional/case tunnels and every scanned object is compatible; or
- keep the main cast at `Tunnel` and add a separate optional `ConditionalTunnel` cast/property branch, handling a failed cast for ordinary tunnels.

Do not target `ConditionalTunnel` merely because one expected case output has that concrete class unless the scan is restricted to those objects. A plain `Tunnel` encountered during a general scan would fail the child cast.

One terminology concern: confirm through your reporter that the objects carrying Case #5540?셲 outputs really report `ConditionalTunnel`. ?쏞onditional tunnel??is also used for loop conditional-indexing behavior, so the class assumption deserves a cheap census before specializing the entire Op.

4. Avoiding the full tunnel scan

Yes?봲tarting from the wire should be cheaper, and it is the direction I would pursue first.

A wire has one source and potentially multiple sinks; NI documents that basic wire topology explicitly. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

For a Case output tunnel, the outer-side tunnel terminal should normally be the source of the outer wire. Therefore the direct route is:

```text
known outer Wire
  ??source Terminal
  ??Terminal.Owner
  ??owner class + owner UID
```

Your existing `OpWireSource_v1` already implements most of this and is reporting the source-owner class. If wires 5975 and 5637 report a tunnel class, adding owner UID to that same operation is the direct O(1) solution; scanning 132 tunnels is unnecessary.

But this brings you back to the missing Generic-owner-to-GObject cast. The plan change does not eliminate that need if direct wire-to-owner UID is the desired optimization. `OpTunnelRead_v0` avoids building v2 only by accepting the O(number of tunnels) discovery scan.

A potentially cleaner variant is to examine whether the terminal reference?셲 own `Owner` property is typed more specifically than the `Generic.Owner` currently used. If it yields `GObject`, you could reach `UID` without the second TMSC. If it is still `Generic`, there is no obvious cast-free direct route.

My verdict:

- Abandoning v2 is technically viable.
- `OpTunnelRead_v0`?셲 parent-class design is sound for the common tunnel properties.
- Specialize to `ConditionalTunnel` only for the optional conditional property.
- But the scan is not the cheapest architecture. Repairing the copy helper so its same-session `added` identities are passed into `finish()` would make v2 straightforward and give direct outer-wire ??tunnel UID lookup. The copy helper already computed exactly the identity information the recipe needed; the API discarded it at the hook boundary.

## Sources

(extract from answer)

## What was done with it

Both halves accepted, and the fix went into the TOOLKIT rather than the recipe: `gscript.copy_by_index` now passes
its own `added` delta (computed before/after the copy in the same loaded universe) to the finish hook when the hook
takes a second argument — the identity the reviewer pointed out was being discarded at the hook boundary;
one-argument hooks still work. My "LabVIEW reused the uid" guess is withdrawn as unsupported: the real and
sufficient defect is comparing uid sets across a reload. The recipe is reordered so the VI is RUNNABLE at every save
boundary — `create_control` leaves the seed wired (runnable → saved → copied), and the cut happens inside the finish
hook, which ends runnable anyway. The `OpTunnelRead_v0` plan is kept as the fallback, with the reviewer's warnings
recorded: retargeting a cast must be MEASURED (ExecState + the new property attaching), a `Tunnel`-targeted cast
cannot reach `ConditionalTunnel.Use Default if Unwired`, and the concrete class of #5540's output tunnels must be
censused before specialising an op to it. Rerun: `tools/bench/build_opwiresource_v2.log` run 2.
