# diag_c161_a1_1 facts (card 161-a1-1, PD393(a): every delete_wire op is a required executor checkpoint)

## Pin sweep, written BEFORE the edit (stagexec ddf23a31b10767015da246be8ceaa2e2)
- Code pins of `ddf23a31` (assert on bytes): `tools/bench/selftest_c156_b2_2_invcheck.py:106` (own glob selftest_c15*: re-pin);
  `tools/bench/prep_c160_b3_1_mk.py:46`, `tools/bench/prep_c160_c3_1_pred.py:39`, `tools/bench/prep_c160_c3_1_md5.py:17` (NOT in this card's globs: card 161-a1-2 re-makes).
- Card inputs pinning ddf23a31 (closed cards, record only): task_160-b3-1/c3-1/c3-2/c3-3/e4-1/f3-2.json; task_161-a1-1.json:11 (this card).
- Callers of `checkpoint_ops`: `tools/stagekit.py:2376` (RingSession.CHECKPOINTS), `tools/bench/selftest_c157_innerface.py:165-166`,
  `selftest_c158_runcheck.py:79-86`, `selftest_c158_wire0face.py:258-259`, `diag_c160_f3_2.py:65`, `prep_c157_a1_4_cut.py:70,78`, `prep_c160_c3_1_pred.py:62`.
- Independent required-set code: the validator `tools/stagexec.py:2621-2634`; stagexec self-test T35/T40 `bindk` `:5514-5516`, `:5626`
  (synthetic plan carries `delete_wire 7`, `:5120`); recipe `tools/recipes/stage_d1_ring_p5s01a.py:39` (BIND|{0,last}).
- Executors built with a set: stagekit `:2429`, `selftest_stagexec_s4.py:152-153`, `selftest_c158_runcheck.py:105`, stagexec `:5517-5634`.
- Stored sets: pred `memory_pred.checkpoints` + `e1.checkpoints[].op` of plan_ring_p5s01a/p5s01b/p5s02a/p5s02b_pred.json;
  `delete_wire` actions: p5s02b.json yes, p5s01a/p5s01b/p5s02a none (grep `"op": "delete_wire"`).

## Edit (stagexec ddf23a31 -> a4df7e15c495b9fcbcdadf0d8047bc69)
- `REREAD_KINDS=("delete_wire",)` :2125; `_runs_in` :2129; `required_checkpoints` :2135 (the ONE rule); `checkpoint_ops` :2164 = {0}|that;
  validator :2647-2654 calls it, message adds `delete_wire op(s) not in the set: [..]`. Docstrings checkpoint_ops/Executor updated.
- stagexec self-test: T35/T40 `bindk` + delete_wire; T35d rewritten :5551 (its old stale retry at op 8 after delete_wire op 7 can no longer occur).
## Self-test `selftest_c161_delckpt.log` (last run): RESULT 11/0 on a4df7e15
- (i) p5s02b compiled delete_wire ops = **[1, 4, 8]** (brief named 4, 8; first run FAILED D1 on that); checkpoint_ops = (0,1,2,3,4,5,7,8,9,10) = stored (0,2,3,5,7,9,10)|{1,4,8}.
- (ii) non-collecting dry: without 4 -> CHECKPOINT naming [4]; without 8 -> [8]; without 1 -> [1]; old set -> [1,4,8]; 0 backend calls each; full set accepted.
  FACT: dry with full set PASS, all 10 ops, reads_real [1,2,3,4,5,7,8,9,10], skipped [6] -> gets past ops 5 and 9.
- (iii) p5s01a (0,1,2,4,5,6,7,8,9,10,12,13,14) and p5s01b (0,2,4,6,7,8): validate UNCHANGED. p5s02a stored pred set (0,1,3,6,8,9,15,16,17)
  is REFUSED before and after this card: lacks 12 = move_in run-closer (card 158-a1-2 rule), not delete_wire. 0 delete_wire ops in all three.
## Suites re-run
- stagexec selftest 141/0 (`selftest_stagexec_c161_a1_1.log`, 2nd run; 1st 140/1 T35d); selftest_c158_runcheck 10/0; selftest_c158_wire0face 24/0;
  selftest_c157_innerface 12/1: `P pins` stagesim eb99c6ba != 95a162ba (pre-existing since 160-a1-1, not this card; K1 PASS).
- NOT RUN (guard_peer BLOCK on the c157 log, Jev `new-problem p=0.664`, card peers []): selftest_stagexec_s4, selftest_c156_b2_2_invcheck (re-pinned to a4df7e15, :106).
- md5 UNCHANGED: stagesim 95a162ba, stagekit 0b5bb678, stage_prerun 7605116f, plan f4520b10, pred 48b50b29. No tools/hooks edit.
OPEN: p5s02b gains 3 reads (ops 1, 4, 8), not PD393's 2 - X10 MAIN <= 675 to be re-measured. | `selftest_stagexec_s4.py:163` hand-copies the
old rule (BIND|last) on plan_ring_p4_s01 (6 delete_wire acts): B2 will be refused; outside this card's globs. | c157 pin drift + fp-85; guard_write flags card 160-c3-2 (no result file) as open on ddf23a31.
