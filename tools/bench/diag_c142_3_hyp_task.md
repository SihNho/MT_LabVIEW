# Hypothesis review for card 142-3 (failed prediction of build_ringpickslot_v1.py / build_ringpickslot_v1.log)

ATTACK the diagnosis and the desk-check findings below. They drive the next LabVIEW build (a `_v2` script).

## What failed
Card 142-2 ran `tools/bench/build_ringpickslot_v1.py` -> `tools/bench/build_ringpickslot_v1.log` (16 pass / 1 fail).
It builds `claudeDev\RingPickSlot_v0.vi` by VI Scripting on a copy of `claudeDev\EMPTY_v0.vi`: a 1-D I32 control `Num`
made by a scaffold (generator For loop -> Greater?.y, then Create Control on Greater?.x, scaffold deleted), a scalar I32
control `last` made by a helper Less? whose y holds an I32 constant (Create Control on its x, helper deleted), then a For
loop with Select inside, Array Max & Min, Less?, three indicators. The run stopped at the scaffold-end re-read:
`GATE FAIL T one terminal {'owner_uid': 3, 'is_source': True} [(202, 'x', 212), (84, 'x 2', 0)]` (log :39).

## Claim A (the failure is our script, not LabVIEW)
`build_ringpickslot_v1.py:46` takes `lo = one(R, wire_uid=<H.x wire>, is_source=True)["owner_uid"]`. For a
ControlTerminal the terminal table row (`tools/allterms.py` read_terms) has term_uid = the ControlTerminal's own uid and
owner_uid = the DIAGRAM (#3, TopLevelDiagram) - log :32 `(84, 'x 2', 97)`, and `tools/bench/build_ringpickslot_v1.log:12`
ControlTerminal #202 owner 'TopLevelDiagram'. So `one(R, owner_uid=3, is_source=True)` (v1.py:50) matches every top-level
control terminal. The measured end state otherwise matched the prediction (log :36-39: GT.y #166 wire 0, GT.x #169 wire
212, KMX2 source #51 wire 0, `last` #84 wire 0).

## Claim B (desk-check of the part v1 never reached)
- B1. Every `gscript.for_loop()` call leaves THREE unwired constants on the target's TOP-LEVEL diagram: one numeric
  constant and two array constants, each array with one element = 5 entries of the 'Constant' traverse. Reason:
  `OpForLoop_v0.vi` contains three erdosmiller `Create Constant.vi` calls wired to the target's top-level diagram
  (`tools/bench/probe_opforloop.log:8,12-13,16`). This explains the five unidentified constants of v1
  (`build_ringpickslot_v1.log:15-21`: Constant traverse [50,59,75,84,100,127,138]; deleting #59 also removed #75,
  deleting #84 also removed #100; #138 was inside the deleted For; #127 = the For's N constant, the same uid the same op
  sequence gave in `tools/bench/diag_c138_6_facts.md:15`). Consequence: v1's SECOND for_loop (the For with the Select,
  v1.py:55) would have left 5 junk entries in the saved VI and failed its census gate "Constant 2" (v1.py:81-82).
- B2. `node_labels` reads a For loop node's label as 'For Loop' (`tools/bench/stage_d1_qrt_pool_scratch.log:52`), so
  v1's label census (v1.py:83-84, expects exactly Array Max & Min / Greater? / Less? / Select) would have failed too.
- B3. The junk numeric constant is NOT wired to the new For's N: `docs/toolkit-capabilities.md:36` (an EMPTY For from
  the same op has its N unwired; ExecState 0 -> 1 only after N is wired by script).

## The v2 plan these claims lead to
(1) every terminal addressed by its OWN term uid: each node's rows read once after creation ({name: term_uid}), control /
indicator terminals by the uid create_control / create_indicator return, each use re-checked (uid -> owner, name,
direction) in the latest terminal-table read; (2) right after the second for_loop: read the new Constant entries
(predict exactly 5: three owned by TopLevelDiagram, two owned by ArrayConstant), gate that none of their terminals is
wired, delete them, re-read: Constant set == {the one I32 constant made before}; (3) label census expects Array Max & Min,
For Loop, Greater?, Less?, Select. All other steps as v1 (scaffold deletes as measured in v1 log :14-35).

## Questions
1. Is Claim A the whole story, or could the next steps (GT.y <- the UNWIRED `last` control terminal by
   `gscript.connect_term_uid`, `tools/gscript.py:5130`) fail for a reason the claim hides?
2. Is B1 right - could the five constants come from another op used again later (create_const_loop_term,
   OpPrimCopyNested_v0 = `gscript.create_primitive_nested`, `create_control` / `create_indicator`, `connect_term_uid`)?
3. Could deleting objects whose class we only infer remove something the subVI needs; what read before the delete
   would separate "junk from Create Constant.vi" from "a constant LabVIEW made for a terminal"?
