# diag_c162_a2_2_facts - card 162-a2-2 (offline, no LabVIEW) - status PASS
## 1. Pin check + JSON compare - prep_c162_a2_2_check.py (new) -> prep_c162_a2_2_check_r2.log 3/0 (BGRUN END rc=0)
- Pins at selftest_c161_delckpt.py:137-138: stagesim 95a162ba, stagekit 9b8f82c1, stage_prerun 7605116f, plan p5s02b f4520b10 EQUAL;
  ONLY pred plan_ring_p5s02b_pred.json a1fd43fb -> now 4cef0a8c STALE (r2.log:3-8). Agrees with prep_c162_a2_1_pinsweep.log:41-45.
- pred_before_a1_2.json md5 a1fd43fb (= the old pin). Keys before 26 / now 27; removed none; added census_source; changed census,
  census_overall -> differing set exactly [census, census_overall, census_source] (r2.log:10-11), as diag_c162_a1_2_facts.md:40.
- Run 1 (prep_c162_a2_2_check.log, 2/1) FAILed G3 only because the gate required equal key sets (my gate wording; census_source is ADDED);
  data identical in both runs; gate fixed to count added keys, removed must be none, re-run r2 3/0.
## 2. The one pin edit
- tools/bench/selftest_c161_delckpt.py:138 pred pin a1fd43fb -> 4cef0a8c (comment names card 162-a1-2); md5 9bd4889a -> c1354705.
- Docstring mentions of a1fd43fb at :11 and :25 left as written (not pins; ONE edit rule).
## 3. Self-test - selftest_c161_delckpt_c162_a2_2.log: 11/0 (BGRUN END rc=0 after 31s)
- D1, D2, V1, V2, V3, V5, V4, S x3 PASS - same labels and order as the 162-a2-1 run (selftest_c161_delckpt_c162_a2_1.log, 10/1);
  only change: `P pins unchanged` FAIL -> PASS (:21).
## 4. Drained row - gate_fp.py drain --id fp-84 --fixed tools/stagexec.py:2125 --selftest selftest_c161_delckpt
- stagexec.py:2125 = `REREAD_KINDS = ("delete_wire",)` (card 161-a1-1, PD393(a)): a fresh read after every delete_wire.
- fp-84 before: status open, no fixed/selftest; after: status drained, fixed tools/stagexec.py:2125, selftest selftest_c161_delckpt,
  drained_iso 2026-10-10 11:34:57 (gate_fp_queue.jsonl:84). Queue md5 b5a32198 -> 3273bdbb.
- Hook rows fp-75/80/81/83 still open (gate_fp.py list); selftest_c159_a4_1.py not touched; no tools/hooks/** or stage-tool edit.
## OPEN
- OPEN: selftest_c159_a4_1.py:300 stagexec pin 7a712ccb is stale (stagexec now a4df7e15) - not in this card.
