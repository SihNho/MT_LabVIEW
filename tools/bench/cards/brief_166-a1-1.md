---
card: 166-a1-1
status: current
date: 2026-10-12
---
# Brief 166-a1-1 (assignment 166-1) - P5 CLOSE-OUT READ: ONE read-only LabVIEW session on the P5 final, then `load_by_vi` and the census

Plan: `docs/d1/ring-p5c.md` PD403(b) (line 252-260). Read that paragraph and `tools/bench/diag_c165_a3_4_facts.md` first.
The P5 final is `claudeDev\D1_ring_p5_20261010_172913.vi` 75773b0d (adopted by card 165-3-4, scratch 20/0, peak 594.8). Nothing is built here.
Only the READ is LabVIEW work. Nothing is saved: every VI is opened from a NEVER-SAVED byte copy, or read through the prepared script, which does that itself.

## Steps, in this order (stop at the first unexpected result and return with the facts)
1. **Hash first** (hashlib script `tools/bench/diag_c166_a1_1_hash.py`, scope header, `RESULT {...}` line, run under `bgrun --material`): the card inputs, and the VIs
   `D1_ring_p5_20261010_172913.vi` 75773b0d, `D1_ring_p5s01_20261009_124542.vi` 7f2582ae, plus eb1d0f31, 94ffff94, f9ae7751, 564d8cbe, 6dcd5c3d (names: `diag_c165_a3_4_hash.py`, reuse it by CALL or copy
   only the name list, say which). Any md5 different from the purpose's = RETURN (drift).
2. **Graph read** = the prepared script, UNCHANGED (df5b47b5, plan 0aaef82b, prerun PASS in card 165-3-4):
   `py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c165_a3_4_graph.log -- py -u tools/bench/diag_c165_a3_4_graph.py`
   (the log must not exist before; check_launch on the exact string first, expect ALLOW). It writes `tools/bench/graph_ring_p5s02e_<ts>.json` and prints `MEM after load: X MB private` (the load line). Quote the log's gate lines (G1, G2, G3, FS1, B, E5, X, LabVIEW gone). A FAIL of any = RETURN with the line.
3. **Quote from the graph file** (facts, with file:line or json path): (a) the terminal sets of w4337 and w9636 versus the same wires in base graph `graph_ring_p5s02d_20261010_154830.json` 2a5fa0c4: equal except that the
   outer terminals of #5204 / #10404 are now SOURCES; (b) t8776 and t24342 (the LoopTunnel inner faces of #5204/#10404): the real source of each versus the stagesim end graph of plan p5s02e (K3f net: t31815 on OK3 #31803; K4f net: new OK4); a difference = list it, RETURN.
4. **Rule-1a tunnel check, #5204 and #10404**: indexing mode (IndexMode) and the outer-terminal data type, read in 75773b0d AND in 7f2582ae with an EXISTING verb. The candidate is `gscript.tunnels` (`tools/gscript.py:1272-1300`: uid, index_mode, out_name,
   out_is_source ...); check with `py tools/protocol.py requires <card>` and `docs/toolkit-capabilities.md` that it exists and is the verb that reads these; if it cannot read the OUTER TYPE, say so. Run it read-only in ONE LabVIEW session on two never-saved byte copies
   (or the graph read's own session for 75773b0d, if the verb is already inside it). EQUAL in both files = record in the facts. DIFFERENT = RETURN with both values (rule 1a, the assignment hands back).
   NO existing verb (or the type is unreadable) = report it, build NOTHING, write "P6 pre-run item" in the facts, and go on.
5. **After LabVIEW:** `tasklist` shows no LabVIEW, handles verified, and the ref/handle count of every VI Server reference you opened is closed (`docs/rules/labview-execution.md`).
6. **`tools/bench/memory_model.json`** (only after steps 2-4 passed): ONE new `load_by_vi` key = the full md5 of 75773b0d (hashlib), same format as the existing entries, with the cite to the log line of `MEM after load` (file:line).
   Script `tools/bench/diag_c166_a1_1_mm.py` does it; it asserts with a JSON compare that every other key is equal to the old file and `fail_above_mb` is 680.0. Quote old md5 (ff0fabca) -> new md5.
7. **Measured census into the pred** (after step 6; order is graph read -> load_by_vi -> census): script `tools/bench/diag_c166_a1_1_census.py` writes the measured census of the step-5 scratch into
   `tools/bench/plan_ring_p5s02e_pred.json` (census keys ONLY; replace the UNPREDICTED CEN2 entry by the numbers of `diag_c165_a3_4_facts.md:17`
   `DigitalNumericConstant 1, InnerTerminal 6, LeftShiftRegister 1, OuterTerminal 4, RightShiftRegister 1, SelectorTunnel 2, Terminal 1, Wire 5; net Wire 3; lost uids 2`, each cited to the graph read where the graph file shows it).
   Look at how card 164-3-5 / 163-a2-1 did it (`tools/bench/diag_c164_a3_5_facts.md`, `brief_164-3-5.md`) and CALL the same stagekit function if one exists. Quote old md5 825cbf65 -> new md5.
8. **End of card:** hash eb1d0f31, 7f2582ae, 94ffff94, f9ae7751, 564d8cbe, 6dcd5c3d, 75773b0d again (unchanged) and the originals unopened; LabVIEW gone. Facts `tools/bench/diag_c166_a1_1_facts.md` (<= 40 lines, every number with a file:line).

## Not in this card
No Error List file, no STATUS / INDEX edit (card 166-a1-2), no tooling change, no `tools/hooks/**`, no recipe / plan / licence edit, no motor or camera. Dispatch a peer only if a gate FAILS.
Script rules: `docs/script-writing.md` (calls into shared functions; a new script has the scope header and ends with a `RESULT {...}` line).
