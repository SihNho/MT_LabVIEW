---
type: facts
status: current
date: 2026-10-10
card: 160-f3-2
---
# 160-f3-2: passwire gate D vs card 160-a2-1's t_go / t_ho compile change; offline, no LabVIEW, no tool / hooks / plan edit
- Measure `diag_c160_f3_2.py` -> `diag_c160_f3_2.log` RESULT 4/0 (BGRUN END rc=0). p5s02r_all 15da9551 compiles to 40 ops before and now (log:3).
- | op | before | after |
  | 19 | tunnel acts [30,31,32] (t_go, w_gout, w_gr) in 31 out 32 tunnel new:TG2 | connect_term_uid register_end_case_border, case new:CQ7, same acts/in/out/tunnel (log:5-8) |
  | 22 | tunnel acts [37,38,39] (t_ho, w_hout, w_hr) in 38 out 39 tunnel new:TH2 | connect_term_uid register_end_case_border, case new:CQ7, same acts/in/out/tunnel (log:10-13) |
- No other op differs; `stagexec.checkpoint_ops` equal before/after, 23 checkpoints (log:14-15). p5s02a / p5s01a / p5s01b / p5s01_in equal to the old list (log:17).
- Decision: ADOPTED change (160-a2-1 R3), not a regression -> re-baselined. Writer = `prep_c156_a1_2_lib.compile_all()` + the measure script's json.dump(indent=0, sort_keys=True)
  (`prep_c156_a1_2_measure.py:110-112`), called, not re-written. New `sim/ring_p5s02pw/compile_before_c160a2.json` 36eda07a (206 plans); old compile_before.json 7ca1c4c4 untouched (log:19-20).
- Entries differing old vs new list (all plans): 8, all p5s02*/p5s02b* (log:18); gate D reads only the 5 plans above.
- `selftest_c156_passwire.py` 321ef700 -> 786bc85d: docstring :30-33 names both files and why; gate D :157 reads compile_before_c160a2.json.
- `selftest_c156_passwire_c160_f3_2.log:34` RESULT 20/0 (BGRUN END rc=0 after 543s): D p5s02r_all 40 ops PASS (:27), D p5s02a 17 ops PASS (:28), P pins PASS (:32).
- md5 UNCHANGED: stagesim 95a162ba, stagexec ddf23a31, stagekit 1441bb4c, stage_prerun 7605116f, compile_before.json 7ca1c4c4, plan_ring_p5s02r_all 15da9551,
  plan_ring_p5s02b f4520b10 / _b1 09ebc7a6 / _c159 caef7e1c / _in 56bfddd3 / _in2 927b805c / _licence f61a2514 / _pred 48b50b29. tools/hooks: no edit.
- FACT (not acted on): passwire route-check baseline G/H rows now UNROUTABLE with `connect_term_uid: the sink #24139 is already wired (w24264)` / `#24235 ... (w24300)`
  (`selftest_c156_passwire_c160_f3_2.log:4`, same in `_c160_f3_1.log:4`); before 160-a2-1 they were `ADDRESS: node #24083 not in Diagram[124]` (`_c160.log:4`).
OPEN: p5s02r_all has no delete-wire rows for w24264 / w24300 (160-a2-1's R1 temp plan added dw_go / dw_ho) - does p5s02r_all need them, or is it superseded by p5s02b?
