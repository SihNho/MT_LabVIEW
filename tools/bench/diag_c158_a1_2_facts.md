---
type: facts
status: current
date: 2026-10-09
card: 158-a1-2
---
# Card 158-a1-2 facts: PD384(b) run-closing checkpoints built, offline; part (a) untouched
## What changed (tools/stagexec.py, base 69b1a301 -> df82d75eeea3447d45a17b1757198720)
- NEW `move_in_runs(ops)` stagexec.py:2028 (maximal runs of consecutive move_in ops; last = run closer).
- `checkpoint_ops` stagexec.py:2044: {0, last} | BIND_KINDS | run closers (was every move_in).
- NEW `run_fate_lines(run, ops, step_of, read_rows, bind_term)` stagexec.py:2053: fate_lines of every move_in of the run,
  prev_terms = sim terminals before the run's first op; FATE line format unchanged, step=<n> = each move_in's plan step.
- Executor.run: run_of (runs inside (from_step, last_k], a run cut by stop_after closes at last_k) stagexec.py:2522;
  `need |= run closers` stagexec.py:2525 -> ExecStop CHECKPOINT before op 1 (collecting dry backend: a pre-op row);
  FATE-UNREAD branch removed stagexec.py:2581; FATE emitted only at a run-closing read stagexec.py:2602.
- `dry_run(..., checkpoints=None)` stagexec.py:4589/4603: passes the set to the Executor (None = every op, as before).
- In-file selftest T35/T40 fixture: `bindk` += move_in run closers stagexec.py:5392-5393 (the old hand set {2,3,8,12} lacked
  run closer 1 and is now refused; first after-run crashed there: prep_c158_a1_2_after.log:17, suite out ..._c158after_stagexec.out).
- Not changed: stagekit 0d8f6d25 (RingSession still calls checkpoint_ops, stagekit.py:1929; its comment still says
  "every move_in op"), stagesim eb99c6ba, addrcheck 207beb0d, stage_prerun 9decb20f; loop_inner_face_route, cfw,
  connect_nested_v1 untouched; no plan/pred/licence/recipe/P5 file, no hook edited; no LabVIEW process at any point.
## Measured
- selftest_c158_runcheck.py 10/0 (selftest_c158_runcheck.log:23): R1 p5s02a runs [(10,11,12)], checkpoint_ops
  (0,1,3,6,8,9,12,15,16,17) :4; S1/S2 set missing 12 / 17 on a non-collecting sim backend -> 'CHECKPOINT: ... [12]' / '[17]',
  0 ops dispatched :7-8; S3 collecting backend: one pre-op CHECKPOINT row :9; E1 reads at 1,3,6,8,9,12,15,16,17 :11;
  E2 run_fate_lines called once, at op 12, run (10,11,12); six FATE step=10 lines = the six M3 wires :12-18;
  E3 no FATE-UNREAD (full set and every-op run) :19; E4 recorded step_12 terminals -> same six lines :20.
- selftest_c157_innerface.py: K1 want_cp updated to (0,1,3,6,8,9,12,15,16,17) (selftest_c157_innerface.py:164, docstring :26-27);
  F1-F3 unchanged and PASS; 13/0 (prep_c158_a1_2_after2.log:29).
- prep_c158_a1_1_regress.py after -> prep_c158_a1_2_after2.log: A1 3 op lists EQUAL :8-10; A2 200 stored plans compile
  EQUAL, 0 differ :11; A3 checkpoints = before - move_in + run closers (p5s02 and p5s02a drop 10,11) :12-15; A4 :16.
- Suite (after2.log:17-30) == before.log:9-21: stagexec 141/0, stagesim 106/0, c155 21/0, c120 1/0, case_frame_c124 28/1 (V02,
  as before), stagexec_gate 13/0, tunnel_naming 21/0, fs_c126 13/0, t6_regress 9/2 (c147_b1_2, t4, as before),
  addrcheck_s5 22/0, t7_ring 35/0, c156 20/0, c157 13/0; plus c158_runcheck 10/0. RESULT 9/0, BGRUN END rc=0 after 955 s.
- c155 / c156 pin stagekit only (unchanged): no md5 re-pin was needed.
OPEN: the stagexec in-file T35/T40 fixture (bindk) was updated to the new rule - not named in the card's change list; accept?
OPEN: stagekit.py:1929 comment still reads "every move_in op" (left: card says touch stagekit only if the call needs it).
