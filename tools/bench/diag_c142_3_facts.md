---
type: facts
status: current
date: 2026-10-03
tags: [card-142-3, ringpickslot, subvi, p4, desk-check, for_loop-junk]
---
# Card 142-3 facts: RingPickSlot_v0 build, escalation 1 of 142-1/142-2

Script `tools/bench/build_ringpickslot_v2.py` (119 lines, prediction contract in its docstring) -> `tools/bench/build_ringpickslot_v2.log`.
Hypothesis review of the 142-2 failure: `archive/peer/2026-10-03-c142-3-hyp-rps1.md` (ANSWERED, task `tools/bench/diag_c142_3_hyp_task.md`,
log `tools/bench/peer_c142_3_hyp_rps1.log`).

## Desk check BEFORE the run (v1 steps vs both earlier logs)
| v1 step (build_ringpickslot_v1.py) | evidence | v2 |
|---|---|---|
| bed copy, EMPTY_v0 copy, generator For, N const, k0, Greater? (:34-39) | v0.log:3-13, v1.log:3-13 PASS | unchanged (node index by `_node_index` instead of `TB.walk`, same Nodes[] order) |
| wire GT.y <- k0, Create Control on GT.x = `Num` (:40-41) | v1.log:10-13 (w180, panel #150, terminal #202) | unchanged + F4: GT.x pin type read, must be `Array1D<I32>` (review 2a) |
| scaffold deletes For + every Constant (:42) | v0.log:14-15 strict verify raised; v1.log:14-21 non-strict PASS | unchanged; array elements skipped (they went with their array in v1.log:16-19) |
| KMX2, helper Less?, Create Control on its x = `last`, helper deleted (:43-47) | v1.log:23-35 PASS (terminal #84 'x 2') | unchanged |
| `lo` = OWNER of the `last` row (:46) -> `one(owner_uid=3)` (:50) | v1.log:32,39 FAIL: owner of a control terminal row is the diagram #3 | **F1**: every terminal by its own uid (create_control's ControlTerminal uid; node rows registered once after creation), identity re-checked before each use |
| scaffold-end census: For / Constant / helper (:48-52) | never read (the dict raised first; review §1) | now read and gated (fatal) |
| FMN = second `for_loop` (:55) | never reached; `OpForLoop_v0` holds 3 `Create Constant.vi` on the target's top level (`probe_opforloop.log:8-16`) = v1.log:15-21's #50, #59+#75, #84+#100 | **F2**: its 5 new Constant entries read (class, owner, pos), gated (3 TopLevelDiagram + 2 ArrayConstant, none wired), deleted; v1's census "Constant 2" would have failed |
| label census expects 4 labels (:83-84) | a For node's label is 'For Loop' (`stage_d1_qrt_pool_scratch.log:52`) | **F3**: expects Array Max & Min, For Loop, Greater?, Less?, Select |
| FMN group wiring, indicators, labels, RLE, pane, save, runs (:56-105) | analogs: `diag_c139_3_run.log:34-58` (3 auto-index tunnels by connect_term_uid, IndexMode 1, ExecState 1, runs), `diag_c140_5_run2.log:18,23,27` (control-terminal source, top-level create_indicator, relabel), `replay_vis_76c_skeleton.log:60-62` (pane op + read) | unchanged; relabel stays the last edit before the census so no identity check runs on a renamed terminal (review Q1) |
| plan v17 external wires of the group (:1578-1689) | Num -> GT1.x + TFN1; last -> GT1.y; AMM1.min value -> TN1 (+ LT1.x); AMM1.min index -> TS1; LT1.x < y? -> OR1.x | no difference from brief_142-1.md (2 controls, 3 indicators) |

## The run: PASS 87 / 0 (`build_ringpickslot_v2.log:146-148`, BGRUN END rc=0 after 210 s)
- **Delivered `claudeDev\RingPickSlot_v0.vi` md5 `6fcf153f7b8fecda727f5dcf944faab9`**, ExecState 1 (:122), saved by COM (:128).
  FUNCTIONAL: 7/7 vectors == the Python reference (:130-136); a FRESH LabVIEW instance loaded the saved file (md5 unchanged,
  ExecState 1, :140) and vectors 2 and 5 gave the same outputs (:141-142).
- Census: node labels {#156 Greater?, #44 For Loop, #117 Array Max & Min, #198 Less?, #45 Select} (:116), prim gate PASS (:117);
  constants exactly {#52 KMX2 top -> LT.y, #103 KMX1 in the For body -> Select.f}, I32 2147483647 (:119-120); 3 LoopTunnels
  #235/#99/#199 IndexMode 1 (:121); 12 wires, Is Broken? False (:115); panel Num #150 / last #61 controls, min Num #196 / min slot
  #241 / found #265 indicators, all wired (:113). Types: Num = Array1D<I32> (:20), last = I32 (:55).
- Connector pane read back {11 Num, 10 last, 3 min Num, 2 min slot, 1 found, 0 and 4-9 free} (:128-129) = inputs left, outputs right.
- Handles: over the 7 runs 31,565 -> 31,570; fresh 2 runs 34,016 -> 34,017 (:137,:143). After restart 33,992, after build + runs
  31,568; peak working set 667.0 MB with the bed byte copy loaded as donor (:138). LabVIEW gone (:139,:144); bed copy deleted,
  bed + s01 md5 unchanged (:145).
- F2 MEASURED on both For loops: each `gscript.for_loop` call left {numeric at (-10,-8), ArrayConstant + numeric element at (0,0),
  ArrayConstant + Boolean element at (0,0)} on the top level, all unwired (:21, :57-58); deleting the 3 top-level ones left
  Constant == {KMX2} (:59-62). Correction to F2's wording: gscript.for_loop runs `OpForLoop_v1` (`tools/gscript.py:75`); the probe
  that showed the 3 `Create Constant.vi` was of v0 (`probe_opforloop.py:1`) - the junk itself is measured here on v1.
- uid reuse seen again: H's output terminal #71 -> junk numeric #71 (:33,:57); scaffold N const #127 -> junk Boolean element #127
  (:21,:57); helper Less? #64 -> wire GT.y <- last #64 (:30,:53). F1's identity re-check caught none (all PASS).
- LabVIEW labels a new indicator on `min index (indices)` as `min index(es)` (:101), renamed to `min slot`.

## Review disposition (for `archive/peer/2026-10-03-c142-3-hyp-rps1.md` `## What was done with it`; that path is outside this card's write flags)
Accepted and applied in v2 before its run: §1 (scaffold-end census was never observed) -> now read and gated, PASS (:50); 2a (Num
type unmeasured) -> F4 gates, Array1D<I32> / I32 PASS (:20,:55); 2b (junk split between for_loop and create_const_loop_term) ->
measured on the FMN call with no create_const_loop_term between: the 5-entry signature appears at for_loop (:57); 2c / Q3 (junk could
be wired; read before delete) -> class, owner, pos, wire read and gated before the delete (:57-58); Q1 (identity checks after the
relabel) -> none run after the relabel (v2.py:73). The suggested separate scratch run was not needed: v2 gated each of those reads.
