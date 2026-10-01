# Brief for card 129-2 (cycle 129 judgement) — decisions: `docs/d1-loop12-17-split-plan.md` Pre-decided 264(c)(d)(e)

SCRATCH RUN of ring step P3b-1, on a byte copy. **The real recipe is NOT launched in this card** (that is card 129-3).

## 0. Time arithmetic (budget 55 min; the 60-min backstop refuses NEW bgruns after bind + 60)
Measured on P3a (card 124-8, 22 rows): bind 17:24:28 → scratch pin log 17:21–18:0x, launch saved 18:05:40, final read
ended 18:30:28. For P3b-1 (40 rows):
- prior-art review: ~10–13 min — run it in the BACKGROUND (bgrun) and write the helpers while it runs (step 2)
- two helper scripts as cuts of the P3a ones + their dry/prerun: ~8 min (overlaps the review)
- scratch run `pin`: ~15 min · scratch Error List pin, count-only: ~5–7 min
- measured census into the pred + dry/prerun of the recipe again: ~3 min
- total ≈ 40–45 min. Report real minutes per step; `cost.minutes` must match bind → return.

## 1. Step 0 (seconds)
`py tools/stage_prerun.py --scratch-required tools/recipes/stage_d1_ring_p3b1.py` — record exit code + line (exit 3 is
expected: new classes Unbundler/Select; the full scratch run happens regardless, D-2026-10-01-01).

## 2. Step 1 — prior-art review for P3b-1, dispatched first
`tools/prior_art_review.py` on `tools/recipes/stage_d1_ring_p3b1.py` (new create classes Unbundler #157, Select #529 from
the claudeDev byte copies of vi.lib `Error to Warning.vi` / `Merge Errors.vi`; PD261(a)). Prediction: `PRIOR-ART: novel`.
ANSWERED is required before step 3. Return its verdict, archive path and verdict card. Any verdict other than `novel` is
the first unexpected result: return. **Do not annotate the review** (the judgement session does).

## 3. Step 2 — helpers (while the review runs)
`tools/bench/stage_d1_ring_p3b1_scratch.py` and `tools/bench/stage_d1_ring_p3b1_el.py`, cuts of
`stage_d1_ring_p3a_scratch.py` (81 lines) and `stage_d1_ring_p3a_el.py` (97 lines): import the recipe UNCHANGED, run its own
body on a dated byte copy `claudeDev\scratch_c129_ring_p3b1_<ts>.vi` of the P3a bed (md5 `4dfa44aa…`), keep the NEWOBJ /
CENSUS-ALL observation lines. ≤ 120 lines each, on stagekit. The Error List read of the scratch uses
`errorlist_check.py --count-only --role scratch` (the full per-item read follows automatically only when the per-class counts
differ). Dry + prerun of each helper as the launch gate requires, each in its own process.

## 4. Step 3 — scratch run, `pin` mode
Predictions (from the recipe's docstring and `plan_ring_p3b1_pred.json`): L1 40 actions; E1 every checkpoint == sim; FS one
FlatSequence with 3 frames on diagram 27219; **RB: the Unbundler terminal on Select.s's wire reads back `status`**; D new/lost
wires == sim; TD every base terminal that was wired stays wired; PB cdiff(S1, end) == 16 rows; HB handles ≤ +700; PS saved
(scratch only), input unchanged. CEN2 is CENSUS-UNPREDICTED: record the measured census delta (all classes, with NEWOBJ
owner lines). LabVIEW closed and verified gone after the run.

## 5. Step 4 — scratch Error List pin
Prediction: 54 items (P3a's 55 minus `w27378`'s loose end); the plan's named alternative is 57 (+ CP1's three unnamed
slots). Report total and per class. The EL script deletes the scratch copy afterwards; LabVIEW gone.

## 6. Step 5 — measured census into the prediction (PD264(c))
A script writes the scratch's measured census delta into `plan_ring_p3b1_pred.json` (`census`), citing the scratch log
line; add the samples to `tools/bench/census_samples.json` in its existing format. Never type a number. Then dry + prerun
of `tools/recipes/stage_d1_ring_p3b1.py` again, each in its own process (the pred bytes changed). **Do not launch it.**

## 7. Return
`result/1` (also `tools/bench/cards/result_129-2.json`), validated: step-0 line, prior-art verdict + path, helper md5s and
their dry/prerun lines, every scratch gate line (PASS/FAIL with values), RB's read-back name, the measured census, the
scratch Error List total + per class, the new pred md5, the recipe's dry/prerun lines on it, LabVIEW-gone check, minutes
per step. At the first unexpected result: finish the step (LabVIEW closed, scratch cleaned), record facts, return. If a
gate fails, report the newest `JEV-LADDER` line for that log (log | class p | NEXT-ACTION) and return; do not retry.
