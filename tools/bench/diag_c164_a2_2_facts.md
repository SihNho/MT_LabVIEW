---
card: 164-a2-2
date: 2026-10-10
status: current
---
# 164-a2-2 facts (offline; no LabVIEW process before/after) - result PASS 30/0 (`prep_c164_a2_2_mk.log:138`, BGRUN END rc=0 after 48s :139)
**Outputs md5**: plan_ring_p5s02d.json **872822f3** (written by stagesim.simulate) · plan_ring_p5s02d_all28_false.json **e3054ab6** (= old Final-False, copied aside by
make_step_plan keep_prev, `mk.log:5`, gate ASIDE :112) · plan_ring_p5s02d_jonly.json 1152ce60 unchanged (:113) · prep_c164_a2_2_mk.py d16798ed · prep_c164_a2_2_session.json 746dd63c ·
plan_ring_p5s02d_in.json 40c0e512 · probe in sim/ring_p5s02d/_probe/plan_ring_p5s02dq_in.json c49215a9 · log 67315a75.
**Maker vs prep_c164_a2_1_mk.py**: groups ["J","K3"]; pins from task_164-a2-2.json; card/session/goal names; keep_prev -> all28_false (the old keep_prev=_jonly would have
overwritten 1152ce60 with e3054ab6, `prep_plan_flow_lib.py:95-96`); + a read-only FACT ACTOP print (brief step 5). One call of make_step_plan; no logic copied.
**X10** (START 581.8 = x10_start(564d8cbe), :30; limit 675 kept): J 8 rows MAIN 628.0 (peak 622.9, N 8, R 5) :32 · J+K3 17 rows MAIN 642.5 (peak 637.4, N 13, R 8) :35.
RULE plan = J+K3 (A53..A69, 17 rows) :38.
**Gates** all PASS: M0 :3, GRP [(53,60,8),(61,69,9)] :4, OWN/MAP/MAPALL :6-17, FRM 'True' -> #31517 :20, ROWS :25, **STUB PASS** :29 (K3f not in the rows),
C J :33, C J+K3 :36, X10 :37, SPLIT (no-group-split) :39, PROBE failed null :40, TIE :42, S1 (17 actions, 24 open pairs) :43,
**SB** :107 (REALSIM :106: final True, failed null, 17/17 steps, provisional [], route check PASS, UNROUTABLE 0), C-OUT MAIN 642.5 :108, IDS A53..A69 :109,
X8 control_path_lint clean :110, X17 :111, PASS w_k3pass :135, U pins :137.
**Route rows** (:93-105): k1 delete_wire · k2,k3 delete_object · k4 local_read · k5 primitive · k6 cfw · k7 nested · k8 stop · k9 add_sr · k10 primitive · k11 const_sr ·
k12 connect_term_uid [t_k3o,w_k3out,w_k3r] · k13 connect_term_uid [t_k3i,w_k3l,w_k3pass]. UNROUTABLE 0.
**Compile** (:34, :108): 13 ops - delete_wire[1], delete_object[2], delete_object[3], create[4], create[5], connect[6], connect[7], stop[8], add_sr[9], create[10], connect[11],
connect_term_uid/register_end_case_border[12,13,14], connect_term_uid/register_end_case_border[15,16,17]; checkpoints [0,1,4,5,9,10,12,13]; delete_wire op 1 is a checkpoint.
**K3 pass wire** (:134-135): w_k3pass = plan action 17, op kind connect_term_uid variant register_end_case_border, acts [15,16,17], tunnel new:IK3, in_act 16, out_act 17, case 31308.
w_k4pass not in this plan (:136).
**Action -> op (Error-List-relevant, :117-133)**: A53 dw_cond delete_wire op1 · A54 do_23042 delete_object op2 · A55 do_23501 delete_object op3 · A56 c_lr7 create op4 ·
A57 c_eq7 create op5 · A58 w_eq7_x connect op6 · A59 w_eq7_y connect op7 · A60 w_eq7_cond stop op8 · A61 sr_k3 add_sr op9 · A62 c_k3i create op10 · A63 w_k3i connect op11 ·
A64 t_k3o / A65 w_k3out / A66 w_k3r connect_term_uid(reb) op12 · A67 t_k3i / A68 w_k3l / A69 w_k3pass connect_term_uid(reb) op13.
**UNCHANGED** (md5 before == after, bash md5sum; VIs 564d8cbe/94ffff94/f9ae7751 by gate U :137): stagekit dd57c1ca, stage_shared b688edd4, stagexec a4df7e15, stagesim 95a162ba,
stage_prerun 7605116f, prep_plan_flow_lib 34264f5e, memory_model 8fb432e4, graph 3d5196ab, EL 26d45c71, r_in 4d93c82d, prep_c164_a2_1_mk a2cf4394.
OPEN: K3f/K4f (A70/A80) branch onto LoopTunnel INNER faces #8776/#24342 - unroutable (stagexec.py:1930, diag_c164_a2_1_facts.md); a route/address decision (or an
outer-face rewrite of those rows) is needed before the next step (K3f, K4, K4f).
OPEN: make_step_plan's prefix rule picks prefixes on MAIN + rows only, before the route check (prep_plan_flow_lib.py:171) - unchanged here; J+K3 was set by the group list.
