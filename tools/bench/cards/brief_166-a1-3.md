---
card: 166-a1-3
status: current
date: 2026-10-12
---
# Brief 166-a1-3 (assignment 166-1) - EL TOOLING, OFFLINE: (1) the adoption Error List step judged by `stagekit.el_advisory`, (2) the EL predictor honours `clears_by`

Plan: `docs/d1/ring-p5c.md` PD403(d)(1),(2) (lines 264-272); the decision it applies is `docs/violation-decisions.md:2076-2087` (device-failed) and the rule at `:2063-2074`
(**the acceptance test REPLAYS the literal failing command**, not a unit test of the part we believe failed). Read `docs/script-writing.md` first: logic lives once in a shared module, a new/changed shared function has a docstring that names its self-test.
Nothing here starts LabVIEW. No `tools/hooks/**` edit. Stricter-than-before changes are fine; a loosening is not.

## Facts you start from (verify each by reading the line, they are the assignment's reading)
- Cycle 165's adoption read returned rc 1 on 47 items vs predicted 49 because `tools/errorlist_check.py` ran its by-design verdict (`ERRORLIST-VERDICT MISMATCH`, `tools/bench/diag_c165_a3_4_el.log:82-86`; verdict code `tools/errorlist_check.py` around `:363` and `:658`, `tools/elrule.py:256`) and nothing consulted `stagekit.el_advisory` (`tools/stagekit.py:2782`, `EL_TOTAL_TOL` 3 at `:2758`, `el_advisory_print` `:2805`, `el_advisory_selftest` `:2812`).
  The scratch recipes already call it offline (`tools/recipes/stage_d1_ring_p5s02e_scratch.py`, `stagekit.scratch_offline_modes` `:2841`).
- The predictor's STANDING rule lives in `tools/bench/prep_c164_a2_3_lib.py:118-` (`el(cfg)`), copied into `prep_c160_c3_1_el.py`, `prep_c163_a1_3_el.py`, `prep_c165_a3_3_el.py` (rule text at `prep_c165_a3_3_el.py:10,32`).
  In `errorlist_predicted_D1_ring_p5s02e_end.json` item 4 (w4337) carries `clears_by` A70 `w_k3f` (`:180-186`) and item 49 (w9636) `clears_by` A80 `w_k4f` (`:1005-1013`) and the rule kept both STANDING (uid not named by an action). The read has 47 (diag_c165_a3_4_facts.md:25-28).

## Part 1 - the adoption Error List step uses the advisory (PD403(d)(1))
Make the adoption step (`tools/errorlist_check.py` `--role final` path, and whatever recipe/adopt helper prints the verdict; find the callers by reading) call `stagekit.el_advisory` on the read items with the step's predicted end file and plan,
print its `EL-ADVISORY` line, and let ITS rc (0 = RECORD, 1 = RETURN only on an unseen class or |total diff| > 3) decide the step's pass/fail. The by-design verdict stays as a RECORDED line (printed, no longer deciding rc).
Where the step has no predicted end/plan (older beds, expected-file-only mode) behaviour stays exactly as before. Self-test (new file `tools/bench/selftest_c166_eladv.py`, scope header, RESULT line): (a) the stored cycle-165 read `errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json` (47 items) against the stored predicted end + plan -> rc 0 and the EL-ADVISORY line;
(b) the same items plus ONE planted item of a class in neither the start read nor the prediction -> rc 1; (c) the stored cycle-165 case replayed through the real adoption path function (not just `el_advisory`): rc 0 where the literal log had rc 1.
Stricter-only check: a read whose total differs by > 3 still returns rc 1.

## Part 2 - the EL predictor honours `clears_by` and tunnel-linked items (PD403(d)(2))
Move the predictor (`licence`/`el`/`pred` that the prep_c*_el.py scripts copy) into ONE shared module (the module that owns the topic: `tools/elrule.py`, or a new `tools/elpredict.py` with a self-test; your choice, say why), keep the old prep scripts untouched (they are the record), and change the rule:
1. A `clears_by` action that the PLAN CONTAINS clears the item even when no action names the item's uid.
2. An action that clears a tunnel's undirected item also clears the nosource / While-Loop-to-SubVI items whose sink set holds that tunnel's outer terminal (here: #5204 / #10404 outer terminals t9631 / t24363 flip to source, `diag_c166_a1_1_facts.md`, graph `graph_ring_p5s02e_20261012_173009.json` 7815af09).
**Acceptance = REPLAY of the literal step-5 prediction** from its stored inputs (the inputs of `prep_c165_a3_3_el.py`: plan `plan_ring_p5s02e.json`, pred, licence, the p5s02d expected file 7450dd98/c74200f2 as the prep script names them): total **47, missing 0, extra 0** against the read 0c0664d8 (the expected file for the P5 final is written by card 166-a1-2; if it exists, compare to it as well, else compare to the read).
Steps 1-4: re-make the stored predictions p5s01a, p5s01b, p5s02a..p5s02d (`errorlist_predicted_D1_ring_p5s0*_end.json`) with the new predictor from their stored inputs; each is byte-equal to the stored file OR every differing item is listed (uid, class, old/new, reason). A difference that moves a total away from the adopted read is a RETURN; one that only removes a `clears_by` mismatch is recorded.
The stored predicted files are NOT overwritten: write the re-made ones under `tools/bench/diag_c166_a1_3_replay/` and compare.

## End of card
Quote each self-test's final line. The stored plans `plan_ring_p5s01a/b.json`, `plan_ring_p5s02a`..`e` must still compile and dry byte-equal if your change touched stagekit/stagexec/stagesim (run the existing compile/dry checks those plans already have; state which). `py tools/lint.py` / `tools/dupcheck.py` on the files you touched if they take seconds.
New functions carry docstrings (rule 9); existing ones you changed keep `file:line` citations stable if possible (`docs/fn_descriptions.json` for old ones). Facts `tools/bench/diag_c166_a1_3_facts.md` (<= 40 lines, file:line). Hash the seven VIs before/after (unchanged); no LabVIEW process.
Do NOT touch the PB check, E5 or the reuse detectors (cards 166-a1-4 / 166-a1-5), `docs/violation-decisions.md`, STATUS, INDEX, or the plan file.
