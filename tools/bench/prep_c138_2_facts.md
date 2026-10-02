# card 138-2 facts - X10 counts whole-VI reads from the SOURCE (PD299(b)(c)), offline, 2026-10-02

Level: STRUCTURAL/offline (AST + dry + memory model); no LabVIEW run.

## What changed (tools/stage_prerun.py md5 878d530d)
- `x10_source_reads` (:2109): every call site of a whole-VI read (`census_snapshot report_all read_live live_graph census
  uid_index read_terms`) x the times its enclosing function/lambda is called (summed over that function's call sites,
  recursively). Once: `K.run(body)`, `s._op(verb, fn)`, `s.safe(label, fn)` (:2093; stagekit.py:298-300, :587-592), a for
  loop's `iter`, a comprehension's first `iter` (:2167). UNBOUNDED (-> X10 UNMEASURED = FAIL): read in a loop body /
  comprehension element, fn or lambda passed to any other call or used as a value, recursion. Both `if DRY` branches count.
  A parameter that shares a module function's name is not that function (:2133). Sessions = Stage.start/restart sites; with
  more than one session the total is printed as the per-session bound (reads not split).
- Edit branch (:2268) and read-only branch: R = 1 + max(source, dry). Executor branch (:2309): R = plan checkpoints +
  script source reads; `exec_peak_mb` keeps the Executor-only figure. Prerun prints `FACT  X10 whole-VI reads: source n
  [read@line xk ...]; dry executed m; sessions s`.

## Self-tests (latest RESULT line of each log)
| self-test | result | note |
|---|---|---|
| selftest_x10_c138_2 (new) | 12/0 (`selftest_x10_c138_2.log:57`) | S1 DRY-guarded+lambda+helper: source 5, dry 2 -> R 6; S2/S2b/S3/S4/S6 loop, element, key=, unknown caller -> UNMEASURED; S5 2 sessions; S7 a/b source 2; S8 b R 14 |
| selftest_x10_c136_2 | 6/0 (`selftest_x10_c136_2_c138_2.log:353`) | unchanged asserts; E6 now prints the source count (below) |
| selftest_x10_c132_1 | 4/0 (`selftest_x10_c132_1_c138_2.log:101`) | T1 re-pointed to exec_peak_mb 678.5 vs measured 680.4 (total 683.6); T3 b re-pinned on plan_ring_p3b2b.json |
| selftest_x10_c132_4 | 6/0 (`selftest_x10_c132_4_c138_2.log:29`) | T1 reader source 1 dry 0 R 2 |
| selftest_x10_c130_1 | 9/0 (`selftest_x10_c130_1_c138_2.log:173`) | T1/T2 pinned on exec_peak 744.0/703.6 (with 2 source reads 749.1/708.7); T4 p3a 677.1 PASS |

## c132_1 T3 stale fixture (PD299(c))
- Cause: recipe b's input `scratch_c133_6_ring_p3b2a_20261002_093837.vi` (md5 6cc69221) is deleted; its dry stops at K1
  (`prep_c138_2_x10.log`: `GATE K1 input md5 == 6cc6922192b3e330f163561bb95a8115`), so no Executor is built.
- Re-pin: T3 b feeds x10_gate the Executor record built from the EXISTING `tools/bench/plan_ring_p3b2b.json` (checkpoints by
  the recipe's rule stage_d1_ring_p3b2b.py:27-28); T3 a keeps the probe (input D1_ring_p3b1_20261002_060910.vi exists).

## X10 rerun on the P3b-2 recipes (`tools/bench/prep_c138_2_x10.log`, 2/0)
| recipe | source reads | dry reads | dry | R (was) | peak MB (was) | verdict | recorded prerun |
|---|---|---|---|---|---|---|---|
| tools/recipes/stage_d1_ring_p3b2a.py | 2 (census_snapshot @31 x2) | 0 | PASS | 16 (14) | 676.9 (671.8) | PASS, unchanged | stage_prerun_c134_p1_p3b2a_prerun.log:101 |
| tools/recipes/stage_d1_ring_p3b2b.py | 2 (census_snapshot @33 x2) | 0 | FAIL at K1 (input deleted) | 14 (12), plan record | 672.1 (667.0) | PASS on the plan record; UNMEASURED on its dry | stage_prerun_c134_5_p3b2b_prerun.log:97 |

## The case PD299(b) named
- `tools/bench/diag_c136_1_routes.py` (the cycle-136 edit diagnostic): source 57, dry 3 -> R 58, peak 806.1 MB > 690 ->
  X10 FAIL (`selftest_x10_c136_2_c138_2.log:352`). With the dry count it would have been R 4, peak ~669.5, a PASS.
