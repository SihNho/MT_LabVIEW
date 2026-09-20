# Failed prediction: a fully wired `Close Reference` inside a For Loop leaves the VI BROKEN (ExecState 0), four times, with every wire reading back GOOD

LabVIEW 2026 (26.3.1f1), driven headless over ActiveX/COM by our own VI-Scripting "op" VIs. We are restoring
reference hygiene to three scripting op VIs that traverse a target VI's objects and currently never close the
references they open. The repair adds a `Close Reference` primitive inside a For Loop that auto-indexes the
`References` array returned by `Traverse for GObjects.vi`.

Run log: `tools/bench/build_s0_closeref_v3.log` (`BGRUN END rc=1 after 601s`, 87 PASS / 5 FAIL).
Recipe: `tools/recipes/build_s0_closeref_v3.py`. Nothing was saved; all three targets were deleted as stubs.

## The prediction that failed

Gate **G5**: "after the wiring the repaired op is RUNNABLE (ExecState 1)". Measured **ExecState 0** in ALL FOUR
independent attempts (a scratch arm plus three different op VIs, each in its own freshly restarted LabVIEW):
`:50`, `:99`, `:158`, `:202`.

## What was measured, and it all looked right

Two different shapes were built, and both ended at ExecState 0:

**(a) New For Loop (3 of the 4 attempts, e.g. `OpReport_v3` -> `OpReport_v4`, `:74-:96`)**
- `Traverse for GObjects.vi`'s `References` output already drives wire **w188**; a For Loop was created and the
  copied `Close Reference` (#324) reparented into its body (`:74-:78`).
- The refnum wire was BRANCHED from w188 into `Close Reference.reference` by our wire-anchored writer: sink reads
  back **w636** (a different non-zero uid = a segmented crossing, which our rules count as survival), the op's own
  ORDERED `Wire.Is Broken?` readback = **False**, and a new **LoopTunnel #642 whose IndexMode reads 1 AS READ**,
  i.e. LabVIEW itself made it auto-indexing (`:80-:86`).
- Ordering: the panel `error out` net (w425, driven by the Traverse) was branched into
  `Close Reference.error in (no error)`: sink w672, `Is Broken? False`, new LoopTunnel #678, IndexMode 0 (`:93-:96`).
- Auto error handling was then switched off (`:97`). **ExecState 0** (`:98`).

**(b) EXISTING For Loop, no new structure at all (`OpReportAll_v0` -> `_v1`, `:178-:201`)**
- The op already has a working For Loop auto-indexing `References`; its body holds two chained Property nodes
  (#114 reads the auto-indexed element off LoopTunnel #511 on w421, its `Owner` output drives w548 into #115).
- `Close Reference` #738 was reparented into that body, its `reference` BRANCHED off w421: sink reads back
  **w421 itself, wire-count delta 0** (a true branch: one Wire object shared by both sinks), `Is Broken? False`
  (`:191-:194`).
- Its `error in` was wired from #115's `error out` (a fresh wire, both terminals previously unwired): both ends
  read **w865** (`:197-:199`).
- **ExecState 0** (`:201`). The same VI read ExecState **1** immediately before any change (`:168`).

So: a VI that was runnable, plus one primitive and two wires that every reader we own calls good, is broken.

## The hypothesis we are about to act on — attack it

**H**: the wires are not actually good. Our `Is Broken?` readback is taken inside the same op run that performs
`Terminal.Connect Wire`, ordered after the Invoke by an error-wire dependency, so it may report before LabVIEW has
run TYPE PROPAGATION. The wire carrying a **GObject reference** into `Close Reference.reference` is therefore the
suspect: `Close Reference` may not accept a GObject/Generic scripting reference at all, which would also explain
our own archived note that this exact sink "defeated four wiring attempts" and that the `Close Reference` was
deliberately REMOVED from the ancestor op (`archive/WORKLOG.md:84-86`).

Questions, in order of what would change our next build:
1. Is H the best explanation, or is there a better one for "ExecState 0 with every wire non-bare and `Is Broken?`
   False, in both a new loop and an existing one"?
2. Does LabVIEW's `Close Reference` function accept a **GObject / Generic VI-Server scripting reference** as its
   input (the class of reference `Traverse for GObjects.vi` returns), or does closing those require something
   else? Cite NI or the LabVIEW Wiki, not inference.
3. Is there any OTHER reason adding a `Close Reference` to these particular diagrams would break the VI — e.g.
   something about a copied primitive's terminals, about a loop whose only inputs are tunnels, or about the
   `error out` of a node also feeding a front-panel indicator?

## Already ruled out by measurement in this run (do not re-propose these)

- "The branch did not land / the array went whole into a scalar input": refuted — the created tunnel reads
  **IndexMode 1 AS READ** before anything set it, and in shape (b) no tunnel was involved at all (same-diagram
  branch, wire delta 0, sink reads the branched wire's own uid).
- "The body's Property nodes are parallel, so the ordering wire is wrong": refuted — measured chain
  (`tools/bench/s0_body_census.log:47,:49,:60`), and shape (b)'s error wire reads identical uids on both ends.
- "It is a mid-build transient": ExecState was read AFTER every wire was in place and after auto error handling
  was disabled, in four independent LabVIEW instances, with the same result each time.
- "It is the `error 2` memory blocker": no `error 2` appears anywhere in this run's 601 s.

## Constraints on any test you propose

Read-only or cheap: we cannot read LabVIEW's compiler error list (`VI.Get Errors` 452 is absent from the exported
ActiveX interface over our COM path), and we may not modify any original VI. We can create scratch copies, drop
nodes, wire by script, and read `ExecState`, `Wire.Is Broken?`, terminal names, tunnel IndexMode and node
positions. GUI clicking is allowed only where scripting is verifiably unreachable.
