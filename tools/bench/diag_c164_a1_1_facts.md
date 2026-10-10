---
card: 164-a1-1
date: 2026-10-10
status: current
---
# 164-a1-1 facts (offline; no LabVIEW process before, during, after)
**Part 1 md5** (`prep_c164_a1_1_hash.log:3-26`, 22/0): all EQUAL - r_in d84634bd, graph 3d5196ab, memory_model 8fb432e4, EL 26d45c71, stage_shared b688edd4,
stagekit dd57c1ca, stagexec a4df7e15, stagesim 95a162ba, stage_prerun 7605116f, ring-p5c.md 70fe6983, the 7 other card inputs, VIs 564d8cbe f9ae7751 94ffff94 7f2582ae eb1d0f31 (bytes read).
**Part 2** (`prep_c164_a1_1_cmp.log`, 5/0): copy `plan_ring_p5s02r_in_pre164.json` d84634bd (byte copy); `plan_ring_p5s02r_in.json` d84634bd -> **4c8d3645**.
A69/A79 ends were STRINGS (`"new:IK3.inner"`, `pre164.json:837-838,935-936`), so the A33 layout `{uid, side, frame}` replaces each string by a dict:
raw leaf diff = string -> {uid, side, frame} on 4 ends (`cmp.log:7-8`); normalised by `stagexec._sym_of` (`stagexec.py:227-235`, same end) the diff is exactly the
4 added `frame`='True' keys, nothing else (`cmp.log:9-11`). guard_write flagged open card 158-a3-3 pinning r_in d84634bd (no result file) - not re-pinned (outside globs).
**new:CQ7 'True'** -> new:CQ7.f1 -> sim -30 -> real **#31517** (`creation_map/plan_ring_p5s02a_4284c22a_20261010_023453.jsonl:35`; case #31308 line 29, f0 #31506 line 34);
on 3d5196ab frames of #31308 = [31506, 31517] (`prep_c164_a1_1_mk.log`, FRM lines). new:TD7 -> sim -19 -> **#31735** by the step-3 run's map
(`creation_map/plan_ring_p5s02c_930699ec_20261010_130008.jsonl:21`). Each symbol bound by the ONE adopted step that made it (OWN gate), sim ids never mixed.
**Shared flow**: `tools/bench/prep_plan_flow_lib.py` 34264f5e = prep_c163_a1_1_mk.py:47-183 parametrised; replay self-test 28/0 (`prep_plan_flow_lib.log:287`):
163-a1-2 reproduced from 431cfd83 + pre164 input - plan_in md5 eb48fabc EQUAL, chosen I, MAIN(I) 658.3 / MAIN(I+J) 677.0 as `prep_c163_a1_2_mk.log:28-34`.
Not byte-equal (930699ec vs replay): exact differences = `finalized.at`, `finalized.summary.md5` (summary records the plan path) and the step-file md5 chain -
each step file stores `prev.path` (absolute) of the previous step file; every step file equal after the path map (T3), 930699ec's step files unchanged on disk (T3a).
Maker `prep_c164_a1_1_mk.py` cafbad95 = 50 lines, inputs + one `make_step_plan` call.
**X10 per prefix** (START = `stage_prerun.x10_start(564d8cbe)` = **581.8** = 575.9 load + 5.9 op0, called; limit 675 unchanged):
| prefix | rows | MAIN | result |
|---|---|---|---|
| J (A53..A60) | 8 | **628.0** (Exec peak 622.9, N 8, R 5) | fits |
| J+K3 (A53..A69) | 17 | not computable | **compile refused**: "action 15: tunnel new:IK3 must be followed by exactly one wire into it and one out of it" (`stagexec.py:901-902`) |
Stopped there (rule: longer prefixes not tried). **Plan = J**, ids dw_cond do_23042 do_23501 c_lr7 c_eq7 w_eq7_x w_eq7_y w_eq7_cond.
**Why K3 refuses**: `stagexec.case_pass_wire` (card 156-a1-2, `stagexec.py:6286-6288`) accepts a pass wire only with a FRAMELESS src (dst `frame` = the in-tunnel's body frame);
a src with `frame` returns False, and a `frame` wire is never a group wire (`stagexec.py:896-897`) -> IK3 has no out-wire. PD397(b)'s both-ends shape (A33/A40/A52) hits this.
**plan_ring_p5s02d.json 1152ce60** (written by stagesim.simulate only; no older file existed): REALSIM final True, failed None, 8/8 replayed, 0 PROVISIONAL, route PASS,
0 UNROUTABLE. Routes: k1 delete_wire / k2 delete_object / k3 delete_object / k4 local_read / k5 primitive / k6 connect cfw / k7 connect nested / k8 stop.
plan_in `plan_ring_p5s02d_in.json` 0a259370 (8 actions, 24 open pairs = the 930699ec base open rows); probe `sim/ring_p5s02d/_probe/plan_ring_p5s02dq_in.json` 56b2a747.
**Compile J**: 8 ops delete_wire[1], delete_object[2], delete_object[3], create[4], create[5], connect[6], connect[7], stop[8]; checkpoints [0, 1, 4, 5, 8];
delete_wire op 1 is a checkpoint. delete_object compiles as its own op kind (one op per row, no variant); it is NOT a checkpoint under `SX.checkpoint_ops`.
DW dw_cond w23489 on 3d5196ab: rows (23042 'x = y?' src; 23405 x2 sinks), not sourceless; DO 23042 Comparison, 23501 LoopTunnel.
Gates: ROWS PASS (A58 w_eq7_x TD7 -> #31735; K rows CQ7 -> 31308/31506/31517), C-OUT == candidate, IDS, SPLIT, X8 clean, X17 PASS, TIE 26 end rows all tied.
**STUB (non-fatal) FAIL**: K3f w_k3f dst t8776 carries w10362, K4f w_k4f dst t24342 carries w25232 in 3d5196ab, no plan delete_wire removes them (not in plan J).
Maker RESULT 26/1 (`prep_c164_a1_1_mk.log`), first_fail = that STUB line.
**UNCHANGED** (md5 at end == start): stagekit dd57c1ca, stagexec a4df7e15, stagesim 95a162ba, stage_prerun 7605116f, stage_shared b688edd4, memory_model 8fb432e4,
graph 3d5196ab, EL 26d45c71, the 5 VIs (U gate PASS). No tool edit.
OPEN: K3/K4 pass wires - PD397(b) both-ends `frame` vs `stagexec.py:6286-6288` (frameless src, dst frame): which shape, before K3/K4 can be planned?
OPEN: step 4 = J alone (MAIN 628.0, 8 rows) - accept, or wait for K3 to compile and plan J+K3.. together?
OPEN: K3f/K4f sinks t8776 (w10362) / t24342 (w25232) are already wired in 3d5196ab - a delete_wire / stub row is owed for the step that takes them.
