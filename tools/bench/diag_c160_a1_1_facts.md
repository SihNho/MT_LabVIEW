---
type: facts
status: current
date: 2026-10-10
card: 160-a1-1
---
# 160-a1-1: termless-Wire delete branch in stagesim + stagexec (PD390(a)(b)); offline, no LabVIEW
## Diffs (two tools only)
- `tools/stagesim.py:621-625` new shared `termless_wire(st, w)`: True only if `w` is in the CURRENT `st["objs"]` as class 'Wire' AND `wire_rows` is empty.
- `tools/stagesim.py:1432-1434` (op_delete_wire): `if not rows and termless_wire(st, w)` -> remove that one Wire object from `st["objs"]`, effect
  `{wire, n_terminals 0, auto_removed_tunnels [], termless_wire_object True}`. No terminal row, pair or other wire touched. All other paths unchanged.
- `tools/stagexec.py:2846-2850` (Executor.execute 'delete_wire'): `if not ts and SS.termless_wire(prev, w)` -> live uid = bind obj (identity for base),
  ExecStop if a live row carries that wire, else `be.delete_wire(lw, op, plan_wire=w)` = LVBackend.delete_wire -> `stagekit.Stage.delete_wire` (stagekit.py:687,
  found==1 postcondition). compile_plan unchanged (stagexec.py:905 already emits {'kind':'delete_wire'}). No remove_bad_wires.
## Self-test `selftest_c160_delwire.py` -> `selftest_c160_delwire.log:26-51` RESULT 12/0 (graph 7ac24924 = 94ffff94 read)
- T1 log:30-37: w10394 Wire 0 rows; sim effect termless_wire_object True; terminal rows identical, `wire_end_pairs` identical, `sim_census_snapshot`
  diff == {10394: 'Wire'}; compile -> [{'kind':'delete_wire','acts':[1]}]; executor -> Stage.delete_wire calls [(10394, 'stagexec')]; dry SimBackend removes the
  object, rows unchanged; pre-edit tools refuse ('wire 10394 is not in the current graph' / 'its 0 terminals sit on 0 live wires []').
- T2 log:38-39: absent 99999999 refused, sim + executor messages == pre-edit; no Stage call.
- T3 log:40-41: SubVI 26582 (owns 10 rows, carries 0) refused, == pre-edit; termless_wire False.
- T4 log:42-43: Wire 32594 (2 rows): effect + full state == pre-edit stagesim (eb99c6ba copy); executor call [(32594,'stagexec')] == pre-edit stagexec (7a712ccb copy).
- T5 log:44-45: second delete of w10394 after T1's state: refused (sim + executor), no Stage call; w10394 still in the base objs.
- Pre-edit copies kept as `selftest_c160_delwire_stagesim_eb99c6ba.txt` / `_stagexec_7a712ccb.txt` (written by `diag_c160_a1_1_probe.py`, log PASS 3/0);
  imported from %TEMP%, temp dir removed (log:46).
## Suites on the new bytes (counts == last pass)
- `selftest_c159_cen2_ends_c160.log:16` PASS 8/0 (last `selftest_c159_cen2_ends_final.log:50` 8/0); no pin change (it pins no stagesim/stagexec).
- `selftest_c158_runcheck_c160.log:23` PASS 10/0 (last `selftest_c158_runcheck.log:23` 10/0); stagesim pin re-pinned 160-a1-1 from eb99c6ba to a3261b56 (:24, :152).
- `selftest_c158_wire0face_c160.log:40` PASS 24/0 (last `selftest_c158_wire0face.log:81` 24/0); stagesim pin re-pinned from eb99c6ba to a3261b56 (:29, :260).
## md5
- stagesim eb99c6ba -> a3261b56216d83f975d730dcaf3ad47b; stagexec 7a712ccb -> c4a6e0b6e36d5c0a21cfab9e223be1fb.
- Unchanged: stagekit ac3a8f57, stage_prerun 7605116f, addrcheck 207beb0d, vigraph a7eb58c7. VIs 94ffff94 / eb1d0f31 / 2482fe7b / 7f2582ae unchanged
  (selftest_c160_delwire.log:46 V1, selftest_c159_cen2_ends_c160.log V1). tools/hooks: no edit by this card; `git status` shows only
  tools/hooks/material_marker.log (hook-written log).
OPEN: stagexec.py:32 module docstring still says delete_wire is resolved by its terminals only; not edited (out of the named branch).
