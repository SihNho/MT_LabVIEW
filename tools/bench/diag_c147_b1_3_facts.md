---
type: facts
status: current
date: 2026-10-08
card: 147-b1-3
---
# Card 147-b1-3: T6 of 147-b1-2 - STOPPED at the first unexpected result (FAIL)
tasklist LabVIEW count before 0, after 0.

## Step 1 - NEW stagekit 06b8d844
- `py tools/bgrun.py --material --max-min 1 --log tools/bench/selftest_td_key_c147b13_new.log -- py -u tools/bench/selftest_td_key_c141_3.py` -> rc 0, RESULT 9/0.
- `py tools/bgrun.py --material --max-min 1 --log tools/bench/selftest_stagekit_c147b13_new.log -- py -u tools/bench/selftest_stagekit.py` -> rc 1, GATES 47 pass / 2 fail
  (no RESULT line; the script has none). First fail: J1 (selftest_stagekit.py:336), then case_j IndexError at :339.
- J1 cause (read, not run): stagekit.py:794 `create_local_read` calls REAL `g.create_local_read` (since cycle 102, comment :790-792); the test stubs only
  `diag_s3b_l0_localname_v2` via K.mod (selftest_stagekit.py:330), so the call went to COM -> `gscript.open_panel` com_error 5507 'LabVIEW: File not found' (stub.vi) after 14.7 s.
- That code is NOT in the 147-b1-2 diff (`git diff HEAD -- tools/stagekit.py`: hunks @@1371, @@1379, @@1395 only) -> J1 expected to fail on HEAD too (not measured).
- The COM call means the LabVIEW automation server answered during the run (card rule "no LabVIEW process may start"); no LabVIEW process at check time.

## Steps 2-4 NOT RUN (return at first unexpected result)
- Pre-edit runs not started: selftest_stagekit on HEAD would repeat the same COM call. Runner prepared: tools/bench/diag_c147_b1_3_runold.py
  (HEAD source from `git show`, md5 checked == 9a3fceaf, in memory; no scratch dir on disk). selftest_c147_b1_2 re-run not done.

## Step 5 - pins after (all == card)
stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, memory_model 88eeb037, plan cfbd9823, plan_in db72d8af, pred c4a6a35a,
licence 7dce79aa, recipe 9150f15b, scratch recipe 31009bfc. No tool/plan/licence/recipe edited.
OPEN: selftest_stagekit case J's stub predates stagekit.py:794 and reaches LabVIEW by COM - fix the stub (stub g.create_local_read/panel_wiring) or skip J, then run the before/after pair?
