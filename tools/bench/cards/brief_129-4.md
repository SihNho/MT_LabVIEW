# Brief for card 129-4 (cycle 129 judgement) — RETRY of 129-2's scratch run; decisions PD264(c)(e)

**What happened to 129-2 (measured):** the prior-art review for P3b-1 ran and ANSWERED `novel` (`priorart_c129_2_ring_p3b1.log:35`,
already annotated by the judgement session — do not re-dispatch it). The two helpers exist (`tools/bench/stage_d1_ring_p3b1_scratch.py`,
`_el.py`). The scratch `pin` run started 01:26:11 (`stage_d1_ring_p3b1_scratch_pin.log:1`), passed L0 / K1–K3 (`:33-50`), and
the log stops at 01:28:01 with NO `BGRUN END`: the agent ended its turn with "Waiting for the scratch run to finish" and its
exit killed bgrun (PID 16692 gone). LabVIEW PID 15600 was left running with
`claudeDev\scratch_c129_ring_p3b1_20261002_012612.vi` open. That run is a NON-RESULT: rerun from the beginning, never resume.

## 0. Time arithmetic (budget 50 min; backstop: no NEW bgrun after bind + 60)
cleanup ~2 min · Jev/guard check (+ a hypothesis review only if the gate demands one, ~5–8 min) · helper dry + prerun ~1 min
· scratch `pin` run ~15 min (40 rows; never measured — report it) · scratch Error List count-only ~5–7 min · census into pred
+ recipe dry/prerun ~3 min · total ≈ 30–40 min. Report real minutes per step.

## ⚠️ THE RULE THAT 129-2 BROKE — `.claude/agents/material.md:92-98`
Start every run longer than a few minutes with `run_in_background`, then WAIT FOR IT IN THE SAME TURN until its log has
`BGRUN END` or `BGRUN TIMEOUT` — the Monitor tool with an until-loop (load it with ToolSearch `select:Monitor`), or the
bounded foreground loop of `material.md:96-97`, repeated as often as needed. **Never write a final message while a run you
started has no END line: your exit kills it.**

## 1. Cleanup (first)
Confirm PID 15600 is that orphan (LabVIEW.exe, start time ≥ 01:26 today; no bgrun/python process of the scratch alive), kill
it, verify no LabVIEW.exe remains. Delete `claudeDev\scratch_c129_ring_p3b1_20261002_012612.vi` (scratch artefact of the killed
run; check the name starts with `scratch_c129_` — never touch the bed `D1_ring_p3a_20261001_180540.vi`). Record both.

## 2. Gates
If `guard_peer` holds the relaunch on the killed log, read the newest `JEV-LADDER` line for it and report it as one row. If a
hypothesis review is owed: `-Agent claude -Role hypothesis`, the claim to ATTACK = "the run was killed by its parent agent's
exit at 01:28, not by the stage: the log ends after K3 with no BGRUN END, bgrun PID 16692 is gone, LabVIEW 15600 was
orphaned"; wait for ANSWERED; a refutation is the first unexpected result → return. Then dry + prerun of both helpers again,
each in its own process (a killed run invalidates the pre-run records).

## 3. Scratch `pin` rerun — new log `tools/bench/stage_d1_ring_p3b1_scratch_pin2.log`, waited on (rule above)
Predictions unchanged from `brief_129-2.md` §4: every recipe gate PASS — L1 40, E1, FS one FlatSequence with 3 frames on
27219, **RB reads back `status`**, D, TD, PB cdiff 16, HB ≤ +700, PS; CEN2 vacuous → record the measured census (all classes,
NEWOBJ owner lines). LabVIEW closed and verified gone after.

## 4. Scratch Error List pin — `errorlist_check.py --count-only --role scratch`
Prediction 54 (P3a 55 − `w27378`); named alternative 57 (+ CP1's three unnamed slots). Total + per class. Scratch deleted after.

## 5. Measured census into the prediction (PD264(c)) — then STOP before any launch
A script writes the scratch's measured census delta into `plan_ring_p3b1_pred.json` (`census`), citing the log line; samples
into `tools/bench/census_samples.json` (existing format). Never type a number. Dry + prerun of
`tools/recipes/stage_d1_ring_p3b1.py` again, each in its own process. **Do not launch the recipe** (card 129-5 does).

## 6. Return
`result/1` (`tools/bench/cards/result_129-4.json`), validated, plus `py tools/card_clock.py tools/bench/cards/result_129-4.json`
(must print OK; fix `cost.minutes` if it does not). Facts: cleanup lines, every scratch gate line with values, RB's read-back
name, the measured census, the Error List total + per class, new pred md5, the recipe's dry/prerun lines, LabVIEW-gone check,
minutes per step. At the first unexpected result: finish the step (LabVIEW closed, scratch cleaned), record, return.
