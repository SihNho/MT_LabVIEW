---
type: facts
status: current
date: 2026-10-08
card: 150-a2-5
---
# Card 150-a2-5 facts: the s07 --rebase now PASSES; the pred step stops at V18E-R (cdiff 3 on #2626 rows) - FAIL, returned at step 3
Offline, no LabVIEW process before or after (`prep_c150_a2_5_check_before.log` / `_after.log`, LV PASS). No stage tool, hook or elrule edited.
## 1. Rebase (`prep_c150_a2_5_rebase.log` 28341ad1, RESULT 1/0, `BGRUN END rc=0 after 46s`)
- CREATION-MAP s06 cfbd9823 map (obj 4, term 8); MAP-BOUND {-19:30300,-17:30294,-10:30290,-5:30287}; FALLBACK-COUNT 0; REBIND 4 nodes, terminals by map 8.
- RENAMED-OLD 5: 2832/4160/4165 #2626 'array'->'element'; 9508/9505 #9503 'Value'->''. FLIPPED-OLD 3: 29779 #29777, 9505 #9503, 10179 #10177 (src False->True).
- 30 STEPs simulated ok (cdiff 13 -> 19); log :80 `REBASED ... 18 uid(s) bound ... completeness PASS; re-simulated on the real base: final=True failed=None`.
- Plan md5 10a4f59a -> **08c2ad4d**2e6dd4bddd4dd5b18326562c; new base `sim/ring_p4_s07v18_base_real_fsmap.json` 765c687c (written by the tool).
## 2. X11 (`prep_c150_a2_5_x11.log` e3b5eba5, `--buildarray-check`, rc 2)
- `FLAG ... row p4_rbB_sel_t4168 node #2626 wired 'array' open sibling ['element'] licensed None` -> op 150 IS flagged (licence needs `rename_by_uid` #2626).
## 3. Pred (`prep_c150_a2_5_pred.log` 8b047037, RESULT 3/1, rc 1) - the failing step
- Script `prep_c150_a2_5_pred.py` 85196a77 = copy of `prep_c147_a1_3_pred.py` (rebased form), s06 -> s07 names; base 569ffbf5, EL base 51 (expected b47995c8, read 899e2656).
- PASS: M0 (graph a3ecb92b, EL files, requiredness 13b0d75f); RB (rebased, FINAL, open_rows_match, 30 actions, no negative uid); RB2 (base vi 569ffbf5, real_graph a3ecb92b).
- **FAIL (log :8-9) V18E-R**: rebased s07 end rows 19 vs v18 sim after #177 (p4_rbE_sel) rows 22; only s07 []; only v18
  ['2626|Terminal|array|1', '2626|Terminal|array|2', '2626|Terminal|array|3'] (cdiff 3). The gate is fatal: the pred was NOT written.
- The 3 rows are the #2626 inputs the real s06 graph renamed 'array'->'element' (RENAMED-OLD above); not diagnosed further (protocol: return).
- Rebased plan holds the #2626 keys '2626|Terminal|array|0', 'element|0', 'element|1', 'element|2' (grep of the plan).
## 4. Not run (steps after the failure)
- X10 after the rebase (not computed: the pred gate X10 comes after V18E-R); recipes NOT regenerated; licence NOT written; dry / prerun /
  `--scratch-required` NOT run; prior-art / PROVEN-PATTERN not checked.
- Read for the recipes (fact, no edit): the 150-a1-1 session census has TWO sink rows needing a sink gate (`prep_c150_a1_1_session.json:395-420`:
  n1 p4_rbA_re2 -> [23166,'Pos: Diffraction Pattern'], n28 p4_rbD_sel_t25573 -> [23166,'autofocus reset count (1.2 to 1.1)']); the s07 MAIN recipe
  declares ONE (`stage_d1_ring_p4_s07v18.py:47-48,90`); an undeclared sink error stops the run (`stagexec.py:2985`, `:2756`).
## 5. Files
| file | before | after |
|---|---|---|
| plan_ring_p4_s07v18.json | 10a4f59a | 08c2ad4d (rebase) |
| sim/ring_p4_s07v18_base_real_fsmap.json | absent | 765c687c |
| _in / _pred / recipes MAIN / scratch | 7b890070 / e888ab67 / d6c8da7b / 273dc3de | unchanged |
| _licence.json | absent | absent |
New: prep_c150_a2_5_check.py 9a99d7a8 (copy of a2-3's, pin c739eb86), _probe.py 9506ebf9, _pred.py 85196a77, their logs.
## 6. Invariants (`prep_c150_a2_5_check_after.log`: B 99/99, PIN pass incl. stage_prerun c739eb86, A after == before 99 files)
stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun c739eb86, s06 569ffbf5, s05 3f9ac26b, s04 95e408ff, bed 39511877,
memory_model 8eec443c, adopted_scratch 658fe5b9, graph a3ecb92b, s06 plan/pred/in/licence/recipes, sim/ring_p4_s06v18 tree, creation maps: unchanged. No --launch.
## 7. Jev ladder
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| prep_c150_a2_5_pred.log | no JEV-LADDER row in jev_gate.log | - | returned | FAIL V18E-R cdiff 3 |
OPEN: is a V18E-R cdiff of exactly the 3 #2626 rows renamed 'array'->'element' by s06 acceptable (gate keyed on names), and does s07 need a second sink gate for row 28?
