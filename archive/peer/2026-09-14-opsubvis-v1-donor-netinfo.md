---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# opsubvis-v1-donor-netinfo

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (102s)
- **why asked:** FAILED PREDICTION (tools/bench/test_opsubvis.log): OpSubVIs_v0 read only diagram 0 on the main VI; my reading was "wrong donor - OpNodeInfo_v0's `index` is a node index, not a diagram index". Rule: the explanation formed under pressure gets attacked before it drives the next build (OpSubVIs_v1 on donor OpNetInfo_v1).
- **verdict:** diagnosis CONFIRMED as leading; acted on. (1) No cast-free route to a nested Diagram-typed ref exists (peer search + NI docs) → keep the Traverse→IA→TMSC(Diagram) front half = donor OpNetInfo_v1. (2) Peer's identity test on the creator was run inside the v1 recipe (build_opsubvis_v1.log): the creator was found by terminal signature (uid 243, 'Diagram in','ID String','Inputs','Outputs'), deleted by its own SubVI index, re-reported ABSENT, ExecState 1 after Remove Bad Wires — so spec §33's "0 gone" was a wrong-reference result, and v1 is built creator-free (T0 in test_opsubvis.py measures junk per call). (3) The +0.95 handles/run on the main VI is recorded as OPEN with the peer's 4-block matrix (minimal open/close, OpReportAll, OpSubVIs scratch, OpSubVIs main, + idle recount + All VIs in Memory) as the next discriminating test — not called a refnum leak. (4) "invalid diagram index must ERROR" is a release criterion (T3b).

## Question

FAILED PREDICTION review + plan attack. RESULT (tools/bench/test_opsubvis.log, op built by tools/recipes/build_opsubvis_v0.py): OpSubVIs_v0 passes on a scratch (2 subVI calls on its top-level diagram: names, paths, UIDs exact) but returns EMPTY arrays with NO error on the main VI for diagram 43 (cache says 6 subVI calls incl. the kernel uid 5058), for diagram 1, and even for diagram index 9999 (no error on the SubVIs[] node's own error out). MY EXPLANATION: wrong donor. OpNodeInfo_v0's chain is VI -> Block Diagram (23C) -> Nodes[] -> Index Array() -> node props: its  is a NODE index in the TOP-LEVEL diagram, there is no diagram selection at all, so the new op always reads diagram 0 (scratch: subVIs live on diagram 0 -> correct; main VI diagram 0 holds one sequence structure and no subVI -> empty; 9999 only reaches the vestigial node chain, whose error is not on our indicator). ATTACK THAT (what else could give empty-without-error on the main VI: a VI Path vs name problem, ref invalid but error swallowed, arrays not updated?). PLAN v1: same recipe with donor OpNetInfo_v1.vi (tools/recipes/build_opnetinfo.py: Traverse 'Diagram' by  -> Index Array -> To More Specific Class -> Diagram-typed ref -> Nodes[] property node -> per-node/terminal readers; this is the op behind gscript.net_map, which selects diagrams by  correctly on the main VI every day), adding SubVIs[] + For loop + SubVI[VI Name, VI Path, UID] node from its Nodes[]-node 'reference out' exactly as v0 did (that part is proven: rows attached, loop compiled, scratch results exact). KNOWN COST of that donor (docs/keystone-op-spec.md s33): it carries an erdosmiller Create Invoke Node creator that drops ONE untyped junk Invoke node on the TARGET per run even with empty class/ID; Generic.Delete on that creator node once returned '0 gone'. So every run of the v1 op on the main VI would leave one junk Invoke in its in-memory copy (never saved) - protocol: purge after (report_all + delete_object per junk + Remove Bad Wires; ~3 s per call on the main VI). QUESTIONS: (1) Is there a cast-free way to obtain the k-th DIAGRAM as a Diagram-typed reference without the To More Specific Class node? (e.g. VI.Block Diagram gives the top level; nested diagrams hang off Structure nodes whose refs come back as Node/GObject from Nodes[] - any property on AbstractDiagram/Node/Structure that yields typed sub-diagram refs? AbstractDiagram.'Structures[]'? Node.'Owner'? ) (2) Could the creator SubVI be removed from the COPY another way: delete the WIRE into it, delete by a different class name (SubVI vs Node), or does Generic.Delete fail because the node is inside a structure / has a required input? (3) Handle audit finding to interpret: on the scratch 30 runs = +0.03 handles/run; on the MAIN VI 50 runs = +0.95 handles/run (+49) although the op returned ZERO element references on that target (diagram 0 empty) - so the growth cannot be SubVIs[] element refs; is ~1 handle/run for Open VI Reference on a 473 KB VI with 98 subVI call sites plausible LabVIEW behaviour (VI load caching) or a leak of the top-level VI reference (the op wires Close Reference on it)? What discriminating test separates them cheaply (e.g. the same 50 runs of OpReportAll_v0 on the main VI)? (4) test T6 also failed: index 2 = 999 on the main VI returned 0 rows - explained by the same donor error (diagram 0 has none), agree? Give concrete failure scenarios and the cheapest test for each; cite NI docs where they exist.

## Answer

Your wrong-donor explanation is the leading diagnosis. The three observations form a tight signature:

- Scratch succeeds because its subVIs are on the top-level diagram.
- Main diagrams 43 and 1 both return empty because the effective source remains diagram 0.
- Index 9999 also returns empty because that index affects only the vestigial node-index chain, while its error is disconnected from the reported error path.

NI/community evidence agrees that `Diagram.SubVIs[]` is diagram-local, not recursive: it returns only calls at that diagram level. [NI Community: ?쏷his VI?셲 SubVIs??(https://forums.ni.com/t5/LabVIEW/Is-it-possible-to-retrieve-quot-This-VI-s-SubVIs-quot/m-p/4471372)

## 1. Cast-free diagram selection

I found no documented cast-free route from an arbitrary nested object to a statically `Diagram`-typed reference.

The likely routes all end in a generic reference:

- `GObject.Owner` conceptually identifies the containing object, but the returned reference is Generic/GObject; accessing diagram-specific properties therefore still requires a downcast. [NI Community discussion of `Owner`](https://forums.ni.com/t5/LabVIEW/how-to-upclass-from-a-control-withing-cluster-to-cluster-s-label/td-p/3133890)
- `AbstractDiagram.All Objects[]` returns references to only the top-level objects of that particular diagram; it does not itself select or recursively type nested subdiagrams. [NI API: All Objects[]](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/abstractdiagram/allobjects.html)
- Structures contain subdiagrams, but structure contents are separate subdiagrams rather than nodes on the parent diagram. [NI: Loops and Other Structures](https://www.ni.com/docs/ar-SO/bundle/labview/page/loops-and-other-structures.html)

So I would retain the already-proven `Traverse Diagram ??Index Array ??To More Specific Class(Diagram)` chain. It is materially safer than inventing an `Owner` walk: `Owner` would also require knowing when the returned generic object is the desired subdiagram rather than another container.

Cheap confirmation: expose the selected diagram reference?셲 class name plus one diagram-local invariant?봮bject count or known UID?봣or indices 0, 1, 43, and 9999. Require 9999 to produce an error on the op?셲 actual error indicator.

## 2. Removing the junk creator node

Deleting its incoming wire first is worth trying diagnostically, but a required input or attached wire should not normally make a diagram node intrinsically undeletable. The more likely explanations for ?? gone??are:

1. The delete operation received the wrong reference.
2. The reference was stale or invalid.
3. The creator resides in a nested subdiagram while deletion searched only the top level.
4. The delete occurred, then the still-present creator logic recreated the target junk node during the same or next run.
5. Error/status from `Generic.Delete` was not on the observed error chain.

Changing the cast from `Node` to `SubVI` should not help if `Generic.Delete` is genuinely inherited and invoked on the same underlying object. A different type name helps only if it changes which object reference reaches Delete.

Cheapest discriminating test:

- Report the creator?셲 UID, class name, owner class, and bounds before deletion.
- Delete by that exact UID-derived reference.
- Immediately report that same containing diagram again before executing the op.
- Run once and report again.

Interpretation:

- Missing before run, present after run ??recreation/order problem.
- Still present immediately after Delete ??wrong reference, invalid reference, wrong containing diagram, or swallowed error.
- Creator absent but junk still appears ??some other creator is responsible.

Deleting the wire first is then a one-variable test, but I would not build v1 around a mandatory three-second purge until the identity/order test is done.

The cleaner production plan is still to remove or neutralize the creator in the op copy itself. Runtime cleanup on the target is an avoidable mutation and creates another failure path.

## 3. The +0.95 Windows handles/run result

Treat the near-exact `+49` over 50 runs as suspicious, but do not yet call it a leaked LabVIEW refnum.

Two different resources are being conflated:

- NI says every `Open VI Reference` creates a reference allocation that should be closed. [NI: Closing References](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)
- NI also says closing a reference invalidates the refnum immediately, but disposal of the referenced object can happen asynchronously; the VI may remain cached in memory temporarily. [NI: Closing References](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)
- NI recommends `All VIs in Memory` to distinguish whether a VI remains loaded after Close. [NI: Closing References](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)

A Windows process-handle count is not documented by NI as a one-to-one counter of VI Server refnums. Therefore `+1 OS handle/run` does not prove that the top-level VI reference wire missed `Close Reference`.

Also, ordinary load caching is a weak explanation for strictly linear growth. Caching should tend to plateau once the same VI and dependencies remain loaded; continued one-per-run growth looks more like an unreleased per-call resource, deferred cleanup that never catches up, or instrumentation/COM-side handle growth.

Run this cheapest matrix in one fresh LabVIEW session, using the same main target:

| Test | Purpose |
|---|---|
| 50횞 minimal open-main ??close, no child properties | Baseline Open/Close and load-cache behavior |
| 50횞 `OpReportAll_v0` | Exercises target/object traversal without `SubVIs[]` |
| 50횞 `OpSubVIs_v0` on scratch | Existing low-growth control |
| 50횞 `OpSubVIs_v0` on main | Reproduce target-dependent growth |
| After each block: wait 30??0 seconds and recount | Separates deferred disposal from permanent growth |
| Record `All VIs in Memory` and process working set too | Separates retained VI loading from an OS-handle-only leak |

NI explicitly notes that closing a parent VI reference automatically closes its child-object references, provided child references are no longer used afterward. [NI: Closing References](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html) Thus zero `SubVIs[]` elements does not eliminate every reference-lifetime bug, but it does make leaked element references an implausible explanation for this particular run.

Most informative outcomes:

- Minimal Open/Close also gives ??1/run: isolate the opener/COM runner or LabVIEW disposal behavior.
- ReportAll and SubVIs grow, minimal does not: suspect diagram/object property references or the common op wrapper.
- Only SubVIs-on-main grows: suspect a target-dependent internal branch, error bypass, or property-node reference lifetime.
- Handle count falls after waiting while `All VIs in Memory` stabilizes: deferred disposal.
- Handle count grows while working set and loaded-VI set plateau: likely a non-VI OS/COM/UI handle leak.

NI identifies its Desktop Execution Trace Toolkit as the supported tool for locating reference leaks if the cheap differential test implicates LabVIEW code. [NI: Investigating Memory Growth](https://www.ni.com/en/support/documentation/supplemental/16/investigating-memory-growth-issues-in-labview-code-modules-calle.html)

## 4. T6: index 2 = 999

Yes?봠onditionally. If index 2 is the supposed diagram selector but actually feeds only the donor?셲 top-level `Nodes[] ??Index Array` chain, then T6 is explained by the same donor defect. The op still queries `SubVIs[]` from diagram 0, so the value `999` is irrelevant to the returned rows.

However, T6 currently proves only ??99 does not affect the result.??It does not independently prove why. Make the rebuilt v1 test stronger:

- Valid diagram 43 ??six expected calls, including UID 5058.
- Valid diagram 1 ??its independently known count.
- Diagram 0 ??zero.
- Diagram 9999 ??nonzero error, not merely zero rows.

The last assertion is essential. An out-of-range index conventionally produces an invalid/default reference downstream only if its error/ref validity is actually observed; empty output plus no propagated error remains compatible with another disconnected error chain or default-array path.

Bottom line: proceed with `OpNetInfo_v1` as donor, but make ?쐇nvalid diagram index must error??a release criterion. Before accepting the per-run purge protocol, perform the UID/class/owner/delete/report test on the creator copy; it should reveal whether deletion is targeting the wrong object or whether the creator is simply being recreated.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
