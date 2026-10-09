---
type: facts
status: current
date: 2026-10-09
card: 154-a3-3b
---
# Card 154-a3-3b facts: heading fixed; P5-1a scratch PASS 23/0, ADOPTED 2482fe7b; EL 47 (s09 45, pred 48); graph 15/0, load 602.6; load_by_vi added
## Step 0, heading time format (Edit tool, one line)
- `docs/violation-decisions.md:1992` "07:0x" -> "07:00"; md5 34da9f4f -> 6497e984; diff vs git HEAD (34da9f4f) = exactly 1 changed line (`diag_c154_a3_3b_diff.log`, 2/0;
  the log's first segment died on my own result_line call, segment 2 PASS). `py tools/violations.py`: inference-over-measurement "answered 2026-10-09 07:00",
  "0 slug(s) awaiting a response". guard_cycle did not refuse the launch.
## Pre-checks on MAIN aee20128 / scratch 3b02d9a7 (== diag_c154_a3_2b / a3_3 facts)
- dry MAIN 1/0 (`diag_c154_a3_3b_dry.log`); prerun MAIN 16/0, X10 677.3, Executor 672.2, X17 PASS, X14 WARN rows 20/15 (`_prerun.log`); prerun scratch 16/0,
  X10 672.2 (`_scr_prerun.log`); `--scratch-required` rc 3, CENSUS-UNPREDICTED rows 1..20 (`_scrreq.log`); `--check-launch` ALLOW rc 0 (`_checklaunch.log`).
- Invariants before 40/0 (`diag_c154_a3_3b_inv_before.log`; card pins + step-8 pins, violation-decisions pinned at its post-fix 6497e984).
## Scratch (ONE run) `diag_c154_p5s01a_scratch.log` RESULT 23/0 (:271), BGRUN END rc=0 after 493 s
- NEW byte copy of eb1d0f31 = `claudeDev\D1_ring_p5s01a_20261009_101219.vi` (K3); saved md5 2482fe7bf3426e18b0801c77ec629073, 322158 B (S2, PS).
- SG 0 rows; L1 20 actions -> 14 ops, checkpoints (0,1,2,4,5,6,7,8,9,10,12,13,14); every STEPX checkpoint diff 0; E1 PASS (14 ops); NG PASS (0 ops).
- PRIM PASS c_obt #31258 'Obtain Queue', c_enq #30756 'Enqueue Element', c_inc #31078 'Increment'. FR PASS 8 created on frames [686, 4866, 30922].
- D new 10 == sim 10, lost 1 == 1, reuse none; TD renames 0, unlicensed []; PB == pred 21 rows / 19 open pairs (:240). CENSUS-ALL lost 0 (:235-237). X11 n/a (CLEAN, prep).
- Memory: METER start 578.1 MB (:68) vs pred start 602.6 (d -24.5); peak 618.0 vs X10 MAIN 677.3 (d -59.3) / Executor 672.2 (d -54.2) (:273); MEM/MEML/IN/GONE PASS (:274-277).
- Handles: PH 45688 -> 46181, HB PASS (:241-242); H5 9 == 9 (:255).
## Adopt `diag_c154_a3_3_adopt.log` 3/0 (stagexec.adopt_scratch by import)
- `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p5s01a_20261009_101219.vi` md5 2482fe7b..., input eb1d0f31; adopted_scratch.jsonl -> c6041e64.
## Final Error List (elrun) `diag_c154_a3_3_el.log`: 47 items == window N 47, rc 1 MISMATCH vs s09 expected (extra 2, missing 0); 630.5 s
- Read `errorlist_D1_ring_p5s01a_20261009_101219_20261009_102108.json` 286e7c12; bed md5 unchanged; handles 37245 -> 31286.
- Expected `errorlist_expected_D1_ring_p5s01a_20261009_101219.json` aee0d9fe, total 47, 10 entries (`diag_c154_a3_3_elexp.log` 5/0). Dropped s09 entries [];
  added 'Enqueue Element: Contains unwired or bad terminal' x1, 'Tunnel: Missing assignment to tunnel' x1.
- elcls read: input 2, tunnel-missing-assignment 1, not-connected 22, loose-ends 21, two-types 1. vs pred 48 (carry and no-carry both 48): input -2, tunnel +1, total -1.
  vs s09 45: input +1, tunnel +1, total +2. No Obtain Queue item (pred #-3); TC2 shows as the tunnel class, not `input`.
## Graph `diag_c154_a3_3_graph.log` 15/0, 171 s (dry 1/0, prerun 15/0 with --graph graph_ring_p4s09_20261009_062044.json; plan `diag_c154_a3_3_graph_plan.json` 6d8ffdfd)
- `tools/bench/graph_ring_p5s01a_20261009_103621.json` md5 bd67a51131d6205d170200e098a9bd99: 6134 rows, 10693 objs, 25 loops, 23 FS, 74 border tunnels (:304).
- MEM after load 602.6 MB (:24), after read 614.3; handles 45655 -> 45930 (:303). E5 PASS 8 made / 10 new wires present (:302). 1055 lines at :42, :278 (gates passed).
## New-node rows (`diag_c154_a3_3_nodes.log` segment 2, 4/0; segment 1 FAILED my gate N: Case / ControlTerminal own no rows, script fixed)
- Obtain #31258 (frame 686): 'element data type' t31287 w30830 (from 1-D DBL const #30766 t30765); unwired: name, create if not found?, error in, max queue size, queue out, created new?, error out.
- Enqueue #30756 (frame 30922): 'element' t30945 w30993; unwired: queue, timeout, error in, queue out, timed out?, error out.
- Case #30726 frames [30914, 30922]; selector Tunnel #30897 outer t30893 w30457 <- #29724 'valid' t29900 (gate S PASS). Control #31071 'records final (1.2 to 1.7)' w31163 <- const #30845.
- Count SR sr_n on #10170 (the refnum SR sr_q is op 18, P5-1b, not built): L #31004 outer t31024 w31253 (<- const #31015) / inner t31023 w31194; R #30996 inner t31007 w31171 / outer t31016 UNWIRED.
- Case tunnels: t_el #31000 outer w31017, inner 30922 w30993 / 30914 open; t_ci #31175 outer w31194, inner 30922 w31162 / 30914 open;
  t_co #31186 outer w31171 (src), inner 30922 w31206 / 30914 OPEN (= the 'missing assignment' item). Increment #31078 x w31162, x+1 w31206.
- Declared s09 open owners: 11 unwired rows found by owner (10068, 11261 x2, 29240, 29625, 376 x2, 5058 x3, 8634); the PB gate's 19-pair check PASSED (scratch :240).
## memory_model `diag_c154_a3_3_memload.log` 5/0: 6f2b5687 -> 386a4cf4; added /load_by_vi/2482fe7b.../{cite,value 602.6,vi} only; removed [], changed [].
## After `diag_c154_a3_3b_inv_after.log` 40/0: every pin unchanged; 153 P4 recipe/plan + tools/hooks files unchanged; no _elc_/scratch_c154_ left; tasklist LabVIEW 0.
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c154_a3_3_el.log | new-problem 0.598 | hypothesis review owed | review c154-a3-3b-el47 | ANSWERED: claim stands; elrule rule A over-counts optional primitive sinks |
| diag_c154_a3_3_nodes.log | new-problem 0.658 | hypothesis review owed | review c154-a3-3b-nodes | ANSWERED: not refuted; gate S added, re-run 4/0 |
OPEN: elrule.py:153-158 counts optional unwired primitive sinks (Obtain) and has no 'tunnel' class (archive/peer/2026-10-09-c154-a3-3b-el47.md:55-59) - fix in a tooling card?
