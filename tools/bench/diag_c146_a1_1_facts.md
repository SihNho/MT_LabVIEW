---
type: facts
status: current
date: 2026-10-07
---
# Card 146-a1-1 - gate-fp fp-43..50 drained (offline)

## md5 old -> new
| file | old | new |
|---|---|---|
| tools/hooks/guard_write.py | 5c7ec80c2652a144089569ed92794e11 | 391a832448bce5cdbec2233317bf09c1 |
| tools/hooks/guard_peer.py | 1c54c874a9f9f9f6583dae3260d28aea | f30355d144a34cc0cffc47b6b3edfd05 |
| tools/bench/selftest_c_e3.py | 98a4b4535dc78156f405ef2cdc1e1f53 | 428878a5412e479aae33a23a965663b7 |
| tools/bench/gate_fp_queue.jsonl | 42c30ecad25dec445953839f8ce75d19 | 00b7ab89c68d4e2df370fac0732694ec |
| tools/bench/selftest_guard_peer_c146.py | (new) | 63fbc78f073029b35322274b90546675 |
| tools/bench/diag_c146_a1_1_repro.py | (new) | 1e265eb2bf8cac62cdadc554ec8bc18e |
| tools/bench/diag_c146_a1_1_run.py | (new) | f6da1f805238612ba787dcb8eda15402 |

## Repro (before: tools/bench/diag_c146_a1_1_repro_before.log; after: _repro_after.log)
- fp-43/45/47/48/49/50: each cited card copied as an OPEN card; every one lists its pinned file in flags.write
  (in_flags.write True, fp-47 included) -> before STALE, after no message. Scratch pair: own-write pin STALE -> none;
  non-write pin STALE -> STALE (unchanged).
- fp-44: diag_c144_2_cls.log first run (refusal-time text) fails `class per bound uid`; script header labview none /
  hardware none; main() with the recorded ladder line (jev_gate.log:4689 new-problem p=0.750) rc 2 -> rc 0
  RULE-OFFLINE-NEWPROBLEM. (The log's LAST run is now PASS, diag_c144_2_cls.log:45-46, so the live log no longer arms.)
- fp-46: prep_c145_2_pred.log fails X10 (rc 1); header none/none; ladder jev_gate.log:4755 new-problem p=0.800;
  rc 2 -> rc 0. The log carries NO non-fatal marker (prep_c145_2_pred.log:11 `GATE FAIL | X10 ...`; the script's gate()
  prints the same text fatal or not, prep_c145_2_pred.py:46-50), so it is released by the fp-44 header rule, not by a
  log-text rule.

## Fixes
- guard_write.py:79-88 - a pin on a file the pinning card's own flags.write covers (protocol.path_in_globs) is skipped
  for that card only.
- guard_peer.py:635-667 `offline_new_problem` + :1345-1358 RULE-OFFLINE-NEWPROBLEM - only on a JEV-LADDER new-problem
  line; every script of the log's LAST run must carry a RAW header labview none + hardware none (offline-args readings
  do not count), no TIMEOUT, no STALL; else the old block.

## Self-tests (pass/fail; before tools/bench/diag_c146_a1_1_before.log, after _after2.log)
| test | before | after |
|---|---|---|
| selftest_c_e3 | 62/0 | 64/0 (+WR10, WR11) |
| selftest_guard_peer_budget | rc 0, 0 FAIL lines | 12/0 |
| selftest_guard_peer_failre | rc 0, 0 FAIL lines | 29/0 |
| selftest_guard_peer_jev | 29/0 | 29/0 |
| selftest_guard_peer_ladder | rc 0, 0 FAIL lines | 21/0 |
| selftest_guard_peer_samerow | 21/0 | 21/0 |
| selftest_guard_peer_scan_tmp | rc 0 (RESULT PASS, no counts) | rc 0 |
| selftest_guard_peer_77_measure | 1/0 | 1/0 |
| selftest_guard_peer_scrreq_c144 | 12/0 | 12/0 |
| selftest_guard_peer_c146 (new) | - | 11/0 (A, B positive; C-I negative) |

## Queue
`gate_fp.py drain` fp-43/45/47/48/49/50 -> guard_write.py:84 + selftest_c_e3; fp-44/46 -> guard_peer.py:1352 +
selftest_guard_peer_c146. `gate_fp.py list --open` prints 0 lines.
