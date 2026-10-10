---
card: 164-a2-3
status: current
date: 2026-10-10
---
# Brief 164-a2-3 (assignment 164-2) - OFFLINE: step-4 (p5s02d, groups J + K3 = A53..A69) recipe pair + pred + licence + predicted Error List; gates; prior art; NOT launched

`labview: none` (no LabVIEW process before, during or after), no `--launch`, no `tools/hooks` edit, no edit of `tools/*.py` stage tools. Read `docs/d1/ring-p5c.md` PD397(d), PD398 and `docs/script-writing.md`.
Card 164-a2-2 PASSED: `tools/bench/plan_ring_p5s02d.json` 872822f3 is FINAL on graph 3d5196ab (VI 564d8cbe): groups J + K3 only, 17 rows A53..A69, 13 ops, checkpoints [0,1,4,5,9,10,12,13],
MAIN 642.5 (START 581.8, limit 675). K3f, K4, K4f are NOT in this step (K3f/K4f sinks are inner-face of LoopTunnel, unroutable: facts `tools/bench/diag_c164_a2_1_facts.md`). So this step ends at A69, its adopted file
is the IN-BETWEEN `D1_ring_p5s02d_<ts>.vi` (not counted). Facts `tools/bench/diag_c164_a2_2_facts.md`, session `prep_c164_a2_2_session.json` 746dd63c (action -> op: ops 1..11 one action each,
op12 = A64-A66, op13 = A67-A69).
Group J has `delete_wire` (1 checkpoint) and `delete_object` x2: a NEW op kind for P5 (no passing launch yet), so a prior-art review is probably owed: decide from the gate output, not from this sentence.

## Template: card 163-a1-3 did exactly this for step 3 (p5s02c). Copy its flow, call its pieces, do not paste its blocks
Read `tools/bench/cards/brief_163-a1-3.md` and its facts `tools/bench/diag_c163_a1_3_facts.md`; its makers `tools/bench/prep_c163_a1_3_pred.py`, `prep_c163_a1_3_licence.py`, recipes
`tools/recipes/stage_d1_ring_p5s02c.py` and `stage_d1_ring_p5s02c_scratch.py`, outputs `plan_ring_p5s02c_pred.json` 721b9546, `plan_ring_p5s02c_licence.json` c8fdf33a. Step 4's base is 564d8cbe
(`D1_ring_p5s02c_20261010_125755.vi`, graph `graph_ring_p5s02c_20261010_131658.json` 3d5196ab, expected Error List `errorlist_expected_D1_ring_p5s02c_20261010_125755.json` 26d45c71). New files:
- `tools/bench/prep_c164_a2_3_pred.py` (+ `.log`) -> `tools/bench/plan_ring_p5s02d_pred.json`; `prep_c164_a2_3_licence.py` -> `plan_ring_p5s02d_licence.json`
- `tools/recipes/stage_d1_ring_p5s02d.py` and `stage_d1_ring_p5s02d_scratch.py`: inputs-only files on the shared `stagekit.RingSession` gates (one literal each for PLAN / PRED / LICENCE / SG census file,
  names, output name; everything else CALLED). Base VI path / md5 read from the plan's base graph, never typed. FRESH LabVIEW -> `claudeDev\D1_ring_p5s02d_<ts>.vi` (in-between, broken by design,
  rule-6 GUI save, not counted: D-2026-10-02-02). The scratch recipe uses the log name equal to its own constant (copy the 163 delta).
- Where a block of the 163 makers is identical, import / call it; if impossible without editing a file outside your write globs, list it as `OPEN:` with file:line.

## Content of the pred (PD396(d), PD391(d), PD389(c))
Per action A53..A69 (ids and uids from the plan's rows / session table, never typed): the delete_wire, the two delete_object, the local_read / primitive / case_frame_wire / nested rows, and the K3
case-border tunnel group (register_end_case_border, pass wire frame on the DST end). CEN2 section declares the by-ends judgement (`stagekit.gate_cen2`); E1 checkpoints = the real list from
`stagexec.compile_plan` + the `stagesim` step files (13 ops, [0,1,4,5,9,10,12,13] expected), each step file named. MAIN limit 675, START from `stage_prerun.x10_start(564d8cbe)`.
PB by POSITION (PD370(b)); licence classes as the step-3 licence file.

## Predicted step-4-end Error List -> `tools/bench/errorlist_predicted_D1_ring_p5s02d_end.json` (+ short table in the facts)
Start from the 26d45c71 expected file (do NOT edit it). Item by item with the action named: CLEARED (items a group-J / K3 action connects or deletes: quote the row ids), RAISED (every class a new object or wire of
A53..A69 can raise, or `UNPREDICTED:<action id>` where it cannot be decided offline), STANDING (the rest unchanged; predicted total). Use `tools/elrule.py` / `stagekit.el_class`; no second classifier.
Print cleared N, raised M, unpredicted K, total T. `errorlist_check.compare` on the file's own form must accept it.

## Gates on the FINAL bytes, quoted with PASS/FAIL (command forms exactly as in the 163-a1-3 logs; background under `py tools/bgrun.py --material --max-min N --log ... -- ...`)
- `stage_prerun.py` dry on EACH recipe (target PASS or PASS-UNVERIFIED with only CEN2 unverified), prerun PASS (X10 MAIN <= 675, X14, X17, X8), `--check-launch` on the FULL scratch command (with
  `--unverified-card` if the dry was PASS-UNVERIFIED; confirm first that the scratch's log name does not exist, move it aside if it does), and `py tools/stage_prerun.py --scratch-required <recipe>` exit code
  (quote the reason line; 3 = scratch required). The PB check (position-key gate) runs in the dry; a PB BLOCK = FAIL with the row, add no class (PD397(d)).
- Prior art: if `stage_prerun` / the launch gate says a prior-art review is owed for a changed line or op kind, run `py tools/prior_art_review.py` per its usage, quote the verdict (`novel` needed) and write the
  disposition; if it says PROVEN-PATTERN, quote that line. Do not decide it from memory.
- Do NOT run `--launch`. A hook false positive: `py tools/gate_fp.py log ...` and report; never an env bypass.

## Report `tools/bench/diag_c164_a2_3_facts.md` (<= 40 lines, facts only)
md5 of every output; per-action pred entries (ids only); E1 checkpoints; Error List cleared / raised / unpredicted / total with row ids; dry / prerun / check-launch / scratch-required / prior-art lines
quoted (rc); the exact scratch and real launch command lines; md5 UNCHANGED list (stagesim 95a162ba, stagexec a4df7e15, stagekit dd57c1ca, stage_prerun 7605116f, stage_shared b688edd4, memory_model 8fb432e4,
plan_ring_p5s02d.json 872822f3, graph 3d5196ab, the 26d45c71 EL file, VIs 564d8cbe / f9ae7751 / 94ffff94 / 7f2582ae / eb1d0f31). `OPEN:` lines with file:line.
