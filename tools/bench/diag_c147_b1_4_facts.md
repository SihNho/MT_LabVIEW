---
type: facts
status: current
date: 2026-10-08
card: 147-b1-4
---
# Card 147-b1-4: T6 of 147-b1-2 - stagekit before/after with COM blocked (PASS)
tasklist LabVIEW count before 0, after 0. Driver: tools/bench/diag_c147_b1_4_run.py (new; COM block = win32com Dispatch/dynamic/gencache, gscript lv/_invoke/_run/open_panel/create_local_write/_recover_poison/create_local_read, subprocess naming LabVIEW.exe -> raise+count).
Case J: stagekit.py:794 calls g.create_local_read(work, idx); test stubs only K.mod creator (selftest_stagekit.py:322-330). Driver routes that call, only inside case_j, to the test's creator stub with the label from the test's panel_wiring stub (:328) and adds is_source=[True] (stagekit.py:797 needs it; test stub returns {'err': None}).
## Runs (all BGRUN END rc=0)
- OLD 9a3fceaf: `py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c147_b1_4_old_stagekit.log -- py -u tools/bench/diag_c147_b1_4_run.py old tools/bench/selftest_stagekit.py` -> test rc 0, 51 pass / 0 fail, COM leaks 0, J-routed 2.
- NEW 06b8d844: same with `new`, log diag_c147_b1_4_new_stagekit.log -> rc 0, 51 / 0, COM leaks 0, J-routed 2.
- td_key OLD: `... --log tools/bench/diag_c147_b1_4_old_tdkey.log -- py -u tools/bench/diag_c147_b1_4_run.py old tools/bench/selftest_td_key_c141_3.py` -> rc 0, 9 / 0, COM leaks 0 (NEW 9/0 from 147-b1-3).
- `py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c147_b1_4_selftest_c147_b1_2.log -- py -u tools/bench/selftest_c147_b1_2.py` -> rc 0, 17 / 0.
## Comparison
- selftest_stagekit per-check lists OLD == NEW, 51 checks (diff of diag_c147_b1_4_{old,new}_selftest_stagekit.json differs only in mode/md5 lines 2-3). J1, J2, J3x2 PASS on both.
- 147-b1-3's 47/2 = 47 + J1 fail + case_j exception (J2/J3 never ran); full count is 51 (prediction 49 in the driver docstring was miscounted).
## Pins after (all == card)
stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, memory_model 88eeb037, plan cfbd9823, pred c4a6a35a, licence 7dce79aa, in db72d8af, recipe 9150f15b, scratch recipe 31009bfc. No tool/test/plan/licence/recipe edited.
OPEN: case J's stub (selftest_stagekit.py:322-330) is stale on HEAD too (pre-existing since cycle 102, stagekit.py:790-794): without a driver it reaches COM - patch the test to stub g.create_local_read (+ is_source) in a tooling card?
