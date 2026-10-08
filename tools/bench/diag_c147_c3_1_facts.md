---
type: facts
status: current
date: 2026-10-08
card: 147-c3-1
---
# Card 147-c3-1: case-J stub of g.create_local_read in selftest_stagekit.py (offline, PD357(c))
LabVIEW processes (tasklist): before 0, after 0. selftest_stagekit.py md5 f90cdaaf -> 29df9b64 (sha256 0007d034...).
`git diff tools/bench/selftest_stagekit.py` = 3 hunks, 5 added lines, 0 removed, all inside case_j_local_read_index:
```
@@ -317,6 +317,7 @@   +    saved_clr = K.g.create_local_read
@@ -328,6 +329,9 @@   +        # card 147-c3-1 (PD357(c)): stagekit.py:794 calls g.create_local_read since cycle 102 - route it to _L, no COM
                        +        K.g.create_local_read = lambda _t, i: dict(_L.create_local(_t, K.g.panel_wiring(_t)[i]["label"], i),
                        +                                                   is_source=[True])
@@ -348,6 +352,7 @@   +        K.g.create_local_read = saved_clr        (in the finally, after the existing restore line)
```
## Runs
- COM blocked, NO case-J routing: new driver tools/bench/diag_c147_c3_1_run.py (b1_4 driver's routing cannot be switched off) -> `py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c147_c3_1_blocked.log -- py -u tools/bench/diag_c147_c3_1_run.py`: BGRUN END rc=0, test rc 0, 51 pass / 0 fail, COM leaks 0 (log :81-84); J1/J2/J3x2 PASS (:75-78).
- Plain run REFUSED by guard_bash (classifier stage_prerun.is_vi_modifying): exemption is a sha256 byte pin, stage_prerun.py:3130 = 82ab60d4...; HEAD/pre-edit bytes were already 2bcfc734... (stale before this card). Gate's own route `stage_prerun --dry` also FAILS: it reads the test's intentional case_b `GATE g-bad` as DRY FAIL. Logged fp-56 (gate_fp_queue.jsonl).
- `selftest_c147_b1_2.py` under bgrun: rc 0, 17 / 0 (diag_c147_c3_1_selftest_c147_b1_2.log:26-27).
- `selftest_td_key_c141_3.py` under bgrun: rc 0, 9 / 0 (diag_c147_c3_1_selftest_td_key.log:12-13).
## Pins after (all == card)
stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, memory_model 88eeb037, plan cfbd9823, pred c4a6a35a, in db72d8af, licence 7dce79aa, recipe 9150f15b, scratch 31009bfc.
OPEN: re-pin VI_MOD_EXEMPT_PATHS for selftest_stagekit.py to sha256 0007d034a4e1f5d1d7b50739fc2281aa582c26a52f6e7a5889a32df5329f346f (and teach --dry to ignore a self-test's intentional FAIL rows) in a tooling card, then run the plain self-test?
