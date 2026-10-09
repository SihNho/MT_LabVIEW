---
type: facts
status: current
date: 2026-10-09
card: 156-a2-2
---
# Card 156-a2-2 facts: launch ALLOWED; the ONE scratch FAILED 14/2 at op 16 of 17 (ExecStop ADDRESS on inner face #24360 of LoopTunnel #24357); NOT adopted; LabVIEW gone
## Invariants before `diag_c156_a2_2_inv_before.log` RESULT 60/0 (helper `diag_c156_a2_1_inv.py` ab4ff13c called unchanged; every card-156-a2-1 pin == file)
## Launch gate on the FULL command text `diag_c156_a2_2_checklaunch.log` 3/0 (`diag_c156_a2_2_checklaunch.py`, calls stage_prerun.check_launch(cmd))
- CMD `py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c156_p5s02a_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02a_scratch.py
  --unverified-card tools/bench/cards/task_156-a2-2.json`; UNITS [the scratch recipe]; NAMED ['PB frame-keyed cdiff']; `ALLOW` (why ''). Flag after the
  script: the recipe ignores unknown argv (scratch_offline_modes only reads --el-advisory*, stagekit.py:2210-2219). Pre-checks not re-run (no md5/record moved).
## Scratch `diag_c156_p5s02a_scratch.log` (md5 8ba9071d) BGRUN END rc=1 after 379 s; RESULT FAIL 14/2 (:277)
- L0, K1-K3, SG, L1 PASS (:28-49); L1 checkpoints = ops (1, 3, 6, 8, 9, 15, 16, 17) (:49,55). Ops 10/11/12 (move_in) are NOT checkpoints:
  `STEPX 10/11/12 move_in ... diff skipped (not a checkpoint)` (:177,196,215) -> no per-op E1 for mv_376 / mv_3052 / mv_3453 (pass item 2 NOT met).
- E1 diff 0 at every checkpoint reached: ops 0,1,3,6,8,9,15 (:52,64,91,124,143,158,243). PRIM PASS c_deq #31262 'Dequeue Element', c_rel #31266 'Release Queue' (:88,121).
- Bound: sr_q7 {-1:31347,-2:31352}; c_tmo #31448; c_case7 Case #31308 frames/tunnel {-29:31506,-30:31517,-31:31485}; t_el7 #31568 (:64,143,158,243).
- move_in #376/#3052/#3453 -> Diagram #31506: each made a 6-terminal 0-wired junk Invoke, purged, census 704->705->704 (:160-213); op 13 one STALE-ADDRESS retry (:217).
- STOP op 16 `tunnel` acts 18-20 ids t_in1 / w_in1_t / w_in1_376: "ADDRESS: #24360 is an INNER face of LoopTunnel #24357: only the outer face's
  owner route is measured (l2a1_faces_81.log)" (:254-255), raised at tools/stagexec.py:1784-1787. Op 17 not run.
- Plan routes: op 16 recorded `route: "cfw"`, unroutable null (plan_ring_p5s02a.json:1326-1328); action 19 src {uid 24357, term_uid 24360} (:419-427).
- sim summary: wire 24330 (src t24360 on #24357) fate "ambiguous"; allow_either [3060,24190,24288,24360,24367,25235] (sim/ring_p5s02a/summary.json:2884-2900).
- METER start 605.0 MB (:50) vs 597.5 (+7.5); peak 654.0 MB (:279) vs X10 MAIN 672.1 (-18.1) / Executor 667.0 (-13.0); MEM, MEML, IN, GONE PASS (:280-283).
- Handles: 0 before restart (:41), 46063 at start (:50), 40540 after work/exit (:262,272); H5 refs opened 11 == closed 11 (:261); H2/H3 pins PASS.
- Saved (gui_save, broken by design, ExecState 0): claudeDev\D1_ring_p5s02a_20261009_152721.vi md5 cac5236b171aab9d82283d7dff9611ef 323358 B (:250);
  resume record tools/bench/resume/resume_plan_ring_p5s02a_20261009_153334.json from_step 15 (:253). Left in place (H6, :271); NOT adopted.
## Not done (depend on a structural PASS): adopt, final Error List, fresh-load graph json, load_by_vi entry. memory_model c87d170a and adopted_scratch.jsonl
  dd0aa787 unchanged.
## Jev ladder / review
| log | ladder class p | NEXT-ACTION | what I did | result |
| diag_c156_p5s02a_scratch.log | new-problem p=0.738 (jev_gate.log, 15:34:40) | hypothesis review owed | dispatched claude -Role hypothesis (flags.peers) | ANSWERED 234 s |
- Review `archive/peer/2026-10-09-c156-a2-2-p5s02a-innerface.md`: claim "inner-face route missing in the executor" attacked; alternative: the sim kept the
  ambiguous wire 24330 so the route check chose `cfw`, while LabVIEW dropped it at mv_376, so the live read had t24360 unwired and connect_route fell to
  the triple route (stagexec.py:1489-1490, :1563); the op-15 diff 0 is blind to it via allow_either (stagexec.py:2533-2534). Live read not logged.
  Offline test proposed: connect_route on sim step_15_tunnel.json with #24360 wired vs wire_uid 0. Prediction: op 17 source #24367 stops the same way.
## Invariants after `diag_c156_a2_2_inv_after.log` RESULT 59/0: every pin unchanged; 153 P4 + tools/hooks files unchanged; no _elc_* / scratch_c156_*;
  claudeDev P5 files = p5s01 7f2582ae, p5s01a 2482fe7b, p5s01b 7f2582ae, p5s02a_20261009_152721 cac5236b (new). tasklist LabVIEW: none.
## Files written: diag_c156_a2_2_checklaunch.py/.log, _inv_before/_after.log, _peer_task.md, _peer.log, this file; the recipe wrote the scratch log/json/sum,
  the VI and resume record above; archive peer file (+ disposition).
OPEN: which explanation holds (missing inner-face route vs ambiguous-wire fate) - run the offline connect_route test before any retry?
OPEN: ops 10-12 are not E1 checkpoints in this plan's compile (L1 :49) though PD379(e) asks E1 per move_in op - a recipe/plan change for the retry?
OPEN: keep or delete the failed work copy D1_ring_p5s02a_20261009_152721.vi (cac5236b) and its resume record (from_step 15)?
