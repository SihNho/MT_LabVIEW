---
type: brief
status: current
date: 2026-10-07
---
# Brief 145-a2-5 — RETRY of 145-a2-2: make the selftest's own gate R4 pass (item_class misses one Local item) — offline, alone

Read first: `tools/bench/cards/brief_145-a2-2.md` and `tools/bench/cards/result_145-a2-2.json` (3 pass items met; S04 re-derives 58 ==
read 5e53096a; U7 negative +1; S01-S03/R1 PASS; subvi_requiredness.json built). The ONE failing gate is R4, a gate the card added itself:
the recorded s03->s04 per-class change is `{local 0, cond -1, sr 0}` vs re-derived `{local +1, cond -1, sr 0}`, total 58 == 58. Cause per
`tools/bench/diag_c145_a2_2_insp.log`: the s04 read has a Local item with EMPTY `raw` and detail 'This local or global variable is not
wired'; `elrule.item_class` `L_RE` (`tools/elrule.py:196`) returns None for it. With that item counted as local the two agree.

## Do
1. Make `item_class` classify that item as `local` (match the detail text as well as raw, the way the recording classifier is described
   in `selftest_elpred.py` header). Smallest edit only.
2. `item_class` also feeds `by_design_verdict`. Before and after the edit, classify EVERY recorded Error List file the selftests and
   `tools/bench/errorlist_*.json` use (list them) and report any item whose class changes. **If any recorded item other than this one
   changes class, or any by-design verdict changes (selftest_s5 22/0 must stay 22/0), RETURN with the diff and revert the edit.**
3. Run `selftest_elpred.py` to the end: S01-S04, R1, R4, U7, U8 all PASS. Run `diag_c145_a2_2_selftest_s5` regression: 22/0.
4. md5 before/after: plan, pred, recipes, stagekit, stagesim, stage_prerun, stagexec unchanged. Write results into
   `tools/bench/diag_c145_a2_2_facts.md` (append a section "retry 145-a2-5").

## Never
LabVIEW, camera, motor; editing plan / pred / recipes / other stage tools; weakening R4 or any existing selftest expectation (the fix
is in the classifier, not in the gate); touching s05 files.

## Return
`result/1`; the class-diff table over all recorded Error List files; selftest and s5 line counts.
