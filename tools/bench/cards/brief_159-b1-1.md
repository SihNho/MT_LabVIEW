---
card: 159-b1-1
status: current
date: 2026-10-10
---
# Brief 159-b1-1 (assignment 159-2) - OFFLINE: expected Error List of base 94ffff94, the CEN2 extra wire, delete the failed copy

No LabVIEW is started. `tools/stage_prerun.py` may change by ONE constant (`DRY_RULE`) while this card runs (card 159-b2-1): do not pin it,
do not write it. Decision text: `docs/d1/ring-p5b.md` PD388(a)(b). Base: `claudeDev\D1_ring_p5s02a_20261010_023239.vi` md5 94ffff94 (never opened here).

## 1. Expected Error List of the base (PD388(a)) - one row per observed item
Inputs: the observed list `tools/bench/errorlist_D1_ring_p5s02a_20261010_023239_20261010_024108.json` (56 items), the attribution
`tools/bench/attrib_c159_p5s02a.md` / `.json` (per class, 8 new-class items, net +3), the P5-1 file
`tools/bench/errorlist_expected_D1_ring_p5s01_20261009_124542.json` (the format and the 45 inherited items), the step-2 and step-3 actions in
`tools/bench/plan_ring_p5s02r_in.json` (A24..A80). Write `tools/bench/errorlist_expected_D1_ring_p5s02a_20261010_023239.json` in the SAME format
as the P5-1 file. For EVERY one of the 56 items one row: item text and class as observed, the graph object(s) it belongs to (from the attribution),
and `clears_by`: the plan action (`A<n>` + wire/step name, step 2 or step 3) that removes it, or `standing` with the reason (base item the P5
plan never touches), or - for the not-connected item of termless wire 10394 - `delete_wire 10394` (the FIRST action of step 2 under PD388(a)).
Items you cannot attribute to an action or to `standing` with a cause line are listed as `unattributed`, not guessed. Do NOT copy the 56 observed
items as one block with a blanket reason: each row carries its own citation. Print counts: total 56, per `clears_by` kind, per class, and
"after step 2" / "after step 3" predicted totals computed from the rows (these two numbers feed the plan card).

## 2. The CEN2 12th wire (PD388(b))
The repaired dry reported CEN2 on `tools/bench/plan_ring_p5s02a.json` 4284c22a: simulated Wire count 11, measured 12. Measure which wire LabVIEW
has and the simulation does not: regenerate the simulated end of that plan from its base graph
`tools/bench/graph_ring_p5s01_20261009_125622.json` (6716c499) with `tools/stagesim.py` / `stagekit` (read-only use, output only under
`tools/bench/sim/ring_p5s02a_c159/`), diff its wire set against `tools/bench/graph_ring_p5s02a_20261010_032547.json` (7ac24924), restricted to the
census scope the CEN2 gate uses (read the gate code to quote the scope). Compare wires by (source terminal uid, sink terminal uids, frame); for a
wire with no terminals compare by uid and frame. Write `tools/bench/diag_c159_cen2_wire.md` (<= 30 lines): the CEN2 scope (file:line), the extra
wire's uid, both ends, frame, whether it equals termless wire 10394, and any OTHER difference found (wires in the sim missing in LabVIEW too).
If the extra wire is not 10394, or there is more than one difference, say so in the first lines - the assignment session hands that back.

## 3. Delete the failed copy (after 1 and 2 are written)
`claudeDev\D1_ring_p5s02a_20261009_152721.vi`: verify md5 `cac5236b...` FIRST (quote it), delete it, and delete its resume record (grep for
`152721` under `tools/bench/` for the record; quote the path). Delete nothing else. Quote md5 of `D1_ring_p5s02a_20261010_023239.vi` (94ffff94),
s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae before and after (a plain file hash; no LabVIEW needed).

## Report `tools/bench/diag_c159_b1_1_facts.md` (<= 35 lines)
Counts from step 1; the two predicted totals; the CEN2 finding in one line; deletions with md5; pins before/after; `OPEN:` lines. Facts only.
