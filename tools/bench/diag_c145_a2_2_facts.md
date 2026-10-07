---
type: facts
status: current
date: 2026-10-07
---
# Card 145-a2-2: elrule counts a created SubVI's unwired input only for a MEASURED Required pane terminal (PD351(c))

## Rule (tools/elrule.py, md5 50f29adc)
- A created node whose terminal rows carry `owner_class == "SubVI"` (the field elrule already uses to tell Local / Diagram /
  RightShiftRegister apart) is an A ('input') item ONLY if an unwired sink row has pane rule 1 (Required) in
  `tools/bench/subvi_requiredness.json` (md5 13b0d75f). Rule 0 (free slot) / 2 / 3 rows give no item.
- VI identity: from the plan's create action (`class` SubVI, `subvi_path`, `as`) bound by sym `new:<as>` (`elrule.subvis_from_plan`);
  `session_prediction` passes it. Row -> pane index by position when the node's row names equal the table's, else unique name.
- Unknown VI / VI not in table / row not in table -> `uncertain_subvi_terminals` (reported, never counted). Non-SubVI nodes unchanged.

## Table (tools/bench/subvi_requiredness.json, from diag_c145_a2_3_facts.md:10-33; build log diag_c145_a2_2_build_table.log 5/0)
RingPickSlot_v0.vi 6fcf153f7b8fecda727f5dcf944faab9 and RingSeqCheck_v0.vi 0295a8d349a3b61151cd87797119b9b1: 12 terminals each,
no rule 1 (T4 PASS).

## Selftest (tools/bench/selftest_elpred.log, 20 pass / 1 fail)
- U1-U6, S01 51, S02 53, S03 55, UNC, R1 51/53/55, R2, R3: PASS (unchanged expectations).
- U7 NEGATIVE PASS: synthetic SubVI, Required 'req' unwired -> 10 -> 11, item names only 'req'; wired -> 10.
- U8 PASS: VI not in table / identity unknown -> +0, 2 unwired sinks reported uncertain.
- S04 PASS: re-derived 58 (base 55; new input -53/-34/-26, local -51/-32; closed cond 29699, local 29720); S04b PASS (no item for
  PS1 -1 / SQ1 -38); S04c PASS uncertain [] / [].
- R4 FAIL (gate added by this card): recorded s04 count 58 == re-derived and md5 5e53096a OK, but per-class change s03->s04
  recorded {local 0, cond -1, sr 0} vs re-derived {local +1, cond -1, sr 0}.
- Fact behind R4 (diag_c145_a2_2_insp.log): the s04 read holds one item with EMPTY raw text whose detail is "This local or global
  variable is not wired to anything ..."; `elrule.item_class` (L_RE needs "local variable ... not connected") classes it None. Item
  diff s03->s04: +3 Index Array unwired, +1 Local (titled), +1 Local (empty raw), -1 Local, -1 While cond, Build Array OCR variant +1/-1.
- selftest_s5 (by-design verdict) regression 22/0 (diag_c145_a2_2_selftest_s5.log).

## PS1 item of the pred
`plan_ring_p4_s04v18_pred.json:120-122` `["input", -1]` (detail :247-257, seven '' sinks = RingPickSlot free slots rule 0) and
`:108-110` `["input", -38]` (SQ1: free slots + discards/Latest/n2, rule 2): the new rule gives NO item for either -> 58, not 60.

## Byte-identical (diag_c145_a2_2_md5_after.log M1 PASS, 228 files)
plan f349c39a, pred a2bbc8bf, stagekit, stagesim, stage_prerun, stagexec, errorlist_check, prep_c143_3_elrule, tools/recipes/*,
stage_d1_ring_p4_s0*.py, s04 recording 5e53096a.

## Gate false positives logged
fp-48, fp-49 (guard_write stale-pin fires on the card's own edit of its own pinned input).

## retry 145-a2-5 (2026-10-07 23:07-23:09, offline)
- Edit (one line): `tools/elrule.py:196` `L_RE` gains the alternative `local\s*or\s*global\s*variable\s*is\s*not\s*wired` (the detail
  text); item_class still runs on "raw detail" (errorlist_check.py:423/512). elrule md5 50f29adc -> a5ee7d5c. selftest_elpred.py unchanged
  (e0baa236): R4 not weakened.
- Class diff over ALL recorded reads (`diag_c145_a2_2_classdiff.py` -> `.log`, old regexes vs new item_class): 212 files / 8720 items;
  29 files skipped (expected/meta files, no `items` list - listed as NOITEMS in the log). Old {local 8, cond 5, sr 35}, new {local 10,
  cond 5, sr 35}. Exactly ONE distinct item text changes, None -> local: the empty-raw 'This local or global variable is not wired ...'
  row, once in the s04 read 5e53096a and once in its `_raw.json` twin. No other item in any file changes class (C1, C2 PASS).
  The detail also occurs in s02/s03/c138_6 reads, always under a titled 'Local Variable ... not connected' raw already classed local.
- selftest_elpred: 21/0 (`diag_c145_a2_2_selftest_elpred_r2.log`); S01 51, S02 53, S03 55, S04 58, R1, R2, R3, U7, U8 PASS; R4 PASS:
  recorded s04 (58, {local 2, cond 0, sr 2}), per-class s03->s04 {local +1, cond -1, sr 0} == re-derived.
- selftest_s5 regression 22/0 (`diag_c145_a2_2_selftest_s5_r2.log`); C1-C3 by-design verdicts unchanged.
- Byte-identical: M1 228 files vs the 145-a2-2 snapshot (`diag_c145_a2_2_md5_after_r2.log`): plan f349c39a, pred a2bbc8bf, s05 plan
  files, recipes, stagekit, stagesim, stage_prerun, stagexec, errorlist_check.
- Gate FP: fp-50 (guard_write stale-pin on this card's own write target, same class as fp-48).
