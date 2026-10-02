---
type: facts
status: current
date: 2026-10-02
tags: [card-139-5, ring-p4, v13, stop-route, offline]
---
# Card 139-5 facts (offline only; LabVIEW NOT opened; returned FAIL at the first unexpected gate, maker pass MS)
## 1. Tool edit: stop onto a BASE While's cond (pass 1) — only the stop-route branch changed (git diff: stagexec +25/-1, stagesim +6/-1)
- `stagexec.base_cond` (`tools/stagexec.py:189-201`): `{"uid": <loop uid>, "term": "cond"}` -> int uid; anything beside uid/term -> ExecStop.
- `check_symbols` (`:479-485`): refuses a malformed base cond and a base cond used as a wire SOURCE. `compile_plan` (`:737-738`): -> kind `stop`, loop = uid.
- `stagesim.cond_target` (`tools/stagesim.py:1364-1372`): accepts the dict form with an int / digit uid; WhileLoop class, cond_row, already-wired and
  source-on-body rules unchanged. Executor/LVBackend/dry `stop` untouched (they already take an int loop uid).
- Self-test `selftest_c139_5_stop.py` -> `selftest_c139_5_stop.log:18-33` PASS 13/0 (C1 plan-made form unchanged, C2/C2b base form, C3/C4 refusals,
  S0-S5 simulator incl. already-wired, non-While, source off-body, plan-made form unchanged). Run 1 (`:3-15`) was the test's own gate()
  argument order + a missing `owners` map in the toy graph; fixed in the test only.
## 2. The cond's existing incoming wire (pass 2) — `prep_c139_5_probe.log` (run 2 PASS 4/0)
- #10170's one body = #23166 (graph owners); its cond row = t23246 (raw graph lists it twice, deduped on load as stagesim does), wire **w23310**,
  source **#10171 'x = y?'** (Comparison, S2 scaffold). Removed by v12 action **1 `p4_dw_23310`** (delete_wire) and #10171 by action 2
  `p4_do_10171`, both before `p4_w_stop12` (action 9). #10170 is in the loops table (index 1).
## 3. Older self-tests (pass 3) — counts == the c138_1 baseline
- `c125_1_offline_measure_c139_5.log:5-16` PASS 6/0: c134_1_dry 11, case_frame_c124 29, census_hookin_c123 12, fs_c126 13, stagexec selftest 136
  (== `c125_1_offline_measure_c138_1.log`). stagesim selftest 105/0, fsexit_c138_1 14/0 (`selftest_c139_5_stop.log:29-32`).
## 4. v13 (pass 4) — `prep_c139_5_mkv13.log` (rc=1 after 263 s, 7 pass / 1 fail)
- v13 = v12 with ONLY `p4_w_stop12.dst` -> `{uid 10170, term cond}` (`:4`). Replay END 186 steps, per-step cdiff == v12 at every id,
  end cdiff 24 == v12, fs_routes ids == v12 (`:363-364`); sim step 9: cond_of 10170, dst t23246, new wire (`:362`).
- compile 167 == v12; route compare differs ONLY on (p4_w_stop12,): connect -> stop loop 10170 (`:365-366`). Route check v12 FAIL [p4_w_stop12]
  -> v13 **PASS, 0 UNROUTABLE**, row 9 route `stop` (`:367-369`).
- **FAIL MS (`:8`)**: 28 v13 ids have NO step in `plan_ring_p4_v3_meta.json` (the v10/v11 additions: StopAll x4, For-min group, fd/dt tunnels,
  rbR x8). Prior makers assign them by inheritance in code, not in the meta file (`prep_c139_p2_mkv11.py:164-174`); this maker did not copy that,
  so the step-1 cut, its plan/pred, and the recipe dry/prerun/X10 were NOT run. `plan_ring_p4_v13_meta.json` = v3 meta + the PD316(a) re-cut only.
## 5. Written, not run: `tools/recipes/stage_d1_ring_p4s1.py` (91 lines, P3b-2a pattern; FR gate generalised to the simulated end's frames; TD
gate excludes rows the plan deletes). Needs `plan_ring_p4s1.json` + `_pred.json` (not produced). Step-1 open_rows: v12 itself is not final
(`plan_ring_p4_v12.json:2484,2581` open_rows_match false; 11 declared pairs vs 24 end cdiff rows) — a carried open_rows will not make step 1 FINAL.
