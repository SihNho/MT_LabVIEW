---
type: facts
status: current
date: 2026-10-10
card: 164-a2-3
---
# 164-a2-3: p5s02d (J + K3, A53..A69) recipe pair + pred + licence + predicted EL (offline). Gates PASS; PRIOR-ART NOT novel -> FAIL; NOT launched
- Outputs (`prep_c164_a2_3_md5.log`): pred `plan_ring_p5s02d_pred.json` 37cfa1bc; licence `plan_ring_p5s02d_licence.json` ace1f32e (0 renames, X11
  CLEAN `prep_c164_a2_3_x11.log`); EL `errorlist_predicted_D1_ring_p5s02d_end.json` 653712a8; SG census `prep_c164_a2_3_session.json` dbacb666 (0 rows);
  recipes `stage_d1_ring_p5s02d.py` 61998a98, `stage_d1_ring_p5s02d_scratch.py` 750ee02f (inputs only on stagekit.RingSession, p5s02c pair shape).
- Makers: NEW shared `prep_c164_a2_3_lib.py` (licence / el / pred / unchanged as functions of a cfg; selftest 2/0) - the 163 makers are top-level
  scripts; drivers `prep_c164_a2_3_{licence,el,pred,md5}.py` are inputs + one call. Runs: licence 5/0 (:12), el 10/0 (:25), pred 17/0 (:58), md5 1/0.
- Pred per action (`prep_c164_a2_3_pred.log:40-56`): DELETE A53 dw_cond #23489; DELETE-OBJECT A54 #23042, A55 #23501; NEW A56 LR7, A57 EQ7, A61 SK3L/R,
  A62 KI3, A64 OK3, A67 IK3; PLAN wires A58 (cfw) A59 (nested) A60 (stop) A63 (const_sr) A65 A66 A68 A69 (#31517). WS 8/8, RT route_check PASS.
- E1 checkpoints [0,1,4,5,9,10,12,13] == checkpoint_ops == session; step files step_00/01/04/05/09/10/12/13 (md5 == recorded); delete_wire op 1.
- X10: x10_start(564d8cbe) == x10_plan_start == session 581.8 -> Executor 637.4, MAIN 642.5 <= 675; X17 PASS.
- Sim note: the delete_wire opmodel keeps Wire #23489 in `objs` after step 1 (off every terminal row); DW judged by terminal rows (lib, recorded).
- Error List (`prep_c164_a2_3_el.log:22`): CLEARED 0; RAISED 0 (elrule new [] closed []); UNPREDICTED 4 = A64 t_k3o group, A67 t_k3i group
  (reb), A54 do_23042 (wire 23460 on it), A55 do_23501 (23460, 23519; 23519 left in the sim, :17-18); STANDING 53; TOTAL 53 (upper 57).
  STALE (STANDING, :7-12): items 4, 6, 7 (A70 w_k3f), 8, 49, 50 (A80 w_k4f). compare(read 53, file) 0/0; W: compare(read, file's own entries) 0/0.
- DRY main `prep_c164_a2_3_dry.log:72` `=== DRY PASS-UNVERIFIED CEN2 ...` rc 0 (L1 :24, E1 :55, FR :57, D 8==8 lost 4==4 :58, CEN2 UNPREDICTED :59,
  TD :60, PB PASS :67). PB RECORD 5 rows :62-66: cal cluster path 1, error in 3, file size 1, selected path 1, total data array in 3. No PB BLOCK.
- DRY scratch `prep_c164_a2_3_scr_dry.log:95` PASS-UNVERIFIED CEN2, same 5 RECORD rows :80-84, rc 0.
- PRERUN main `prep_c164_a2_3_prerun.log:98` PASS 16/0: X10 642.5 (:94), X17 (:83), X8 (:74); X14 WARN rows 17 budget 15 proven no (:95).
- PRERUN scratch `prep_c164_a2_3_scr_prerun.log:121` PASS 16/0 (X10 637.4 :117, X14 WARN :118).
- --scratch-required `prep_c164_a2_3_scrreq.log:3` rc 3: `SCRATCH-REQUIRED | stage_d1_ring_p5s02d.py | CENSUS-UNPREDICTED ... rows [1..17]`.
- check_launch (`prep_c164_a2_3_checklaunch.log`, 4/0; scratch log absent :3): own card task_164-a2-3 REFUSE (:6, names no DRY-UNVERIFIED-OK);
  stand-in task_163-a2-2.json ALLOW (:10).
- Prior art: readers (`prep_c164_a2_3_pa.log`) proven_pattern False both, priorart_diff None, new classes [] -> owed. Review
  `prep_c164_a2_3_priorart.log:48-49` `PRIOR-ART: settled-already` / `contradicted` ($1.39); STOP RECORDs armed on both recipes (:53-54).
  A1: PD321(b)/PD323(a) delete order - delete_wire every wire whose other end is the node before delete_object; this plan deletes #23042/#23501
  with 23460/23519 attached. A3: ring-p5c.md:57 "delete_object has no passing launch" contradicted (diag_c140_3_facts.md:14,22).
  Disposition written (archive/peer/2026-10-10-priorart-priorart-c164-a2-3-p5s02d.md "What was done with it"), no FIXED/REFUTED line.
- Commands for later: scratch `py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c164_p5s02d_scratch.log -- py -u
  tools/recipes/stage_d1_ring_p5s02d_scratch.py --unverified-card <launch card naming DRY-UNVERIFIED-OK: CEN2 new-object census>`; real
  `py tools/bgrun.py --material --max-min 50 --log tools/bench/launch_c164_p5s02d.log -- py -u tools/recipes/stage_d1_ring_p5s02d.py`.
- md5 UNCHANGED (`prep_c164_a2_3_md5.log` U 14/14): stagesim 95a162ba, stagexec a4df7e15, stagekit dd57c1ca, stage_prerun 7605116f, stage_shared
  b688edd4, memory_model 8fb432e4, plan 872822f3, graph 3d5196ab, EL 26d45c71, VIs 564d8cbe / f9ae7751 / 94ffff94 / 7f2582ae / eb1d0f31. No tool / hook
  edit; LabVIEW never launched (dry/prerun COM stubbed).
- OPEN: prior-art A1 - add delete_wire rows (23519; 23460 if its sinks are only #23501) under PD321(b)'s sink-subset gate and re-make plan_ring_p5s02d
  (prep_c164_a2_2_mk.py), or REFUTE in writing; recipes stay STOP-RECORDed until then (prep_c164_a2_3_priorart.log:53-54).
- OPEN: docs/d1/ring-p5c.md:57 premise contradicted by diag_c140_3_facts.md:14,22 (outside globs).
- OPEN: check-launch needs a launch card naming `DRY-UNVERIFIED-OK: CEN2 new-object census`; X14 WARN 17 rows > 15 (not proven).
