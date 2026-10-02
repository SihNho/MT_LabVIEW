---
type: facts
status: current
date: 2026-10-02
tags: [card-139-7, ring-p4, step-1, x10, offline]
---
# Card 139-7 facts (LabVIEW NOT opened; returned FAIL at the first unexpected gate, pass 1 SP = X10 memory prediction)
## 1. Step-1 plan maker — `tools/bench/prep_c139_7_s1.py` -> `tools/bench/prep_c139_7_s1.log` (rc=1 after 88 s, 7 pass / 1 fail)
- Copy of `prep_c139_6_mkv14.py:170-274` (step-1 half) reading steps from `plan_ring_p4_v14_meta.json` 29f6535b; the maker's all-steps
  `<= 42` gate replaced by MS1 (step 1 only). M0 PASS (v14 22f58271, meta 29f6535b, graph 50595c62, mkv14 8a9d618e) (`:3`).
- MS1 PASS: per step {1: 39, 2: 43, 3: 40, 4: 36, 5: 27}, no late refs into step 1, every id stepped (`:4-5`).
- SA PASS: pass A (no open_rows) replays 39/39 to its end (`:48`). Step 0 rows 16, end rows 16, none gone (`:49`).
- TIE PASS: all 16 end cdiff rows are open on the BED at step 0 and every (node, term) pair is a declared open row of
  `plan_ring_p3b2b.json`; **0 rows made by a step-1 action** (`:66`, own 0 / bed 16).
- SB PASS: `plan_ring_p4s1.json` e6992800 FINAL, open_rows_match True, route check PASS, 11 open pairs, end rows == pass A (`:147-148`).
- EL prediction for the step-1 end: total 51 (= bed), alternative 64 (+13 unwired created sinks) (`:149-151`; pred `errorlist`).
- **FAIL SP (`:152`)**: X10 predicted peak **750.7 MB > fail 690.0** (`plan_ring_p4s1_pred.json:384-388`); start 606.1 MB (600.2 bed load +
  5.9 op-0 read), N = 39 ops, **R = 29 whole-VI reads** (`:311-312`) = checkpoints {0, end} + every bind op (the recipe's
  `CHECKPOINTS = {0, len} | BIND`, `stage_d1_ring_p4s1.py:25-26`). Ops: create 24, connect 5, wire_remove_loose_ends 3, connect_term_uid 2,
  add_sr 2, delete_wire 1, delete_object 1, stop 1 (`:150`). Census: 0 classes predicted, every created action CENSUS-UNPREDICTED (`:150`).
- Written anyway (the maker writes pred before the SP gate): `plan_ring_p4s1_in.json` 7e5c05ce, `plan_ring_p4s1.json` e6992800,
  `plan_ring_p4s1_pred.json` 93ae6129 (`below_fail: false`).
## 2. Not run (return-at-first-unexpected)
- Recipe dry / prerun / X10 / `--scratch-required`, the scratch run, the Error List read, the steps 2-5 re-cut (pass 5).
- `tools/recipes/stage_d1_ring_p4s1_scratch.py` names moved c139_6 -> c139_7 only (log, prerun log, scratch name, out json); not run.
- No JEV-LADDER row for `prep_c139_7_s1.log` in `tools/bench/jev_gate.log` at return time.
## 3. For judgement
- At 600.2 MB load, this 39-action step with 29 checkpoint reads cannot pass X10 at 690; the earlier "≤ ~40 edits per session" sizing
  (PD301/D-2026-10-02-04) does not hold for this action mix unless checkpoints per session drop or the step splits by memory.
