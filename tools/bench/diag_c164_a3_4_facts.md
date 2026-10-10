---
card: 164-3-4
date: 2026-10-10
status: current
---
# 164-3-4 facts (offline; no LabVIEW) - FAIL at the DRY: L0 refuses plan 725cd68e's plan_in name (both recipes); NOT launched
- Outputs (`prep_c164_a3_4_md5.log`): pred `plan_ring_p5s02d_pred.json` 9b99fcce; licence `plan_ring_p5s02d_licence.json` b33fbb51 (0 renames, X11 CLEAN
  `prep_c164_a3_4_x11.log`); EL `errorlist_predicted_D1_ring_p5s02d_end.json` a84daf96; SG census `prep_c164_a3_4_session.json` 0143bfc8 (0 rows);
  recipes `stage_d1_ring_p5s02d.py` 46c7be60, `stage_d1_ring_p5s02d_scratch.py` b0f4b770 (inputs only on stagekit.RingSession); review file af784c98.
- Makers = drivers on `prep_c164_a2_3_lib.py` (licence 5/0, el 10/0, pred 17/0, md5 1/0) + `prep_c164_a3_4_pd399.py` 5/0 (PD399(a) key `pd399a` in the pred;
  the lib has no wire_remove_loose_ends parameter).
- Pred per action (`prep_c164_a3_4_pred.log`): DELETE A53 dw_cond #23489, A54 dw_23460 #23460; DELETE-OBJECT A55 #23042 (wires before []), A56 #23501
  ([23519]); PLAN A57 rle_23519; NEW A58 LR7, A59 EQ7, A63 SK3L/R, A64 KI3, A66 OK3, A69 IK3; PLAN wires A60 cfw, A61 nested, A62 stop, A65 const_sr,
  A67 A68 A70 A71 (#31517). WS 8/8, RT PASS, FM w_k3pass #31517.
- E1 checkpoints [0,1,2,6,7,11,12,14,15] == checkpoint_ops == session; step files step_00/01/02/06/07/11/12/16/19 (md5 == recorded).
- X10: x10_start(564d8cbe) 581.8 == plan == session -> Executor 642.7, MAIN 647.8 <= 675; X17 PASS. 15 ops.
- PD399(a) (`prep_c164_a3_4_pd399.log`): G1 w23460 owners [23042, 23501] only; S1 w23460 3 rows at step 1, 0 at step 2 and at step 19 (sim keeps the Wire
  object, recorded); S2 w23519 src [8494] sinks [7606, 23241, 23450] at step 5 and at the end == base sinks outside the deleted nodes.
- Error List (`prep_c164_a3_4_el.log`): CLEARED 0; RAISED 0 (elrule new [] closed []); UNPREDICTED 3 = A66 t_k3o group, A69 t_k3i group (reb), A56
  do_23501 (w23519 on it, kept); STANDING 53, STALE 6 (items 4, 6, 7 = A70 w_k3f; 8, 49, 50 = A80 w_k4f); TOTAL 53 (upper 56). compare F 0/0, W 0/0.
- **DRY main** `prep_c164_a3_4_dry.log:22` `=== DRY FAIL: first_fail=GATE L0 plan FINAL, open_rows_match, plan_in = plan_ring_p5s02d_in[N]; ...` rc 1 (:24).
  **DRY scratch** `prep_c164_a3_4_scr_dry.log:46` same L0 FAIL, rc 1 (:48). Gate: `tools/stagekit.py:2552-2553` calls `plan_in_matches_stem`
  (`:3015-3022`: basename must be `plan_ring_p5s02d_in` or `_in<digits>`); plan 725cd68e's `finalized.plan_in` = `tools/bench/prep_c164_a3_1_plan_in.json`
  (`plan_ring_p5s02d.json:341-344`, written by card 164-3-1). PB never reached (no PB RECORD / BLOCK rows). Not retried (return at first fail).
- NOT RUN (follow the dry): prerun, --scratch-required, check-launch with a launch card.
- check_launch (`prep_c164_a3_4_release.log`): REFUSE "has no dry + prerun PASS record for sha256 f66407f8eb18... plan md5s {...725cd68e}"; scratch log
  `diag_c164_p5s02d_scratch.log` absent; launch card `task_164-3-5.json` absent.
- Prior art released: 4 FIXED lines under "What was done with it" in `archive/peer/2026-10-10-priorart-priorart-c164-a2-3-p5s02d.md` (A1 -> plan :143;
  A3 -> ring-p5c.md:57; and each re-made recipe :27 / :31 = premature_build's disposition exemption). `prep_c164_a3_4_release.log`: released_slugs
  ['contradicted', 'settled-already'], rejected []; fixed_claim both recipes claimed+released.
- STOP RECORDs as found (stop_records.json): scratch sha ca0c1bde684c, main c9377ad5eeb1, released null, verdict [settled-already, contradicted].
  After release: record_state both `kind blocking state released decision(build) allow` (read-only; not stamped - stop_records.json outside the globs).
- Commands for later: scratch `py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c164_p5s02d_scratch.log -- py -u
  tools/recipes/stage_d1_ring_p5s02d_scratch.py --unverified-card tools/bench/cards/task_164-3-5.json`; real `py tools/bgrun.py --material --max-min 50
  --log tools/bench/launch_c164_p5s02d.log -- py -u tools/recipes/stage_d1_ring_p5s02d.py`.
- md5 UNCHANGED (`prep_c164_a3_4_md5.log` U 14/14): stagesim 95a162ba, stagexec a4df7e15, stagekit dd57c1ca, stage_prerun 7605116f, stage_shared b688edd4,
  memory_model 8fb432e4, plan 725cd68e, graph 3d5196ab, EL 26d45c71, VIs 564d8cbe / f9ae7751 / 94ffff94 / 7f2582ae / eb1d0f31. No tool / hook / plan-doc edit.
- OPEN: L0 needs plan_in named plan_ring_p5s02d_in[N]: re-make the plan with its plan_in under that name (164-3-1's maker prep_c164_a3_1_mk.py), or
  judge it a gate false positive (stagekit.py:3015-3022) - both outside this card's globs.
- OPEN: prep_c164_a2_3_lib.pred has no wire_remove_loose_ends row handling (prep_c164_a2_3_lib.py:297-318); PD399(a) added by a separate driver.
