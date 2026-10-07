---
type: facts
status: current
date: 2026-10-07
---
# Card 144-a2-2 facts: s04 plan rebased on the REAL s03 graph (PASS); X10 at 598.5 = 680.1 > 680 (margin -0.1); EL 60; dry + prerun PASS on both recipes

OFFLINE only; no LabVIEW (tasklist: none). Card inputs md5-checked 8/8 match. No stage tool, hook, recipe or s03 file edited.

## Step 1 - rebase (prep_c144_a2_2_rebase.log) PASS, rc 0, 33 s
- Provisional bytes kept: `tools/bench/plan_ring_p4_s04v18_provisional_3353cfc4.json` (md5 3353cfc4..., == card).
- Plan **3353cfc4 -> 9ff46b0ece1f238c831d7786616c4f05**; base -> `tools/bench/sim/ring_p4_s04v18_base_real_fsmap.json` a63f5929 (vi 282301ca,
  fs_carried.real_graph 5638469b); 49 uid(s) bound; completeness PASS; re-simulated on the real base final=True failed=None (prep_c144_a2_2_rebase.log:56 `REBASED`; :7 `REBIND`).
- `REBIND 15 node(s), 1 frame(s), terminals by {'map': 26}; unbound created terminals []; frames {-46: '29699 (map)'}; re-issued uid(s) []`.
- **No REUSE-NOTED line.** MAP-BOUND by the creation map (creation_map/plan_ring_p4_s03v18_da66a030_20261007_203225.jsonl);
  `row-less {-45: 16483}` (W1 = While #16483, the uid of the wire the plan cut - as 144-a2-1 noted); `FALLBACK node #-46 -> #29699 inferred by map
  (no creation-map entry)`, FALLBACK-COUNT 1.
- LABEL-DIFF ArrayConstant #-3 -> #29422 (sim '' real 'pos in cal image in'). ADDRESS-RESOLVED x3 (PD348): #-28.'inner' a13/a15 src -> #29548.'inner'
  (row #29582) by face; #-45.'cond' a20 dst -> #16483.'cond' (row #29710) by cond.
- BASE-FLIPS seeded 6 terminals on 3 undirected tunnels [9503, 10177, 29777]. Steps 01..23 ok, cdiff 16 each. ROUTE 13 `p4_w_last_gt` -> `wire_sr:LeftIn`.

## Step 2 - X10 at the measured start 598.5 (prep_c144_a2_2_pred.log) - report only, no re-cut
- Compiled plan N 19, R 15: **peak 680.1 > fail_above 680.0, margin -0.1 MB** (provisional was 677.6 at 596.0; +2.5 MB = the start shift).
- Per-op formula (prep_c144_p1_mk.py:75) at 598.5: ops 79..97 peak 680.1; **next op 98 peak 684.0**; first op over 680 = **97** (the last op of s04).
- The pred script's X10 gate is the one FAIL (6/1, rc 1; written non-fatal so the pred was still written with `below_fail: false`).
- Prerun's own X10 (its start, not 598.5): main 656.7 (R 17), scratch 651.6 (R 15), both PASS - UNMEASURED meter.
- Scratch recipe: `MEM_STOP_MB 680.0; X10 from the md5-pinned pred 680.1` (prep_c144_a2_2_scr_dry.log:16) - the scratch stop is below the predicted peak.

## Step 3 - pred EL block by PD349 (pred 90eff870c8afc31a42bb6f3558ad4923, was f325cdc9)
- Basis: `errorlist_expected_D1_ring_p4s03_20261007_202957.json` 2b8f9f25, **measured 55**; owners from the real base fsmap a63f5929.
- **Predicted 60** = 55 + new 7 [input -49, -38, -34, -26, -1; local -47, -32] - closed 2 [cond 29699, local 29720]; uncertain [].
  Open at start: cond 29699, local 29720, sr 29403, sr 29648. -1 = PS1 (7 unnamed unwired inputs); -38 = SQ1 (n2, Latest, discards).
- Same total as the provisional pred (60 on base 55 = s03 PREDICTED); item uids now real/rebased.
- Census {} - 23/23 actions UNPREDICTED. X17 PASS (5 primitives).

## Step 4 - dry + prerun at current recipe bytes (fe3f630c main, f5e4bdf8 scratch)
- Main dry **PASS** (prep_c144_a2_2_dry.log): L0/K1/L1 PASS, E1 19 ops == sim, NG, FR 12 objects, D 9 new wires, TD, PB 16 rows + 11 open pairs, PS.
- **PS1 drop resolves in the dry**: `STEPX 01 create acts [1] ids ['p4_s1_pickslot'] bound {-1: 10000001} diff 0` (dry.log). SQ1 (op 10) bound -38 diff 0.
- One `STALE-ADDRESS op 14: fresh read + one retry (ADDRESS: node #29548 not in Diagram[122] (#23166).Nodes[])` - the retry passed (STEPX 14 diff 0).
- Main prerun **16/0** (prep_c144_a2_2_prerun.log); WARN X13 x3 (no replayer const/primitive/wire_sr), X14 rows 23 > budget 15 (proven: no).
- Scratch dry **PASS** (prep_c144_a2_2_scr_dry.log); scratch prerun **16/0** (prep_c144_a2_2_scr_prerun.log), same WARNs.
- `--prerun stage_d1_ring_p4_s04v18.py --scratch-required ...`: exit **3** SCRATCH-REQUIRED, CENSUS-UNPREDICTED rows 1..23 (prep_c144_a2_2_scrreq.log).

## md5s
| file | md5 |
|---|---|
| tools/bench/plan_ring_p4_s04v18.json (rebased) | 9ff46b0ece1f238c831d7786616c4f05 |
| tools/bench/plan_ring_p4_s04v18_provisional_3353cfc4.json | 3353cfc483976702fb8e6b2ee8031ce4 |
| tools/bench/plan_ring_p4_s04v18_pred.json (NEW) | 90eff870c8afc31a42bb6f3558ad4923 |
| tools/bench/sim/ring_p4_s04v18_base_real_fsmap.json | a63f59294ef4267932b8904336b4ccb8 |
| tools/recipes/stage_d1_ring_p4_s04v18.py | fe3f630c428e00143d54e5be0e18631d |
| tools/recipes/stage_d1_ring_p4_s04v18_scratch.py | f5e4bdf823cf206e7701a8673235046d |
| tools/elrule.py | dae49641768b7e427f264ebf0227fea8 |
