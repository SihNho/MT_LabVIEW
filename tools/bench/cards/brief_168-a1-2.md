---
card: 168-a1-2
status: current
date: 2026-10-12
---
# Brief 168-a1-2 (assignment 168-1) - PD405(c): ONE scratch: RBW, delete #11261, ExecState, full Error List, graph, save gates as FACTS

Plan: `docs/d1/ring-p6.md` PD405(c)(d)(g) (lines 111-138). Bed: `claudeDev\D1_ring_p5_20261010_172913.vi` 75773b0d (P5 final, Error List 47, ExecState 0).
Offline card 168-a1-1 (`tools/bench/diag_c168_a1_1_facts.md`, accepted) found: of 19 BuildArray nodes only #11261 has an unwired input
(t11270 'array', t11273 'element': no source); its output t11267 reached only t8323 'Force (pN) vs Extension (nm) ' (display-only by the graph); after RBW no wire is
attached to #11261, so deleting it is predicted to leave the Wire-object count at 2066 (`p6_buildarray.md:114-116`). This card MEASURES; nothing is adopted or saved,
no repair is chosen from the result.

## Steps, in this order (ONE scratch run; stop at the first unexpected result and return with the facts)
1. **Hash first**: CALL `prep_c168_hashlib.check(<this card>, "before")` from a thin script `diag_c168_a1_2_hash.py` (as `diag_c168_a1_1_hash.py` does). Drift = RETURN.
   `py tools/protocol.py requires <this card>` must PASS (RBW verb `remove_bad_wires_scripted`, delete verb `delete_object`).
2. **Script `tools/bench/diag_c168_a1_2_rbwdel.py`** (scope header `# labview: build`, `RESULT {...}` line, run under `bgrun --material`). Same sequence and calls as
   `diag_c167_a1_1_rbw.py` (read it; do not paste its blocks): Stage on the bed with a scratch name `scratch_c168_a1_2_rbwdel`, `discard_work()` so the copy is never saved and
   never adopted. Inline blocks of that script that this one also needs (`el_read` :52-84, the `mem` meter :44-49) are EXTRACTED once into a new
   `tools/bench/prep_c168_a1_2_lib.py` with a self-test that replays recorded data (e.g. `errorlist_check.class_counts` on the stored items of
   `errorlist_D1_ring_p6rbw_20261012_191349.json`); the new script CALLS it; report the old inline copy in `facts` (file:line); do not rewrite the 167 script.
   Sequence on the scratch:
   a. ExecState BEFORE (`gscript.exec_state`).
   b. RBW by the 167 verb: `s._op("rbw_method410", lambda: s.broken_wire_count(W, allow_mutation=True, ...))` exactly as `diag_c167_a1_1_rbw.py:100-101`
      (op label `rbw_method410`, accepted in PD405(f)). ExecState AFTER RBW and Wire count before/after.
   c. Delete #11261 with the EXISTING route `Stage.delete_object("BuildArray", 11261, tag)` (`tools/stagekit.py:700`; the class string is the one the graph
      stores for #11261, check `p6_buildarray.json`). ExecState AFTER the delete; Wire-object count after; #11261 absent from the object list of its class.
   d. Graph read of the scratch (`prep_c167_a1_1_graphlib.read_graph`, ends with `stagekit.e5_check`; quote its line). Write
      `tools/bench/graph_ring_p6rbwd_<stamp>.json` + md5. e5 edits: deleted_nodes [11261], deleted_wires the 22 termless F1 uids (as 167) - base 7815af09.
   e. FULL Error List of the in-memory scratch (the `el_read` function, live session, no save): file + md5, `errorlist_check.class_counts`, EVERY item's text and uid
      (or the word `unread`). Written as `tools/bench/errorlist_D1_ring_p6rbwd_<stamp>.json`.
   f. Save gates as FACTS, PASS/FAIL + evidence, NO save (compute them from the live scratch / the graph; none of them is a launch gate):
      F-S1 ExecState after the delete == 1; F-S2 Error List item count == 0; F-S3 #2626 has its 4 inputs wired (element x3 + array) in the scratch graph (compare to
      7815af09 sources); F-S4 LoopTunnels #5204 and #10404 IndexMode + outer terminal type of the scratch vs the stored 7f2582ae values
      (`diag_c166_a1_1_facts.md:24-25` and the read of `diag_c166_a1_1_tun.py`; call `gscript.tunnels` / `gscript.read_term_type` on the scratch, do NOT open 7f2582ae);
      F-S5 frame-keyed `vigraph.computation_diff_frame(S1, scratch graph)` (S1 = `docs/wiki/subvi/D1_s1_copy.json` 5de014fe, both graphs `build4(..., frame_keyed=True)`,
      the way `p6_closure` computed it - find the call in the 167-a1-3 script, CALL the same code) -> the row set, and the set of `p6_closure.json` rows classed R and DISP:
      list BOTH differences (rows only in the diff; rows only in the closure's R+DISP). If ExecState after the delete is 0, say so and attempt NO further repair.
3. **Launch gates** (PD405(g)): the dry run can only STUB these four, so they are named expected-unverified in this card's `rules` (DRY-UNVERIFIED-OK) and launched with
   `--unverified-card tools/bench/cards/task_168-a1-2.json`. Give the script gates exactly these label prefixes: `A0 ExecState BEFORE RBW` (== 0), `A1 ExecState AFTER RBW`
   (== 0, as 167 measured on the same bed), `R1 Wire count drop after RBW` (2091 -> 2066), `D1 #11261 absent after delete` (and Wire objects 2066). The ExecState after the delete is a ROW
   (unpredicted), never a gate. A launch gate that refuses the run is NOT turned into a row or relabelled (CLAUDE.md rule 7): return BLOCKED with the refusal text.
   Memory: X10 per-session limit 675 from 647.8; measure each MEM line (167 measured a 610.5 peak; the model said 677.5 and the launch was allowed). If stage_prerun refuses on X10, return BLOCKED, no memory_model edit.
4. **Hygiene**: scratch deleted (name listed), VI Server references opened/closed counted (balanced), `tasklist` shows no LabVIEW, the 7 VIs rehashed unchanged
   (`prep_c168_hashlib.check(<this card>, "after")`), no original opened, no tools/hooks edit, no motor or camera.
5. **Facts** `tools/bench/diag_c168_a1_2_facts.md` (<= 45 lines, every number with a file:line): ExecState before / after RBW / after delete, wire counts, F-S1..F-S5 PASS/FAIL with evidence,
   Error List file + md5 + class counts + each item, graph file + md5 + e5_check line, MEM peak, scratch names deleted, handles.

## Not in this card
No adoption, no save of the scratch, no `load_by_vi` entry, no memory_model / STATUS / INDEX / plan / hook / stagekit / recipe edit, no repair proposal, no second scratch.
Dispatch a peer only if a gate FAILS. Script rules: `docs/script-writing.md`.
