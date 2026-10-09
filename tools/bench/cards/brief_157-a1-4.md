# Brief 157-a1-4 (assignment 157-1): measure planned X10 MAIN at the two nearest group cuts; close fp-76. Offline, measurement only

Context: card 157-a1-2 found `plan_ring_p5s02a.json` (actions 1..23, ops 1..17) at planned MAIN 679.7 MB (limit 675 per PD379(c), fail 680)
with checkpoints (0,1,3,6,8,9,10,11,12,15,16,17) on stagexec 69b1a301 / stagekit 0d8f6d25 (`tools/bench/diag_c157_a1_2_facts.md:15-21`).
Group ends of the all-groups plan `plan_ring_p5s02r_all.json`: [7,8,9,14,17,20,23,26,33,40,52,60] (`diag_c156_a1_1_facts.md:21`).
Judgement decides whether to re-cut; this card only MEASURES. Do NOT write any plan, pred, licence, recipe or P5 file under its stored name.

## Part 1 - X10 at the cuts (MEASURE)
For cuts at action 20 (end of F1) and action 26 (the next group end), compute the planned X10 MAIN peak and Executor-only peak with the
SAME checkpoint rule (RingSession: every bind op, every move_in op, first and last) and the same memory model (`memory_model.json`
c87d170a). Use the stage_prerun / stagekit function that produced the 679.7 (name it with file:line) on a cut copy of the plan written under
`tools/bench/sim/ring_p5s02a_c157/cut20/` and `cut26/` (an existing plan cutter / maker for the all-plan, `tools/bench/prep_c156_a1_1_mk.py`
or a shared function, if one gives you the cut; else say what is missing - do not invent a cut by hand-editing JSON beyond the action list).
Report for each cut: actions, ops, which op indices fall in the last group (so judgement can see whether ops 15..17 = tunnel + the two cfw
of #24360 / #24367 are inside the step), checkpoints, MAIN peak, Executor-only peak, R reads, and whether the cut splits a group (it must not).
Also report the meter the memory model would give for the existing 23-action plan with checkpoint 10-12 but WITHOUT 11 and 12 (i.e. what
each extra read costs: +7.6 MB for the three, per `diag_c157_a1_2_facts.md:18`) - one number per read, from the model.

## Part 2 - fp-76
Run `py tools/gate_fp.py close --id fp-76 --reason "..."` (read `tools/gate_fp.py` usage at the top of the file first). Reason: the launch
gate was correct - the scratch card 156-a2-1 named no `DRY-UNVERIFIED-OK` string although the dry's PB gate is PASS-UNVERIFIED
(`diag_c156_a2_1_facts.md:19-22`, stage_prerun.py:4888-4895); card omission, not a gate fault. Cite those two path:lines in the reason text.
Quote the closed record.

## Report `tools/bench/diag_c157_a1_4_facts.md` (<= 30 lines)
Numbers per cut with file:line of the producing log, the function used, md5 of any file written, the closed fp-76 record. `OPEN:` per
unresolved thing. Facts only, no recommendation. Failure budget 2; no LabVIEW; no hook edit.
