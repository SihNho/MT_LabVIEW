---
card: 167-a1-3
status: current
date: 2026-10-12
---
# Brief 167-a1-3 (assignment 167-1) - P6-0 (c)(e), OFFLINE: the closure table `p6_closure` (.md + .json)

Plan: `docs/d1/ring-p6.md` PD404(c) (lines 63-67) and (e) (lines 77-81). Read both first. Offline, stored files only: NO LabVIEW, no VI opened. The table proposes NO fix; U and C rows are judged by the next judgement under rule 1a.
Inputs (all measured before this card): P5 final graph `tools/bench/graph_ring_p5s02e_20261012_173009.json` 7815af09; S1 `docs/wiki/subvi/D1_s1_copy.json` 5de014fe; `tools/bench/plan_ring_p5s02e.json` fd23974e (`open_rows` lists at :12 and :319);
the 47-item facts `tools/bench/p6_facts.json` 707bc678 (F1 rows) and `p6_facts.md`; the RBW measurement of card 167-a1-1: `tools/bench/p6_rbw_deleted.json` / `.md`, `tools/bench/graph_ring_p6rbw_20261012_191349.json`, `tools/bench/errorlist_D1_ring_p6rbw_20261012_191349.json` (1 item left), facts `tools/bench/diag_c167_a1_1_facts.md`;
the C rows of card 167-a1-2: `tools/bench/p6_crows.json` / `.md`; the decisions the classes cite: `docs/d1/ring-p4.md` (U12 at :53, PD210), `docs/d1/ring-p5*.md` (PD374(b) record counter, PD374 queue 1.2 -> 1.7, PD366(d), PD246(c)), `docs/d1/ring-p6.md`.

## Steps
1. **Hash first** the inputs and the seven VIs (75773b0d 7f2582ae 94ffff94 f9ae7751 564d8cbe 6dcd5c3d eb1d0f31; names as in `tools/bench/diag_c166_a1_1_hash.py`). Drift = RETURN.
2. **Row set (e):** the union of (i) the 47 Error List items (F1, uid-keyed where F1 has a uid; item-only rows kept as 'item-only, uid unread'), (ii) the declared `open_rows` of `plan_ring_p5s02e.json` (BOTH lists, :12 and :319; quote each list's length and where it sits), (iii) `vigraph.computation_diff(S1, 7815af09)` (find the call with `grep -n "def computation_diff" tools/vigraph.py`; CALL it, do not re-implement).
   **Quote the set equality of (ii) and (iii)** (rows only in one side listed one by one; equal = say so with the counts).
3. **Per row** (columns; every cell has a `source` file:line or json path, nothing inferred): sink (owner uid + class, terminal uid + name, loop name via the owner chain; loop names 637 = 1.1, 10170 = 1.2, 23032 = 1.5, 23041 = 1.7),
   S1 source (owner/terminal), P5-final source, **class** and its **citation**, the RBW wire it maps to (from `p6_rbw_deleted.json`, or none) and **whether its Error List item is gone after RBW** (compare the 47 items with the 1 left item; an item-only row whose uid is unread: say "unknown which item", never guess).
   Classes (PD404(c), by CITATION only; no citation = U): **R** = the sink's new source is a designed replacement (ring slot read, queue element, record counter PD374(b), a local; cite the PD); **DISP** = pure-display indicator (U12, PD210); **D** = carries no data (termless wire, or loose-end branch whose sinks are fed elsewhere);
   **C** = a consumer of `#644` i or of FrameIdx (the 7 consumers of `p6_crows.json` / F2; cite p6_crows row); **U** = none of these. A row may get ONE class; if two apply, take the first in the order C, R, DISP, D and state the other in a 'also' cell.
4. **Counts per class**, the list of U rows (one line each), the list of C rows, the DISP count (PD404(b): decides whether DISP rows may stay unfed in P6-1), and the count of rows whose Error List item is gone after RBW.
5. Outputs: `tools/bench/p6_closure.md` (table + counts + equality quote) and `tools/bench/p6_closure.json`, written by script `tools/bench/diag_c167_a1_3_closure.py` (scope header `# labview: none`, `RESULT {...}` line, run under `bgrun --material`, CALL shared functions; `docs/script-writing.md`).
   Facts `tools/bench/diag_c167_a1_3_facts.md` (<= 35 lines): equality line, counts per class, U rows, output md5s.
6. End: hash again, unchanged; `tasklist` shows no LabVIEW.

## Not in this card
No LabVIEW, no repair row, no fix, no STATUS / plan / hook edit, no shared-module edit (the tooling card does that later). A row you cannot class by citation is U and is listed, never forced into R.
