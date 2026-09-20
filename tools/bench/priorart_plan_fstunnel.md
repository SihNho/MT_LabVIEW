# PLAN under review: `OpFsTunnelTerm_v0.vi` — the UID-addressed flat-sequence tunnel reader

Recipe: `tools/recipes/build_opfstunnelterm_v0.py` (written, not yet run). Cycle 20 step 2,
`docs/cycle20-plan.md:36-48`.

## What is built, exactly

    IN  : vi path + the UID of a FlatSequenceOuterTunnel
    OUT : OuterTerminal uid, InnerTerminal uid, and for the OUTER terminal its `Is Source?`, its
          CONNECTED WIRE uid (the hop that crosses the flat-sequence border) and its OWNER class + uid

Chain: `uid -> UID to GObject Reference.vi -> To More Specific Class(FlatSequenceOuterTunnel) ->
FlatSequenceOuterTunnel[Outer Terminal 3195B800 | Inner Terminal 3195B801] -> Terminal{Is Source? /
Connected Wire -> UID / Owner -> Class Name / Owner -> cast -> UID}`.

## Why it exists

`docs/vi-server-ids.json:142` records the gap in this project's own words: *"_NOT_YET_MEASURED: A LIVE READ of
any of these properties on a real instance. Attaching an id to a class proves membership, NOT that a runtime
reference casts to that class ... That read needs UID -> To More Specific Class(FlatSequence*Tunnel) -> property
node, i.e. a new op."* The cycle-19 backward walk from the startup ASI move stopped at hop 1 on
`FlatSequenceOuterTunnel uid 43605` (`tools/bench/probe_flatseq_walk_run2.log:82-83`) because no reader can
address that object.

## What is reused rather than rebuilt (the audit done before writing the recipe)

* property ids MEASURED, not re-derived: `3195B800 OuterTerminal`, `3195B801 InnerTerminal`
  (`tools/bench/probe_flatseq_outer.log:20-22`), `632A813 GObject.UID`, `634A000 Terminal.Connected Wire`,
  `6327806 Generic.Owner` (`docs/vi-server-ids.json:61-63,137-139`).
* DONOR `OpWireSource_v5.vi`: its BACK HALF (Terminal -> Is Source? / Connected Wire -> UID / Owner -> Class Name
  / Owner -> cast -> UID) is exactly this op's output set and is kept unchanged, with its existing indicator
  labels (`tools/bench/opwiresource_v5_labels.json`). Only the FRONT changes: `TMSC(Wire) -> Wire.Terms[] ->
  Index Array` is deleted and replaced by `TMSC(FlatSequenceOuterTunnel) -> OuterTerminal`.
* THE SEED for the cast: no class-specifier constant, no GUI, no NI example. The donor's two casts are already
  typed by refnum CONTROLS (`seedW`/`seedG` = "reference 2"/"reference 3"); the FSOT-typed control is made the
  way `tools/recipes/build_oploopcast_v0.py:201-202` makes a ForLoop-typed one — `create_control` on a
  FlatSequenceOuterTunnel property node's `reference` INPUT takes that terminal's type.
* gscript helpers unchanged: `node_terms_uid`, `report_all/uids/count`, `delete_object`,
  `remove_bad_wires_scripted`, `build_property`, `create_control`, `create_indicator`, `wire`, `wire_control`,
  `set_auto_error_handling`, `save`, `exec_state`, `tunnels`.
* the known-good fixture (`LoopTunnel #28343 -> Max Trans Pos.vi · 'Magnet position output'`,
  `docs/frame-loop-wire-graph.md:264`) is resolved with the EXISTING `gscript.tunnels()` + `OpWireSource_v5`,
  not with the new op — and is also used as a DELIBERATE BAD INPUT for it (a LoopTunnel must be refused by a
  FlatSequenceOuterTunnel cast).
* `archive/peer/` was searched first (cycle-20 Pre-decided 5). The only prior-art review of a tunnel reader is
  `2026-09-17-priorart-tunnelsource-onehop.md`; all five of its findings were accepted and disposed, and its
  closing paragraph names THIS gap as still open.

## Prediction contract (each line machine-checked in the recipe)

* I1 IDENTITY measured first, because getting it wrong invalidates the run: for BOTH the V6 working copy and the
  3StateClamping ORIGINAL, whether uid 28343 is a LoopTunnel, whether 43605 is a FlatSequenceOuterTunnel and
  whether 44036 is a SubVI (STATUS.md:59-61 records the census keyed to the ORIGINAL and the node/terminal cache
  keyed to the COPY).
* I2 the fixture resolves to `Max Trans Pos.vi · Magnet position output` through the existing ops.
* B1-B5 donor copy legal; front section deleted and every back-half `reference` sink BARE before anything is
  wired; exactly one new CONTROL from `create_control`; the FSOT property node ACCEPTS the cast output
  (ExecState 1 — if the seed did not type the cast this is where it shows); ExecState 1 before the single save
  and again cold in a fresh LabVIEW.
* L1 LIVE READ on uid 43605 returns a non-zero OuterTerminal uid, a connected wire and an owner, with no error.
* L2/L3 REFUSALS: uid 28343 (a LoopTunnel) and uid 999999 (nonexistent) are both refused.
* L4 the backward walk from d10 uid 44036 T[8] (wire 44089) advances PAST the border that stopped cycle 19; hop
  count recorded.
* I0/L5 both originals' md5 before AND after, handle count before and after, one scratch VI created and deleted
  in the same run, no motor, no serial port, no camera (cycle-20 Pre-decided 1).

## The question for this review

Has this reader — or this composition, or this seed trick applied to a flat-sequence class — already been built,
already been measured, or already FAILED here under another name? And is any fact cited above contradicted by
our own files?
