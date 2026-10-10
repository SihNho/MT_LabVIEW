---
card: 159-a3-1
status: current
date: 2026-10-10
---
# Brief 159-a3-1 (assignment 159-1) - OFFLINE attribution of the 11 extra Error List items of 94ffff94 (PD387(c))

No LabVIEW, no tool/hook edit, no deletion, no expected Error List. Plan: `docs/d1/ring-p5.md` PD387(c) (line 387) and its (a)-(b) context. Read-only except the two
outputs `tools/bench/attrib_c159_p5s02a.md` and `tools/bench/attrib_c159_p5s02a.json` (and one helper script `tools/bench/diag_c159_a3_1_attrib.py`, header
`labview: none / hardware: none`, on shared functions: `tools/vigraph.py` join_wires / severed, `tools/errorlist_check.py`, `tools/addrcheck.py` - call them, do not copy them).

## Measurement
Cycle 158 adopted `D1_ring_p5s02a_20261010_023239.vi` (94ffff94) with Error List 56 vs P5-1's 45 (predicted 47). Read: P5-1 `errorlist_D1_ring_p5s01_20261009_124542_20261009_124554.json`
(2e49ed9f) vs P5-2a `errorlist_D1_ring_p5s02a_20261010_023239_20261010_024108.json` (25d6084b); graphs: P5-1 `graph_ring_p5s01_20261009_125622.json` (6716c499), P5-2a
`graph_ring_p5s02a_20261010_032547.json` (7ac24924). The plan with all actions: `plan_ring_p5s02r_in.json` (d84634bd), A24..A80 are steps 2-3. The review
`archive/peer/2026-10-10-c158-a3-2b-el56.md` (answer section) is a HYPOTHESIS (K3/K4 re-feed out-tunnels #5204/#10404; A48 `#376` already open in P5-1; the +3 same-class items are net
counts) - test it against the graphs, do not adopt it.

1. Recompute `join_wires` and `severed` offline from BOTH graph jsons with the shared vigraph functions; diff them. Record per Error List class: new, resolved, net (Error List
   classes as `errorlist_check.py` / the scratch log name them).
2. The 8 items of a class absent from P5-1 (no-source x5 [items 1, 2, 4, 6, 50], LoopTunnel-undirected x2 [7, 8], While-input-to-SubVI-input x1 [49]): for EACH give the
   source object+terminal uid, ALL sink uids, the owning frame/structure, and the A24..A80 action(s) in `plan_ring_p5s02r_in.json` that wire or remove it (action id + the line/key);
   if none does, write `UNATTRIBUTED`. The Error List has no object ids (selection-list op unbuilt); attribute by the graph (an open terminal / wire whose endpoints exist only in
   the P5-2a graph's open-terminal set and match the item's class). If a screenshot `tools/bench/errorlist_shots/*_after*.png` is the only way to place an item, READ that image
   (Read tool) and quote what it shows; if it cannot place the item, say UNATTRIBUTED.
3. The net +3 of same-class items (not-connected 22->23, loose ends 21->23, +1 more per the scratch log): list the new/resolved pairs (graph objects) that add to the net. A
   pair you cannot list stays a count, marked UNEXPLAINED.
4. For each attributed item, also say whether the clearing action is in step 2 (A24..A60) or step 3 (A61..A80).

## Outputs
- `tools/bench/attrib_c159_p5s02a.json`: `{"items":[{"no":n,"class":..,"source":{"uid":..,"term":..},"sinks":[..],"frame":..,"action":"A..|UNATTRIBUTED","step":2|3|null,"evidence":"file:line or graph key"}],"classes":{<class>:{"p51":n,"p52a":n,"new":n,"resolved":n}},"net3":[..],"unattributed":[..]}`.
- `tools/bench/attrib_c159_p5s02a.md` (<= 60 lines): the same as a table, then `OPEN:` lines. Facts only. State the count of attributed vs UNATTRIBUTED items on the last line
  (`ATTRIBUTED k/8`, `NET3 explained m/3`).
Do NOT write the expected Error List and do NOT delete anything: those are decided from this result by the assignment session.
