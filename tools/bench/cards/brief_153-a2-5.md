---
card: 153-a2-5
status: current
date: 2026-10-09
---
# Brief 153-a2-5 - retry of 153-a2-3: finish the fp-70 proof by also converting the plans' open_rows in TEMP copies (docs/d1/ring-p4d.md PD371(b)); offline

Read `tools/bench/cards/result_153-a2-3.json` (facts + open) and `tools/bench/cards/brief_153-a2-3.md` first. Card 153-a2-3 built a converter
(`tools/bench/selftest_c153_poskey_convert.py`, 7/0) and showed converted preds equal the candidate rows exactly (extra [] missing []). The only
remaining FAILs (t6 38/5, c147 17/3 = N2 / T1 / T1n PB rows) come from the PB gate's second check: the rows' (node,name) set must equal the plan's
`open_rows` (selftest_t6_poskey.py:149, selftest_c147_b1_2.py:122), and the stored plans s03-s06 still list the name-keyed open pair (2626,'array'),
which the position-keyed rows (correctly) no longer contain. A mode-B probe (temp plan copy without that pair) already gave t6 43/0 and c147 19/1.

## ASSUMPTION this card runs under (the judgement session may overturn it; flag it in `OPEN:`)
The plans' `open_rows` are name-keyed bookkeeping of the same facts as the preds, so they are converted by the SAME mechanical rule, in TEMP
copies only: a (node,name) pair that the pred conversion removed entirely (a pair whose lost+new rows became a changed row of another name, or whose
sources were equal) is dropped from the temp plan's `open_rows`; every other pair stays. No stored plan, stored pred or suite file is edited.

## What to do
1. Extend the converter file `tools/bench/selftest_c153_poskey_convert.py` (stay <= 120 lines; split the plan-side function into
   `tools/bench/diag_c153_a2_5_plan_convert.py` if needed) with `convert_open_rows(plan_open_rows, old_rows, new_rows)` implementing the rule above; add
   >= 3 self-test cases (pair dropped, unrelated pair kept, idempotent). Converter self-test must pass.
2. Re-run the wrapper from card 153-a2-3 (`tools/bench/diag_c153_a2_3_run.py`, or a copy named `diag_c153_a2_5_run.py`) so each suite reads the
   TEMP converted pred AND the TEMP converted plan (names `*_poskey_conv_*`), candidate a7eb58c7 as module copy, suites unedited.
3. Required: `selftest_t6_poskey` 43/0; `selftest_c147_b1_2` 19/1 with the single FAIL being its pre-existing P0 pin; `selftest_c153_compdiff_poskey`
   8/0 on the candidate copy. Quote final lines and log paths.
4. Quote md5 before/after of every stored pred and plan file read (unchanged), the suites, and `tools/vigraph.py` (stays 13be0847).

## Stop rules
Any other FAIL: STOP, return the exact failing rows as `OPEN:`; do not loosen a suite, do not edit a stored file. Failure budget 2.
Do not write `tools/vigraph.py` (card 153-a2-4 does).

## Invariants
vigraph 13be0847 (candidate a7eb58c7 only as module copy); stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun
c739eb86, stagesim 78b8d5a1; s09 VI eb1d0f31. No LabVIEW, no tools/hooks edit, no motor or camera.

## Return (<= 30 lines)
Converter md5 + counts; both suite results with log paths; stored-file md5 table; vigraph md5; `OPEN:` stating the open_rows assumption as an assumption.
