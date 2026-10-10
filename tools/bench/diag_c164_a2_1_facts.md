---
card: 164-a2-1
date: 2026-10-10
status: current
---
# 164-a2-1 facts (offline; no LabVIEW process before, during, after) - result FAIL at gate SB (Final False, 2 UNROUTABLE)
**Part 1 md5** (`prep_c164_a2_1_hash.log`, 26/0): all 21 card inputs + 5 VIs EQUAL (bytes read): VI 564d8cbe f9ae7751 94ffff94 7f2582ae eb1d0f31, graph 3d5196ab,
EL 26d45c71, memory_model 8fb432e4, r_in 4c8d3645, pre164 d84634bd, p5s02d 1152ce60, stagekit dd57c1ca, stage_shared b688edd4, stagexec a4df7e15, stagesim 95a162ba, stage_prerun 7605116f.
**Part 2** (`prep_c164_a2_1_cmp.log`, 8/0): byte copy `plan_ring_p5s02r_in_both164.json` = 4c8d3645; Edit tool removed `"frame": "True"` from A69/A79 src;
`plan_ring_p5s02r_in.json` **4c8d3645 -> 4d93c82d**. (i) vs pre164 d84634bd normalised: exactly 2 ADDED A69/A79 `/dst/frame`='True' (raw: string ends -> dicts);
(ii) vs both164 4c8d3645: exactly 2 REMOVED A69/A79 `/src/frame`='True', raw == normalised. Ends now `{uid new:IK3, side inner}` -> `{uid new:OK3, side inner, frame True}` (same K4).
**#31517 binding**: `creation_map/plan_ring_p5s02a_4284c22a_20261010_023453.jsonl:35` = `"kind": "diag", "sim": -30, "real": 31517, "owner_real": 31308`;
mk log: `w_k3pass end new:OK3: frame 'True' = index 1 of new:CQ7 -> new:CQ7.f1 -> sim -30 -> real #31517; graph frames of #31308 [31506, 31517]` (same w_k4pass); FRM 2/2 -> '#31517'.
**Compile K3/K4 on 3d5196ab ACCEPTS the dst-only shape** (`prep_c164_a2_1_mk.log:42-53`): t_k3i/w_k3l/w_k3pass = op `connect_term_uid` variant `register_end_case_border`
acts [15,16,17]; t_k4i/w_k4l/w_k4pass = same kind/variant acts [25,26,27] (OK3/OK4 groups [12,13,14] / [22,23,24] same). A `frame` wire counts as the group's
out-wire only via case_pass_wire (stagexec.py:897 grp excludes frame wires, :899-900 `or case_pass_wire(...)`), and the variant is reached only after
ins/outs == 1 each (:901-902) -> case_pass_wire True for both. The direct per-op check in the maker (out_act) did not run: the SB gate stopped the script first.
**X10 per prefix** (START = x10_start(564d8cbe) = 581.8, called; limit 675 unchanged):
| prefix | rows | MAIN | Exec peak / N / R |
|---|---|---|---|
| J | 8 | 628.0 | 622.9 / 8 / 5 |
| J+K3 | 17 | 642.5 | 637.4 / 13 / 8 |
| J+K3+K3f | 18 | 646.4 | 641.3 / 14 / 9 |
| J+K3+K3f+K4 | 27 | 660.9 | 655.8 / 19 / 12 |
| J+K3+K3f+K4+K4f | 28 | 664.8 | 659.7 / 20 / 13 |
make_step_plan's prefix rule (MAIN + rows only) chose **J+K3+K3f+K4+K4f, A53..A80, 28 rows** (`mk.log:55`); SPLIT PASS, PROBE failed null, TIE 26 end rows tied, S1 validates (28 actions, 24 open pairs).
**SB FAIL** (`mk.log:160-161`): `plan_ring_p5s02d.json` **e3054ab6** written by stagesim.simulate with **final False**: failed null, 28/28 replayed, provisional [],
route check FAIL, **UNROUTABLE 2**: k=14 branch [w_k3f] "ADDRESS: #8776 is an INNER face of LoopTunnel #5204: only the outer face's owner route is measured
(l2a1_faces_81.log)"; k=20 branch [w_k4f] same for #24342 / LoopTunnel #10404 (raised at stagexec.py:1930). `FINALIZE REFUSED` at mk.log:110.
Route rows k1..k13, k15..k19 all routed (delete_wire, delete_object x2, local_read, primitive, cfw, nested, stop, add_sr, primitive, const_sr, connect_term_uid x2; same for K4).
Compile of the full prefix: 20 ops, checkpoints [0,1,4,5,9,10,12,13,15,16,18,19,20]; delete_wire op 1 is a checkpoint. X8 / X17 / C-OUT / IDS not reached (SB is fatal).
**K3f/K4f STUB**: STUB gate FAIL (non-fatal, mk.log:37): w_k3f dst t8776 carries w10362, w_k4f dst t24342 carries w25232 in 3d5196ab, no plan delete_wire removes them.
The chosen prefix CONTAINS K3f (A70, k=14) and K4f (A80, k=20); those two rows are exactly the 2 UNROUTABLE rows (branch onto an inner face), so for this prefix
they are a real obstacle (Final False). J+K3 (17 rows, MAIN 642.5) compiles and contains neither; it was not simulated (no other shape/prefix tried in the card).
Plan files: `plan_ring_p5s02d_jonly.json` = **1152ce60** (J alone, final True, kept aside by keep_prev, `mk.log:5`); `plan_ring_p5s02d_in.json` 5ca92597.
`prep_c164_a2_1_session.json` NOT written (make_step_plan stopped at SB before the dump).
**Part 4** (`prep_c164_a2_1_pins.log`, 1/0): `result_158-a3-3.json` written (`protocol new result`), status FAIL, note RETIRED..., `protocol validate` OK (CLOCK-UNMEASURED warn:
no bind line, it never ran); `guard_write.open_card_pins(plan_ring_p5s02r_in.json)` -> `[]` (158-a3-3 no longer listed). Hook not edited.
**UNCHANGED** (`prep_c164_a2_1_hash_end.log`, 24 equal, 2 changed): stagekit, stagexec, stagesim, stage_prerun, stage_shared, memory_model, graph 3d5196ab, EL 26d45c71,
prep_plan_flow_lib, prep_c164_a1_1_mk, pre164, the 5 VIs. Changed only: plan_ring_p5s02r_in.json (Part 2 edit) and plan_ring_p5s02d.json (simulate, Final False).
Duplication note: `norm_end` in prep_c164_a2_1_cmp.py repeats prep_c164_a1_1_cmp.py:31-37 (the shared home, prep_plan_flow_lib, is outside this card's write globs).
OPEN: plan_ring_p5s02d.json is now a Final-False 28-row file (e3054ab6); J-alone 1152ce60 is in _jonly - which file is step 4 (restore J, plan J+K3, or route K3f/K4f)?
OPEN: K3f/K4f (A70/A80) branch onto inner faces #8776/#24342 - unroutable per stagexec.py:1930; needs an address/route decision or an outer-face rewrite of those rows.
OPEN: make_step_plan's prefix rule ignores routability (prep_plan_flow_lib.py:171) - prefixes are chosen before the route check runs.
