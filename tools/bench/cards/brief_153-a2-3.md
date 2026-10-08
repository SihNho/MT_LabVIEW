---
card: 153-a2-3
status: current
date: 2026-10-09
---
# Brief 153-a2-3 - fp-70 proof by CONVERTING the stored name-keyed preds (docs/d1/ring-p4d.md PD371(b)); offline; NO write to tools/vigraph.py

Read `docs/d1/ring-p4d.md` PD371(b) (line 172) and `tools/bench/cards/result_153-b2-1.json` (facts + open). Background: the fp-70 candidate
(`tools/bench/diag_c153_b2_1_vigraph_poskey.txt`, md5 a7eb58c7) keys `computation_diff` rows by position (owner, index, class). Against the STORED
name-keyed preds, `selftest_t6_poskey` went 43/0 -> 38/5 and `selftest_c147_b1_2` 19/1 -> 17/3, all five/two new FAILs being PB rows of #2626
`array|0..3` that the stored preds list as 3 lost+new PAIRS + 1 rename. Judgement decided (PD371(b)): the reporting rule is ONE row per changed input
slot (owner, index, class) holding both the old and new name/source; a slot whose source is unchanged gives NO row even if renamed. So the stored preds
must be CONVERTED to that rule and the two suites must pass against the converted preds. This card builds and runs the converter and the proof; it does
NOT adopt the candidate (card 153-a2-4 does).

## What to do
1. Write the converter as a function in a NEW file `tools/bench/selftest_c153_poskey_convert.py` (<= 120 lines): maps a stored name-keyed row list to position
   rows - a lost + new pair at the same (owner, index, class) becomes ONE changed row (carrying both names/sources); a pair whose sources are equal
   becomes NOTHING; every other row passes through unchanged. Self-tests in the same file (>= 6 cases: pair->1 changed, equal-source pair->0, a real
   removal stays, a real new stays, an unrelated row passes through, idempotent on already-converted rows).
2. Run `tools/bench/selftest_t6_poskey.py` and `tools/bench/selftest_c147_b1_2.py` against the CONVERTED stored preds WITHOUT editing those self-tests or the
   stored pred files: e.g. a wrapper script in `tools/bench/diag_c153_a2_3_*.py` that loads each stored pred, converts it into a TEMP file under
   `tools/bench/` (name `*_poskey_conv_*`), and runs the suite with the temp file substituted (a copy of the suite with only the pred path changed is also
   fine - say which). The suites run against the CANDIDATE vigraph, loaded from the .txt file as a module copy (`tools/bench/diag_c153_a2_3_vigraph_cand.py`,
   byte copy of a7eb58c7), never by overwriting `tools/vigraph.py`.
3. Required result: `selftest_t6_poskey` 43/0 and `selftest_c147_b1_2` 19/1 where the single FAIL is its pre-existing P0 (memory_model.json /
   plan_ring_p4_s06v18_pred.json pin drift). Quote both logs' final lines. Also run the old `selftest_c153_compdiff_poskey` against the candidate copy (8/0).
4. Quote md5 before/after of every stored pred file the suites read (must be unchanged), and of `tools/vigraph.py` (must stay 13be0847).

## Stop rules
If the converted preds do not give 43/0 and 19/1 (any other FAIL): STOP, return the exact failing rows (suite line, expected vs got) as `OPEN:`; do
not loosen a suite, do not edit a stored pred. Failure budget 2.

## Invariants
`tools/vigraph.py` 13be0847 (do not write it); stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86,
stagesim 78b8d5a1 (a read is fine, no edit); s09 VI eb1d0f31. No LabVIEW (labview none), no tools/hooks edit, no motor or camera.

## Return (<= 30 lines)
Converter file md5 + self-test counts; the two suite results with log paths; the stored-pred md5 table; vigraph md5; `OPEN:` for anything needing judgement.
