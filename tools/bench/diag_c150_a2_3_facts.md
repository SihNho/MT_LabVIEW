---
type: facts
status: current
date: 2026-10-08
card: 150-a2-3
---
# Card 150-a2-3 facts: the s07 --rebase onto the real s06 graph FAILS with a tool exception from the 150-a2-2 edit (FAIL, returned)

This ran offline. No LabVIEW process was present before or after (`prep_c150_a2_3_check_before.log` / `_after.log`, LV gate PASS).
The card stopped at the first unexpected result (step 1), as its rules say: a tool fault is a return. Nothing was diagnosed beyond reading the
raising line, nothing was retried, and no stage tool was edited.

## 1. Rebase (`prep_c150_a2_3_rebase.log`, `BGRUN END rc=2 after 1s`)
- Command: `py tools/stage_prerun.py --rebase tools/bench/plan_ring_p4_s07v18.json --graph tools/bench/graph_ring_p4s06_20261008_192149.json` (under bgrun).
- Binding passed this time:
  - CREATION-MAP `plan_ring_p4_s06v18_cfbd9823_20261008_175325.jsonl` (obj 4, term 8)
  - MAP-BOUND nodes {-19:30300, -17:30294, -10:30290, -5:30287}
  - FALLBACK-COUNT 0
  - `REBIND 4 node(s) ... terminals by {'map': 8}`
- RENAMED-OLD (5): 2832/4160/4165 #2626 'array'->'element'; 9508/9505 #9503 'Value'->''.
- FLIPPED-OLD (3): 29779 #29777, 9505 #9503, 10179 #10177, src False->True.
- LABEL-DIFF (4 LoopTunnels): -12->30293 and -11->30301 ('# DT points'); -7->30289 and -6->30292 ('# FD points').
- Next line: FS-CARRY (fs None, fs_pairs added 0, owners changed []).
- Then `rebase raised AttributeError: 'bool' object has no attribute 'get'` (RESULT FAIL 0/1; handler `tools/stage_prerun.py:4998`).
- Cause, read from the source:
  - `tools/stage_prerun.py:4305` `for u, o, a, b in info.get("flipped_old") or []:` was added by card 150-a2-2. It re-binds the rebase's local
    `b`, which is the plan base dict (set at `:4261`), to the last FLIPPED-OLD value, True.
  - `:4415` `provisional={"path": b.get("path"), ...}` then raises.
  - `:4303`, the RENAMED-OLD loop from 150-a2-1, shadows `b` the same way.
  - Fixing this needs a stage_prerun edit, which this card forbids.
- Plan md5 before 10a4f59a = after 10a4f59a (not rewritten). `sim/ring_p4_s07v18_base_real_fsmap.json` was not written. Steps 2-6 were NOT run:
  - no X10 after the rebase
  - no pred, recipes or licence regenerated
  - no dry, prerun or --scratch-required
  - no X11
  - no prior-art / PROVEN-PATTERN check
- Jev ladder: no JEV-LADDER row for `prep_c150_a2_3_rebase.log` in `tools/bench/jev_gate.log`.

## 2. Files
- New: `tools/bench/prep_c150_a2_3_check.py` d09e2aff (a copy of `prep_c150_a1_1_check.py` with the stage_prerun pin set to 6208b7b7 and CHG lines added), its two logs,
  `prep_c150_a2_3_md5_before.json`, `prep_c150_a2_3_rebase.log` 704e2fbf.
- Unchanged (CHG before = after):

  | file | md5 |
  |---|---|
  | plan s07 | 10a4f59a |
  | _in | 7b890070 |
  | _pred | e888ab67 |
  | recipes | d6c8da7b / 273dc3de |
  | licence | absent |

## 3. Invariants (`prep_c150_a2_3_check_after.log`: B 99/99, PIN pass, A after == before for 99 files)
These files did not change:
- stage tools: stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun 6208b7b7
- VIs: s06 569ffbf5, s05 3f9ac26b, s04 95e408ff, bed 39511877
- data: memory_model 8eec443c, adopted_scratch 658fe5b9, graph a3ecb92b
- the s06 plan, pred, in, licence and recipes, the `sim/ring_p4_s06v18` tree, and the creation maps

No `tools/hooks/**` file was edited. There was no --launch.

OPEN: the rebase needs `b` un-shadowed at `stage_prerun.py:4303`/`:4305` (loop variable renamed). That is a stage-tool edit by another card, and after it this card can be re-run unchanged.
