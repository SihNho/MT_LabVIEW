---
type: facts
status: current
date: 2026-10-10
card: 158-a2-2
---
# Card 158-a2-2 facts: pre-checks == prediction; the ONE scratch ran all 17 ops (ops 16/17 took connect_term_uid) but FAILED 16/5 (D, CEN2, TD, PB); NOT adopted; LabVIEW gone
## Invariants before `diag_c158_a2_2_inv_before.log` 63/0 (helper `diag_c158_a2_2_inv.py` = copy of diag_c156_a2_1_inv.py, pins/names only)
- Every card pin == file (stagexec 7a712ccb, stagekit 0d8f6d25, plan 4284c22a, pred 31d8e9be, licence e8fd6a98, MAIN b52b9ff5, scratch 71c3aed4, ring-p5 59a0c310 ...);
  P5-1 7f2582ae, P5-1a 2482fe7b, P5-1b 7f2582ae, failed copy 152721 cac5236b; memory_model c87d170a; adopted_scratch dd0aa787; 153 P4 + hooks files snapshotted.
## Pre-checks on stagexec 7a712ccb (records now on these bytes)
- dry MAIN PASS 1/0, PASS-UNVERIFIED PB, coverage 35/36 (`diag_c158_a2_2_dry.log`); dry scratch PASS 1/0, PASS-UNVERIFIED PB, 29/32 (`_scr_dry.log`); E1 PASS 17 ops both.
- prerun MAIN PASS 16/0: X10 planned peak **674.7** MB <= 675 (fail 680.0), R 12; Executor-only 669.6; X17 PASS; X14 WARN rows 23 budget 15 (`_prerun.log`).
- prerun scratch PASS 16/0, X10 669.6, recorded meter 654.0 (old c156 run) (`_scr_prerun.log`); `--scratch-required` rc 3 CENSUS-UNPREDICTED rows 1..8,10..23 (`_scrreq.log`).
- Launch gate on the FULL command (`diag_c158_a2_2_checklaunch.log` 3/0): units [scratch recipe], NAMED ['PB frame-keyed cdiff'], ALLOW.
## Scratch: `diag_c156_p5s02a_scratch.log` segment :285-590 (appended; the recipe's LOG constant, stage_d1_ring_p5s02a_scratch.py:27), BGRUN END rc=1 after 690 s
- Command `... --log tools/bench/diag_c156_p5s02a_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02a_scratch.py --unverified-card tools/bench/cards/task_158-a2-2.json`.
- Work copy D1_ring_p5s02a_20261010_005009.vi (NEW byte copy of 7f2582ae); E1 diff 0 at checkpoints 0,1,3,6,8,9,12,15,16,17 (:336..548), E1 PASS (:549).
- move_in ops 10/11/12: each made a junk Invoke, purged, census 704->705->704 (:444-497); ops 10/11 NOT checkpoints ("diff skipped"); E1 at op 12 diff 0 (:506).
- FATE (read at op 12, :500-505): src_wire=0 for 24091 (src t25235), 24153 (t24367), 24330 (t24360); kept 24285, 24312. Dry run kept all five src wires.
- Op 16: `connect_term_uid #5760 <- #24360 -> err '' (6.3 s)`, node census 704->704 (:535-537), STEPX 16 diff 0 (:540). Op 17: `#5778 <- #24367` err '' (:543), diff 0 (:548).
  Wired act `cfw` not used; per-op class census NOT printed (only node census) -> measured vs predicted R1 (SelectorTunnel 1, Outer 1, Inner 2, Wire 2) not available per op.
- Whole-run CENSUS-ALL net: SelectorTunnel 3, OuterTerminal 6, InnerTerminal 10, Wire 10 (new 12), CaseStructure 1, Diagram 2, Function 2, SR L/R 1/1 (:554-556).
- FAIL D new wires 21 vs sim 22, lost 12 == 12 (:552). FAIL CEN2 measured Wire 12/Outer 6/Inner 10 vs declared 1/1/2 (:553).
- FAIL TD unwired (25223, 1, InnerTerminal) (:557). ExecState 0 (by design) (:558).
- FAIL PB (FATAL) extra open pairs (376,'cal cluster path'), (376,'file size') (:559) -> STOP before save (:560). Sinks = t5760 / t5778 of ops 16/17.
- METER start 610.9 MB (:334) vs 597.5 (+13.4); peak 664.6 MB (:547, :585) vs planned MAIN 674.7 (-10.1) / scratch X10 667.0 (-2.4); MEM, MEML, IN, GONE PASS (:586-589).
  scratch_tail reads METER over the WHOLE file (stagekit.py:2227): old segment peak 654.0 < 664.6, so the value is this run's.
- Handles: 0 before restart, 46017 at start (:334), 46624 after work, 34008 at exit (:578); H5 refs opened 10 == closed 10; H2/H3 pins PASS; H4 work copy deleted (:568); H6 files left [].
## Not done (need a structural PASS): adopt, final Error List, graph json, load_by_vi. memory_model c87d170a, adopted_scratch dd0aa787 unchanged.
## Failed copy D1_ring_p5s02a_20261009_152721.vi (cac5236b) + tools/bench/resume/resume_plan_ring_p5s02a_20261009_153334.json NOT deleted (only after adoption, brief item 6).
## Jev ladder / review
| log | ladder class p | NEXT-ACTION | what I did | result |
| diag_c156_p5s02a_scratch.log | new-problem p=0.868 (jev_gate.log 01:02:00) | hypothesis review owed | dispatched claude -Role hypothesis (flags.peers) | ANSWERED 402 s, $2.85 |
- `archive/peer/2026-10-10-c158-a2-2-p5s02a-loopface.md`: my claim (ops 16/17 left no wire) REFUTED from the run's own json: 5760/5778 wired via new case
  tunnels #31546/#31557 (json:9761-9786, :9698-9708); alternative: PB keys sources by `<tunnel>/f<frame ordinal>`, ordinal by uid rank, reversed for negative
  sim uids (vigraph.py:287-291, 322, 812-836); D/TD = uid bookkeeping (LabVIEW deleted 24091/24153/24330, recycled 24153 for w_prog); CEN2 fails on any run
  (pred census UNPREDICTED, pred.json:23-47). Offline test proposed (section 4). Disposition written; no action taken.
## Invariants after `diag_c158_a2_2_inv_after.log` 61/0 + `_inv_after2.log` 62/0: every pin unchanged; 153 P4 + hooks unchanged; s09 D1_ring_p4s09_20261009_060515.vi
  eb1d0f31 (after only - not pinned in the before run), P5-1a 2482fe7b, P5-1 7f2582ae; no _elc_* / scratch_c15*_*; tasklist LabVIEW: none.
## Files written: diag_c158_a2_2_inv.py, _checklaunch.py, _adopt.py (unused), _peer_task.md, the logs above, this file; archive peer file + disposition.
OPEN: run the review's offline PB-keying test (negative-uid frame ordinal) before deciding gate artefact vs real difference?
OPEN: CEN2 declared census covers only the case op (pred census UNPREDICTED) - is CEN2 expected to FAIL on this plan, and the scratch's census the measurement?
OPEN: the scratch recipe's LOG is fixed to the c156 log (appended; METER over whole file) - give the retry its own log?
