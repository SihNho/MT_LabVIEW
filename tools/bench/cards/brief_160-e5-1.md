---
card: 160-e5-1
status: current
date: 2026-10-10
---
# Brief 160-e5-1 (assignment 160-2) - OFFLINE retry of 160-e4-1: re-pin the stagekit md5 in the suites/diags that pin it (1441bb4c -> 0b5bb678)

`labview: none`, no `tools/hooks` edit, no plan / pred edit, **no `tools/stagekit.py` edit** (it is final: 0b5bb678169d659feed7408648a63354; the gate_l0 predicate was added by 160-e4-1, `diag_c160_e4_1_facts.md`).

## Why
160-e4-1 passed its predicate + self-test (14/0) but five regression suites fail ONLY on a pinned stagekit md5 (`diag_c160_e4_1_facts.md:20-21`): basecase_frame 21/0 -> 20/1, b2_2_invcheck 20/0 -> 18/2,
passwire 20/0 -> 19/1, delwire 20/0 -> 18/2, regface 12/0 -> 10/2. The tool change is the one function; the pins say "this exact stagekit was reviewed". Re-pinning is the standard consequence of a reviewed tool edit
(precedent: `selftest_c156_b2_2_invcheck.py:96` "re-pinned 160-f2-1 from aec03c6c"; `selftest_c160_delwire.py:17`). Not a loosening: the pin value changes, the check does not.

## Do
1. Replace the stagekit pin `1441bb4c` (and the full md5 `1441bb4ca75eb5a59afaa3555690db37` in the exact GATE text) by `0b5bb678` / `0b5bb678169d659feed7408648a63354` in exactly these places (nothing else; a pin of another tool stays):
   `selftest_c155_basecase_frame.py:28,207`; `selftest_c156_b2_2_invcheck.py:96,106`; `selftest_c156_passwire.py:34,164`; `selftest_c160_delwire.py:17,51` (docstring line: append "160-e5-1 re-pinned 1441bb4c -> 0b5bb678", keep the history text);
   `selftest_c160_regface.py:43`; plus the pin-only helpers `diag_c160_h1_1_check.py:24`, `diag_c160_g1_1.py:11,27`, `diag_c160_b2_1_md5.py:13`, `prep_c160_b3_1_mk.py:46`, `prep_c160_b1_1_mk.py:39` (a comment like
   "re-pinned 160-e5-1 from 1441bb4c" on the changed line is enough; one short line, no prose).
   Do NOT touch `prep_c160_c3_1_*` (card 160-c3-2 owns them) or `selftest_c160_l0stem*`.
2. Re-run exactly the five changed suites with the commands their last logs used (look at `tools/bench/diag_c160_e4_1_after.log` / `selftest_c160_l0stem_regress.py` for how `run_suite` calls them; logs to `tools/bench/selftest_*_c160_e5_1.log`).
   Prediction contract: basecase_frame (0,21,0), invcheck (0,20,0), passwire (0,20,0), delwire (0,20,0), regface (0,12,0) - **identical to the pre-edit counts**. A count that differs is a FAIL: report the first FAIL line, do not loosen.
3. Re-run `selftest_c160_l0stem.py` (14/0) and `selftest_c160_stagemap.py` (5/0) once as a final check on the final bytes.
4. md5s: stagekit 0b5bb678 (unchanged), stagesim 95a162ba, stagexec ddf23a31, stage_prerun 7605116f unchanged; no plan_ring_* / hooks file edited.

## Report `tools/bench/diag_c160_e5_1_facts.md` (<= 20 lines, facts only)
Per file: the line changed (old -> new); the five RESULT lines (rc,pass,fail) next to the pre-edit counts; md5 of each edited file; unchanged md5 list; `OPEN:` lines (any remaining pin of 1441bb4c found by grep outside `prep_c160_c3_1_*`).
