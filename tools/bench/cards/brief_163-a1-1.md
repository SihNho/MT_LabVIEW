---
card: 163-a1-1
status: current
date: 2026-10-10
---
# Brief 163-a1-1 (assignment 163-1) - OFFLINE: hash the inputs, then `plan_ring_p5s02c.json` on the real p5s02b graph 431cfd83 (PD396(a)(b)(c))

`labview: none` (no LabVIEW process before, during or after), no `--launch`, no `tools/hooks` edit, no edit of `tools/stagekit.py`, `stagexec.py`, `stagesim.py`,
`stage_prerun.py`, `stage_shared.py`. Read `docs/d1/ring-p5b.md` PD396 (line 323 on) and `docs/script-writing.md` first. Cycle 162 adopted step 2 as
`claudeDev\D1_ring_p5s02b_20261010_105511.vi` (f9ae7751, scratch 20/0, peak 657.1, load 601.2). Step 3 takes groups I + J (A41..A60) if the memory rule allows, else group I alone.

## Part 1 - hash the inputs FIRST and quote them (before any other act)
Write `tools/bench/prep_c163_a1_1_hash.py` (+ `.log`) that prints md5 (hashlib) of: `tools/bench/plan_ring_p5s02r_in.json`, `tools/bench/graph_ring_p5s02b_20261010_111905.json`,
`tools/bench/memory_model.json`, `tools/bench/errorlist_expected_D1_ring_p5s02b_20261010_105511.json`, `tools/stage_shared.py`, `tools/stagekit.py`, `tools/stagexec.py`,
`tools/stagesim.py`, `tools/stage_prerun.py`, `docs/d1/ring-p5b.md`, and (if the permission layer allows; else say "not hashed") the four VIs in
`C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev`: f9ae7751 `D1_ring_p5s02b_20261010_105511.vi`, 94ffff94 (`D1_ring_p5s02a_20261010_023239.vi`), 7f2582ae (P5-1), eb1d0f31 (s09).
Judgement-time values to compare: plan_ring_p5s02r_in d84634bd, graph 431cfd83, memory_model def9e640, stage_shared b688edd4, stagekit 9b8f82c1, stagexec a4df7e15, stagesim 95a162ba,
stage_prerun 7605116f, ring-p5b.md 70b89fac, expected EL 60e02787. A mismatch is explained in the facts BEFORE you go on (a pin that only drifted is not a reason to stop; a changed graph or plan input is).

## Part 2 - the plan, made by CALLING shared functions
Write `tools/bench/prep_c163_a1_1_mk.py` (<= 150 lines): the flow of `tools/bench/prep_c160_b3_1_mk.py` (read it; it maps with the shared `stagekit` functions and gates every step), re-based:
1. Input plan for `stagesim.simulate` = the A41..A60 (groups I and J) rows of `tools/bench/plan_ring_p5s02r_in.json`, base = graph 431cfd83 (p5s02b VI f9ae7751), mapped with the stagekit mapping functions
   (`map_symbols`/`map_frames`/`apply_map`/`bound_from_cmap`, PD390(c)) and `stage_shared` helpers where they apply (e.g. `insert_stub_deletes` only if a base sink-only stub appears; say if one does - do not invent one).
   Symbols made by earlier steps are bound through the binding records of the ADOPTED steps (p5s01a / p5s01b / p5s02a / p5s02b), never typed uids. Do not retype a uid.
2. **Memory rule (PD396(c), mechanical, no judgement):** compute planned MAIN = X10 on `SX.checkpoint_ops` (`stage_prerun.x10_*`, read-only; limit 675 UNCHANGED, `START` = measured `load_by_vi` f9ae7751 = 601.2 from
   `memory_model.json`). If I + J (A41..A60) <= 675 -> the plan is A41..A60 (one step). Else the plan is group I alone (A41..A52) and group J is left for p5s02d. A group is NEVER split. If group I alone > 675 -> FAIL
   (hand back) with the number. Quote the planned MAIN for BOTH candidates (I+J and I) whichever you choose.
3. Keep the previous `plan_ring_p5s02c.json` if one exists (copy aside first). Output `tools/bench/plan_ring_p5s02c.json` is written ONLY by `stagesim.simulate` (final True).
4. Gates (each prints a FACT line and a gate line, quoted PASS/FAIL): ROWS (mapped rows equal the input except uids), SB (REALSIM final True on 431cfd83, failed None, all actions replayed, 0 PROVISIONAL, route check PASS
   and 0 UNROUTABLE; quote every route row's k / op / route), C compile (`stagexec.compile_plan` on real owners: quote the op list and checkpoints; every `delete_wire` is a checkpoint - group J's `delete_object` rows are a
   NEW op kind for P5: say how the compile handles them, quote), X10 MAIN, X8 control_path_lint, X17, no-group-split check, action id range check (A41..A60 or A41..A52).
   A stale expectation inherited from the b3 maker is changed and reported, never loosened silently.

## FAIL conditions (return FAIL with the line, no workaround)
Final False; any UNROUTABLE; MAIN > 675 for group I alone; a mapped row differs from the input; the compile cannot express a group-J op (state which op: then the plan is group I alone only if the
memory rule alone would pick it - otherwise FAIL). A tool edit looks needed -> FAIL (hand back); no tool edit is allowed in this card.

## Report `tools/bench/diag_c163_a1_1_facts.md` (<= 40 lines, facts only)
Part 1 md5 table with equal/changed against the judgement-time values; the planned MAIN for I+J and I and which plan was made (and why, citing the number); plan md5 + final + REALSIM line; the action ids in order; route rows;
compile op list + checkpoints; md5 UNCHANGED list (stagekit, stagexec, stagesim, stage_prerun, stage_shared, plan_ring_p5s02r_in, graph 431cfd83, memory_model, the VIs); `OPEN:` lines with file:line.
