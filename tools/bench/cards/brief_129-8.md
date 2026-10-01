# Brief for card 129-8 (cycle 129 judgement) — PD265(c): checkpoint set + predicted memory for the P3b recipes; card_clock fix

OFFLINE ONLY. No LabVIEW, no recipe launched, no gate code (`stage_prerun.py`, `protocol.py`, `tools/hooks/*`) edited.
Purpose: cycle 130 opens directly on the P3b-1 scratch run.

## 0. Time arithmetic (budget 25 min)
recipe edits (2 × ~3 lines) ~4 min · dry + prerun, P3b-1 recipe + scratch helper, own processes ~3 min · prediction script
~4 min · prior-art only if the gate demands it on the new bytes (~2 min; 129-2's took 71 s) · card_clock fix + self-test
~5 min · total ≈ 15–18 min.

## 1. Checkpoint set (PD265(c), established form)
In `tools/recipes/stage_d1_ring_p3b1.py` and `tools/recipes/stage_d1_ring_p3b2.py`: pass the Executor
`checkpoints = {0, len(ops)} | BIND`, BIND = every compiled op whose kind is in `SX.BIND_KINDS` — exactly as
`tools/recipes/stage_d1_l2b3.py:16-18` does (the Executor refuses a set missing a binding op, `stagexec.py:1726-1733`).
Print the set in the recipe's L1 gate line. Nothing else in the recipes changes. The scratch helper imports the recipe
unchanged; its next log is `tools/bench/stage_d1_ring_p3b1_scratch_pin3.log`.

## 2. Predicted peak memory (written into `plan_ring_p3b1_pred.json` / `_p3b2_pred.json` by a script, cited)
peak = 570 + R × 2.53 + N × 1.4 MB, where R = number of whole-VI reads in the set (checkpoints incl. 0 and the end),
N = op count; 570 = pin2 k0 (`stage_d1_ring_p3b1_scratch_pin2.log:55`), 2.53 = read slope (`diag_c129_6_mem.log:55`),
1.4 = edit 0.58 (`:87`) + 0.8 unattributed (pin2 3.9/op − 2.53 − 0.58). Report R, N and the peak for both halves next to
X10's 690 MB. Report only; do not change the set to hit a number.

## 3. Checks
`py tools/stage_prerun.py --dry` then `--prerun` (own processes) on `tools/recipes/stage_d1_ring_p3b1.py` and on
`tools/bench/stage_d1_ring_p3b1_scratch.py`; P3b-2's recipe stays provisional (dry/prerun after the rebase, PD264(b)) —
compile its set offline only (`SX.compile_plan`) and report R. If the launch gate demands a new prior-art review for the
changed recipe bytes, dispatch it (`tools/prior_art_review.py`), wait for ANSWERED, return the verdict; do not annotate.

## 4. card_clock fix
`tools/card_clock.py:77`: a CLOCK-UNMEASURED result must print a valid RESULT line (status `SKIP`, `first_fail`
"CLOCK-UNMEASURED: <reason>"), exit code 2 unchanged; today it raises (status `BLOCKED`). Add a self-test case that runs
`main()` on a result without `cost.minutes` (`result_129-5.json` copy) and expects exit 2 + a parseable RESULT line;
`selftest_card_clock.py` stays green (5/5).

## 5. Return
`result/1` (`tools/bench/cards/result_129-8.json`), validated + `py tools/card_clock.py` OK: both checkpoint sets, R/N/peak
for both halves, recipe + helper md5s, the four dry/prerun lines, any prior-art verdict, self-test counts, minutes.
