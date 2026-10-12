---
card: 171-a2-2
status: current
date: 2026-10-13
---
# Brief 171-a2-2 (assignment 171-2) - offline: re-apply the value-criterion patch af6937e8 and run the four checks, one at a time

Plan: `docs/d1/ring-p6b.md` PD413(a)-(c). The measurement is in: `tools/bench/diag_c171_a2_1_facts.md` - on the UNPATCHED db81a1d3,
`selftest_dry_c130_5` T3 FAILs at the same GATE PB line (`diag_c171_a2_1_c130_5_unpatched.log:8`, class A), so the patch is not its cause.
Offline only (`flags.labview none`): no LabVIEW, no camera, no motor, no VISA. Edit tool only for `tools/stage_prerun.py`, never a heredoc, never `git apply`/`patch`.

## Step 1 - re-apply the patch
Read `tools/bench/diag_c171_a1_2_patch.diff` (md5 f8f1fd95, +136/-0) and make exactly its edits to `tools/stage_prerun.py` (now db81a1d3) with the Edit tool.
Check: `stage_prerun.py` md5 starts `af6937e8`. If it does not, diff your file against the patch's added text, fix the difference once; if it still differs, RETURN (no new version of the patch is tried: PD413(c)).
Keep the docstring of `_stub_shaped` as the patch has it (rule 9). Quote the md5 and `git diff --stat`.

## Step 2 - the checks, ONE AT A TIME, each under `py tools/bgrun.py --max-min 10 --log <file> -- <cmd>`, read the log, never infer
a. Plan-170 dry: `py -u tools/stage_prerun.py --dry tools/recipes/stage_replay_swap.py --plan 170` (log `tools/bench/diag_c171_a2_2_dry170.log`; this is the run whose prerun record must be the NEWEST plan-170 record, so run it WITHOUT `--no-record`).
   Expect gate A2 `UNVERIFIED`, no FAIL, ends `DRY PASS-UNVERIFIED`, unverified 7 (round 1: `diag_c171_a1_2_dry170.log:10,28`). Quote the A2 line and the END line.
b. `py tools/bench/selftest_c134_1_dry.py` (log `diag_c171_a2_2_st134.log`): expect 11/0 = its record `selftest_c134_1_dry_c160_f3_1.log:15`.
c. `py tools/bench/selftest_c171_a1_1_taint.py` (log `diag_c171_a2_2_taint.log`): expect 9/0.
d. `py tools/bench/selftest_dry_c130_5.py` (log `diag_c171_a2_2_c130_5.log`): expect the SAME T2/T3/T4 lines as the unpatched run `diag_c171_a2_1_c130_5_unpatched.log:5-9` (T1 SKIPPED, T2 PASS, T3 FAIL at the same GATE PB text, T4 PASS, totals 2/1). Quote T3's line and say "same text" or list the difference.
Any result other than the expected one = RETURN with the lines; do not edit again, do not re-run (this is the card the purpose depends on).

## Step 3 - state at the end
`stage_prerun.py` stays PATCHED (af6937e8). Plans/recipe md5 unchanged (plan 170 01c21526, recipe fa94e80c). Do NOT drain fp-103, do NOT run the prior-art review, do NOT touch fp-102 (next card / last).

## Facts file `tools/bench/diag_c171_a2_2_facts.md` (<= 20 lines, file:line)
New md5 + diff size; the four results with log line numbers; T3 same-text statement; newest plan-170 record line in `prerun_records.jsonl` (quote its verdict).

## Hygiene
No LabVIEW process before/after (`tasklist`), no `.vi` written, no hook edit, no STATUS/INDEX/plan edit. A new unexpected result = RETURN with the facts.
