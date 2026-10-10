---
type: facts
status: current
date: 2026-10-10
card: 160-c3-3
---
# 160-c3-3: makers re-pinned + re-run byte-identical; L0 now PASS; DRY FAIL at EXECUTOR-STOP UNROUTABLE 2 (fp-84 logged); NOT launched
- Re-pin: `prep_c160_c3_1_md5.py:17`, `prep_c160_c3_1_pred.py:39` stagekit 1441bb4c -> 0b5bb678 (no other edit).
- md5 maker `prep_c160_c3_3_md5a.log`: `GATE PASS | U 14 pinned files unchanged | []`, rc=0 (stagesim 95a162ba, stagexec ddf23a31, stagekit 0b5bb678,
  stage_prerun 7605116f, plan f4520b10, in 56bfddd3, in2 927b805c, graph 7ac24924, 56-row 1fd016bf, b3-1 session e5279899, 4 VIs).
- pred `prep_c160_c3_3_pred.log` 14/0 rc=0: pred 48b50b295fc636bd464754613a0e051e, session 287827be1ed21ee671b571a55a7f6b2d == c3-1 (byte-identical).
- licence `prep_c160_c3_3_licence.log` 5/0 rc=0: f61a2514c47913557531c9862018b850 == c3-1.
- EL `prep_c160_c3_3_el.log` 9/0 rc=0: errorlist_predicted_D1_ring_p5s02b_end.json 79ec32079ceee2b99dac24e554d86856 == c3-1.
- DRY recipe (`prep_c160_c3_3_dry.log`, same form as c3-1) rc=1 after 41s. L0 PASS (:17, `plan_in = plan_ring_p5s02b_in[N]`); K1, DRY graph, SG 0 rows, L1 10 ops PASS.
  `=== DRY FAIL: first_fail=EXECUTOR-STOP tools/bench/plan_ring_p5s02b.json: executed 9 of 10 ops, stopped IN op {'k': 10, 'op': 'case_frame_wire',
  'ids': ['w_hpass']}: ExecStop: UNROUTABLE 2 row(s): acts [9, 10, 11] ['t_go', 'w_gout', 'w_gr']: connect_term_uid: the sink #24139 is already wired
  (w24264); acts [17, 18, 19] ['t_ho', 'w_hout', 'w_hr']: connect_term_uid: the sink #24235 is already wired (w24300) coverage 30/36 lines, first
  mutation Stage._op delete_wire, unverified 1, graph tools/bench/graph_ring_p5s02a_20261010_032547.json` (:54)
- Unverified 1 = `E1 the run reached its last op (record mode; stopped IN op ... w_hpass)` (:52) - NOT CEN2; CEN2 never reached.
- Sequence (:34-45): op 4 delete_wire dw_go, op 5 connect_term_uid w_gr; op 8 delete_wire dw_ho, op 9 connect_term_uid w_hr; every STEPX diff 0.
  w24264 / w24300 are the wires dw_go / dw_ho delete (`diag_c160_c3_1_facts.md:15`). Message source `stagexec.py:4158`.
- Also :48 `RESUME save failed: ... D1_ring_p5s02b_20261010_081747.vi does not exist` (dry: no copy made).
- Logged fp-84 (checker:stagexec:connect_term_uid-sink-already-wired, SUSPECTED) in gate_fp_queue.jsonl. No JEV-LADDER row for this log yet.
- NOT RUN (return at the first unexpected result): scratch dry, prerun (X10/X14/X17/X8), --check-launch, --scratch-required.
- VIs (`prep_c160_c3_3_hash.py`, hashlib only, `prep_c160_c3_3_hash.log` 4/0): p4s09 eb1d0f3107bbba49c9ae67a47c0ee50f equal; p5s01a
  2482fe7bf3426e18b0801c77ec629073 equal; p5s01_20261009_124542 7f2582ae54dc5bc42c3df0bdf3c72d2e equal; p5s02a_20261010_023239 94ffff9413599d5153a5e6fb409294ab equal.
- md5 UNCHANGED (md5a log): tools/plan/in/in2/graph as above; recipes 083fda6d / 3f6fb898. No --launch, no LabVIEW, no tools/*.py or hook edit.
- OPEN: is fp-84 a dry-backend defect (stub routing check for connect_term_uid not seeing the earlier delete_wire) or a plan defect? Needs a tooling card.
