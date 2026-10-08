---
card: 147-c3-2
date: 2026-10-08
status: PASS - licence `renames` (5) + build recipe on the PD356(b) gate API; dry/prerun PASS on final bytes; stored s06 read D/TD/PB ALL PASS
---
# Facts - card 147-c3-2 (offline; no LabVIEW process before/after, tasklist count 0)

## Diff
- `plan_ring_p4_s06v18_licence.json` 7dce79aa -> 7f70bbf9: `decided_by` + one clause citing PD356(d)/PD357(e); NEW top-level `renames` (:16-31) =
  {node 2626, term_uids [2832,4160,4165], from "array", to "element"} + {node 9503, term_uids [9505,9508], from "Value", to ""}, each with a `why`.
  `rename_by_uid` byte-identical. `stagekit.licence_renames` -> exactly 5 keys (diag_c147_c3_2_check2.log C1); `stage_prerun.pb_licences(plan)` =
  {2626: licence file} before (diag_c147_c3_2_before.log) and after (check2.log C2).
- `stage_d1_ring_p4_s06v18.py` 9150f15b -> d947df5d: `:30` REN = K.licence_renames(licence file, read by path); `:128-129`
  term_identity_gates(..., renames=REN, bind={"term": x.bind["term"], "obj": x.bind["obj"]}) (x.bind = Executor.bind, stagexec.py:1931);
  `:130-132` D text/detail: d_new/d_lost, reuse_noted, reuse_bad; `:134-137` TD text/detail: td_key, renames, unlicensed_renames;
  `:143` pbr, restored, unlic = K.pb_rename_rows(BASE terminals, sim end, real, REN) -> build4(pbr, ...) at :144; `:147-149` PB adds `unlic == []`,
  detail restored/unlicensed. No other gate changed.
- `stage_d1_ring_p4_s06v18_scratch.py` unchanged (31009bfc): it runs R.body (:80) and imports R (:29), so the new gates apply as-is.

## Runs on the FINAL bytes (each `py tools/bgrun.py --material --max-min N --log <log> -- py -u ...`)
- `tools/bench/diag_c147_c3_2_check.py` -> 11/0 rc 0 (diag_c147_c3_2_check2.log): PC py_compile both recipes OK; C1-C3; R1 binding 6030/6030;
  D new 16 == sim 16, lost 8 == sim 8, reuse_noted [23807], reuse_bad []; TD lost [] == gone [], unwired [], 5 renames, unlicensed [];
  PB cdiff == pred 18 rows + 13 open pairs, restored the 5 keys, unlicensed []; P1 pins unchanged.
- `stage_prerun.py --dry` build -> PASS 1/0 rc 0 (diag_c147_c3_2_dry.log:93-94; D :83, TD :85, PB :87 PASS in dry); scratch -> PASS 1/0 rc 0 (scr_dry.log:115-116).
- `stage_prerun.py --prerun` build -> PASS 16/0 rc 0 (prerun.log:119-120; X6 uids [] names [] :109; X10 679.3 <= 680 :114; X11 licensed :95);
  scratch -> PASS 16/0 rc 0 (scr_prerun.log:141-142).
- `stage_prerun.py --scratch-required` build -> rc 3 as expected (CENSUS-UNPREDICTED rows 1..25, diag_c147_c3_2_scrreq.log).
- prerun_records.jsonl pins script sha256 + plan md5 cfbd9823 + input 3f9ac26b; it does NOT pin the licence md5.
- NOT RUN: scratch `--el-advisory-selftest` (guard_bash RETRY CAP: scratch ran 3x in cycle 147) -> gate-fp fp-58. Bare `py -m py_compile <recipe>`
  refused by guard_cycle (dup of fp-54) -> compiled inside the diag. Licence edit warned by guard_write (open card 147-a2-1 pins 7dce79aa; that
  card was killed and resumed by 147-a1-6/7) -> fp-57.

## Unchanged (md5 after)
stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, memory_model 88eeb037, plan cfbd9823, pred c4a6a35a, in db72d8af; selftest_stagekit.py not touched.

OPEN: the scratch launch needs (a) a prior-art review (guard_cycle DIFF-ONLY vs stage_d1_ring_p4_s03v18.py) and (b) a RETRY_CARD (3 runs > cap 2 in cycle 147);
selftest_c147_b1_2.py P0 pins licence 7dce79aa + recipe 9150f15b and will now FAIL P0 - re-pin or accept?
