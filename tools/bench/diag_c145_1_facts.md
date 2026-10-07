---
type: facts
status: current
date: 2026-10-07
---
# Card 145-a1-1 facts: P4 session 4 scratch STOPPED in op 10 (SQ1 RingSeqCheck_v0 drop, terminal binding); not adopted

## Before
- `diag_c145_1_check.log` 10/0: 7 card inputs md5 == card; s03 282301ca and bed 39511877 unchanged; no LabVIEW. No gate refused the
  scratch launch (no prior-art review asked for; the `diag_c144_2_el.log` rc=1 gate did not hold it -> n/a).

## Scratch (ONE run) `tools/bench/diag_c144_p4s04v18_scratch.log` (BGRUN END rc=1, 409 s; log name fixed by the recipe's LOG constant)
- RESULT 15/2 (:276-278). First fail: E1 stopped IN op 10 (`p4_s2_seqcheck`, SQ1) on BINDING (:255-256).
- Ops 1..9 PASS, STEPX diff 0; PS1 RingPickSlot_v0 drop bound -1 -> #29719 (:83), 12 rows = 5 named + 7 '' (:66-78).
- Op 10: drop RingSeqCheck_v0.vi on Diagram #23166 err '' -> SubVI #29724, 12 rows: 8 named + 4 '' sinks (t0, t4, t5, t6) (:230-242).
  Binding: sim 8 keys (plan_ring_p4_s04v18.json:310-357, why "PROVISIONAL terminals ... unassigned '' rows unread") vs real 8 + ('Terminal',False,''):4.
- Peak 608.0 MB (X10 680.1, d -72.1); MEM 680 stop not hit; MEM/MEML/IN/GONE PASS (:280-284). Handles meter 45787 (k1) -> 46109 (k10);
  at exit 40233; ref counts opened 6 / closed 6 (:261-263).
- Saved by the broken-intermediate route: `claudeDev\D1_ring_p4s04_20261007_212230.vi` abb76d41 (318197 B, ExecState 0) (:251);
  resume record `tools/bench/resume/resume_plan_ring_p4_s04v18_20261007_212913.json` from_step 9. NOT adopted (final None).
- Census not written (run incomplete). Error List not read. Graph not read.

## Review (owed by the Jev ladder)
- JEV-LADDER `diag_c144_p4s04v18_scratch.log` our-script-bug p=0.596 -> hypothesis review owed (jev_gate.log).
- `archive/peer/2026-10-07-c145-1-sq1-bind.md` ANSWERED (opus 5.5 high, $1.36): cause = stale plan row; the pane was MEASURED
  2026-10-03 (`diag_c142_4_facts.md:22-23`, `build_ringseqcheck_v0.log:216-217`: slots 11..7 n1 n2 last Latest discards, 3..1 next last /
  next discards / valid, 0 and 4-6 free); prerun bound SQ1 to a placeholder (`prep_c144_a2_2_prerun.log:47`) and has no check of a
  `subvi_path` create against the measured pane (tool gap); uid re-use #29724 (purged Invoke op 8) / #29721 to watch.

## After
- `diag_c145_1_check_after.log` 10/0: inputs, s03 282301ca, bed 39511877 unchanged; no LabVIEW process.
