# Card 137-6 facts (offline, 2026-10-02; no tools/*.py edited, no LabVIEW). Inputs: v6 99586b73, graph p3b2b 50595c62
Script `tools/bench/prep_c137_6_mkv7.py` (a737db7d), log `tools/bench/prep_c137_6_mkv7.log` (`BGRUN END rc=0 after 174s`, `:195`;
RESULT 6/0 = plan-construction gates only; the stagesim prediction FAILED, see 3).

## 1. v7 = v6 with decide p4_dec_reseed (v6 #158) replaced by PD300(b) option 2 (8 actions, v7 #158-165, `log:8-15`)
- `tools/bench/plan_ring_p4_v7.json` md5 **01ab0893f3a9440e02bbc180bc467bdf**, 172 actions (`log:7`); gates (`log:5-19`): one decide
  in v6; RB7/LRR1/new ids unused; v7 = v6 - 1 + 8; every other action identical to v6; no top-level key changed; re-read = built.
- Routes (each `why` cites; shapes copied from v6 groups A #115-124 and D #145):
  158 `delete_wire` p4_rbR_dw w25415 - MEASURED (delete_wire launched P2a, as p4_rbA_dw)
  159 `wire` p4_rbR_re0 #9647 t9668 -> Tunnel #10465 t10469 (raw restore) - PRECEDENT (as p4_rbA_re0)
  160 `create` p4_rbR_sel Select RB7 on 23166, donor DonorErrSel_MergeErrors #529 - MEASURED (as p4_rbF_sel)
  161 `create` p4_rbR_lr Local read LRR1 "autofocus reseed flag (1.2 to 1.1)" on 23166 - PRECEDENT (plan_l2a3_in.json:16, as p4_lr_stop12)
  162 `wire` p4_rbR_t #9647 t9668 -> RB7.t - PRECEDENT; 163 `wire` p4_rbR_f LRR1 -> RB7.f - PRECEDENT;
  164 `wire` p4_rbR_s AND1 'x .and. y?' -> RB7.s - PRECEDENT; 165 `wire` p4_rbR_out RB7 -> {uid 25557, term_uid 25557} - PRECEDENT
  (as p4_rbD_sel_t25573). UNMEASURED: none new; all PRECEDENT rows are unrun shapes as in v6.

## 2. #10465 and the flag in the bed graph (`log:20-28`)
- w25415: source #9647 t9668 (23166); sinks t10469 (Tunnel #10465 outer, 23166) and t25557 (indicator "autofocus reseed flag
  (1.2 to 1.1)", ControlTerminal on 23166 = loop 1.2 body of While #10170).
- #10465 is a Tunnel of CaseStructure #10445 (on 23166); its inner terminals t10467 (frame 10453) and t10468 (frame 10459)
  both have wire_uid 0 (`log:21-22,28`) => **no downstream sink of #10465 in the graph**; it stays in loop 1.2.
- An existing Local of the flag: #25576 on diagram 639 (loop 1.1), t25585, wire 9921 (`log:25`) - LRR1 is a 2nd Local.

## 3. stagesim replay of v7 (`tools/bench/sim/ring_p4_v7`)
- Steps 1-158 ok (158 delete_wire w25415 ok, cdiff 23 -> 24, `log:189`).
- **STOP at step 159 `wire` p4_rbR_re0: "#10465 (10465) owns no terminal in the current graph"** (`log:190`), raised at
  `tools/stagesim.py:680-681` (`node_rows` empty). The base graph lists 3 rows for #10465 (`log:20-22`).
  Predicted: stop at p4_x_n2_out (v7 #171). final=False, candidates 18; re-written plan md5 3f17e2f6 (`log:191`).
- Same message class as PD300(a)'s step-102 "#686 owns no terminal" (real graph lists t8936).

## 4. compile_plan (`stagexec.py:639`)
- **v7: OK, 160 ops**, per meta step {1:33, 2:27, 3:37, 4:36, 5:27} (`log:192`); same on the sim-rewritten plan (`log:193`).
  The FS exit p4_x_n2_out compiled as a plain op (PD309(b) notes stagexec files it as `connect`).

## 5. Step counts (v3 meta cut; decide was step 5, new 8 inherit it, `log:29-30`)
- Actions per step **{1:33, 2:35, 3:41, 4:36, 5:27}**, none without a meta step; step 3 = 41 > 40 still.

OPEN: (a) stagesim loses #10465's rows after delete_wire w25415 (or never addresses a Case tunnel by owner uid) - simulator
fix or a different address for t10469 (e.g. term_uid only)? (b) #10465 has no inner sink - does the raw re-wire need to exist?
