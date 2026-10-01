# Brief 130-1 — X10 memory check fixed, then P3b re-cut by predicted memory (offline)

Decisions applied (do not re-open): PD267(b), PD266(b), PD265(b)(c), PD261(d), PD264(a)(b) in
`docs/d1-loop12-17-split-plan.md:2889-2973` (frozen; read only those lines). Device decision:
`docs/violation-decisions.md` 2026-10-02 02:57.

## Part A — X10 (tools/stage_prerun.py) — target ≤ 25 min
1. X10 predicts a LabVIEW stage recipe's peak memory from its COMPILED plan and its checkpoint set:
   `peak = start + R × read + N × (edit + other)`, R = whole-VI checkpoint reads in the set, N = ops.
   Coefficients come from ONE model file (e.g. `tools/bench/memory_model.json`) whose every number cites its log line:
   start 570 (pin2 k0), read 2.53 and edit 0.58 (`tools/bench/diag_c129_6_mem.log:40-56,58-88`), other ≈ 0.8
   (PD265(b), pin2's 3.9 MB/op). It works for ANY stage recipe (not P3b-specific code).
2. X10 FAILS when the prediction > 675 MB, and FAILS `UNMEASURED` for a LabVIEW stage recipe whose plan or checkpoint set
   it cannot compile. (Today it printed UNMEASURED and PASSED: `tools/bench/stage_prerun_c129_1_p3b1_prerun.log:137`.)
3. Self-test (new file): the 129-1 bytes of `tools/recipes/stage_d1_ring_p3b1.py` (read after every op, from git
   history; ≈ 723 MB) → FAIL; the 129-8 bytes (current, 688.5 MB) → FAIL; a recipe with no plan → FAIL UNMEASURED; a
   small proven-stage recipe that passed before → PASS. Rerun the existing stage_prerun self-tests and list every FAIL
   with its id (E1 of `selftest_stage_prerun_c106e` is known red, fp-20 — report, do not fix here).

## Part B — re-cut — target ≤ 25 min
4. Re-cut `tools/bench/plan_ring_p3b1_in.json` + `plan_ring_p3b2_in.json` (70 actions together) to minimise the LARGER
   X10 peak. Constraints (PD261(d)): each ≤ 40 actions, dependency-closed, IMAQ Copy + every guard row in the same half,
   each RLE row in the half of its loose end. Use `tools/bench/plan_ring_p3b_split.py`.
5. Finalize both; show the P3b-1 → P3b-2 replay reaches the same end graph as the unsplit 70 (cdiff, objects/owners/
   terminals/wires as `plan_ring_p3b_split_c129_7.log`). Preds carry `memory_pred` written by script; both recipes keep
   `{0, len(ops)} | BIND`.
6. X10 value printed for BOTH halves (P3b-2 from its compiled plan; its dry/prerun stay owed until the rebase, PD264(b)).
7. P3b-1 recipe + `tools/bench/stage_d1_ring_p3b1_scratch.py`: dry PASS + prerun PASS, own processes; then
   `py tools/stage_prerun.py --scratch-required tools/recipes/stage_d1_ring_p3b1.py`, report its exit code.
8. Prior-art only if the launch gate asks for the new bytes; report the verdict, do not annotate.

## Return
Return at the first unexpected result (finish the step, record facts). If no cut reaches ≤ 675 on both halves, return the
best cut's (N, R, peak) per half and stop — a third half is the user's decision, not this card's.
Report per half: N, BIND count, R, predicted peak, dry/prerun line refs.
