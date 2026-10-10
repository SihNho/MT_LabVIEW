---
card: 159-a4-1
status: current
date: 2026-10-10
---
# Brief 159-a4-1 (assignment 159-1) - OFFLINE device repair in stage_prerun/stagekit, PD387(e)

No LabVIEW, no hook edit (`tools/hooks/**` is never changed by a runner card). Plan `docs/d1/ring-p5.md` PD387(e) (line 369-375); decision
`docs/violation-decisions.md:2019-2030` (`device-failed`, evidence `tools/bench/diag_c158_a2_2_dry.log:70`). Runs beside the offline attribution card 159-a3-1, which reads
`vigraph.py`, `errorlist_check.py`, `addrcheck.py` only - this card must NOT edit those three.

## The defect (from the decision text)
The 2026-10-02 device ("an offline check must not pass what it did not verify") printed `UNVERIFIED-DRY` for CEN2, but the dry's final `unverified N` counted only PB; and
`census_gate` treats only an EMPTY declaration as UNPREDICTED, so a declaration for one op of seventeen passed; PB ran on stub input and was waved through.

## Repair (all three in `tools/stage_prerun.py` / `tools/stagekit.py`, whichever owns the code; find the owners by reading, `Grep UNVERIFIED-DRY|census_gate|census_overall|unverified`)
1. The dry's final `unverified N` counts EVERY gate line that printed `UNVERIFIED-DRY` (all gates, not PB only).
2. A census declaration that does not cover every op of the plan, or a pred whose `census_overall` is `UNPREDICTED`, is UNPREDICTED - never a partial PASS.
3. The dry runs the recipe's own PB, D, TD and CEN2 against the SIMULATED END (stagesim's end graph), not stub input. If any of the four cannot be run on the simulated end for a
   structural reason, it prints `UNVERIFIED-DRY` with the reason and counts in (1).

## Self-test (new file `tools/bench/selftest_c159_a4_1.py`, header `labview: none / hardware: none`; call the shared functions, no copies)
- Stored c158-a2-2 inputs (`tools/bench/diag_c158_a2_2_dry.log`, `_scr_dry.log`, `_prerun.log`, `_checklaunch.py`: census declared for the Case op only, PB on stub input): the repaired
  dry reports CEN2 and PB as unverified or FAIL, and its final `unverified N` counts both.
- A fully declared census + all four gates run on the simulated end -> `unverified 0` (use an existing passing plan, name which).
- All stored plans in `tools/bench/plan_*.json` still compile equal (before/after: same exit and same counts as the pre-edit tool; state the method).
- Existing suites that cover these files keep their counts: run `selftest_stagekit`, `selftest_t7_ring`, `selftest_c134_1_dry` and quote before/after counts. The c158 wire0face / runcheck /
  gates386 selftests unchanged (find them: `Glob tools/bench/selftest_c158*`).

## Part 2 (after Part 1 is green and quoted; independent of it): fp-77
`tools/gate_fp.py list` row fp-77: `checker:stage_prerun:is_vi_modifying` refused `bgrun --material -- py -u tools/bench/selftest_c157_innerface.py` because the script imports stagekit.
Read the row's note (`py tools/gate_fp.py list`, and `tools/bench/gate_fp_queue.jsonl` line 77), find the cause line in `stage_prerun.is_vi_modifying`, repair it so that a self-test
that only IMPORTS stagekit (no VI-modifying call at run time) is not VI-modifying, and a script that does call a modifying verb still is. Self-test both cases in
`selftest_c159_a4_1.py`. Then `py tools/gate_fp.py drain` for fp-77 with a note citing the repaired file:line and the self-test. If the repair would weaken the check for a real modifying
script, STOP, leave fp-77 open and report the reason as `OPEN:`. Note: fp-56's note says `VI_MOD_EXEMPT_PATHS` carries a sha256 pin of stage_prerun.py - re-pin it correctly if your edit moves
the pinned bytes (state how).

## Report `tools/bench/diag_c159_a4_1_facts.md` (<= 40 lines)
Edit list (file:line before/after), the self-test result lines, before/after suite counts, fp-77 outcome, then `OPEN:` lines. Facts only.
