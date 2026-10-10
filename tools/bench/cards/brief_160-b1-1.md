---
card: 160-b1-1
status: current
date: 2026-10-10
---
# Brief 160-b1-1 (assignment 160-1) - OFFLINE: step-1 mapping into `stagekit`, then `plan_ring_p5s02b.json` final True on the real 94ffff94 graph (PD390(c))

`labview: none`: no LabVIEW process, no stage launched, no `tools/hooks` edit. `docs/script-writing.md` binds you (shared functions are CALLED, a new function
carries a docstring naming its self-test). You may edit `tools/stagekit.py` ONLY by adding the mapping functions below (no existing function changes); `tools/stagesim.py`
and `tools/stagexec.py` are final (card 160-a1-1: stagesim a3261b56, stagexec c4a6e0b6, they now delete a termless Wire; do not edit them).

## Part 1 - the mapping becomes a shared stagekit function
`tools/bench/prep_c159_c1_1_lib.py` (186 lines) holds `made_symbols`, `used_symbols`, `map_symbols`, `map_frames`, `apply_map`, `bound_from_cmap` (+ `_head`, `FRAME_SYM`).
Move them into `tools/stagekit.py` as module-level functions with the same names and behaviour (add a short section; `bound_from_cmap` keeps its
`stage_prerun.read_creation_map` call; `map_frames` keeps its `stagesim` import local to the function). Do not change any body except the import path.
- The self-test of those functions is the lib's `--selftest` (replays card 155-a2-1's recorded case, PREDICTION 3/0). Make it call the stagekit functions:
  write `tools/bench/selftest_c160_stagemap.py` (+ `.log`), the same T1..T3 gates on the same recorded inputs, plus (T4) a check that for each of the six
  functions `stagekit.<f>` and `prep_c159_c1_1_lib.<f>` return identical values on the 155-a2-1 inputs. Print `RESULT n/0`. Docstrings of the stagekit functions
  name `selftest_c160_stagemap`.
- Leave `prep_c159_c1_1_lib.py` in place and unedited (history; the old maker imports it).
- Find the suites that pin `tools/stagekit.py` (grep `ac3a8f57` under `tools/bench/selftest_*.py` and `tools/stage_prerun.py`). Re-pin ONLY the stagekit prefix
  (old -> new, say so in its docstring line) in the four you may write: `selftest_c158_runcheck.py`, `selftest_c158_wire0face.py`, `selftest_c159_cen2_ends.py`,
  `selftest_c160_delwire.py`; run each, quote the result; a count that differs from its last pass (8/0, 10/0, 24/0, 12/0) is a FAIL, not a re-pin.
  Every other file whose pin moved is listed as `OPEN:` with file:line (a later card re-pins it); if `tools/stage_prerun.py` pins stagekit in CODE, do not edit it: `OPEN:`.

## Part 2 - the plan, made by CALLING the stagekit functions
Write `tools/bench/prep_c160_b1_1_mk.py` (<= 150 lines): a copy of the flow of `prep_c159_c1_1_mk.py` (242 lines) that imports `stagekit` for the mapping instead of
`prep_c159_c1_1_lib`, and reads the same inputs (the plan input `tools/bench/plan_ring_p5s02b_in.json` 56bfddd3 is the input; `diag_c159_c1_1_facts.md` is its report).
Build `tools/bench/plan_ring_p5s02b.json` anew (the existing file caef7e1c, final False, is kept as `plan_ring_p5s02b_c159.json` by copy first):
- 18 actions: action 1 `delete_wire` 10394 (uid read from P5-1's #3052 'File # Saved' row, not typed), then A24..A40; cut stays at the end of group H (MAIN 654.6).
- Now that the termless branch exists, REALSIM must replay action 1 and all 18 actions on the real graph `tools/bench/graph_ring_p5s02a_20261010_032547.json`
  (94ffff94): failed null, 0 PROVISIONAL, the route check runs. Planned MAIN <= 675 with START_ASSUMED 603.4 (`tools/bench/memory_model.json` 5b87de43, unchanged).
- Output `final: True`. Gate SB of the old maker (the only one that failed 20/1) must PASS; if it still fails, report which row, the line, and STOP (FAIL, no workaround).
- Each of A28 A32 A35 A39 keeps its ASSUMPTION text (MERGE, expected sim-end uid w24285 / w24264 / w24312 / w24300, CEN2 judges by wire ends, PD389(b)); quote them.
- Compile `stagexec.compile_plan` on real owners (expect 8 ops: delete_wire 1, tunnel 5, case_frame_wire 2; checkpoints [0,2,3,4,6,7,8]) and quote.

## Report `tools/bench/diag_c160_b1_1_facts.md` (<= 40 lines, facts only)
stagekit diff (file:line of the six new functions), self-test result line, the suites re-pinned (old -> new prefix) with results, the plan md5 + final + REALSIM line
+ planned MAIN + compile result, the four MERGE rows, md5 before/after of `tools/stagekit.py`, and md5 UNCHANGED: `tools/stage_prerun.py` 7605116f, `tools/stagesim.py`
a3261b56, `tools/stagexec.py` c4a6e0b6, `tools/addrcheck.py` 207beb0d, `tools/vigraph.py` a7eb58c7, `prep_c159_c1_1_lib.py` 218af76c; VIs 94ffff94 / s09 eb1d0f31 /
P5-1a 2482fe7b / P5-1 7f2582ae unchanged; `tools/hooks` untouched (a hook-written `material_marker.log` is not an edit). `OPEN:` lines with file:line.
