# Card 137-P3 facts (offline, 2026-10-02; no tools/*.py edited, no LabVIEW). Inputs: plan v4 a30f7700, graph p3b2b 50595c62
## 1. v5 = v4 + explicit #10170 loop-input tunnels for the crossings that really cross #10170 (2, not 3)
- Output `tools/bench/plan_ring_p4_v5.json` md5 **91f6476e269afd2d0c54a3e0cc72f2d1**, written by scratch
  `tools/bench/prep_c137_p3_mkv5.py` (json.dump indent=1 as `tools/stagesim.py:2409-2410`); log `tools/bench/prep_c137_p3_mkv5.log`.
- Form copied from v3's pool crossing `plan_ring_p4_v4.json:1069-1095`: tunnel `p4_t_pool` (loop 10170, body 23166,
  parent 686, dir in, as TP1) -> wire src -> `new:TP1.outer` (`p4_x_pool`) -> wire `new:TP1.inner` -> dst (`p4_w_pool_in`).
- **p4_x_n2_out is NOT a #10170 crossing** (`prep_c137_p3_mkv5.log:5-6`): src `new:IAN1.element`, IAN1 created on
  `new:FS4.f0` (`plan_ring_p4_v4.json:648-652`), dst `new:EQ2.y`, EQ2 on 23166 (`:678-682`); FS4 sits on 23166 (`:622-628`).
  It crosses the plan-made FS4 frame border (frame -> enclosing body exit), and `op_tunnel` models only loops/cases
  (`tools/stagesim.py:1224-1238`), so a #10170 loop tunnel does not apply. Left UNCHANGED. The v3 meta grouped it with
  the other two by DIAGRAM ("connect_term_uid @ base While #10170 body 23166", `plan_ring_p4_v3_meta.json:815-826`).
- Diff v4 -> v5 (`prep_c137_p3_mkv5.log:13-24`): 167 actions (v4 163); 161 unchanged; top-level keys unchanged
  (`stage` still `ring_p4_v3`, as in v4):
| v5 # | action id | change |
|---|---|---|
| 102 | p4_t_fd | INSERT tunnel loop 10170 body 23166 parent 686 dir in as TFD1 |
| 103 | p4_x_fd | dst `{uid 10068, term y}` -> `new:TFD1.outer`; why -> "ROUTE branch" (src t8936 '# FD points' unchanged) |
| 104 | p4_rle_x_fd | unchanged (of p4_x_fd) |
| 105 | p4_w_fd_in | INSERT wire `new:TFD1.inner` -> `{uid 10068, term y}` |
| 106 | p4_t_dt | INSERT tunnel loop 10170 body 23166 parent 686 dir in as TDT1 |
| 107 | p4_x_dt | dst `{uid 29240, term y}` -> `new:TDT1.outer`; why -> "ROUTE branch" (src t28844 '# DT points' unchanged) |
| 108 | p4_rle_x_dt | unchanged (of p4_x_dt) |
| 109 | p4_w_dt_in | INSERT wire `new:TDT1.inner` -> `{uid 29240, term y}` |
- Inner wire placed AFTER the crossing's RLE so each (wire, RLE) pair stays adjacent; the pool precedent has no RLE.

## 2. Per-build-step counts (v3 meta cut, per-action `step` of `plan_ring_p4_v3_meta.json`; `prep_c137_p3_mkv5.log:26`)
- v4 {1:33, 2:35, 3:39, 4:36, 5:20}; **v5 {1:33, 2:35, 3:43, 4:36, 5:20} - step 3 = 43 > 40** (both crossings are
  step 3 / unit U12 / session 3.3, `plan_ring_p4_v3_meta.json:2078-2111`). Gate FAIL `prep_c137_p3_mkv5.log:27`.
- Arithmetic only (not applied): dropping the 2 RLEs gives step 3 = 41; a unit-boundary re-cut U10+U11 | U12+U13+U14A+U14B |
  rest gives 26 | 40 | 33 from the meta session counts (`plan_ring_p4_v3_meta.json:273-421`, 3.3 = 13 + 4).

## 3. stagesim replay of v5 on graph_ring_p3b2b_20261002_133824.json (`tools/bench/prep_c137_p3_sim.log`)
- Command: `py -u tools/stagesim.py simulate tools/bench/plan_ring_p4_v5.json <graph> --out-root tools/bench/sim/ring_p4_v5
  --plan-out tools/bench/sim/ring_p4_v5`; `BGRUN END rc=1 after 106s` (`:110`); re-written plan
  `tools/bench/sim/ring_p4_v5/plan_ring_p4_v3.json` md5 157255e81c88e1a2ecfa9e2346b9fcbe (`:109`).
- BASE-FLIPS 6 on [9503, 10177, 29777] (`:3`); steps 1-101 as v4 (cdiff 16 / 18 at 98 / 20 at 99-101, `:100-104`).
- **Step 102 `tunnel` p4_t_fd ok** (opmodel tunnel.json, `:105`); **step 103 `wire` p4_x_fd ok** (connect_from_wire, `:106`)
  - the old stop (`stagesim.py:1366-1368`) is passed.
- **Last step reached 104. Stop: step 104 `wire_remove_loose_ends` id `p4_rle_x_fd`** (`:107-108`): "`of` 'p4_x_fd' names no
  earlier crossing row". Raised at `tools/stagesim.py:1950-1952`: `act_wires` is filled only by a FS-border connect
  (`:1865` in `_fs_border_wire`, `:1928`), so an RLE `of` a same-diagram branch has nothing to clean. final=False,
  end_cdiff_rows=None, candidates 18 (`:108`). Inference, not replayed: p4_rle_x_dt (v5 #108) has the same shape.

## 4. Route class of the new actions
- tunnel @ base While #10170 border: **UNMEASURED** - meta class `plan_ring_p4_v3_meta.json:697-705` (only p4_t_pool, measured_by
  "S-TUN scratch ... no census_samples.json record"), per-action `:1634-1643` level UNMEASURED. Now 3 actions in the class.
- branch @ base While #10170 border (p4_x_fd, p4_x_dt now): same class as p4_x_pool `:708`, `:1646-1656` level **UNMEASURED**.
- TFD1/TDT1 inner -> dst: as p4_w_pool_in `:1658-1667`, **UNMEASURED** ("this context never run").

OPEN: (a) p4_rle_x_fd / p4_rle_x_dt now follow a same-diagram branch, which stagesim does not give an RLE row - drop them
(pool form has none) or keep them for the real executor? (b) step 3 = 43 > 40 - which re-cut? (c) p4_x_n2_out (FS4 frame ->
body exit) needs its own route; not a #10170 tunnel.
