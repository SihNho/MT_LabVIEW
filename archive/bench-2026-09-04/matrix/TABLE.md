---
type: narrative
status: historical
date: 2026-09-05
tags: [archive]
---

## Model x effort matrix (protocol v2, verified by verify_op.py; n = attempts per cell)

| model | effort | pass /12 | U1 | U2 | U4 | U5 | min | cost $ | turns | out tok | GUI acts | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku | low | 2/12 | 2 | 0 | 0 | 0 | 9.8 | 0.94 | 91 | 25794 | 46 | 1 |
| haiku | medium | 3/12 | 3 | 0 | 0 | 0 | 6.8 | 0.55 | 63 | 16206 | 20 | 1 |
| haiku | high | 3/12 | 3 | 0 | 0 | 0 | 14.4 | 0.70 | 68 | 21531 | 32 | 1 |
| haiku | xhigh | 3/12 | 3 | 0 | 0 | 0 | 8.4 | 0.71 | 80 | 16736 | 25 | 1 |
| haiku | max | 3/12 | 3 | 0 | 0 | 0 | 9.4 | 0.86 | 86 | 24832 | 45 | 1 |
| sonnet | low | 12/12 | 3 | 3 | 3 | 3 | 15.8 | 3.16 | 110 | 24975 | 47 | 1 |
| sonnet | medium | 11.7/12 | 3.0 | 2.7 | 3.0 | 3.0 | 14.9 | 3.59 | 132.0 | 25816 | 45.7 | 3 |
| sonnet | high | 12/12 | 3 | 3 | 3 | 3 | 13.8 | 4.73 | 156 | 30333 | 45 | 1 |
| sonnet | xhigh | 12/12 | 3 | 3 | 3 | 3 | 13.6 | 5.10 | 156 | 33524 | 43 | 1 |
| sonnet | max | 12/12 | 3 | 3 | 3 | 3 | 20.6 | 5.72 | 169 | 65501 | 44 | 1 |
| opus | low | 12/12 | 3 | 3 | 3 | 3 | 9.3 | 3.53 | 66 | 14134 | 43 | 1 |
| opus | medium | 12/12 | 3 | 3 | 3 | 3 | 12.2 | 5.92 | 97 | 22935 | 44 | 1 |
| opus | high | 12/12 | 3 | 3 | 3 | 3 | 13.3 | 7.77 | 132 | 25209 | 43 | 1 |
| opus | xhigh | 12/12 | 3 | 3 | 3 | 3 | 13.3 | 7.06 | 115 | 27073 | 43 | 1 |
| opus | max | 12/12 | 3 | 3 | 3 | 3 | 11.3 | 4.84 | 80 | 22700 | 43 | 1 |
| fable | low | 12/12 | 3 | 3 | 3 | 3 | 10.3 | 9.95 | 83 | 17310 | 45 | 1 |
| fable | medium | 12/12 | 3 | 3 | 3 | 3 | 9.4 | 7.52 | 65 | 15639 | 43 | 1 |
| fable | high | 12/12 | 3 | 3 | 3 | 3 | 12.0 | 9.53 | 79 | 22213 | 54 | 1 |
| fable | xhigh | 11/12 | 3 | 2 | 3 | 3 | 9.2 | 9.84 | 77 | 24508 | 44 | 1 |
| fable | max | 12/12 | 3 | 3 | 3 | 3 | 27.1 | 18.63 | 113 | 63510 | 45 | 1 |

Pass = trial verified over COM by verify_op.py (position delta / new node / ExecState / window list); the cell cannot mark its own trial. cost $ = list-price API cost reported by `claude -p`; min = wall time of the cell run; turns = num_turns; GUI acts = gated lv_gui actions logged in the run window.

## Non-results (excluded from the table)

| cell | protocol | why |
|---|---|---|
| bench-gui-haiku-medium | v1-selfreport | INVALID: the agent registry served the STALE definition (100-loop VI task) although the GUI task was on disk;  |
| bench-gui-haiku-medium | v1-selfreport | STALE guard fired: registry still served the old definition in the same turn. 47.5k tokens = Haiku spawn fixed |
| bench-gui-haiku-low | v1-selfreport | protocol v1-selfreport |
| bench-gui-haiku-low | v1-selfreport | protocol v1-selfreport |
| bench-gui-sonnet-low | v2-verify_op | INFRA: cell backgrounded its first command and yielded (print-mode run ended after 2 turns); rerun queued |
| bench-gui-fable-xhigh | v2-verify_op | INFRA: revert hung, cell backgrounded it and yielded after 10 turns (print-mode run ended); rerun queued |
| bench-gui-fable-max | v2-verify_op | USAGE LIMIT: interrupted after 708 s at 04:40, rerun from scratch at 06:22 per protocol |
| bench-gui-fable-xhigh | v2-verify_op | ACCOUNTING LOST: 12/12 verified lines exist (gui_results, later tagged #prior) but no cost/time JSON; rerun |
| bench-gui-sonnet-medium | v2-verify_op | ACCOUNTING LOST (driver died mid-cell, 3rd time); rerun |
