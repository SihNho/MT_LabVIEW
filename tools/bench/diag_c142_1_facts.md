---
type: facts
status: current
date: 2026-10-03
tags: [card-142-1, ringpickslot, subvi, p4, delete_object]
---
# Card 142-1 facts: RingPickSlot_v0 build, stopped at the scaffold delete (run 1 of the card)
Script `tools/bench/build_ringpickslot_v0.py` (prediction contract in its docstring) -> `tools/bench/build_ringpickslot_v0.log`
(BGRUN END rc=1 after 67 s, 9 pass / 1 fail). Out JSON `tools/bench/diag_c142_1_out.json`; record
`tools/bench/scratch_verify/ringpickslot_c142_1_092211.json` (status FAIL).

## What ran (log lines)
- bed + s01 md5 before PASS (:3); bed byte copy == bed (:4); `RingPickSlot_v0.vi` did not exist (:5).
- Scaffold for the 1-D I32 `Num` control (as diag_c140_5_run.py:40-44): generator For #43 (N const 20) with I32 0 const #138
  (DonorSRInit_v0 #248) in its body #114; Greater? #156 (bed copy donor #11721, class `Comparison`) on the top level.
- Wire GT.y <- k0 through the For border: w180, err '', broken False (:10-11).
- `create_control` on GT.x: panel object #150 label `x`, ControlTerminal #202, wired w212 (:12-13).
- `delete_object(ForLoop #43)`: ForLoop uid set lost exactly {43} (:14).
- Then the loop over `sorted(uids(Constant))` deleted #50 (the For's N constant) and `gscript.delete_object`'s own verify raised:
  **Constant uid set lost 2 objects, expected 1** (`gscript.py:2852-2854`; log :15, :29). The second one is presumably k0 #138
  inside the deleted For (still in the Constant traverse after the For delete) - UNMEASURED which uids vanished.
- Not reached: the `last` helper, FMN group, indicators, labels, pane, save, the 7 runs, the fresh-instance re-runs.

## End state (log :31-32)
- LabVIEW gone (taskkill + tasklist); scratch bed copy AND the partial `RingPickSlot_v0.vi` deleted (it was never saved);
  bed 39511877 and s01 dc61e193 md5 unchanged. Handles/peak MB not recorded (the read follows the runs).

## Prediction that failed
- Docstring: "no ForLoop/Constant left after the scaffold delete". Our script assumed deleting the For removes its body constant
  from the Constant traverse at once and deleted the remaining constants one by one with gscript's strict 1-gone verify.
