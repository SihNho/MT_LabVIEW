---
type: facts
status: current
date: 2026-10-10
card: 159-b1-1
---
# CEN2 12th wire of p5s02a (PD388(b)): NOT w10394, and more than one difference
**The extra is NOT termless w10394 (PD388(b)'s hypothesis refuted): the 12th new uid is 31587, and the census-scope diff has 3 differences
(2 real-only, 1 sim-only), all wire-UID identity, not topology.**
Run `diag_c159_b1_1.py` -> `diag_c159_b1_1_final.log` (C1, C2 PASS; C3 FAIL as predicted-wrong), data `diag_c159_b1_1_raw.json` `cen2*`.
## Scope (what CEN2 counts)
- `stagekit.py:2414-2426` gate_cen2: dry c0/c1 = `sim_census_snapshot` of step_00 and the sim end, kept to the pred's census classes
  (`stagekit.py:2307`, `plan_ring_p5s02a_pred.json:15-29`); `stagekit.py:333` counts `set(after) - set(before)` = NEW UIDS by class.
- Sim side: objs by class + every `wire_uid` on a terminal row as Wire (`stagekit.py:2250-2267`). Real side (scratch run): `report_all(GObject)`
  (`stagekit.py:301-305`). Offline real = Wire objs of graph_ring_p5s02a 7ac24924 minus graph_ring_p5s01 6716c499.
## Measured
- Regenerated sim end (stagesim.simulate, `sim/ring_p5s02a_c159/ring_p5s02a/step_23_wire.json`) == stored step_23 b1892ad9; sim new Wire 11 (C1).
- Real new Wire uids 12: 11774 31343 31391 31392 31396 31443 31491 31530 31537 31551 31562 31587; gone 24091 24153 (C2).
- Keyed diff (base term uid / created-object class, frame): 10 of 12 match. Real-only: **31562** (#24357 LoopTunnel 24360 -> SelectorTunnel
  #31546 31559, frame 23405, A19 w_in1_t) and **31587** (#24361 LoopTunnel 24367 -> SelectorTunnel #31557 31577, frame 23405, A22 w_in2_t).
  Sim-only: sim wire -37 (#376 'file progress' 5704 -> 'file progress' 3453, case frame; A14 w_prog).
- Counterparts (same ends, any uid): sim carries 31562's pair on OLD uid 24330 and 31587's pair on OLD uid 24153; real carries -37's pair on
  OLD uid 24330. In P5-1, 24330 = 24360 -> #376 'cal cluster path' 5760; 24153 = 24367 -> #376 'file size' 5778; 24091 = 25235 -> #376
  'selected path' 5787.
- So: 24330 is a uid SWAP (net 0: real keeps it on the A14 pair, sim on the A19 pair); the +1 is 31587 - LabVIEW deleted 24153 and made a new
  wire for A22's pair, the sim kept 24153 (the sim's "join onto the old wire" keeps the uid).
- Whole termed-wire set (outside the census scope): sim end 2049 vs real 2048 wires with terminals; real-only 0; sim-only 1: a source-only stub on #25223 25235 (sim keeps P5-1's 24091 as a
  stub; LabVIEW removed it, 25235 unwired - as `attrib_c159_p5s02a.md:52`).
- Termless: real 23 vs P5-1 22, real-only termless = 10394. 10394 is NOT a new uid (it is P5-1's 3060->5772 wire, in both censuses), and
  the sim's objs table still carries base Wire 10394 (2061 Wire objs at step_23 == base) - so w10394 is not what CEN2 counted.
