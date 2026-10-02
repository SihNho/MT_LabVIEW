# Card 138-P1 facts (offline, 2026-10-02; no LabVIEW). Inputs v8 059b5296, graph p3b2b 50595c62 (mkv9.log:21-22)
Maker `tools/bench/prep_c138_p1_mkv9.py` -> `tools/bench/plan_ring_p4_v9.json` **b91cf4d7** + recipe notes
`tools/bench/plan_ring_p4_v9_recipe_gates.json` **d9d0f269**; log `tools/bench/prep_c138_p1_mkv9.log` run 3 (:19-425, 19/0).
Runs 1-2 stopped on the maker's own why text > 400 chars (:7, :16); shortened, no plan logic changed.
## 1. Diff by action id (v8 181 -> v9 182; 174 unchanged, identical and in v8 order, :29-43)
- ADDED #4 `p4_i_stopall` (before `p4_lr_stop12`). REMOVED none. No top-level key changed (goal kept).
- MODIFIED 7, keys only: `why` for p4_k_max, p4_k_max_found, p4_t_fnum, p4_t_fgt, p4_t_fsel; `label`+`terminals`+`why` for
  p4_lr_stop12 and p4_lr_stop_w1 (:32-41).
## 2. Pass 1: MAX donor (PD312(c))
- KMX1 (v9:454) and KMX2 (v9:474): const_donor `claudeDev\DonorI32Max_v0.vi`, uid **0 SENTINEL kept** (:44); whys say PENDING 138-6,
  bind the donor object's uid from 138-6's record before launch; KMX2's why records const_row REFUTED (diag_c137_7_types.log:218).
## 3. Pass 2: IndexMode gates (PD312(c), PD235(c) form)
- recipe_gates.json:9 / :21 / :33 = TI-TFN1 / TI-TFB1 / TI-TFS1: `be.index_mode_fix(R(<as>), True)` after Executor.run, pass
  `im == 1 and not e_`, fatal, before any save (form stage_d1_qrt_pool.py:46-47; LVBackend.index_mode_fix stagexec.py:2970-2979).
- Tunnel whys cite it (v9:1026, :1051, :1083). Not plan rows: stageplan/1 has no index-mode op (docs/protocol/stageplan.json:251-264).
## 4. Pass 3: stop route
- v8 did the NON-latch form: Locals of `stop (end)` itself, LRS2 in #10170 body 23166 (v8 action 4) -> cond t23246 (action 5), LRS1
  in W1.body (action 34) -> OR1.y -> W1.cond (actions 66-67). That is invalid for a latch Boolean (Mechanical Action 4,
  diag_c138_5_facts.md) => v9 takes PD298(e)'s LATCH branch, copied from plan_ring_p4_v3_latch_in.json:94-122,560-575.
- v9:95 `p4_i_stopall`: ControlTerminal indicator `StopAll` on diagram 639, `born_on` {642, 642} = CT `stop (end)` t642 by its OWN uid
  (PD303(a); the v3 latch draft had {639, 642}, the owner-diagram form PD303(a) rejected). Branch of w6929 -> written each iteration.
  Route class: compile `create indicator` (:49); indicator_nested on a node terminal ran (stage_d1_l2a3.log:47 #9647.t0); on a CT
  terminal UNMEASURED. No panel label `StopAll` exists in the bed graph (grep 0).
- v9:109 / :599 LRS2 / LRS1 now Locals of `StopAll` (route local_read, compile :50,:53; local of a plan-made indicator = v8
  p4_lr_bufdiff11 / P3b-2 p3b_lr_rotpos). Wires p4_w_stop12, p4_w_stop_or, p4_w_or_cond unchanged.
## 5. Pass 4: replay + compile
- compile_plan(v9) OK, **164 ops** (v8 163 + 1); per meta step {1:36, 2:28, 3:37, 4:36, 5:27}, all <= 40 (:47,:57-58).
  Actions per step {1:36, 2:42, 3:41, 4:36, 5:27} (:46). Kinds: create 51 (+1), connect 69 (+1), fs_border 2 (-1) (:48).
- **UNEXPECTED (step FAIL, not diagnosed):** compile_plan op-by-op v8 vs v9 (`tools/bench/prep_c138_p1_cmp.log:3-6`): besides the new
  p4_i_stopall, 3 UNCHANGED actions compile to a different route: p4_w_b_out connect -> connect_term_uid/fs_border_inner_branch;
  p4_x_bufdiff connect_term_uid/fs_border -> connect; p4_x_i_rab1 connect_term_uid/fs_border_inner_branch -> connect.
- Replay on the bed graph: **END**, 183 steps (base + 182), no error, last 182 p4_rle_x_n2_out, final False (:407-408, :418).
- Step 4 p4_i_stopall ok, effect {ControlTerminal, diagram 639, wire 6929} (:409). All new/modified steps ok (:409-416).
- cdiff vs v8: per-step cdiff equal at EVERY step id (0 differ, :417); end cdiff 24 rows == v8's 24 (only-in [] / [], :419-421).
  open_rows_match False / classed ok False as v8 (carried, prep_c138_4_facts.md §4). Sim plan_out a4bf1c98 (:422).
## 6. Review `archive/peer/2026-10-02-priorart-c138-4-p4v8-forloop.md`: FIXED settled-already (recipe_gates:9) + REFUTED helper-exists
(diag_c137_7_types.log:218); already-built / unread-evidence NOT released. `docs/NAMES.md` new section: 6362C01, 6333808, Target 0 = FP.
OPEN: StopAll is a plain indicator, so at the START of a run it holds the previous run's last value (True after a stop) until #639's
first iteration writes it; W1/1.2 can read that stale True and stop at once. Reset at start (e.g. a write before the loops) is a
design call, not in PD298(e)/PD312(d).
