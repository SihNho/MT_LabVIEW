---
type: facts
status: current
date: 2026-10-07
---
# Card 145-a2-3: connector-pane wiring rules READ (OpWiringRules_v0)

| VI | pane index | control | rule | meaning | dir | wired at PS1/SQ1 |
|---|---|---|---|---|---|---|
| RingPickSlot_v0 | 0 |  | 0 | Invalid | free | None |
| RingPickSlot_v0 | 1 | found | 2 | Recommended | output | True |
| RingPickSlot_v0 | 2 | min slot | 2 | Recommended | output | False |
| RingPickSlot_v0 | 3 | min Num | 2 | Recommended | output | True |
| RingPickSlot_v0 | 4 |  | 0 | Invalid | free | None |
| RingPickSlot_v0 | 5 |  | 0 | Invalid | free | None |
| RingPickSlot_v0 | 6 |  | 0 | Invalid | free | None |
| RingPickSlot_v0 | 7 |  | 0 | Invalid | free | None |
| RingPickSlot_v0 | 8 |  | 0 | Invalid | free | None |
| RingPickSlot_v0 | 9 |  | 0 | Invalid | free | None |
| RingPickSlot_v0 | 10 | last | 2 | Recommended | input | True |
| RingPickSlot_v0 | 11 | Num | 2 | Recommended | input | True |
| RingSeqCheck_v0 | 0 |  | 0 | Invalid | free | None |
| RingSeqCheck_v0 | 1 | valid | 2 | Recommended | output | False |
| RingSeqCheck_v0 | 2 | next discards | 2 | Recommended | output | False |
| RingSeqCheck_v0 | 3 | next last | 2 | Recommended | output | False |
| RingSeqCheck_v0 | 4 |  | 0 | Invalid | free | None |
| RingSeqCheck_v0 | 5 |  | 0 | Invalid | free | None |
| RingSeqCheck_v0 | 6 |  | 0 | Invalid | free | None |
| RingSeqCheck_v0 | 7 | discards | 2 | Recommended | input | False |
| RingSeqCheck_v0 | 8 | Latest | 2 | Recommended | input | False |
| RingSeqCheck_v0 | 9 | last | 2 | Recommended | input | True |
| RingSeqCheck_v0 | 10 | n2 | 2 | Recommended | input | False |
| RingSeqCheck_v0 | 11 | n1 | 2 | Recommended | input | True |

Source log: tools/bench/diag_c145_a2_3_measure.log (ROW lines). Wired-at-drop: tools/bench/diag_c145_a2_1_table.log:16-31.
Handles (after restart, end): (33954, 34007). Gates: {'0 pinned md5s before': True, '0 reader hygiene record PASS and md5 == reader file': True, 'R RingPickSlot_v0 read: no error, len == 12 terminals': True, 'R RingSeqCheck_v0 read: no error, len == 12 terminals': True, 'T every unwired input at PS1/SQ1 is NOT Required': True, 'T every named terminal has a rule in 1..3': True, 'E LabVIEW gone (tasklist)': True, 'E pinned md5s unchanged': True, 'H abb76d41 + its resume record deleted': True}
