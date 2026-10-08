---
type: facts
status: current
date: 2026-10-08
card: 150-a2-4
---
# Card 150-a2-4 facts: rebase() no longer rebinds the plan base `b` in the RENAMED-OLD/FLIPPED-OLD log loops (PASS)
Offline; no LabVIEW process (tasklist 21:17, 21:23); no hooks file edited; `--rebase` on s07 NOT run.
## Other names (rebase() stage_prerun.py:4252-4478, read by hand)
- `b` set :4261, read :4262/:4264/:4276/:4415; only rebinds were :4303/:4305. `u` (:4301/:4391/:4395) is not read after the loops outside them;
  `o` only in the :4402 generator (own scope); `a` re-assigned by the :4318 loop before any read; x/n/v/f/st/rt/why assigned before read. No other shadowing.
## Edit (stage_prerun.py 6208b7b7 -> c739eb86; diff = lines 4303-4306 only)
- Loop targets `a, b` -> `old_v, new_v` in both loops with matching `.format` args; comment added at :4306; format strings unchanged.
- py_compile rc 0 (`prep_c150_a2_4_compile.log`). Pre-edit copy `prep_c150_a2_4_stage_prerun_before.py` (6208b7b7).
## Self-test selftest_rebind_c150.py (78820816 -> ce9d8502, 120 lines; R5 static ast check, writes nothing)
- R5 on the pre-edit copy FAILS as predicted: rebinding lines [4303, 4305] between :4261 and :4415 (`prep_c150_a2_4_r5_before.log`, rc 1).
- `--phase post` 8/0 rc 0 (`selftest_rebind_c150_post4.log`): R5 PASS (c739eb86, []), R0, R1 x2, R2, R3a, R3b, R4 PASS; FLIPPED-OLD count 3.
## Regressions (`prep_c150_a2_4_selftest_<t>_after.log`), all equal to 150-a2-2 AFTER
- rebind_c142_5 4/0 rc 0; rebind_c132_5 7/0 rc 0; rebase_c132_6 8/0 rc 0.
- rebase_uidreuse_c143_4 U1/U2 FAIL, U3/U4 PASS, KeyError 'sim_of', rc 1, NO RESULT LINE (pre-existing, identical).
## Invariants (before = after)
stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, graph a3ecb92b, plan s07 10a4f59a, pred e888ab67, memory_model 8eec443c,
adopted_scratch 658fe5b9. s05/s06/bed VIs are outside the project; this card neither opened nor wrote them.
Gate FP: guard_write flagged closed card 149-a3-4's stale pin dcd45aba -> logged fp-66 (dup of fp-64/65); the edit was not blocked.
OPEN: none from this card; card 150-a2-5 can re-run the s07 `--rebase`.
