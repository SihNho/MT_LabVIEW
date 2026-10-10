---
card: 160-c3-1
status: current
date: 2026-10-10
---
# Brief 160-c3-1 (assignment 160-2) - OFFLINE: step-2 recipe pair + pred + licence + predicted Error List for plan_ring_p5s02b.json (PD391(d)(e), PD390(c)); NOT launched

`labview: none` (no LabVIEW process before, during or after; `tasklist` shows none), no `--launch`, no `tools/hooks` edit, no `tools/*.py` edit. Read `docs/d1/ring-p5b.md` PD388(c),
PD389(b)(d), PD390(c), PD391(d)(e) and `docs/script-writing.md`. Card 160-b3-1 PASSED: `tools/bench/plan_ring_p5s02b.json` f4520b10 is FINAL on 94ffff94 (20 actions: delete w10394,
A24..A40, `dw_go` / `dw_ho` stub deletes; 10 ops; MAIN 657.4 <= 675), session table `tools/bench/prep_c160_b3_1_session.json` e5279899, report `tools/bench/diag_c160_b3_1_facts.md` e38a4f74.
Cards in this assignment moved `stagesim` to 95a162ba and `stagexec` to ddf23a31; `stagekit` 1441bb4c and `stage_prerun` 7605116f are unchanged - these are the FINAL tool bytes the
dry / prerun must record. Another card (160-f3-1) edits self-test files only (`selftest_c134_1_dry`, `selftest_c156_b2_2_invcheck`, ...); you must not touch them.

## Template: card 156-a1-1 did exactly this for step 1 (p5s02a). Copy its flow, do not paste its blocks
`tools/bench/prep_c156_a1_1_pred.py` (27fc52dc), `prep_c156_a1_1_licence.py`, `prep_c156_a1_1_lib.py` (fc6ce5f6, `Gate`, `main_of`, `step_facts`), recipes
`tools/recipes/stage_d1_ring_p5s02a.py` (b52b9ff5) and `_scratch.py` (64b4f18b), results `diag_c156_a1_1_facts.md`. Step 2's base is 94ffff94 (the saved p5s02a file, graph
`graph_ring_p5s02a_20261010_032547.json` 7ac24924), not the P5-1 file. New files (prefix c160_c3_1 for makers, `p5s02b` for the stage):
- `tools/bench/prep_c160_c3_1_pred.py` (+ `.log`) -> `tools/bench/plan_ring_p5s02b_pred.json`; `prep_c160_c3_1_licence.py` -> `plan_ring_p5s02b_licence.json`
- `tools/recipes/stage_d1_ring_p5s02b.py` and `stage_d1_ring_p5s02b_scratch.py`: inputs-only files on the shared `stagekit.RingSession` gates (PD390(c): one literal each for PLAN / PRED /
  LICENCE / SG census file, names, output name; everything else CALLED). Base VI path / md5 read from the plan's base graph, never typed. FRESH LabVIEW -> `claudeDev\D1_ring_p5s02b_<ts>.vi`
  (in-between file of step P5-2, broken by design, rule-6 GUI save, not counted: D-2026-10-02-02).
- Where a block of the 156 makers is identical, import / call it; if impossible without editing a file outside your write globs, list it as `OPEN:` with file:line.

## Content of the pred (PD391(d), PD389(c))
Per action: A28 and A35 (LSR faces, stubs w24285 / w24312): MERGE with the expected uid (read from the plan's rows / session table, not typed) and "CEN2 judges by wire ENDS";
A32 and A39: stub deleted first + fresh connect, the new wire uid is NOT predicted; the delete rows `dw_go` / `dw_ho` and the A13-remnant delete of w10394 have their own entries.
CEN2 section declares the by-ends judgement (`stagekit.gate_cen2`). E1 checkpoints from the plan's compiled ops (10 ops, checkpoints [0,2,3,5,7,9,10] per facts; take the real list from
`stagexec.compile_plan` + `stagesim` step files, with each step file named). MAIN limit 675, START from `stage_prerun.x10_start(94ffff94)`. PB by POSITION (PD370(b)).

## Predicted step-2-end Error List (PD389(d)) -> `tools/bench/errorlist_predicted_D1_ring_p5s02b_end.json` (+ a short `.md` table in the facts file)
Start from the 56-row `errorlist_expected_D1_ring_p5s02a_20261010_023239.json` (1fd016bf; do NOT edit it). Item by item, with the action named:
- CLEARED by step 2: w10394 'not connected' item (delete_wire 10394), the `File # Saved`-style notconnected items on the LSR/RSR faces that A28/A35/A32/A39 now connect, plus the two sink-only
  stubs w24264 / w24300 (their 'no source' / 'not connected' items) - find each by `clears_by` in the 56-row file; quote the row ids;
- RAISED by step-2 actions: every Error List item class a new object or wire of A24..A40 can raise (new unwired terminals, new Build/Select/Equal inputs, a loop/case tunnel without
  a source, new `undirected` etc.) - name each with its action id, or write `UNPREDICTED:<action id>` where the class cannot be decided offline (the scratch measures it);
- STANDING: the rest, unchanged; and the predicted total. Use `tools/elrule.py` / `stagekit.el_class` to class items; do not write a second classifier.
Both counts printed (cleared N, raised M, unpredicted K, total T). `errorlist_check.compare` on the file's own form must accept it (same entry form as the 56-row file).

## Gates to run on the FINAL bytes, quoted with PASS/FAIL
`stage_prerun.py` dry on the recipe (target PASS, unverified 0), prerun PASS (X10 MAIN <= 675, X14, X17, X8), `--check-launch` result, and
`py tools/stage_prerun.py --scratch-required <recipe>` exit code (expected 3 because PD391(e): new structure class; quote the reason line). Use exactly the command forms the 156-a1-1 logs
used (`prep_c156_a1_1_dry.log`, `_prerun.log`, `_checklaunch.log` show them); background anything LabVIEW-adjacent under `py tools/bgrun.py --material --max-min N --log ... -- ...`.
Do NOT run `--launch`. If a gate refuses on a hook false positive, log it with `py tools/gate_fp.py log ...` and report - never an env bypass, never a hook edit.
A stale expectation in the 156 template (counts, names) is changed and reported, never loosened silently.

## Report `tools/bench/diag_c160_c3_1_facts.md` (<= 40 lines, facts only)
md5 of every output; the per-action pred entries (ids only); E1 checkpoints; Error List cleared / raised / unpredicted / total with the row ids; dry / prerun / check-launch / scratch-required
lines quoted (rc); md5 UNCHANGED list (stagesim 95a162ba, stagexec ddf23a31, stagekit 1441bb4c, stage_prerun 7605116f, plan_ring_p5s02b.json f4520b10, plan_ring_p5s02b_in*.json, graph 7ac24924,
VIs s09 eb1d0f31 / P5-1a 2482fe7b / P5-1 7f2582ae / 94ffff94; "not hashed" if the permission layer refuses). `OPEN:` lines.
