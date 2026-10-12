---
card: 169-a1-1
status: current
date: 2026-10-12
---
# Brief 169-a1-1 (assignment 169-1) - PD406(c)(d)(e): P6-1, ONE launch: RBW + delete #11261 on a byte copy of 75773b0d, saved ONLY on the gates, then the post-save reads

Plan: `docs/d1/ring-p6.md` PD406 (lines 141-182). Bed: `claudeDev\D1_ring_p5_20261010_172913.vi` 75773b0d (P5 final, Error List 47, ExecState 0).
Card 168-a1-2 (`tools/bench/diag_c168_a1_2_facts.md`, result PASS 24/0) ran exactly P6-1's two rows on a never-saved byte copy and is accepted as P6-1's full scratch:
RBW (op `rbw_method410`) then `Stage.delete_object("BuildArray", 11261)` -> ExecState 0, 0, 1; Error List 0 items; graph `graph_ring_p6rbwd_20261012_205248.json` 57f33e7c;
peak 611.7 MB. This card makes the SAME two rows on a fresh byte copy, and this time SAVES it - but only if every pre-save gate passes. No third row, no repair, no
second scratch (unless a tool demands one, step 3). No hook, plan, stagexec, stage_prerun or memory-limit edit.

## Steps, in this order (stop at the first unexpected result and RETURN with the facts)
1. **Hash first**: CALL `prep_c168_hashlib.check(<this card>, "before")` from a thin script `tools/bench/diag_c169_a1_1_hash.py` (as `diag_c168_a1_2_hash.py` does; it holds only the
   card path and the mode). Drift in any card input or any of the 7 claudeDev VI pins = RETURN. `py tools/protocol.py requires <this card>` must PASS.
   Purpose item 0 asks for these hashes by name: bed 75773b0d, graph 7815af09, 168 graph 57f33e7c, 168 EL f71773bc, memory_model d12bcd3b, S1 json 5de014fe, p6_closure 502a43d4 (all are card inputs).
2. **Recipe `tools/recipes/stage_d1_ring_p6.py`** (scope header `# labview: build` / `# hardware: none`, `RESULT {...}` line, run under `bgrun --material`). Per
   `docs/script-writing.md`: the recipe holds INPUTS and CALLS. The 168 script `tools/bench/diag_c168_a1_2_rbwdel.py` is the sequence to follow and its logic is already
   shared: `prep_c168_a1_2_lib` (`Meter`, `el_read`, `tunnel_read`, `gone_and_count`, `frame_cdiff`, `inputs_of`, `closure_rd_diff`) and `prep_c167_a1_1_graphlib.read_graph` +
   `stagekit.e5_check`; `Stage.delete_object` (stagekit.py:700), `Stage.save` (stagekit.py:1204), `gscript.exec_state`. CALL them. Do NOT paste any block of the 168 script.
   If the recipe needs logic the 168 script holds inline (the F-S3 / F-S4 / row-set comparisons at `diag_c168_a1_2_rbwdel.py:142-163`), EXTRACT it first into
   `tools/bench/prep_c168_a1_2_lib.py` (or `stagekit` if it belongs there) with a self-test that replays the recorded 168 data, switch the recipe to it, and report the old copy as
   file:line. If the extraction is outside this card's `write` globs, RETURN with `open:` naming the block. The recipe has exactly two edit rows: `rbw_method410` and
   `delete_object` BuildArray #11261 (class string and uid from `diag_c168_a1_2_plan.json`); nothing else. Work copy = a byte copy of 75773b0d named
   `claudeDev\D1_ring_p6_<ts>.vi` (the `Stage` name argument `D1_ring_p6`; check how `stage_d1_ring_p5s02e.py` and `Stage.__init__` form `<name>_<ts>.vi`).
   Sequence on that copy (the 168 script's a-d, then the gates, then save):
   a. ExecState BEFORE (== 0); b. RBW (ExecState after == 0, Wire count 2091 -> 2066); c. `Stage.delete_object("BuildArray", 11261)`, ExecState after, #11261 absent,
   Wire objects 2066; d. graph read + `e5_check` of the in-memory copy (base 7815af09, deleted_nodes [11261], deleted_wires the 22 termless F1 uids, as 168); e. full Error List
   of the in-memory copy (`el_read`, no save); f. the PRE-SAVE gates of PD406(e), now REAL GATES (not facts):
   - S-1 ExecState after the delete == 1;
   - S-2 Error List 0 error items (item count 0, window N 0);
   - S-3 (F-S3) #2626 has its 4 inputs wired and equal to 7815af09's sources;
   - S-4 (F-S4) LoopTunnels #5204 / #10404 IndexMode + outer terminal type == the stored 7f2582ae values (`diag_c166_a1_1_tun.json`, read the scratch with `gscript.tunnels` / `gscript.read_term_type`; do NOT open 7f2582ae);
   - S-5 (PD406(b), replaces 168's F-S5) the frame-keyed `computation_diff(S1 5de014fe, this copy's graph)` row set == the same diff computed on the 168 graph 57f33e7c, row for row
     (30 rows). List BOTH differences (rows only in this copy's diff; rows only in the 168 diff); both must be EMPTY. Use `frame_cdiff` for both graphs, then compare the two sets.
   Any S-gate FAIL = NO SAVE: the copy is deleted (`Stage` hygiene), the Error List and graph are returned in `facts`, and the card ends. A gate that is wrong is not edited here (rule 7).
   Every MEM line <= 675 (`Meter`); the Error List read is skipped with a gate FAIL if the meter exceeds the headroom, exactly as 168 (`EL0`).
   g. SAVE: `Stage.save()` with `broken_ok=False` (ExecState is 1, so the scripted route and the cold re-open check apply). md5 of the saved file; the input 75773b0d unchanged.
3. **Dry and prerun BEFORE any launch** (none of these start LabVIEW for the real run):
   - `py tools/stage_prerun.py --dry tools/recipes/stage_d1_ring_p6.py --graph tools/bench/graph_ring_p5s02e_20261012_173009.json` (7815af09; this explicit form is the one fp-100 accepted:
     the default graph pick would take the RBW'd 6221-row graph labelled 75773b0d and fail R1/D1 in the dry). Quote the verdict.
   - `py tools/stage_prerun.py --prerun tools/recipes/stage_d1_ring_p6.py` - X10 must PASS on the model AS IS (168 predicted 678.9 against fail_above 680, measured 611.7; `memory_model.json` d12bcd3b is
     NOT edited). Quote X10 and any other verdict line. If X10 or any prerun check refuses, RETURN BLOCKED with the refusal text; no model edit, no gate-to-row change.
   - Quote `--scratch-required`'s exit code (PD406(c)). Exit 0 = go. **Exit 3 = ONE scratch on a fresh byte copy first** (that is the tool's rule, not a new decision): run it as the 168 script
     did (never saved, deleted), then continue. Any other exit = RETURN. If `check_launch` asks for a scratch, the same rule applies.
   - Gates a dry run can only STUB are named expected-unverified in this card's `rules` (below; DRY-UNVERIFIED-OK) and the run is started with `--unverified-card tools/bench/cards/task_169-a1-1.json`.
     Give the recipe gates exactly these label prefixes: `A0 ExecState BEFORE RBW`, `A1 ExecState AFTER RBW`, `R1 Wire count drop after RBW` (2091 -> 2066, ONE physical line as 168 did, fp-100),
     `D1 #11261 absent after delete` (reads inside the gate statement via `LB.gone_and_count`). Do not relabel a refused gate as a row (rule 7): return BLOCKED with the text.
4. **ONE launch** (`py tools/bgrun.py --material --max-min 60 --log tools/bench/launch_c169_p6.log --unverified-card tools/bench/cards/task_169-a1-1.json -- py -u tools/recipes/stage_d1_ring_p6.py`;
   one LabVIEW client, `labview-lock` per `docs/rules/labview-execution.md`; hardware: none; no motor, no camera, no VI run). Quote the three ExecState values and every MEM line.
5. **Post-save reads from the SAVED bytes** (in the same session if the meter and the deadline allow, otherwise a SECOND session on the saved file; say which):
   - ExecState 1 on reload; - the full Error List with `py tools/errorlist_check.py --vi <saved file> --role final` (0 error items; the result is kept as the EXPECTED Error List
     file `tools/bench/errorlist_expected_D1_ring_p6_<ts>.json` - quote the name the tool writes and its md5; if the tool needs `--expected`, the expected file is the 168 read f71773bc, 0 items);
   - graph read + `stagekit.e5_check` on the saved bytes: `tools/bench/graph_ring_p6_<ts>.json` + md5 + the e5 line; - PD406(b) S-5 re-checked on that graph (both differences empty).
   Any FAIL here: the saved file STAYS on disk (it is a new file, not an original; do NOT delete it), is NOT adopted, and the card RETURNS the facts. (A saved file that fails its post-save read is
   a finding for the judgement session.)
6. **`load_by_vi`**: ONE entry in `tools/bench/memory_model.json` keyed by the saved file's md5 (`value` = the MEM-after-load line of the post-save read, `vi`, `cite` file:line), in the style
   of the existing entries (`memory_model.json:38-...`). Edit with the editor tool; touch nothing else in that file (the model's limits and fit stay as they are). Quote the new md5 of memory_model.json.
7. **Hygiene**: scratch/work copies other than the saved file deleted (names listed), VI Server references opened == closed (quote the counter), handle counts quoted, `tasklist` shows NO LabVIEW (verify
   by process listing, not by assumption), the 7 VIs of the pin list (75773b0d 7f2582ae 94ffff94 f9ae7751 564d8cbe 6dcd5c3d eb1d0f31) rehashed UNCHANGED via `prep_c168_hashlib.check(<this card>, "after")`, no original opened,
   no `tools/hooks/**` edit. Gate false positives from hooks: `py tools/gate_fp.py log ...` and go on (the chat drains them).
8. **Facts** `tools/bench/diag_c169_a1_1_facts.md` (<= 50 lines, every number with a file:line): the three ExecState values, wire counts, each S-1..S-5 PASS/FAIL with evidence and both S-5 differences, MEM lines,
   saved path + md5 + size, post-save ExecState / Error List (file + md5 + class counts) / graph (file + md5 + e5 line) / S-5 re-check, the new load_by_vi entry and the memory_model md5, the dry/prerun/scratch-required
   verdicts verbatim, the old inline copies you extracted (file:line), hygiene.

## Not in this card
No bed move (card 169-a1-2 moves `current-bed:` and the INDEX), no STATUS/INDEX/plan edit, no fp drain (card 169-a1-3), no replay, no motor, no camera. Dispatch a peer only if a gate FAILS and the card's failure
budget is not spent. Script rules: `docs/script-writing.md`.
