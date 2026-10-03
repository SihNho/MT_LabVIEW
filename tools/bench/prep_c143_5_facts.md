---
type: facts
status: current
date: 2026-10-03
---
# Card 143-5 facts: Local address fixed, s03 REBASED (final=True); the pred script's RB gate FAILED on a '-1' inside a `why` text = RETURN

OFFLINE only; no LabVIEW. Card inputs md5-checked (all 7 match). stagexec/stagekit/stagesim/stage_prerun/gscript unchanged.

## Step 1 - Local term address fix (prep_c143_5_fix.py, log prep_c143_5_fix.log, 13/0)
- Every s03 action end on a BASE Local: exactly one, `p4_w_stop12` src #-20 'value'; base row #-21 'StopAll' (base_provisional.json).
  Rewritten to 'StopAll' (name read from the base row by script) in plan_ring_p4_s03v18.json AND its stage input plan_ring_p4_s03v18_in.json.
- Real graph eda9db40 Local rows named 'StopAll': term 23310 (source), 23276 (sink).
- s03-CREATED Locals also address 'value' while their create action declares 'BufDiff': p4_w_b_arr src 'new:LRB1.value',
  p4_w_b_out dst 'new:LWB1.value' - not rewritten (no base row; card scope). The re-simulation accepted them (rebase2 STEP lines ok).
- First version appended a note to action 1's `why`; stageplan/1 caps `why` at 400 chars -> rebase #1 refused
  (prep_c143_5_rebase.log: "$.actions[0].why: 545 chars > limit 400"; FAILURE 1 of 2). Note removed; `why` byte-identical to before.

## Step 2 - rebase (prep_c143_5_rebase2.log) PASS
- `REUSE-NOTED 23276 ('ParameterTerminal','Comparison')->('Terminal','Local')`; `REBIND 6 node(s), terminals by {'conn': 9, 'shape': 3}`,
  re-issued [23276, 29071, 29299]; FS-CARRY ran; `REBASED ... 20 uid(s) bound, base -> sim/ring_p4_s03v18_base_real_fsmap.json; completeness PASS;
  final=True failed=None`.
- Rebased plan md5 da66a030; action 1 src = {uid 6902, term 'StopAll'}; final True, open_rows_match True, 20 actions, 21 step files, 16 end cdiff rows.
- Base = augmented fsmap c4a11939 (vi md5 84cac487 = s02 file; fs_carried.real_graph eda9db40), NOT the graph file - so prep_c143_3_pred.py's
  RB2 (`md5(base file) == eda9db40`) could never pass; prep_c143_5_pred.py (copy) checks fs_carried.real_graph instead.
- plan_in = plan_ring_p4_s03v18_in.json md5 2c2c0edb.

## Step 3 - pred (prep_c143_5_pred.py, log prep_c143_5_pred.log) FAIL 0/1 = FAILURE 2 of 2 -> RETURN
- `GATE FAIL | RB plan rebased ... no negative uid left | neg ['-1']`. The '-1' is TEXT in action `p4_c_bufdiff`'s why
  (plan_ring_p4_s03v18.json:101 "DonorRingConst_v0 #130 I32[20] -1"); the gate (copied verbatim from prep_c143_3_pred.py) tokenises the whole
  action JSON, `why` included. Every other RB condition is true per prep_c143_5_probe.log.
- NOT done: X10 at 596.0, EL fixed-rule prediction, pred file (plan_ring_p4_s03v18_pred.json still e2e69c04 = 143-3's, keyed to an old plan md5),
  dry + prerun on both s03v18 recipes, --scratch-required exit code.
