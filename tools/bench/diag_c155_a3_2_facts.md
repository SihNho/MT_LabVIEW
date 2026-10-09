---
type: facts
status: current
date: 2026-10-09
card: 155-a3-2
---
# Card 155-a3-2 facts: P5-1 adopted as byte copy D1_ring_p5s01_20261009_124542.vi (7f2582ae); EL 45 (== hand 45; P5-1a 47, pred 47); graph 15/0, load 597.5 MB; load_by_vi added
## Invariants before `diag_c155_a3_2_inv_before.log` 43/0 (card input pins + P5-1a / P5-1b files, plan/pred/licence/recipes, memory_model 386a4cf4)
## Copy + adopt `diag_c155_a3_2_adopt.log` 5/0 (stagexec.adopt_scratch by import; ASSUMPTION of the assignment session: rename by byte copy, brief_155-a3-2.md:9)
- Source `claudeDev\D1_ring_p5s01b_20261009_123319.vi` 7f2582ae54dc5bc42c3df0bdf3c72d2e (unchanged after); copy `claudeDev\D1_ring_p5s01_20261009_124542.vi`
  7f2582ae54dc5bc42c3df0bdf3c72d2e, 322490 B both (gate C2). adopt/1: stage stage_d1_ring_p5s01b.py, script ..._scratch.py, log diag_c155_p5s01b_scratch.log,
  input p5s01a 2482fe7b, plan_md5s {plan_ring_p5s01b.json: 75a77a00}, required E1,FR,D,TD,PB,PS, gates pass 20 / log_fails 0, iso 2026-10-09 12:45:42.
- adopted_scratch.jsonl c6041e64 -> dd0aa787; adopted_launch returns the record (gate L).
## Final Error List `diag_c155_a3_2_el.log` (elrun --role final vs P5-1a expected aee0d9fe): 45 items == window N 45, extra 0, missing 2, rc 1 MISMATCH, 580.5 s (:81-84)
- Read `errorlist_D1_ring_p5s01_20261009_124542_20261009_124554.json` 2e49ed9f (raw 8aee86b2); bed md5 unchanged; handles 37242 -> 31286 (:79).
- Expected `errorlist_expected_D1_ring_p5s01_20261009_124542.json` ffc4cf66, total 45, 8 entries (`diag_c155_a3_2_elexp.log` 5/0). Dropped P5-1a entries:
  'Enqueue Element: Contains unwired or bad terminal' x1, 'Tunnel: Missing assignment to tunnel' x1; added [].
- elcls read: input 1, not-connected 22, loose-ends 21, two-types 1. vs pred 47 (predicted_total 47, alternative_total 47): input -1, tunnel -1, total -2.
  vs P5-1a 47: same -1/-1, total -2. vs brief hand prediction 45: +0.
- Jev: no JEV-LADDER row for this log; guard_peer RULE-SAME-ROW discharged it by archive/peer/2026-10-09-c154-a3-3b-el47.md (jev_gate.log:6046).
## Graph `diag_c155_a3_2_graph.log` 15/0, 184 s (dry 1/0, prerun 15/0 X10 592.5 vs graph p5s01a; plan `diag_c155_a3_2_graph_plan.json` c6e998c7, mkgraph 4/0)
- `tools/bench/graph_ring_p5s01_20261009_125622.json` md5 6716c49948f097b8ac0e1780930bfab1: 6145 rows, 10717 objs, 25 loops, 23 FS, 74 border tunnels (:304).
- MEM after load 597.5 MB (:24), after read 608.8; handles 45612 -> 45913 (:303); E5 PASS 1 made (Local #31213) / 8 new wires present (:302); LabVIEW gone (:334).
## Rows (`diag_c155_a3_2_nodes.log` 6/0)
- Case #30726 frames [30914, 30922]; selector Tunnel #30897 outer t30893 w30457 <- #29724 'valid' t29900; inner 30914/30922 unwired.
- t_qi SelectorTunnel #31257: outer t31320 w31340 (<- sr_q L inner), inner 30914 t31260 w31261 (src), 30922 t31281 w31247 (src) -> Enqueue 'queue' t30935 (gate Q).
- t_qo SelectorTunnel #31293: outer t31354 w31254 (src -> sr_q R inner t31238), inner 30914 t31329 w31261, 30922 t31348 w31362 (<- Enqueue 'queue out' t30980).
- sr_q on #10170: L #31225 outer t31249 w31243 (<- Obtain 'queue out' t31335) / inner t31248 w31340; R #31222 inner t31238 w31254 / outer t31246 UNWIRED.
- Frame #30914 rows 6, wired 4 (t_ci->t_co w31210, t_qi->t_qo w31261); unwired: selector #30897 t30906, t_el #31000 t31002.
- Local #31213 'records final (1.2 to 1.7)' t31219 w31214 <- sr_n R outer t31016 (frame 686). sr_n L/R, t_ci, t_co: no open rows.
- Open: Enqueue timeout, error in, timed out?, error out; Obtain name, create if not found?, error in, max queue size, created new?, error out;
  declared-open P5-1a owners 11 unwired rows (10068, 11261 x2, 29240, 29625, 376 x2, 5058 x3, 8634).
## memory_model `diag_c155_a3_2_memload.log` 5/0: 386a4cf4 -> c87d170a; added /load_by_vi/7f2582ae.../{value 597.5, vi, cite graph.log:24} only; removed [], changed [].
- Calibration record (no coefficient changed): scratch start 564.3 vs pred 608.5 (d -44.2); peak 601.8 vs X10 652.1 (d -50.3).
## After `diag_c155_a3_2_inv_after.log` 43/0: every pin unchanged (p5s01b 7f2582ae, p5s01a 2482fe7b, tools, plans); 153 P4 + tools/hooks files unchanged;
  no _elc_* / scratch_c155_* in claudeDev; claudeDev P5 files = p5s01 7f2582ae, p5s01a 2482fe7b, p5s01b 7f2582ae; tasklist LabVIEW.exe none (checked after inv_after).
## Files written (md5): diag_c155_a3_2_inv.py f5573b02, _adopt.py 56fd8843, _elexp.py fe7f11d2, _mkgraph.py b9e4a567, _graph.py b8075faa, _nodes.py 5f445a0b,
  _memload.py 94857308, _graph_plan.json c6e998c7, _graph.json 37687d2a, _inv_snap.json ffa6b57a, + the graph / EL / expected / jsonl / memory_model above.
## Script duplication (docs/script-writing.md rule 4): the 7 helpers are copies of diag_c154_a3_3_* / diag_c155_a3_1_inv.py (gate(), flat(), elcls()); extraction outside write globs.
OPEN: the adopted file is a renamed byte copy (assignment-session assumption) - accepted? ; sr_q R outer t31246 unwired - owed by P5-2? ; extract the per-card diag helpers into a shared module (tooling card)?
