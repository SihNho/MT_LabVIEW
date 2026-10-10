---
card: 164-a1-1
status: current
date: 2026-10-10
---
# Brief 164-a1-1 (assignment 164-1) - OFFLINE: hash the inputs, add the 4 `frame` keys (PD397(b)), make `plan_ring_p5s02d.json` on the real p5s02c graph 3d5196ab (PD397(c))

`labview: none` (no LabVIEW process before, during or after), no `--launch`, no `tools/hooks` edit, no edit of `tools/stagekit.py`, `stagexec.py`, `stagesim.py`,
`stage_prerun.py`, `stage_shared.py`. Read `docs/d1/ring-p5c.md` PD397 (line 17 on) and `docs/script-writing.md` first. Cycle 163 adopted step 3 as
`claudeDev\D1_ring_p5s02c_20261010_125755.vi` (564d8cbe, scratch 21/0, peak 602.0), graph `tools/bench/graph_ring_p5s02c_20261010_131658.json` (3d5196ab). Step 4 takes the
remaining groups of A53..A80 by WHOLE groups: J (A53..A60, `delete_object`), K3 (A61..A69), K3f (A70), K4 (A71..A79), K4f (A80).

## Part 1 - hash the inputs FIRST and quote them (before any other act)
`tools/bench/prep_c164_a1_1_hash.py` (+ `.log`), hashlib md5 of: `tools/bench/plan_ring_p5s02r_in.json`, `tools/bench/graph_ring_p5s02c_20261010_131658.json`,
`tools/bench/memory_model.json`, `tools/bench/errorlist_expected_D1_ring_p5s02c_20261010_125755.json`, `tools/stage_shared.py`, `tools/stagekit.py`, `tools/stagexec.py`, `tools/stagesim.py`,
`tools/stage_prerun.py`, `docs/d1/ring-p5c.md`, and the five VIs in `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev` (hash the bytes only; if the permission layer
refuses, say "not hashed"): 564d8cbe `D1_ring_p5s02c_20261010_125755.vi`, f9ae7751 (`D1_ring_p5s02b_20261010_105511.vi`), 94ffff94 (`D1_ring_p5s02a_20261010_023239.vi`), 7f2582ae (P5-1), eb1d0f31 (s09).
Judgement-time values: plan_ring_p5s02r_in d84634bd, graph 3d5196ab, memory_model 8fb432e4, expected EL 26d45c71, stage_shared b688edd4, stagekit dd57c1ca, stagexec a4df7e15,
stagesim 95a162ba, stage_prerun 7605116f, ring-p5c.md 70fe6983. A mismatch is explained in the facts BEFORE you go on (a pin that only drifted is not a reason to stop; a changed graph
or plan input is).

## Part 2 - the 4 `frame` keys (PD397(b))
Copy `plan_ring_p5s02r_in.json` aside first (`plan_ring_p5s02r_in_pre164.json`, byte copy, md5 quoted). Then in `plan_ring_p5s02r_in.json` the actions A69 (`w_k3pass`) and A79 (`w_k4pass`) gain
`"frame": "True"` on BOTH the source and the destination end, the same shape A33 `w_gpass`, A40 `w_hpass` and A52 `w_c7_pass` already have (read those rows and copy their key layout exactly).
Edit with the Edit tool (no heredoc patching). Prove it with a JSON compare script (`prep_c164_a1_1_cmp.py`, output in the log): the only differences are exactly those 4 added keys; quote old -> new md5.
Anything else different = FAIL (restore the copy).

## Part 3 - `plan_ring_p5s02d.json`, made by CALLING shared functions
Base = graph 3d5196ab (VI 564d8cbe). Input = the A53..A80 rows of the edited `plan_ring_p5s02r_in.json`, mapped with the stagekit mapping functions
(`map_symbols`/`map_frames`/`apply_map`/`bound_from_cmap`, PD390(c)) and `stage_shared` helpers where they apply. Symbols and frames made by earlier steps (including `new:CQ7`,
`new:CQ7.f0|f1`) are bound through the BINDING RECORDS of the adopted steps (find the step-3 record under `tools/bench/sim/ring_p5s02c/**` / `adopted_scratch.jsonl` / the scratch log's binding
lines), never typed uids. QUOTE the uid that the `new:CQ7` 'True' frame resolves to and the file:line of the record it came from.
Flow: `tools/bench/prep_c163_a1_1_mk.py` + `prep_c163_a1_2_mk.py` did this for step 3. They are history and the second one patches the first with text substitutions, which is exactly what
`docs/script-writing.md` rule 4 forbids for new work. So: **extract** the flow of `prep_c163_a1_1_mk.py` into a parametrised module `tools/bench/prep_plan_flow_lib.py`
(function arguments: input plan, action range / group set, base graph, base VI, card id, session file; START from `stage_prerun.x10_start`, never typed), with a replay self-test that reproduces
`plan_ring_p5s02c.json` 930699ec from graph 431cfd83 and the unedited step-3 input (byte-equal, or the exact difference explained). Switch YOUR maker `prep_c164_a1_1_mk.py` (<= 60 lines) to call it.
Do not rewrite the 163 files. If the replay cannot be made byte-equal after one fix, do not keep going: write the maker as a parametrised copy of the 163-a1-1 flow in your own file, report both
copies as `OPEN:` with file:line, and carry on (the plan is the deliverable).

Memory rule (PD397(c), mechanical): for each PREFIX of whole groups (J ; J+K3 ; J+K3+K3f ; J+K3+K3f+K4 ; J+K3+K3f+K4+K4f) compute planned MAIN = X10 on `SX.checkpoint_ops`
(read-only; limit 675 UNCHANGED; `START` = `stage_prerun.x10_start(<VI 564d8cbe>)`, called, not typed, i.e. `load_by_vi` 564d8cbe + op0 read from `memory_model.json`) and the rows of the prefix.
The plan is the LONGEST prefix with MAIN <= 675 and rows <= 40. A group is never split. Quote MAIN and rows for EVERY prefix tried (stop at the first prefix that fails; longer ones are bigger).
If J alone is > 675: FAIL, hand back with the number (do not cut J). Every `delete_wire` is a checkpoint (PD393(a)); group J's `delete_object` rows are a NEW op kind for P5 - state how the
compile (`stagexec.compile_plan`) handles them and quote the op list + checkpoints. Output `tools/bench/plan_ring_p5s02d.json` is written ONLY by `stagesim.simulate` (final True). If a plan with that
name exists, copy it aside first.

Gates (each prints a FACT line and a gate line, quoted PASS/FAIL): ROWS (mapped rows equal the input except uids), SB (REALSIM final True on 3d5196ab, failed None, all actions replayed, 0 PROVISIONAL, route
check PASS and 0 UNROUTABLE; quote every route row's k / op / route), C compile, X10 MAIN, X8 control_path_lint, X17, no-group-split, action id range. A stale expectation inherited from an older maker is changed
and reported, never loosened silently.

## FAIL conditions (return FAIL with the line, no workaround)
Final False; any UNROUTABLE; MAIN(J) > 675; a mapped row differs from the input; the JSON compare shows more than the 4 keys; the compile cannot express a group-J op (say which); a tool edit looks needed
(outside `tools/bench/prep_*`). The `new:CQ7` frame cannot be bound from the record = FAIL with the record's lines.

## Report `tools/bench/diag_c164_a1_1_facts.md` (<= 45 lines, facts only)
Part 1 md5 table (equal/changed); the 4-key compare and old -> new md5; the `new:CQ7` 'True' frame uid + its record cite; MAIN and rows per prefix, which prefix was chosen and which action ids; plan md5 +
final + REALSIM line; route rows; compile ops + checkpoints; md5 UNCHANGED list (stagekit, stagexec, stagesim, stage_prerun, stage_shared, memory_model, graph 3d5196ab, EL 26d45c71, the VIs);
`OPEN:` lines with file:line.
