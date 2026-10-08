---
type: facts
status: current
date: 2026-10-08
card: 147-a1-4
---
# Card 147-a1-4 facts: s06 scratch STOPPED IN op 21 (last op, p4_rbA_re1), RESULT 12/2 -> RETURN, NOT adopted

## Before
- `diag_c147_a1_4_check.log` 22/0: 16 card inputs + elrule a5ee7d5c md5 == pins; s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877; no LabVIEW.
- Scratch recipe dry PASS (`diag_c147_a1_4_scr_dry.log`), prerun 16/0, X10 674.2, X11 PASS licensed (`diag_c147_a1_4_scr_prerun.log:114,133,137`);
  `--scratch-required` rc 3, census unpredicted rows 1..25 (`diag_c147_a1_4_scrreq.log`). No gate refused the launch.

## Scratch (ONE run) `tools/bench/diag_c147_p4s06v18_scratch.log` (BGRUN END rc=1, 443 s), md5 784211e8
- RESULT 12/2; first fail E1 "stopped IN op k 21 connect acts [25] ids ['p4_rbA_re1']" (:311,:313).
- Ops 1..20 ran; PRIM PASS on created Index Array #30300 (p4_ia_bufdiff, :245); op 19 delete_wire w23807 err '' (:277); op 20 p4_rbA_re0
  connect_nested_v1 #5171 -> #10975 err '' after a STALE-ADDRESS retry (:283,:288), readback 'UID 2': 0 (:286).
- Op 21: STALE-ADDRESS retry on #5171 'pos in cal image out' of #5058 (:294), then gscript.wire_indicators N[26] -> 'Pos within cal image'
  raised "target BROKEN after wiring" (:297-298); sink [23166, 'Pos within cal image'], "declared sinks: []" (:310).
- Work copy saved by gui_save: `claudeDev\D1_ring_p4s06_20261008_020717.vi` md5 b58046e33c1f8def1d6b5552d94b7b85, 319393 B, ExecState 0
  (:303,:306); resume record `tools/bench/resume/resume_plan_ring_p4_s06v18_20261008_021435.json` from_step 20 (:309). NOT adopted.
- METERED start 570.2 MB (k0, :60), op-0 read 576.8 (:61) vs prerun assumption 612.6 (d -42.4); PEAK 618.7 MB (:295, sum) vs X10 674.2
  (d -55.5); MEM_STOP 680 / MEMSTOP 695 not hit; MEM, MEML, IN, GONE PASS (:336-339).
- Hygiene: refs opened 22 == closed 22 (:316); H2 input 3f9ac26b unchanged, H3 pins, H6 files PASS; handles post-open 45745 (:60) -> exit 33021 (:328).
- Not reached: E1 at all checkpoints, D/TD/PB gates, Error List, EL-ADVISORY, census, adopt, final EL, fresh load, graph read, load_by_vi entry.
  Scripts written and unrun: diag_c147_a1_4_census.py, _adopt.py, _elexp.py, _mkgraph.py, _graph.py, _memload.py.

## Review (owed by the Jev ladder)
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c147_p4s06v18_scratch.log | new-problem 0.804 | hypothesis review owed (old path) | dispatched `-Role hypothesis` (task diag_c147_a1_4_hyp_task.md) | ANSWERED 172 s, `archive/peer/2026-10-08-c147-a1-4-re1.md` |
- Review REJECTS my claim (op 20 silent decline): wire_indicators raises whenever exec_state(target) != 1 (`tools/gscript.py:2152-2155`, checked),
  and the bed is ExecState 0 by design (scratch log :57); the same RuntimeError on #5058 -> 'Pos within cal image' passed E1 via a declared sink
  gate in `stage_d1_k_r2.log:232-243`; 'UID 2': 0 reads 0 on all 9 connect_nested_v1 calls of this log. Its test: resume from step 20 on a new
  byte copy with a sink gate reading t5171 / t10975 / CT #3173 after ops 20 and 21. Nothing applied (card: no retry, no tool edits).

## After: `diag_c147_a1_4_check_after.log` 20/0: pred c4a6a35a and memory_model 88eeb037 UNCHANGED (census/memload not run); s05 3f9ac26b,
s04 95e408ff, s03 282301ca, bed 39511877 unchanged; no LabVIEW process (`tasklist` "no tasks").
