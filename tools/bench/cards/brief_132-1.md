# Brief 132-1 — stage_prerun tooling before P3b-2 (OFFLINE, no LabVIEW) — the gate-fp drain card

Decision: `docs/d1/tooling.md` **PD275(a)-(e)** (read it first; also PD272 / PD274 in `docs/d1/ring-p3b.md`).
Card 132-2 runs beside you in LabVIEW (read-only graph read of P3b-1); you never touch LabVIEW, never launch a recipe.
If you edit `tools/stagexec.py` or `tools/stagekit.py`, rerun `tools/bench/c125_1_offline_measure.py` (PD252(a)).

## A — X10 final-read term (PD275(a)(b))
1. Add the final whole-VI read term to X10 (`tools/stage_prerun.py` `x10_model_peak`/`x10_gate`, coefficients in
   `tools/bench/memory_model.json`, each cited: +17.4 MB `stage_d1_ring_p3b1_scratch_pin4.log:446-447`, launch peak
   680.4 MB `stage_d1_ring_p3b1.log:430`). FAIL threshold for the model WITH the term = 690 (PD275(b)).
2. Self-test (extend `selftest_x10_c130_*`): P3b-1's current recipe bytes predict 680.4 ± 3 MB; existing cases keep their
   verdicts or you report which flip and why (numbers).
3. MEASUREMENT to report: X10 prediction for `tools/recipes/stage_d1_ring_p3b2.py` on its current (provisional) plan.

## B — per-op tunnel-name gate (PD275(c))
Add to `tools/recipes/stage_d1_ring_p3b2.py` (stagekit style, <=120 lines total stays the target) a gate that after each
crossing op compares each NEW tunnel's name with the simulator's predicted name for that op, read from the finalized
plan / `tools/bench/sim/ring_p3b2/` files — never a typed name. Prefer a reusable helper in stagekit/stagexec if one
fits (P4/P5 reuse it). Offline proof: a self-test that feeds the gate one matching and one mismatching recorded case
(pin3 op 26 `Image Out` vs sim `''` is a recorded mismatch; pin4 ops are recorded matches).

## C — P3b-2 expected Error List, computed (PD275(d))
A script `tools/bench/errorlist_expect_p3b2.py` that derives P3b-2's expected class totals from the simulator's
retired / loose-end wire set and `tools/bench/errorlist_expected_D1_ring_p3b1_20261002_060910.json` (53, loose ends 22).
Run it on the CURRENT provisional plan and report the predicted totals; it is re-run after the rebase (card 132-3).
Also: `tools/bench/diag_c131_5_stubs.py` must make its PASS depend on its check (retrospective-cycle131 carry).

## D — gate-fp drain (PD275(e))
`py tools/gate_fp.py drain --id <fp-n> --fixed <path:line> --selftest <name>` for fp-19 (X5 WIRE_VERB_RE vs SP_WIRING),
fp-20 (X16 term_class on a `Local` create; `selftest_stage_prerun_c106e` E1 must go green), fp-21 (dry/prerun X1 on a
provisional base: dry against stagesim's END graph of the previous stage, `plan["base"]["sim_of"]`). fp-28: close as a
CORRECT refusal, no code change (cite `archive/peer/2026-10-02-retrospective-cycle131.md`); if `gate_fp.py` has no
close form, report that and leave fp-28 open.
Run the full stage_prerun self-test set at the end (counts per suite).

## Return
`result/1` with the counts, the X10 numbers (P3b-1 predicted vs 680.4; P3b-2 predicted), the gate self-test results, the
expected-EL prediction, the fp table, and every edited file's md5. Return at the first unexpected result.
