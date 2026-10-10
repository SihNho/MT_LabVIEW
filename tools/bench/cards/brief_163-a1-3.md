---
card: 163-a1-3
status: current
date: 2026-10-10
---
# Brief 163-a1-3 (assignment 163-1) - OFFLINE: step-3 (p5s02c, group I = A41..A52) recipe pair + pred + licence + predicted Error List; gates; NOT launched

`labview: none` (no LabVIEW process before, during or after), no `--launch`, no `tools/hooks` edit, no edit of `tools/*.py` stage tools. Read `docs/d1/ring-p5b.md` PD396(a)-(e) and `docs/script-writing.md`.
Card 163-a1-2 PASSED: `tools/bench/plan_ring_p5s02c.json` 930699ec is FINAL on graph 431cfd83 (group I alone, 12 actions A41..A52, 8 ops, checkpoints [0,1,2,4,5,7,8], MAIN 658.3 under
`stage_prerun.x10_start(f9ae7751)` = 607.1; the I+J plan is kept aside, J becomes p5s02d). Report `tools/bench/diag_c163_a1_2_facts.md` fe9124b2, session table `prep_c163_a1_2_session.json` e8daf1fe.
Group I has NO `delete_wire` and NO `delete_object` (those are group J), so the "new op kind" prior-art condition may not be owed: decide from the gate output, not from this sentence.

## Template: card 160-c3-1 did exactly this for step 2 (p5s02b). Copy its flow, call its pieces, do not paste its blocks
Read `tools/bench/cards/brief_160-c3-1.md`; its makers `tools/bench/prep_c160_c3_1_pred.py`, `prep_c160_c3_1_licence.py` (and `prep_c156_a1_1_lib.py`), recipes `tools/recipes/stage_d1_ring_p5s02b.py` and
`stage_d1_ring_p5s02b_scratch.py`, its facts `diag_c160_c3_1_facts.md`. Step 3's base is f9ae7751 (`D1_ring_p5s02b_20261010_105511.vi`, graph `graph_ring_p5s02b_20261010_111905.json` 431cfd83). New files:
- `tools/bench/prep_c163_a1_3_pred.py` (+ `.log`) -> `tools/bench/plan_ring_p5s02c_pred.json`; `prep_c163_a1_3_licence.py` -> `plan_ring_p5s02c_licence.json`
- `tools/recipes/stage_d1_ring_p5s02c.py` and `stage_d1_ring_p5s02c_scratch.py`: inputs-only files on the shared `stagekit.RingSession` gates (one literal each for PLAN / PRED / LICENCE / SG census file, names,
  output name; everything else CALLED). Base VI path / md5 read from the plan's base graph, never typed. FRESH LabVIEW -> `claudeDev\D1_ring_p5s02c_<ts>.vi` (in-between file of step P5-2, broken by design, rule-6 GUI
  save, not counted: D-2026-10-02-02). The scratch recipe uses the log name equal to its own constant (brief_162-a1-2.md shows the launch deltas).
- Where a block of the 160 makers is identical, import / call it; if impossible without editing a file outside your write globs, list it as `OPEN:` with file:line.

## Content of the pred (PD396(d), PD391(d), PD389(c))
Per action A41..A52 (ids and uids from the plan's rows / session table, never typed): the new Shift Register / Add-const / Increment / Select-type primitives (route rows 1-8 in the 163-a1-2 facts), the case-border tunnels
(register_end_case_border) and the two `case_frame_wire` rows. CEN2 section declares the by-ends judgement (`stagekit.gate_cen2`); E1 checkpoints = the real list from `stagexec.compile_plan` + the `stagesim` step
files (8 ops, [0,1,2,4,5,7,8] expected), each step file named. MAIN limit 675, START from `stage_prerun.x10_start(f9ae7751)`. PB by POSITION (PD370(b)); licence classes as the step-2 licence file.

## Predicted step-3-end Error List -> `tools/bench/errorlist_predicted_D1_ring_p5s02c_end.json` (+ short `.md` table in the facts file)
Start from the 53-row `errorlist_expected_D1_ring_p5s02b_20261010_105511.json` (60e02787; do NOT edit it). Item by item with the action named:
- CLEARED by step 3: each item a group-I action connects (find by `clears_by` / the item's owner terminal; quote the row ids);
- RAISED by step 3: every Error List item class a new object or wire of A41..A52 can raise (new unwired terminals, tunnel without source, ...) - name each with its action id, or `UNPREDICTED:<action id>` where the class
  cannot be decided offline (the scratch measures it);
- STANDING: the rest unchanged; predicted total. Use `tools/elrule.py` / `stagekit.el_class`; no second classifier. Print cleared N, raised M, unpredicted K, total T.
  `errorlist_check.compare` on the file's own form must accept it (same entry form as the 53-row file).

## Gates on the FINAL bytes, quoted with PASS/FAIL (command forms exactly as in the 160-c3-1 logs: `prep_c160_c3_1_dry.log`, `_prerun.log`, `_checklaunch.log`; background under `py tools/bgrun.py --material --max-min N --log ... -- ...`)
- `stage_prerun.py` dry on EACH recipe (target PASS or PASS-UNVERIFIED with only CEN2 unverified), prerun PASS (X10 MAIN <= 675, X14, X17, X8), `--check-launch` on the FULL scratch command with `--unverified-card`
  if the dry was PASS-UNVERIFIED (confirm first that the scratch's log name does not exist; move it aside if it does), and `py tools/stage_prerun.py --scratch-required <recipe>` exit code (quote the reason line; 3 = scratch required).
- Prior art (purpose item 5): if `stage_prerun`/the launch gate says a prior-art review is owed for a changed line or op kind, run `py tools/prior_art_review.py` per its usage, quote the verdict (`novel` needed) and write the
  disposition; if it says PROVEN-PATTERN, quote that line. Do not decide it from memory.
- Do NOT run `--launch`. A hook false positive: `py tools/gate_fp.py log ...` and report; never an env bypass.

## Report `tools/bench/diag_c163_a1_3_facts.md` (<= 40 lines, facts only)
md5 of every output; per-action pred entries (ids only); E1 checkpoints; Error List cleared / raised / unpredicted / total with row ids; dry / prerun / check-launch / scratch-required / prior-art lines quoted (rc);
the exact scratch and real launch command lines; md5 UNCHANGED list (stagesim 95a162ba, stagexec a4df7e15, stagekit 9b8f82c1, stage_prerun 7605116f, stage_shared b688edd4, memory_model def9e640,
plan_ring_p5s02c.json 930699ec, graph 431cfd83, the 60e02787 EL file, VIs f9ae7751 / 94ffff94 / 7f2582ae / eb1d0f31). `OPEN:` lines with file:line.
