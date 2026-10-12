---
card: 168-a1-1
status: current
date: 2026-10-12
---
# Brief 168-a1-1 (assignment 168-1) - PD405(c) offline: which Build Array is left after RBW, and where #11261 'appended array' goes

Plan: `docs/d1/ring-p6.md` PD405(c) (lines 111-118). OFFLINE, facts only: no LabVIEW, no VI opened, no tool edit outside the write globs.
Graph before RBW: `tools/bench/graph_ring_p5s02e_20261012_173009.json` 7815af09. Graph after RBW: `tools/bench/graph_ring_p6rbw_20261012_191349.json` c5531708
(RBW deleted 25 wires, one data-carrying: w25618 #11261 BuildArray t11267 'appended array' -> #23166 Diagram t8323 'Force (pN) vs Extension (nm) ',
`tools/bench/p6_rbw_deleted.md:35`). Error List after RBW = 1 item "Build Array: Contains unwired or bad terminal", uid unread (`diag_c167_a1_1_facts.md:21`).
Nothing in this card decides a repair; the judgement session reads the facts.

## Steps, in this order (stop at the first unexpected result and return with the facts)
1. **Hash first.** Make ONE small shared function `check(card_path, mode)` in a NEW module `tools/bench/prep_c168_hashlib.py` that does what
   `tools/bench/diag_c167_a1_1_hash.py` does (CALL `protocol.input_md5_changes` and `prep_c156_a1_1_lib.md5/Gate`; the seven VI pins are DATA in the module:
   75773b0d 7f2582ae eb1d0f31 94ffff94 f9ae7751 564d8cbe 6dcd5c3d, names as in that script), with a self-test that replays this card. Two thin scripts
   `diag_c168_a1_1_hash.py` (this card; argv before|after) call it. Card 168-a1-2 will call the same function; do not paste it anywhere.
   Run under `bgrun --material` (scope header `# labview: none`, `RESULT {...}` line). Any drift in a card input or a pin = RETURN with the file named.
   (Purpose item 0: the card inputs ARE the purpose's eight hashes plus the bed pin.)
2. **BuildArray census on c5531708** (`tools/bench/diag_c168_a1_1_ba.py`, read-only). Reuse `vigraph` / `tools/bench/prep_c167_a1_1_graphlib.py` /
   `docs/toolkit-capabilities.md` functions for the terminal and wire reading; do not hand-roll a second graph parser. For EVERY node of class BuildArray
   (all diagrams, loops and cases): owner uid, the diagram/loop/case it sits in (chain to the top), and for EACH input terminal: terminal uid + name, its source
   (the source terminal uid + owner uid/class/name) or `none`, and its type IF the graph stores one (else the literal word `unread`). State for t11270 and
   t11273 of #11261 whether each is wired (source) or empty. Mark a node `has-unwired-input` when at least one input terminal has no source. Quote the
   result as the answer to "which Build Array is left": the list of BuildArray nodes with an unwired input, and the list of those with all inputs wired.
   Do the same census on 7815af09 into the same table (columns before/after), so #2626 and #11261 can be compared; same code, called twice.
3. **#11261 downstream path.** For EVERY terminal of #11261 (all inputs and the output t11267) in 7815af09 AND in c5531708: the wires on it and where each goes.
   For t11267 follow every sink transitively (through branches, loop/case tunnels, shift registers, sub-VI inputs, bundlers) until a leaf, and QUOTE the chain
   (uid, class, name per step, file:row). Class the path with these definitions and name the one that applies, per sink and overall:
   `compute` = reaches any input of a primitive/sub-VI/loop-tunnel/shift-register that feeds another computation; `save` = reaches a file-write/save-trace
   input; `control` = reaches a motor/stage/camera/loop-stop/case-selector input; `display-only` = every sink is a front-panel indicator or graph terminal
   with no outgoing wire. A graph or indicator terminal's own owner (#23166 Diagram t8323) is checked: is it an indicator with no outflow? Also cite
   `docs/d1/ring-p4.md:52` and PD295(b) as stated by the plan, but the class comes from the graph, not the citation.
4. **What deleting #11261 would touch** (a prediction table for the next card, not a decision): every wire still attached to any terminal of #11261 in
   c5531708, its other end, and the expected Wire-object count after a delete of the node (c5531708 count 2066 minus attached wires), so the LabVIEW card's
   wire-count gate has a stated expectation.
5. **Outputs:** `tools/bench/p6_buildarray.json` + `.md` (the census table, the #11261 path with quoted chain, the class, the delete prediction),
   `tools/bench/diag_c168_a1_1_facts.md` (<= 40 lines, every number with file:row or json path; the word `display-only` appears ONLY if step 3 proves it;
   the hash script's module path; md5 of every output). Hash after the work (mode after): all equal.

## Not in this card
No LabVIEW, no VI open, no scratch, no repair proposal, no edit of stagekit / vigraph / gscript / stagexec / hooks / plan / STATUS / memory_model.
Dispatch a peer only if a gate FAILS. Script rules: `docs/script-writing.md`.
