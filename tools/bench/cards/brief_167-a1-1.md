---
card: 167-a1-1
status: current
date: 2026-10-12
---
# Brief 167-a1-1 (assignment 167-1) - P6-0 (d): ONE Remove-Bad-Wires measurement on a scratch byte copy of the P5 final

Plan: `docs/d1/ring-p6.md` PD404(d) (lines 68-76). Read that paragraph first. Nothing here is built, adopted, or kept.
Bed: `claudeDev\D1_ring_p5_20261010_172913.vi` 75773b0d (P5 final, Error List 47, ExecState 0 by design). Graph before: `tools/bench/graph_ring_p5s02e_20261012_173009.json` 7815af09.
Error List before: `tools/bench/errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json` 0c0664d8. This card MEASURES what Remove Bad Wires (RBW) does to this file; it makes no decision from the result.

## Steps, in this order (stop at the first unexpected result and return with the facts)
1. **Hash first** (script under `bgrun --material`, scope header, `RESULT {...}` line; CALL the hashing code that `tools/bench/diag_c166_a1_1_hash.py` or `diag_c165_a3_4_hash.py` uses if it is importable, do not paste it): the card inputs, the VIs 75773b0d,
   7f2582ae, 94ffff94, f9ae7751, 564d8cbe, 6dcd5c3d, eb1d0f31 (names as in `diag_c166_a1_1_hash.py`). Any drift = RETURN.
2. **Find the verb, do not build one.** `py tools/protocol.py requires <this card>` must PASS. The existing verb is `gscript.remove_bad_wires_scripted` (`tools/gscript.py:3104`: VI method 410, scripted, returns wire count after + ExecState;
   `stagekit.broken_wire_count` wraps it at `tools/stagekit.py:543` and REFUSES the stage target, so use it on the scratch). `gscript.remove_bad_wires` (`:1987`) is the GUI-menu version: use it ONLY if the scripted one is unusable, and say why. Quote which one you ran.
3. **One scratch byte copy** of 75773b0d under claudeDev (`stagekit` scratch helper or equivalent; unique name, md5 equal to the bed's, gated). Never adopted, never named like a stage file. Every VI Server reference you open is closed and counted at the end.
4. **Sequence on the scratch (ONE run, no second attempt):**
   a. `gscript.exec_state` BEFORE (expect 0; quote the value).
   b. The graph is already known before (7815af09); do NOT re-read it.
   c. RBW by the verb of step 2. ExecState AFTER (quote). Wire count before/after.
   d. Graph read of the RBW'd scratch. Reuse the graph-read code of `tools/bench/diag_c165_a3_4_graph.py` by CALL/import or run it parameterised on the scratch path; the read ends with `stagekit.e5_check` (rule: every NEW graph-read diagnostic calls it; quote its line). Write `tools/bench/graph_ring_p6rbw_<stamp>.json`, md5.
   e. Full Error List of the RBW'd copy: `tools/errorlist_check.py` copies a FILE (`--vi`), so if it is the route the RBW'd scratch must be on disk: save it under its own scratch name ONLY if the Error List cannot be read in the live session
      (state which). If the VI is broken, saving goes through the existing broken-save route (`gscript.save(..., allow_broken=True)` / gui_save) - this file is a scratch and is deleted at card end; it is not a counted broken file. Write
      `tools/bench/errorlist_D1_ring_p6rbw_<stamp>*.json` (+ `_raw`), md5, per-class counts (use `errorlist_check.class_counts`), and EVERY item's detail text. A GUI step needs the recorded `-Exception`/`-Evidence` of `errorlist_check.py` (it carries them).
   X10 memory: start from the 647.8 MB load of this bed (`tools/bench/memory_model.json`), limit 675 per LabVIEW session. If one session cannot do a-e, split into two sessions (RBW + graph in the first, save under the scratch name; Error List in the second); never exceed the limit.
5. **Deleted wires** = wire uids in 7815af09 not in the after-RBW graph (and any uid NEW after RBW, listed separately). For EACH deleted uid: its terminals before (owner uid + class, terminal uid + name, source/sink) from 7815af09, and the tag
   `data-carrying` (>= 1 source terminal AND >= 1 sink terminal) or `not data-carrying`. For EACH of the 22 termless uids of F1 (`tools/bench/p6_facts.json` F1, class notconnected; gate F1c in `p6_facts.md`): `deleted` or `kept`.
   Script `tools/bench/diag_c167_a1_1_diff.py` -> `tools/bench/p6_rbw_deleted.json` (+ a `.md` table). Reuse `vigraph` / `stagekit` functions for the wire/terminal reading (list in `docs/toolkit-capabilities.md`); do not hand-roll a second graph parser.
   Stated prediction (PD404(d)): RBW deletes the 22 termless wires and some loose-end wires; how many data-carrying wires it deletes, and ExecState after, are UNPREDICTED - report what you measure, no matter which way.
6. **Hygiene:** scratch copies closed and DELETED (list the names); 75773b0d 7f2582ae 94ffff94 f9ae7751 564d8cbe 6dcd5c3d eb1d0f31 hashed again, unchanged; no original opened; `tasklist` shows no LabVIEW; handle count / VI Server references closed (`docs/rules/labview-execution.md`).
7. **Facts** `tools/bench/diag_c167_a1_1_facts.md` (<= 45 lines, every number with a file:line or json path): ExecState before/after, verb used, wire counts, number of deleted wires (data-carrying / not), the 22 termless deleted/kept, Error List
   total + per-class counts + file + md5, graph file + md5, e5_check line, peak MEM line, scratch names deleted.

## Not in this card
No adoption, no `load_by_vi` entry, no memory_model / STATUS / INDEX / plan / hook / recipe edit, no stagekit edit, no fix proposal, no motor or camera. Dispatch a peer only if a gate FAILS. Script rules: `docs/script-writing.md`.
