---
card: 160-c3-2
status: current
date: 2026-10-10
---
# Brief 160-c3-2 (assignment 160-2) - OFFLINE retry of 160-c3-1: re-pin its makers to the final stagekit, then run the dry / prerun / check-launch / scratch-required gates; NOT launched

`labview: none` (no LabVIEW process; `tasklist` may be refused - say so), no `--launch`, no `tools/hooks` edit, no `tools/*.py` edit, no plan / recipe-text edit unless a gate forces it (see 3).
Read `tools/bench/diag_c160_c3_1_facts.md` (c3-1: pred 14/0, licence 5/0, EL 9/0 done; dry FAIL at gate L0 `stagekit.py:2410` only) and `docs/d1/ring-p5b.md` PD390(c), PD391(d)(e).

## What changed since c3-1
- Card 160-e4-1 made `RingSession.gate_l0` accept `plan_in` = `<stem>_in` or `<stem>_in<digits>` (`stagekit.py` function `plan_in_matches_stem`, self-test `selftest_c160_l0stem.py` 14/0). stagekit md5 is now
  **0b5bb678169d659feed7408648a63354** (was 1441bb4c). stagesim 95a162ba, stagexec ddf23a31, stage_prerun 7605116f unchanged. Facts: `tools/bench/diag_c160_e4_1_facts.md`.
- A parallel card 160-e5-1 re-pins stagekit's md5 in OTHER files (selftest_c155/c156/c160_*, diag_c160_b2/g1/h1, prep_c160_b1_1_mk / b3_1_mk). Do not touch those, and do not read their results as yours.

## Do
1. Re-pin your own makers to the final stagekit: `prep_c160_c3_1_md5.py:17`, `prep_c160_c3_1_pred.py:39` (1441bb4c -> 0b5bb678). Re-run `prep_c160_c3_1_md5.py` (expect all pins hold), `prep_c160_c3_1_pred.py`,
   `prep_c160_c3_1_licence.py`, `prep_c160_c3_1_el.py` in the c3-1 order. **Prediction contract: the outputs plan_ring_p5s02b_pred.json (48b50b29), plan_ring_p5s02b_licence.json (f61a2514),
   errorlist_predicted_D1_ring_p5s02b_end.json (79ec3207) are byte-identical to c3-1** unless the pred embeds the stagekit md5 (then name each changed byte-range and why). A different pred/licence/EL content is a FAIL.
2. Dry on the recipe pair with the SAME command forms as c3-1 (`prep_c160_c3_1_dry.log`, `prep_c156_a1_1_dry.log`): recipe `tools/recipes/stage_d1_ring_p5s02b.py`, then `_scratch.py`. Quote the result word-for-word:
   PASS / PASS-UNVERIFIED and the **unverified count with the label of each unverified item**. The pass criterion wants "unverified 0"; c3-1 predicted the census is UNPREDICTED, so `gate_cen2` returns early
   (`stagekit.py:2494-2496`) and unverified may be >= 1. **Report whatever the gate says. Do not add census samples, do not edit stagekit, do not change a gate to reach 0.** If the dry is PASS-UNVERIFIED, continue with 3-5 only if the
   tool lets prerun / check-launch run on a PASS-UNVERIFIED dry; if it does not, report the refusing line verbatim (that is the finding).
3. Prerun (X10 MAIN <= 675, X14, X17, X8) on final tool md5s, then `--check-launch` (no `--launch`), command forms from `prep_c156_a1_1_prerun.log` / `_checklaunch.log`. Prior-art review `archive/peer/2026-10-10-priorart-priorart-c160-d4-1-p5s02b.md`
   was run on recipe bytes 083fda6d: do NOT change the recipe text (md5 083fda6d / 3f6fb898); if a gate forces a recipe change, stop and report the gate line instead.
4. `py tools/stage_prerun.py --scratch-required tools/recipes/stage_d1_ring_p5s02b.py` (form from `prep_c156_a1_1_scrreq.log`): quote exit code and reason line (expected 3, PD391(e)).
5. Hook false positive on your own command text: `py tools/gate_fp.py log ...`, report, no env bypass. Background anything slow under `py tools/bgrun.py --material --max-min N --log ... -- ...`.

## Report `tools/bench/diag_c160_c3_2_facts.md` (<= 30 lines, facts only)
md5 of every file written or re-run output; pred/licence/EL md5 vs c3-1; dry (both recipes) / prerun / check-launch / scratch-required lines quoted with rc, **unverified count + labels**; md5 UNCHANGED: stagesim 95a162ba,
stagexec ddf23a31, stage_prerun 7605116f, stagekit 0b5bb678, plan f4520b10, in 56bfddd3, in2 927b805c, graph 7ac24924, recipes 083fda6d / 3f6fb898, VIs s09 eb1d0f31 / P5-1a 2482fe7b / P5-1 7f2582ae / 94ffff94
("not hashed" if refused); `OPEN:` lines.
