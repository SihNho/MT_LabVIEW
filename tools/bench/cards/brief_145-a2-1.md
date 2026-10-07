---
type: brief
status: current
date: 2026-10-07
---
# Brief 145-a2-1 — ADOPT the s04 scratch file 95e408ff + MEASURE the subVI pane requiredness (docs/d1/ring-p4b.md PD351(b)(e))

Round 1 ended with the s04 scratch at FULL PASS 24/0 (`tools/bench/diag_c145_2_facts.md`, a73ca3f1) and the Error List at 58 vs
predicted 60. The judgement (PD351(b)) explains the 2 missing items as the two SubVI drops PS1 / SQ1 not producing a "required
input" item, and names the cause as working: their inputs are not Required. This card adopts the file and MEASURES that cause.
No new scratch run; no edit of any stage tool.

## Steps
1. **Inputs check (md5, before any LabVIEW):** s04 scratch `claudeDev\D1_ring_p4s04_20261007_215031.vi` = 95e408ff (318509 B);
   s03 `D1_ring_p4s03_20261007_202957.vi` 282301ca; bed `D1_ring_p3b2b_20261002_130007.vi` 395118775a52bc90073f4449b99f899d;
   plan `plan_ring_p4_s04v18.json` f349c39a; pred `plan_ring_p4_s04v18_pred.json` a2bbc8bf; EL read file
   `errorlist_D1_ring_p4s04_20261007_215031_20261007_220024.json` 5e53096a (58 items). A different md5 = RETURN.
2. **Adopt** 95e408ff as `claudeDev\D1_ring_p4s04_<stamp>.vi` with `stagexec.adopt_scratch` **called by import** from a script (the CLI form
   is refused under `labview: none`, fp-39; `adopted_scratch.jsonl` entry, PD329(a): the scratch IS the run, no second run). Ready scripts from
   round 1, unrun: `tools/bench/diag_c145_2_adopt.py` (7c016f4b), `diag_c145_2_mkgraph.py` (aa188343), `diag_c145_2_graph.py` (f34d5051) —
   read them first, reuse what fits, report any change. Record the adopted file's md5.
3. **Expected Error List file** `tools/bench/errorlist_expected_D1_ring_p4s04_<stamp>.json` built FROM the existing 58-item read 5e53096a
   (no new Error List read of the adopted file unless the tool requires it; if it does, run it once, `--role final`, and report 58 or the
   difference).
4. **Fresh LabVIEW instance:** load the adopted file (peak/load MB measured) and read the whole graph ->
   `tools/bench/graph_ring_p4s04_<stamp>.json` with md5. Handle count before/after (flat +-100).
5. **MEASURE the pane requiredness** (read from the VI, never assumed — in the same fresh instance, read-only): for EVERY input terminal
   of `claudeDev\RingPickSlot_v0.vi` (6fcf153f) and `claudeDev\RingSeqCheck_v0.vi` (0295a8d3) the connector-pane assignment
   Required / Recommended / Optional (VI Scripting: connector-pane terminal "required" property; search NI docs/our `docs/NAMES.md` first,
   external search is mandatory if the property name is not already recorded). Then from the new graph file list which of those inputs are
   UNWIRED at PS1 and at SQ1 (the real s04 drop nodes). Report a table: VI, input name, pane index, requiredness, wired?, source.
   **Any unwired input that reads Required = RETURN** (the working cause fails; say which). Close every reference you open.
6. **Housekeeping, only after steps 2-5 succeeded:** delete `claudeDev\D1_ring_p4s04_20261007_212230.vi` (abb76d41) and its resume record
   (the file named in the 145-a1-1 notes / `tools/bench/resume*` — find it by name, report the path). Our own files; delete, do not move.
7. **Check after:** s03 282301ca and bed 39511877 unchanged; plan / pred / recipes unchanged; LabVIEW closed and verified gone (`tasklist`).

## Never
- run a second scratch or any plan; edit stagexec / stagekit / stagesim / stage_prerun / gscript / elrule (the EL rule fix is the NEXT card,
  145-a2-2, and needs your requiredness table); open the bed or s03 for editing; save any VI except through the adopt path;
- touch the camera or any motor; touch s05 files.

## Return
`result/1` with: adopted file + md5, expected-EL file + item count, load MB, graph file + md5, the requiredness table (step 5) and the verdict
"all unwired inputs at PS1/SQ1 are Recommended/Optional" or the offending input, deleted files, s03/bed md5 before/after, handles before/after,
`tasklist` after. Facts file `tools/bench/diag_c145_a2_1_facts.md` (the requiredness table must be in it, file:line citable).
