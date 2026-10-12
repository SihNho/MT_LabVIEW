---
card: 167-a1-2
status: current
date: 2026-10-12
---
# Brief 167-a1-2 (assignment 167-1) - P6-0 (f), OFFLINE: the C rows - consumers of `#644` i and of FrameIdx

Plan: `docs/d1/ring-p6.md` PD404(f) (lines 82-86) and (c) (lines 63-67). Offline, stored files only: NO LabVIEW, no camera, no motor, no VI opened. Facts only: no fix, no design, no verdict, nothing inferred written as a measurement.
Inputs: P5 final graph `tools/bench/graph_ring_p5s02e_20261012_173009.json` 7815af09; S1 `docs/wiki/subvi/D1_s1_copy.json` 5de014fe; F2 of `tools/bench/p6_facts.md` / `p6_facts.json` (the consumer list already walked, with 'counter (s09 census)' column);
`tools/bench/frameidx_consumers.md` (the s09 census); PD374(g) text `docs/d1/ring-p5.md:94-97`; PD246(c) (the P3a new-frame counter; find it with `grep -n "PD246" docs/d1/*.md`); PD238(i) (the P1 measurement, `grep -n "PD238" docs/d1/*.md docs/*.md`).

## What to produce - for each consumer #1114, #2136, #29411, #12045, #3162, #1628, and #30240 -> #29240 / #10068
1. **Owner chain** (uid, class, loop name from nested diagram owners) in the P5 final graph AND in S1, up to the top diagram. Loop names: 637 = 1.1, 10170 = 1.2, 23032 = 1.5, 23041 = 1.7 (`tools/bench/diag_c108c_graph.py:15`); others `while#uid`. Use the existing graph walker `diag_c108c_graph.Graph.walk` / `vigraph` (CALL, do not copy; if the walker is only importable from a diag script, say so). A consumer absent in one of the two graphs is stated "absent in S1 / absent in P5".
2. **When it runs:** on every 1.1 iteration, or only in the new-frame case (inside the case structure fed by the new-frame boolean), from the case-structure ownership and the selector's feed in the graph (cite the case uid + the selector's source terminal). If the graph cannot show it: "unread".
3. **The P3a new-frame counter terminal uid** (PD246(c)): the terminal on that consumer's diagram that carries the counter, and whether the consumer reads it. "unread" if no stored read names it.
4. **Repeated BufNum fact:** whether the ORIGINAL ever shows the same BufNum on consecutive 1.1 iterations, taken from a STORED record (PD238(i) P1 measurement, the ABBA leg records / `tools/bench/*abba*`, `frameidx_consumers.md`). Quote the record's file:line and the number; none stored = the word "unread".
Output: `tools/bench/p6_crows.md` + `tools/bench/p6_crows.json` (one row per consumer; each cell has a `source` file:line or json path), written by script `tools/bench/diag_c167_a1_2_crows.py` (scope header `# labview: none` / `# hardware: none`, `RESULT {...}` line, run under `bgrun --material`; CALL shared functions, `docs/script-writing.md`).

## Checks
Hash first: the inputs above plus the seven VIs of the purpose (75773b0d 7f2582ae 94ffff94 f9ae7751 564d8cbe 6dcd5c3d eb1d0f31, names as in `tools/bench/diag_c166_a1_1_hash.py`) - hashing a VI is a file read, not LabVIEW. Drift = RETURN.
At the end: hash again, unchanged; `tasklist` shows no LabVIEW was started by this card; outputs' md5 quoted. Facts `tools/bench/diag_c167_a1_2_facts.md` (<= 30 lines).

## Not in this card
No LabVIEW, no STATUS / plan / hook / stagekit edit (a LabVIEW card runs beside this one), no closure-table work (the next card), no repair row.
