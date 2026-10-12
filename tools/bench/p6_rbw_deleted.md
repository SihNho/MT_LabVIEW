---
type: facts
status: current
date: 2026-10-12
card: 167-a1-1
---
# P6-0 (d): wires deleted by ONE VI-level Remove Bad Wires on a scratch copy of 75773b0d (facts only)
Written by `tools/bench/diag_c167_a1_1_diff.py` from `tools\bench\graph_ring_p5s02e_20261012_173009.json` (7815af09) minus `tools\bench\graph_ring_p6rbw_20261012_191349.json` (c5531708). Machine-readable: `tools/bench/p6_rbw_deleted.json`.

Counts: `{"wires_before": 2091, "wires_after": 2066, "deleted": 25, "deleted_data_carrying": 1, "deleted_not_data_carrying": 24, "deleted_by_shape": {"termless": 22, "source-only": 2, "src+sink": 1}, "new": 0, "termless22_deleted": 22, "termless22_kept": 0, "dedupe_before": 32, "dedupe_after": 32}`

22 termless F1 uids: 730 deleted, 4906 deleted, 5637 deleted, 5709 deleted, 5975 deleted, 6096 deleted, 6363 deleted, 9012 deleted, 9868 deleted, 10187 deleted, 10312 deleted, 10573 deleted, 10908 deleted, 11352 deleted, 17287 deleted, 17393 deleted, 23556 deleted, 28847 deleted, 29787 deleted, 31059 deleted, 31166 deleted, 32890 deleted

| wire | tag | shape (src/sink) | F1 termless | terminals before (owner #uid class : term #uid 'name' end) |
|---|---|---|---|---|
| 730 | not data-carrying | 0/0 | yes | (no terminal) |
| 4906 | not data-carrying | 0/0 | yes | (no terminal) |
| 5637 | not data-carrying | 0/0 | yes | (no terminal) |
| 5709 | not data-carrying | 0/0 | yes | (no terminal) |
| 5975 | not data-carrying | 0/0 | yes | (no terminal) |
| 6096 | not data-carrying | 0/0 | yes | (no terminal) |
| 6363 | not data-carrying | 0/0 | yes | (no terminal) |
| 9012 | not data-carrying | 0/0 | yes | (no terminal) |
| 9868 | not data-carrying | 0/0 | yes | (no terminal) |
| 10103 | not data-carrying | 1/0 | no | #10114 LoopTunnel : t10116 '# FD points' source |
| 10187 | not data-carrying | 0/0 | yes | (no terminal) |
| 10312 | not data-carrying | 0/0 | yes | (no terminal) |
| 10573 | not data-carrying | 0/0 | yes | (no terminal) |
| 10908 | not data-carrying | 0/0 | yes | (no terminal) |
| 11352 | not data-carrying | 0/0 | yes | (no terminal) |
| 12256 | not data-carrying | 1/0 | no | #11608 Bundler : t11614 'output cluster' source |
| 17287 | not data-carrying | 0/0 | yes | (no terminal) |
| 17393 | not data-carrying | 0/0 | yes | (no terminal) |
| 23556 | not data-carrying | 0/0 | yes | (no terminal) |
| 25618 | data-carrying | 1/1 | no | #11261 BuildArray : t11267 'appended array' source; #23166 Diagram : t8323 'Force (pN) vs Extension (nm) ' sink |
| 28847 | not data-carrying | 0/0 | yes | (no terminal) |
| 29787 | not data-carrying | 0/0 | yes | (no terminal) |
| 31059 | not data-carrying | 0/0 | yes | (no terminal) |
| 31166 | not data-carrying | 0/0 | yes | (no terminal) |
| 32890 | not data-carrying | 0/0 | yes | (no terminal) |

New wire uids after RBW (not in the before graph): 0
