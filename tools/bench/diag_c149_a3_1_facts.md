---
type: facts
status: current
date: 2026-10-08
card: 149-a3-1
---
# Card 149-a3-1 facts: s06 ADOPTED, EL expected file written (51); RETURNED FAIL at mkgraph (W gate 15 vs 16, re-used uid 23807) - no LabVIEW ran

## Done
- Invariants BEFORE `diag_c149_a3_1_inv_before.log` 12/0 (s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877, s06 569ffbf5, stagekit, stagexec,
  gscript, elrule, errorlist_check, memory_model 88eeb037; no scratch).
- ADOPT `diag_c149_a3_1_adopt.log` 3/0: stagexec.adopt_scratch by import; artefact claudeDev\D1_ring_p4s06_20261008_174730.vi md5
  569ffbf51eb6051bf0fdb58946f9bb02 (before == after); input s05 3f9ac26b; scratch gates pass 22, log_fails 0; record t 1791454105.33 (19:08:25);
  adopted_scratch.jsonl md5 658fe5b9; adopted_launch(stage_d1_ring_p4_s06v18.py) returns it (L PASS).
- EL expected `diag_c149_a3_1_elexp.log` 5/0: tools/bench/errorlist_expected_D1_ring_p4s06_20261008_174730.json md5 b47995c8, total 51, 12 entries,
  from read json 899e2656 (items 51 == n_reported 51; compare extra [] missing []). Dropped 5 s05 entries (BA open rows x2, L2-A3 x2, undirected x3,
  sink-only x1, Local x1); added 5 (shift register unwired x1, not-connected OCR variant x1, not-connected x1, loose ends x1, types differ x1).

## FAIL (first unexpected result -> RETURN, no retry)
- `diag_c149_a3_1_mkgraph.log` 3/1 rc 1: gate W "new wires from term_identity.new == the log's D gate count": term_identity.new 15 uids, D line
  (diag_c147_p4s06v18_scratch.log:1002) "D new wires 16 == sim's 16; ... re-used: noted [23807]". tools/stagekit.py:1513 d_new = len(new) +
  kept_by_key reuse_noted (15 + 1). Plan json written anyway: diag_c149_a3_1_graph_plan.json md5 84e84630 (new_wires 15, deleted_wires [23807]).
- The script is a names-only copy of diag_c149_a1_2_mkgraph.py / diag_c148_a2_4_mkgraph.py, neither ever run (peer: only diag_c147_a1_1_mkgraph ran, 11=11).
- NOT done: graph read (diag_c149_a3_1_graph.py written, unrun), memload (load_by_vi not added; memory_model 88eeb037 unchanged), Void census
  (no script written), graph_ring_p4s06_* (none exists).

## Peer (hypothesis, ANSWERED, $1.20) `archive/peer/2026-10-08-c149-a3-1-mkgraph.md`
- Arithmetic holds; fault is in the DATA mkgraph emits (new_wires omits 23807; deleted_wires [23807] from plan actions), so a gate-only fix makes
  graph E5 (graph.py:64-69, "deleted wires absent") fail in LabVIEW. Alternative: w23807 never fully deleted (op 21 'target BROKEN', :990-991);
  same E5 consequence. Cheapest offline test: set(new)|{kept_by_key} == 16; real_end_rows hold w23807 {5171}->{3173,10975}; E5 with 23807 moved
  deleted -> new.

## Close
- Invariants AFTER `diag_c149_a3_1_inv_after.log` 11/0 (same pins, memory_model 88eeb037 recorded), no _elc_/_c149a31_/scratch copies.
  LabVIEW never started in this card; tasklist: no LabVIEW.exe. Handles not read (no LabVIEW).

| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c149_a3_1_mkgraph.log | new-problem 0.828 (jev_gate.log:5312) | hypothesis review owed | dispatched c149-a3-1-mkgraph | ANSWERED, data defect not gate-only |

OPEN: (1) mkgraph for a session with a kept_by_key re-used uid: count 23807 as new (and not deleted) in the graph plan, as stagekit.py:1480-1481's
"one lost + one new" convention does? Then re-issue graph + memload + census. (2) Is "re-used uid vs never deleted" for w23807 worth a LabVIEW wire read?
