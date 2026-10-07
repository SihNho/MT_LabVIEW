---
type: brief
status: current
date: 2026-10-07
---
# Brief 145-a2-2 — elrule: a SubVI's unwired input is an Error List item only if its pane terminal is MEASURED Required (PD351(c))

OFFLINE, no LabVIEW (`labview: none`), runs ALONE (it edits a gate tool). Measured input, done by card 145-a2-4:
`tools/bench/diag_c145_a2_3_facts.md:10-33` (reader `OpWiringRules_v0.vi`, positive control PASS): **every assigned terminal of
RingPickSlot_v0 (6fcf153f) and RingSeqCheck_v0 (0295a8d3) is Recommended (2); none is Required (1)**; free pane slots read 0.
Consequence: the s04 Error List read (58 items, `errorlist_D1_ring_p4s04_20261007_215031_20261007_220024.json` 5e53096a)
has no item for PS1/SQ1's unwired inputs, while the old rule A counted one per created node (pred 60 = 58 + 2).

## Do
1. Read `tools/elrule.py` (class A, lines ~13-21 and `predict`) and `tools/bench/selftest_elpred.py`. Add a SubVI-requiredness input:
   a table file `tools/bench/subvi_requiredness.json` built from the measured facts (VI file name, md5, per terminal index/name/rule,
   source line in the facts file). Rule: a created node that is a SubVI call (decide it from the graph/plan the way the tool already
   tells node kinds apart; report how) contributes an A item for an unwired input ONLY if that terminal is measured Required (1). A
   SubVI missing from the table, or a terminal not in it, is `uncertain` (reported, never counted, never silently 0) — do not
   default. Non-SubVI created nodes keep rule A exactly as it is now.
2. Selftest: add S04 = re-derive s04 (`plan_ring_p4_s04v18.json` f349c39a, base = s03 measured 55) == **58** = the recorded read 5e53096a;
   keep S01/S02/S03/R1 = 51/53/55 unchanged and PASS; add one NEGATIVE case: a synthetic SubVI terminal with rule 1 and unwired
   makes the count go up by one (the rule is live, not dead code). Run the selftest to the end; report counts.
3. Report, as a fact with file:line, the pred's PS1 item (`plan_ring_p4_s04v18_pred.json` a2bbc8bf, the "required input" entry that had
   no source): does the new rule give it no item? Do NOT edit the pred or the plan.
4. Everything outside `tools/elrule.py`, `tools/bench/selftest_elpred.py`, `tools/bench/subvi_requiredness.json` and your diag
   files stays byte-identical (md5 before/after for plan, pred, recipes, stagekit, stagesim, stage_prerun, stagexec).

## Never
LabVIEW, camera, motor; editing plan / pred / recipes / other stage tools; touching s05 files (next card); lowering any existing
selftest expectation to make it pass.

## Return
`result/1`; facts `tools/bench/diag_c145_a2_2_facts.md` (rule text, selftest line, uncertain list, md5 table).
