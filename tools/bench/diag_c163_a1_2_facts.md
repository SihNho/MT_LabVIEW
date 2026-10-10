---
card: 163-a1-2
date: 2026-10-10
status: current
---
# 163-a1-2 facts - step-3 plan re-made as group I alone (A41..A52) on graph 431cfd83, X10 START = stage_prerun.x10_start (offline, labview none)

**Run:** `prep_c163_a1_2_mk.py` (0fb87dff, 40 lines) under bgrun -> `tools/bench/prep_c163_a1_2_mk.log` (`BGRUN END rc=0 after 35s`), **25 PASS / 0 FAIL** (`:93`).
It executes `prep_c163_a1_1_mk.py` (b6ea1429, unedited) with 8 literal one-line substitutions, each asserted to occur once (START, card id, session file, copy name, goal texts, extra gates); no logic copied.

**Kept I+J (before any rebuild, `:3-4`, gate KEEP `:91`):** `plan_ring_p5s02c_ij.json` 014c7d5277b100761a8a6f4abcca915e · `plan_ring_p5s02c_ij_in.json` caa0f639d8b5f074953f4015ed594fae (byte-equal to the card pins).
**New plan:** `plan_ring_p5s02c.json` 930699ece36e3366e2c1a2cdf9a82c34 (written by `stagesim.simulate`) · `plan_ring_p5s02c_in.json` eb48fabc9679da57966a64e6da302be6 (12 actions, 24 open pairs) · session `prep_c163_a1_2_session.json` e8daf1fe.
**REALSIM (`:83-84`):** final True; failed null; steps 12/12; provisional []; route check PASS; UNROUTABLE 0.
**Action ids (gate IDS `:86`):** sr_c7 c_k07 w_k07 c_inc7 t_ci7 w_ci7_in w_ci7_inc w_c7_fi t_co7 w_inc7_co w_co7_r w_c7_pass = A41..A52; no group split (SPLIT).
**Route rows (`:75-82`):** 1 add_sr/add_sr · 2 create/primitive · 3 connect/const_sr · 4 create/primitive · 5 connect_term_uid/connect_term_uid · 6 case_frame_wire/case_frame_wire · 7 connect_term_uid/connect_term_uid · 8 case_frame_wire/case_frame_wire.
**Compile (`:30`, C-OUT `:85`):** 8 ops [add_sr, create, connect, create, connect_term_uid(register_end_case_border)[5-7], case_frame_wire(branch)[8], connect_term_uid(register_end_case_border)[9-11], case_frame_wire(new_wire)[12]]; checkpoints [0,1,2,4,5,7,8]; no delete_wire in group I.
**Mapping:** new:CQ7 / new:CQ7.f0 via p5s02a creation map; frames 'False' -> #31506, 'True' -> #31517; ROWS PASS (`:22`, mapped rows differ only in symbol/frame leaves).

**X10 (START called, not typed: `stage_prerun.x10_start(f9ae7751)` = (607.1, "601.2 + op-0 read 5.9 (tools/bench/diag_c162_a1_2_graph.log:24 ...; tools/bench/stage_d1_ring_p3b1.log:42-43 ...; card 133-3, PD283(b))"), on SX.checkpoint_ops, limit 675, +2 reads):**
- group I: N 8, R 7, Executor peak 653.2, **MAIN 658.3 <= 675** (`:31`, PLAN-I `:92`) · I+J: N 16, R 10, peak 671.9, **MAIN 677.0 > 675** (`:28`). Rule PD396(c) -> I.

**Gates PASS:** M0, GRP, E1, CM, MAP, FRM, ROWS, STUB, C I+J, C I, C group I, X10 chosen, SPLIT, PROBE, TIE, S1, SB, C-OUT, IDS, X8 (`:87`), X17 (`:88`, 1 primitive create, donor == prim), U (`:89`), M1, KEEP, PLAN-I.

**UNCHANGED md5 (after the run):** stagekit 9b8f82c1 · stagexec a4df7e15 · stagesim 95a162ba · stage_prerun 7605116f · stage_shared b688edd4 · memory_model def9e640 · graph 431cfd83 · prep_c163_a1_1_mk b6ea1429 · VIs f9ae7751 / 94ffff94 / 7f2582ae / eb1d0f31 (U gate). No tool edit.

OPEN:
1. Group J (A53..A60) is left for p5s02d; the kept I+J plan (`plan_ring_p5s02c_ij.json`) is on 431cfd83 and will need a re-base onto the step-3 output graph (`docs/d1/ring-p5b.md` PD396(c)).
