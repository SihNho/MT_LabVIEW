---
card: 150-a2-6
status: current
date: 2026-10-08
---
# Brief 150-a2-6 - retry of 150-a2-5: pred (name-free V18E-R), recipes with BOTH sink gates, licence, dry + prerun; offline, NOT launched

Same task as `tools/bench/cards/brief_150-a2-3.md` steps 2-7 (read it) and `diag_c150_a2_5_facts.md`. The REBASE IS DONE: plan `plan_ring_p4_s07v18.json` is now **08c2ad4d2e6dd4bddd4dd5b18326562c**
(final=True, completeness PASS, `prep_c150_a2_5_rebase.log:80`); do NOT run `--rebase` again unless the plan md5 differs. `stage_prerun.py` stays c739eb86 (no edit).

## Two decisions (judgement-assumptions per CLAUDE.md 2c; the judgement session may overturn them - flag both in your report)
1. **V18E-R compares by the NAME-FREE key, with the measured renamed-old terminals normalised.** The gate in your copy `tools/bench/prep_c150_a2_5_pred.py` (copied from `prep_c147_a1_3_pred.py`)
   keys rows by name (`2626|Terminal|array|n`). The 3 only-v18 rows are the #2626 inputs s06 renamed `array`->`element` (RENAMED-OLD, measured on the real s06 graph:
   `prep_c150_a2_5_rebase.log:6-10`, `plan_ring_p4_s06v18_licence.json:16-30`). A name is a report column, not computation (PD365(c), user chat-T6 direction 2026-10-08).
   Edit ONLY your own pred script: before the compare, replace the name of a row whose (uid, owner) is one of the 5 RENAMED-OLD pairs by the real-graph name on BOTH sides
   (read the pairs from the rebase log or `info['renamed_old']`, do not type them). Acceptance: after normalising, cdiff only-s07 AND only-v18 are BOTH empty and the row counts match
   (19 vs 22 must become equal; if the counts still differ, STOP and RETURN with the row lists - do not weaken the gate any further). Quote the before/after row lists.
2. **The MAIN (and scratch) recipe declares a sink gate for EVERY sink row of the session census**, not one: n1 `p4_rbA_re2` -> `[23166,'Pos: Diffraction Pattern']` and n28 `p4_rbD_sel_t25573`
   -> `[23166,'autofocus reset count (1.2 to 1.1)']` (`prep_c150_a1_1_session.json:395-420`; undeclared sink errors stop the run, `stagexec.py:2985`). Copy the s06 recipe's declaration form
   (`stage_d1_ring_p4_s06v18.py`); read the census, do not type the pairs. Quote the s06 form, the s07 declaration lines and why the count is 2.

## Then, as in brief_150-a2-3 steps 2-7
X10 after the rebase (MAIN <= 680, else longest prefix <= 680, no re-plan) - the rebased plan is final, so a cut means re-running the plan tool on the prefix: if X10 > 680 RETURN with the numbers;
pred written (EL base 51); MAIN + scratch recipes regenerated for the 30 actions; X11 (it flags op 150 -> `rename_by_uid` #2626 in the licence); licence `plan_ring_p4_s07v18_licence.json` written by script from the
rebased plan (pb-licence/1, s06 form, `renames` = every BASE sink terminal (uid, owner) an s07 connect row wires, from/to unset); dry + prerun PASS on the final bytes; `--scratch-required` exit code;
PROVEN-PATTERN or a diff-only prior-art line. Invariants as in the old brief with stage_prerun c739eb86 (copy `prep_c150_a2_5_check.py` 9a99d7a8 to `prep_c150_a2_6_check.py`, same pin). No hooks edit, no LabVIEW, no --launch.

## Return conditions
A stage-tool fault (quote file:line, no edit); counts still unequal after the normalisation; X10 > 680; a prerun gate failing twice at the same place; a protected md5 moved.

## Report `tools/bench/diag_c150_a2_6_facts.md` (<= 35 lines)
Plan md5, the two decisions with before/after evidence, X10 numbers, X11, licence summary, dry/prerun/scratch-required with exit codes, files changed (md5 before/after), invariants, `OPEN:`. Facts only.
