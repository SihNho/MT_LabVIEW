---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, plan]
---

# opsubvis-v0-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (128s)
- **why asked:** plan review before an expensive build (work cycle step 1): the cast-free identity ladder had just compiled (probe_castfree5.log) and was about to become an array-returning op modelled on OpReportAll_v0.
- **verdict:** ACTED ON before the build ran. Taken: (b) net_map check that the inner SubVI node carries exactly VIName/VIPath/UID before wiring the loop; (d) the SubVIs[] node's own `error out` exposed as an indicator (create_indicator on terminal 3) so the test can tell "valid empty" (T3) from "invalid index" (T3b = diagram 9999 must error); (e) donor md5 compared before/after; tunnel indices by uid census instead of fixed 1..3; T2 is exact set equality on diagram 43 (not subset), plus UID uniqueness and a 1-subVI diagram (T2b); T4 = 30/50 runs with samples every 10 and a fitted slope, not a 20-run endpoint. Not taken: deleting the vestigial index 2/3 chain (kept for v0; T6 runs it with index 2 = 999 on a valid diagram and requires correct arrays + no dialog — if T6 fails, v1 deletes the chain). (a) non-recursive SubVIs[] is by design here: the op is called per diagram with the 170-diagram tree from tools/bench/diagram_tree_main.json.

## Question

ATTACK this build plan before it runs (refute, do not confirm). GOAL: OpSubVIs_v0.vi, an op VI that takes 'vi path' + 'index' (diagram index) and returns ARRAYS of every subVI call on that diagram: VI Name[], VI Path[], UID[] - the cast-free identity route proven to COMPILE today (tools/bench/probe_castfree5.log: AbstractDiagram.SubVIs[] 6375802 -> For loop -> SubVI-class property node VI Name 635E401 / VI Path 635E403 = ExecState 1, terminal names read off the machine: 'SubVIs[]','VIName','VIPath'). RECIPE (tools/recipes/build_opsubvis_v0.py, modelled on tools/recipes/build_opreportall_v1.py which built OpReportAll_v0 the same way and is functionally verified): 1) copy donor OpNodeInfo_v0.vi (Open VI Reference -> Traverse Diagram by 'index' -> Index Array -> Nodes[] property node -> ... per-node/per-terminal readers) to OpSubVIs_v0.vi, open_panel; 2) net_map diagram 0 to find the Nodes[]-node uid; 3) build_property AbstractDiagram [SubVIs[]] and wire Nodes[]-node 'reference out' -> its 'reference' (ExecState 0->1 proven); 4) g.for_loop; find body diagram (owner contains 'For'); 5) build_property inside the body, class 'VI Server:SubVI', items [VI Name 635E401, VI Path 635E403, GObject.UID 632A813] (superclass property on a SubVI-class node - OpReportAll's GObject node carries Generic.Class Name the same way; fallback if the creator returns 1077: a second GObject-class node fed from the SubVI node's 'reference out'); 6) wire SubVIs[]-node 'SubVIs[]' -> inner node 'reference' crossing the loop boundary (auto-indexed input tunnel, N from the array, as OpReportAll step 6); 7) exit_loop for ['VIName','VIPath','UID'] -> 3 output tunnels, set_index_mode 1, tunnel_indicator each (LabVIEW names them 'Array','Array 2','Array 3'; discovered by fp_labels diff, saved to tools/bench/opsubvis_labels.json); 8) set_auto_error_handling(False); save only if ExecState 1. The old per-node chain (index 2/index 3 readers) is LEFT IN PLACE as vestigial. FUNCTIONAL TEST after the build: run on a scratch copy of OpFPLabels_v0 (2 SubVI nodes per class census) - expect 2 non-empty names and UID set == report_all(scratch,'SubVI') uids; then main VI diagram 43 (frame loop) - UIDs must be a subset of report_all(main,'SubVI') and the tracking kernel call uid 5058 must be present; then a 20-run LabVIEW handle-count audit (rule: flat +-100; OpReportAll never closes its element refs either). ATTACK POINTS WANTED: (a) does AbstractDiagram.SubVIs[] return SubVI-typed refs that a For loop auto-indexes without a cast, and does it include subVI nodes nested in structures on that diagram or only direct children? (b) does a SubVI-class property node accept GObject.UID? (c) reference leaks: SubVIs[] hands out N refs per run - does LabVIEW close them when the op VI finishes, or do they accumulate (handle-count evidence expected)? (d) error semantics: an empty diagram (0 subVIs) -> empty arrays or error 1055? (e) anything in this plan that would silently change OpNodeInfo_v0 (the donor is copied first, never opened) or leave the vestigial index 2/3 chain popping a dialog when auto error handling is off. Give a concrete failure scenario and the cheapest discriminating test for each. Sources: NI VI Scripting property docs for AbstractDiagram.SubVIs[] and SubVI class if you can find them.

## Answer

Verdict: do not run this plan unchanged. The cast-free identity path is promising, but the evidence does not yet prove the exact loop design, recursive coverage, UID row, error behavior, or reference hygiene. There is also a procedural blocker: [build_opsubvis_v0.py](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_opsubvis_v0.py) does not currently exist at the stated path, so the actual implementation cannot be reviewed before execution.

### (a) `SubVIs[]` typing, auto-indexing, and scope

The probe proves:

`AbstractDiagram.SubVIs[] ??Index Array ??SubVI.VIName/VIPath`

compiles. It does not prove the array can cross the proposed For-loop boundary with auto-indexing. That is likely, because LabVIEW enables auto-indexing by default when an array is wired into a For Loop, but it remains an untested construction here. [NI: Auto-Indexing Tunnels](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG)

More importantly, `SubVIs[]` is not recursive. A recent NI Community answer states that a diagram?셲 `SubVIs[]` returns only subVIs at that diagram level, excluding calls inside nested structures. [NI Community: retrieving a VI?셲 SubVIs](https://forums.ni.com/t5/LabVIEW/Is-it-possible-to-retrieve-quot-This-VI-s-SubVIs-quot/m-p/4470892)

Concrete failure: diagram 0 contains a Case Structure whose active subdiagram contains two subVI calls. Querying diagram 0 returns neither call. The resulting arrays can be internally correct while violating the goal?셲 phrase ?쐃very subVI call on that diagram.??
Cheapest discriminating test:

- Make one scratch VI containing one direct subVI and one subVI inside a one-frame structure.
- Query the top-level diagram: expect only the direct UID.
- Query the structure?셲 child diagram: expect only the nested UID.
- Compare exact ordered UID arrays with `report_all(..., "SubVI")` grouped by immediate owner/diagram, not merely with a global subset.

Also test the final For-loop construction on a two-element input. The existing scalar Index Array proof is insufficient.

### (b) `SubVI` property node carrying `GObject.UID`

This is plausible but unproven. VI Server subclasses inherit superclass properties; NI describes lower-level classes as inheriting properties and methods from higher-level classes. [NI: VI Server class inheritance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YHhtCAG&l=en-US) `SubVI` sits beneath `Node`/`GObject`, and NI documents `UID` on `GObject`. [NI: GObject.UID](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/uid.html)

However, inheritance does not prove that this particular property-node creator accepts a superclass member ID in the same multi-item creation request. The existing control is not equivalent:

- `OpReportAll` proves `GObject + Generic` rows.
- `probe_castfree5.log` proves `SubVI + VIName/VIPath`.
- Neither proves `SubVI + GObject.UID` on one node.

Concrete failure: `build_property("VI Server:SubVI", [...UID...])` returns creator error 1077, or attaches only VIName/VIPath and silently omits UID. The build might remain executable yet produce only two meaningful arrays.

Cheapest discriminating test:

1. On a disposable copy, create only a `VI Server:SubVI` node with `VIName`, `VIPath`, and `UID`.
2. Immediately inspect its terminal names and creator error.
3. Require exactly `VIName`, `VIPath`, and `UID`, then wire one known scalar SubVI ref and require `ExecState == 1`.
4. Only after that build the loop.

If the same-node request fails, the proposed fallback is reasonable, but it too requires a compile test: `SubVI reference out ??GObject.UID` is a superclass coercion not established by the failed `GObject.Position ??second GObject.UID` control in `probe_castfree5.log`.

### (c) Reference leaks

The proposed ?쏰pReportAll does it??justification is too weak. NI explicitly warns that repeated Property Node calls may allocate new reference handles and says to close property-returned references when uncertain. [NI: Closing References in LabVIEW](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)

NI also says LabVIEW automatically closes references when the top-level VI that opened them goes idle, and a VI launched through Run VI is a separate top-level VI. That suggests these child references may be reclaimed after every op run?봟ut NI simultaneously recommends explicit closing because allocation behavior of property-returned references is not guaranteed. [NI: Closing References in LabVIEW](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)

Concrete failure: every run obtains N fresh child refnums; the op remains loaded or cleanup is deferred, producing monotonic handle/private-byte growth despite correct array results.

Cheapest discriminating test:

- Use a target with many direct calls, not the two-node scratch.
- Warm up five runs first.
- Record process handle count and private bytes after every run for at least 100 runs, then wait until the op is idle and sample again.
- Repeat with an explicit-close experimental variant.
- Fail the design if the unclosed version has a statistically monotonic slope that the close variant lacks.

A 20-run 짹100-handle rule can miss a small per-run leak and confound normal handle noise. At minimum, report the fitted slope and final post-idle recovery, not just endpoint delta.

### (d) Empty diagram semantics

The likely result is three empty arrays, not error 1055. An empty auto-indexed array causes a For Loop to execute zero times, and auto-indexed outputs contain one element per executed iteration. [NI: Auto-Indexing Tunnels](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG) Older NI documentation also states that a For Loop given an empty auto-indexed input executes zero times. [NI LabVIEW User Manual, ?쏡efault Data in Loops??(https://docs-be.ni.com/bundle/320999e/raw/resource/enus/320999e.pdf)

But disabling automatic error handling makes ?쐃mpty success??observationally indistinguishable from ?쏿n upstream property errored and outputs remained default-empty.??
Concrete failure: `SubVIs[]` receives an invalid diagram reference, raises 1055, automatic handling suppresses the dialog, and all three indicators still read as empty arrays. The test falsely passes.

Cheapest discriminating test:

- Before suppressing errors, temporarily expose the `SubVIs[]` node?셲 `error out`.
- Run one valid empty diagram and one intentionally out-of-range diagram index.
- Require valid empty = `status false` plus three empty arrays.
- Require invalid index = nonzero error.
- Do not accept array emptiness alone as success.

### (e) Donor safety and vestigial chain

A filesystem copy followed by opening only the destination should not write the donor. Still, protect this mechanically: record the donor?셲 hash and modification time before the build and compare afterward. Copying VIs can also create same-name/cross-link hazards when multiple copies are loaded; NI notes that LabVIEW resolves loaded VIs by name and can link to an already-loaded copy. [NI: Multiple LabVIEW versions and cross-linking](https://www.ni.com/en/support/documentation/supplemental/07/recommendations-when-using-multiple-versions-of-labview-and-labv.html)

The vestigial per-node chain is a real runtime hazard. It remains dataflow-live. An out-of-range Index Array returns default element data, which can become an invalid object reference; with automatic error handling enabled, NI says LabVIEW suspends execution and displays an error dialog. [NI: Execution properties and automatic error handling](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html)

Turning automatic handling off prevents the dialog but does not make the dead chain harmless: it can still generate errors, retain unnecessary work, and?봧f any error wire is shared?봯revent downstream nodes from executing.

Concrete failure: input `index` is valid as a diagram index but exceeds that diagram?셲 `Nodes[]` length. The old Index Array produces an invalid node reference; its Label/Style chain raises 1055. Depending on error wiring and when auto-error handling is persisted, the run either opens a modal dialog or silently returns default old outputs.

Cheapest discriminating test:

- Run the completed op on a valid diagram using a deliberately huge legacy node index.
- Require no visible dialog, `ExecState` returns to idle, and the three new arrays remain correct.
- Read an exposed error output from the vestigial chain if possible.
- Better: delete or fully disable the vestigial chain. Leaving knowingly error-generating executable code in an unattended op is unnecessary risk.

Additional build-plan defects:

- Do not trust fixed tunnel indices `1..3`. Identify new tunnel UIDs by before/after census, then map indicators from those UIDs.
- Do not trust previously saved `Array` labels until the exact three indicators are created in this exact donor copy. Discover them during this build, as `OpReportAll` did.
- `ExecState == 1` proves compilability, not that all three property rows attached or that the output arrays are aligned.
- The UID subset test on diagram 43 is too weak: missing calls still pass. Compare the exact ordered set of direct-child SubVI UIDs for diagram 43.
- Test duplicate call sites to the same VI. `VIName` and `VIPath` will duplicate; UID must remain unique. `VIName` is only a simple name for reentrant call sites, not a clone-qualified identity. [NI Community: qualified VI names from SubVI nodes](https://forums.ni.com/t5/LabVIEW/How-to-get-qualified-VI-name-clone-name-from-SubVI/td-p/3131131)

Minimum gate before the real build: materialize and review the missing recipe, prove the three-row SubVI property node, prove the actual auto-indexed loop on 0/1/2 elements, expose error status for valid-empty versus invalid-index, and test direct-versus-nested coverage explicitly.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
