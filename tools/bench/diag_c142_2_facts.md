---
type: facts
status: current
date: 2026-10-03
tags: [card-142-2, ringpickslot, subvi, p4, delete_object, uid-reuse]
---
# Card 142-2 facts: RingPickSlot_v0 build (retry of 142-1), stopped at the scaffold end re-read
Script `tools/bench/build_ringpickslot_v1.py` (120 lines; = v0 + non-strict scaffold deletes + ONE end re-read) ->
`tools/bench/build_ringpickslot_v1.log` (BGRUN END rc=1 after 72 s, 16 pass / 1 fail). Out JSON `tools/bench/diag_c142_2_out.json`;
record `tools/bench/scratch_verify/ringpickslot_c142_2_092822.json` (FAIL).

## The 142-1 fault is gone
- Scaffold deletes ran without a raise (log :14-21). Constant traverse after the For delete held 7 uids [50,59,75,84,100,127,138]
  (C0); deleting #50 / #59 / #84 / #127 each removed MORE than one entry (#75, #100, #138 were already gone at their turn, :17,:19,:21);
  the traverse ended empty (:21). What uids 59..127 were is UNMEASURED (EMPTY_v0 + one For + 2 constants were all the script made).
- RBW 1 (1, 0) (:22). Helper scaffold built and wired fine (:23-30).

## New fault: our script, scaffold-end lookup of the `last` control (log :31-40)
- `lo = one(R, wire_uid=97, is_source=True)["owner_uid"]` resolved to **3 = the TopLevelDiagram** (the control terminal #84 is its
  own row; its owner is the diagram), so the end re-read `one(R, owner_uid=3, is_source=True)` matched BOTH control terminals
  [(202,'x',212), (84,'x 2',0)] -> gate FAIL (`T one terminal`, :39). Same line exists in v0 (build_ringpickslot_v0.py:55,57; never reached).
- The measured end state itself matches the prediction where read: GT.y #166 unwired, GT.x #169 wired 212, KMX2 source #51 unwired,
  `last` terminal #84 wire 0 (:36-39); helper Less? #64 deleted (Comparison traverse [64,156] before, :34). ForLoop/Constant sets
  not read (the gate dict raised before them).
- uid REUSE observed: #84 was a Constant in C0 and is the `last` ControlTerminal after (:15, :29); #64/#52 are new objects.

## End state (log :41-42)
- LabVIEW gone; scratch bed copy + unsaved `RingPickSlot_v0.vi` deleted; bed + s01 md5 unchanged. Not reached: FMN group,
  indicators, pane, save, the 7 runs, fresh re-runs; handles/peak MB not read.
