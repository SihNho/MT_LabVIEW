---
type: facts
status: current
date: 2026-10-02
tags: [card-138-6, donor, latch, case-tunnel, for-loop]
---
# Card 138-6 facts (LabVIEW, scratch only; run order 0,1,3,4,2; stopped in step 2)
Run `tools/bench/diag_c138_6_run.py` -> `tools/bench/diag_c138_6_run.log` (BGRUN END rc=1 after 617 s, 23 pass / 1 fail, :58-60).
Out JSON `tools/bench/diag_c138_6_out.json`. Bed md5 395118775a52bc90073f4449b99f899d before and after (:57); LabVIEW gone (:55).
## 0. Op hygiene records
- `hygiene_OpStopMode_v0.json` / `hygiene_OpStopModeB_v0.json` copied to `tools/bench/op_hygiene/OpStopMode_v0.json` /
  `OpStopModeB_v0.json`; `op_hygiene_check` None for both; `gscript.op(OpStopModeB_v0)` opened outside hygiene_probe (:5-7),
  and the step-4 read of Mechanical Action ran through it outside the probe (:24).
## 1. `claudeDev\DonorI32Max_v0.vi` md5 c0c8db654c98bb6833b8935dccefb3ee (:12)
- EMPTY_v0 + For loop; constant **uid 127** on the For's N: DigitalNumericConstant, value 2147483647, representation 3 = I32,
  text '2147483647', wired (w140) to N; exactly one new constant; ExecState 1; saved by script (:8-12). v8/v9 uid 0 sentinel -> 127.
## 3. Bed byte copy: delete_wire w25415, then #10465
- Before (offline graph, `diag_c138_6_q1.log`): w25415 = t9668 `x .and. y?` (#9647) -> t10469 (#10465 outer) + CT t25557
  `autofocus reseed flag (1.2 to 1.1)`. Live rows before: 3 (t10469 outer on w25415; t10467, t10468 inner, unwired) (:14-15).
- After delete: **#10465 still exists** (in Traverse('Tunnel')), **all 3 rows kept**, all wire 0 (t10469 now unwired); ExecState 0 (:16-18).
  => LabVIEW does NOT remove a Case tunnel left with no wire on any face; stagesim's fix (keep Tunnel, PD312(a)) matches.
- Error List after delete: **52 items** (bed expected file 51): 20 `wire has loose ends`, 19 `not connected to anything`, 3 BuildArray
  unwired, 3 undirected LoopTunnel, ... (:19). Which item is new was not separated (count read only).
## 4. Latch + local (scratch EMPTY_v0 + While + Boolean `Visible` #157)
- Mechanical Action written 4 -> read 4 (:24). A local READ of it WAS created (Local #134, err '', no refusal) (:26), then
  **ExecState 0** and Error List 2 items: `Boolean 'Visible': Boolean latch action is incompatible with local variables` + the
  unwired local (:27-28). => 4 is a latch action on this machine (measured), PD312(d)'s LATCH branch is the right one.
## 2. For-loop min group (stopped: FIRST UNEXPECTED RESULT = our script's bug, not LabVIEW)
- Created on scratch: FG For #43 (N = 20, body #114), FMN For #45 (body #203), Greater? #46 + Array Max & Min #229 (donors = a
  bed byte copy #11721/#10969, top-level), Select #254 (DonorErrSel_MergeErrors #529) + KMX #284 (DonorI32Max_v0 #127) in #203 (:29-33).
- read_terms lists NO terminal owned by a For loop (FG: [], :34) => the `i` terminal is not reachable that way; Num fell back to an
  I32 0 constant #305 in FG's body (:35-36).
- `connect_term_uid` GT.x (top) <- const in FG body: wire 325, Is Broken? False, err ''; LabVIEW created LoopTunnel #331 on FG
  (outer face t337, source, on the top diagram) (:38-40). IndexMode NOT read (stopped before).
- STOP: `gscript.create_control_nested(GT #46, y)` raised `ValueError: #46 is owned by TopLevelDiagram #3, not by a Diagram`
  (`tools/gscript.py:4149` `_node_term_row`; log :42-54). Not reached: control/indicator, TFN1/TFB1/TFS1, IndexMode read-back,
  Is Broken? per wire, ExecState, the functional runs. No scratch_verify record written.
OPEN: rerun step 2 alone with the control on a NESTED node (or Greater? inside a While/FS), or allow TopLevelDiagram in _node_term_row?
