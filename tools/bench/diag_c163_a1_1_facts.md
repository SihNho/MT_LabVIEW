---
card: 163-a1-1
date: 2026-10-10
status: current
---
# 163-a1-1 facts - step-3 plan `plan_ring_p5s02c.json` on graph 431cfd83 (offline, labview none)

**Part 1 md5 (`prep_c163_a1_1_hash.log:3-19`, hashlib), all EQUAL to the judgement values:** plan_ring_p5s02r_in d84634bd · graph_p5s02b 431cfd83 ·
memory_model def9e640 · expected EL 60e02787 · stage_shared b688edd4 · stagekit 9b8f82c1 · stagexec a4df7e15 · stagesim 95a162ba · stage_prerun 7605116f ·
ring-p5b.md 70b89fac · brief 48f5fedc · script-writing 0165fb24 · prep_c160_b3_1_mk a08aadf5 · VIs f9ae7751 / 94ffff94 / 7f2582ae / eb1d0f31 (read as bytes). 0 changed.

**Memory rule PD396(c)** (X10 on `SX.checkpoint_ops` via `prep_c156_a1_1_lib.main_of`, START 601.2 = `load_by_vi` f9ae7751, limit 675, +2 source reads; `prep_c163_a1_1_mk.log:25-33`):
- I+J (A41..A60): 16 ops, N 16, R 10, Executor peak 666.0, **MAIN 671.1 <= 675** -> plan = A41..A60, one step (`:32`).
- I (A41..A52): 8 ops, N 8, R 7, peak 647.4, **MAIN 652.5**.
- At `x10_start(f9ae7751)` = 601.2 + op-0 read 5.9 = 607.1 (memory_model `start_rule`): I+J MAIN **677.0 > 675**, I 658.3 (`:26`, `:29`). See OPEN 1.

**Plan:** `tools/bench/plan_ring_p5s02c.json` md5 014c7d5277b100761a8a6f4abcca915e, written by `stagesim.simulate`; input `plan_ring_p5s02c_in.json` caa0f639
(20 actions, 24 open pairs from the probe tie). REALSIM: final True, failed None, 20/20 steps, 0 PROVISIONAL, route check PASS, 0 UNROUTABLE (`:113-114`).
No earlier plan_ring_p5s02c.json existed (nothing copied aside).
Action ids in order: sr_c7 c_k07 w_k07 c_inc7 t_ci7 w_ci7_in w_ci7_inc w_c7_fi t_co7 w_inc7_co w_co7_r w_c7_pass | dw_cond do_23042 do_23501 c_lr7 c_eq7 w_eq7_x w_eq7_y w_eq7_cond.

**Mapping (stagekit calls):** symbols used = new:CQ7 -> #31308, new:CQ7.f0 -> #31506 (p5s02a creation map `plan_ring_p5s02a_4284c22a_20261010_023453.jsonl`);
none made by p5s02b. Frames 'False' -> #31506, 'True' -> #31517 == base_case_frames of #31308. Mapped rows differ from the input only in symbol/frame leaves (A44, A45, A48, A49, A52).
No base sink stub: A48's sink t5763 carries no wire; A60's cond wire w23489 is removed by A53 dw_cond (insert_stub_deletes NOT used).

**Route rows (k / op / route):** 1 add_sr/add_sr · 2 create/primitive · 3 connect/const_sr · 4 create/primitive · 5 connect_term_uid/connect_term_uid ·
6 case_frame_wire/case_frame_wire · 7 connect_term_uid/connect_term_uid · 8 case_frame_wire/case_frame_wire · 9 delete_wire/delete_wire ·
10 delete_object/delete_object · 11 delete_object/delete_object · 12 create/local_read · 13 create/primitive · 14 branch/branch · 15 connect/nested · 16 stop/stop (`:97-112`).

**Compile (real owners):** ops [add_sr, create, connect, create, connect_term_uid(register_end_case_border)[5-7], case_frame_wire(branch)[8],
connect_term_uid(register_end_case_border)[9-11], case_frame_wire(new_wire)[12], delete_wire[13], delete_object[14], delete_object[15], create[16], create[17],
branch[18], connect[19], stop[20]]; checkpoints [0,1,2,4,5,7,9,12,13,16]. The one delete_wire (op 9) IS a checkpoint.
Group J delete_object: compiles as its own op kind `delete_object` (no variant), one op per row (ops 10, 11), route `delete_object`; NOT checkpoints
(op 12, a create, is the next read). Targets in 431cfd83: #23042 Comparison, #23501 LoopTunnel (`:23`); w23489 = #23042 'x = y?' -> #23405 (`:22`).

**Gates (`prep_c163_a1_1_mk.log`, 22 PASS / 0 FAIL):** M0, GRP (I 41-52, J 53-60), E1, CM, MAP, FRM, ROWS, STUB, C I+J, C I, C group I, X10 chosen 671.1,
SPLIT (no group split), PROBE, TIE, S1, SB, C-OUT (= candidate ops/checkpoints, MAIN 671.1), IDS (A41..A60), X8 clean, X17 (2 primitive creates, donor == prim), U.

**UNCHANGED (U gate, md5 before == after):** stagekit, stagexec, stagesim, stage_prerun, stage_shared, plan_ring_p5s02r_in, graph 431cfd83, graph 7ac24924,
memory_model, plan_ring_p5s02a / p5s02b, prep_c156_a1_1_session, VIs f9ae7751 / 94ffff94 / 7f2582ae / eb1d0f31. No tool edited.

OPEN:
1. START convention: brief/PD396(c) say START = load_by_vi 601.2 (`docs/d1/ring-p5b.md:345-346`); memory_model `start_rule` and `stage_prerun.x10_start`
   add op-0 read 5.9 (`tools/bench/memory_model.json:119`), as the earlier makers did (603.4 = 597.5 + 5.9). With 607.1 the rule picks group I alone (677.0 > 675). Which start does the prerun X10 gate use?
2. Margin: MAIN 671.1 is 3.9 MB under 675; the step-2 scratch peak was 657.1 vs X10 within 0.9 (`docs/d1/ring-p5b.md:333`).
