---
card: 158-a3-3
status: current
date: 2026-10-10
---
# Brief 158-a3-3 (assignment 158-3) - ATTRIBUTE the 11 extra Error List items of the adopted P5-2 step-1 file, then graph read, expected EL, `load_by_vi`, failed-copy delete

Card 158-a3-2b (`tools/bench/diag_c158_a3_2b_facts.md`, read all of it) ran the ONE retry scratch: PASS 23/0, E1 diff 0 at every checkpoint, D/TD/PB/CEN2 PASS
under the PD386 gates, and adopted `claudeDev\D1_ring_p5s02a_20261010_023239.vi` md5 94ffff94. It returned at the final Error List: 56 items vs P5-1's 45
(pred 47): no-source 0->5, not-connected 22->23, loose ends 21->23, LoopTunnel undirected 0->2, While-input-to-SubVI-input 0->1. The hypothesis review
(`archive/peer/2026-10-10-c158-a3-2b-el56.md`:50-93) partly refuted "all 11 are rows step 2 owes" and says a remnant that no later action re-feeds
would be a rule-1a change. NO new scratch and NO re-adoption in this card: the file stands; this card decides whether it may be the step-2 base.

## 1. Attribution FIRST (offline; the Error List json and screenshots exist, no LabVIEW needed for it)
For each of the 11 items that are new against P5-1 (diff `errorlist_D1_ring_p5s02a_20261010_023239_20261010_024108.json` against the P5-1 expected
file `errorlist_expected_D1_ring_p5s01_20261009_124542.json`; the item classes are in the facts file), give: the item text, the owning object / wire uid
(from the Error List location or the screenshots `errorlist_shots bd_*_after{1,2,4,6,7,8,49,50}.png`, the review's proposed test), and the plan action
that creates it (`plan_ring_p5s02a.json` op, `diag_c158_a3_2b_*` scratch log lines). Then classify each as exactly one of:
 (A) re-fed by a LATER action in `plan_ring_p5s02r_in.json` A24..A80 (name the action id and why it removes the item),
 (B) representation only - exists in the original-equivalent too (cite),
 (C) UNATTRIBUTED - no later action removes it and no cite.
Use the `loop-tunnel` / `no source` terminals of K3/K4 (`#5204`, `#10404`) and wires 24091 / 24153 / 24330 / 10394 (FATE, scratch log :219-224) as the first
suspects. Rule 1a: C means the staged graph may carry a computation difference; count and list every C. **If any item is C: write the table, do NOT run
steps 2-4, RETURN (status FAIL, first_fail = the C rows). If none is C: continue.**

## 2. Only if there is no C row
 2. Expected EL file for the adopted file (`diag_c158_a3_2b_elexp.py`, prepared, call it) - one file `errorlist_expected_D1_ring_p5s02a_20261010_023239.json` + md5.
 3. Graph read in a fresh LabVIEW instance (`diag_c158_a3_2b_graph.py` + plan `diag_c158_a3_2b_graph_plan.json` 91fcfbec, dry 1/0 prerun 15/0 already) ->
    `tools/bench/graph_ring_p5s02a_20261010_023239.json` + md5, the rows brief_156-a2-1 item 5 lists; `load_by_vi` entry (`diag_c158_a3_2b_memload.py`;
    ONLY that entry of `memory_model.json`, key-by-key diff quoted); handle count flat; LabVIEW closed AND verified gone.
 4. Delete the failed copy `claudeDev\D1_ring_p5s02a_20261009_152721.vi` (verify md5 cac5236b first) and `resume_plan_ring_p5s02a_20261009_153334.json`
    (`diag_c158_a3_2b_delete.py`, prepared). Nothing else.
Invariants md5 before = after: s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae, the adopted file 94ffff94, tools/recipes, plan files.

## Not in this card
No scratch run, no re-adopt, no step-2 plan / recipe (the next card, after the attribution), no `tools/hooks` edit, no tool / recipe / plan / pred / licence
edit, no original opened, no motor or camera. Concurrent cards: none.

Report `tools/bench/diag_c158_a3_3_facts.md` (<= 45 lines): the 11-row table (item, owner uid, creating op, class A/B/C with the action id or cite), then
the steps done with md5s. `OPEN:` line per unresolved thing. Facts only; the A/B/C call per row is a measurement against the plan, but a row you cannot
place is C, not a guess.
