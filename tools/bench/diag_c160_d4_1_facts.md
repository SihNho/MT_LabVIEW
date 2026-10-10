---
type: facts
status: current
date: 2026-10-10
card: 160-d4-1
---
# 160-d4-1: prior-art review of plan_ring_p5s02b.json - ANSWERED, verdict novel, disposition written; step 2 NOT launched (offline)
- Plan-under-review `tools/bench/prep_c160_d4_1_priorart_plan.md` 86d34e14 (NEW-vs-earlier i-v at :25-38, questions :40-).
- Dispatch `prep_c160_d4_1_priorart.log` 65c5d15f: flags as 156 (`--trigger new-op --recipe tools/recipes/stage_d1_ring_p5s02b.py`), `BGRUN END rc=0 after 109s`.
- Archive `archive/peer/2026-10-10-priorart-priorart-c160-d4-1-p5s02b.md` 514bcd5c: outcome ANSWERED (106s) (:9); cost $1.6080, out 9077, 102s, 12 turns (:7).
- Verdict card `tools/bench/cards/verdict_priorart-priorart-c160-d4-1-p5s02b.json` 803c2b14: verdict=novel (archive :10, :345); review card `review_priorart-...json` 0c924ffd.
- Log: "STOP RECORD: none"; "NOVEL RECORD written: tools/recipes/stage_d1_ring_p5s02b.py sha b19d6b20b9ef" (released bytes = recipe md5 083fda6d, unchanged).
- Findings -> disposition (archive `## What was done with it`):
  A1 decided (PD391) no action | A2 none | A3 MERGE uid likely re-made (diag_c159_cen2_wire.md:25-26; d1-loop12-17-split-plan.md:2032) -> no plan
  change, pred prints uid as UID-REUSE not judged (plan_ring_p5s02b_pred.json:136-140, :217); carried to scratch | A4 = B4 |
  B4(a) sink-only uid delete already ran in LabVIEW, c115 (diag_c115b_scratch_v2.log:52-57,80-85: err '', diff 0) -> carry: CLEARED 5 (pred :470) vs c115
  ratio 11 deletes / 6 cleared (d1-loop12-17-split-plan.md:2074); my plan text :29 "Never run in LabVIEW" true only for the stagesim branch |
  B2(b) register_end_case_border on a BASE register never run -> scratch (PD391(e)) | (c) same as A3 | B3(d) no shared helper -> OPEN |
  B1 base_register_end no earlier copy | C no user-rule contradiction. No REFUTED:/FIXED: line (none owed under novel).
- Gate check `diag_c160_d4_1_gate.py` 9f3be559 -> `diag_c160_d4_1_gate.log` a357a874 RESULT 4/0: "UNDISPOSED priorart | None";
  "PRIOR-ART VERDICT | newest ...c160-d4-1-p5s02b.md | non-novel [] | released set() | bad [] | open []"; stop_record.check_command allow=True on
  the step-2 scratch and recipe commands (not run).
- md5 UNCHANGED: plan f4520b10, pred 48b50b29, in 56bfddd3, in2 927b805c, graph 7ac24924, recipe 083fda6d. VIs s09 / P5-1a / P5-1 / 94ffff94: not hashed
  (md5sum on claudeDev refused by the permission layer). tools/**: only this card's own new files (prep_/diag_c160_d4_1*); no hook/tool/plan edit.
- NOT launched: no --launch, no stage/recipe run; LabVIEW never started by this card; tasklist refused by the permission layer (not checked).
OPEN: A3 - should a gate/row be forbidden from keying on w24285 / w24312 surviving (reviewer asks it; pred already does not judge the uid)?
OPEN: B4 - add the c115 cleared-per-delete ratio as a named expectation for the step-2 scratch Error List read (CLEARED 5)?
OPEN: B3 - extract the stub-delete insertion (prep_c160_b3_1_mk.py IN2 / selftest_c160_regface.py:70-79) into stagekit (tooling card)?
