---
card: 169-a2-3
status: current
date: 2026-10-12
---
# Brief 169-a2-3 (assignment 169-2) - PD406(f): finish the drain of fp-100 and fp-99 after the fp-98 fix was reverted (retry of 169-a2-2)

Plan: `docs/d1/ring-p6.md` PD406(f). Card 169-a2-2 (`tools/bench/diag_c169_a2_2_facts.md`) fixed fp-100 (`tools/stage_prerun.py:202-208,278`) and fp-99 (`tools/protocol.py:1199-1205`) and
self-tested them, then returned at the FIRST unexpected result: its fp-98 edit (X5 no longer counts `remove_bad_wires*` as a wiring op) made `selftest_stage_prerun_c115c.py` T8
("unplanned remove_bad_wires still a wiring op -> FAIL", card 115-3) worse, 9/1 -> 8/2. It reverted that edit (c115c back to 9/1). fp-98 stays OPEN and this card does NOT touch it:
X5's treatment of an unplanned RBW is a pinned, deliberate rule (115-3), and the 167 script already passes X5 through its label `rbw_method410`
(`diag_c169_a2_2_prerun167_before.log:56,67`). Changing the pinned rule is the judgement session's.

## Steps (stop at the first unexpected result and RETURN with the facts)
1. Hash the card inputs (they already carry the post-169-a2-2 md5s of `stage_prerun.py` db81a1d3 and `protocol.py` 055870f3). Drift = RETURN. `py tools/protocol.py requires <this card>` PASS.
2. `tools/bench/selftest_c169_fp98_100.py`: A1-A4 test the reverted fp-98 fix and fail on the current code. Replace them (editor tool, in place) by checks of what is true now: the 167 script
   (`tools/bench/diag_c167_a1_1_rbw.py`) passes X5 through its label (ops 0) and a plan-less extra `connect_wire` op still FAILS X5; keep B1-B4 and C1-C2. The file ends with its `RESULT {...}` line and passes 100%.
3. Re-run the existing self-tests the two edits can touch, ONE AT A TIME through `py tools/bgrun.py --max-min 12 --log <file> -- <cmd>` (no parallel runs this time, so the timeouts of 169-a2-2 do not repeat):
   `selftest_stage_prerun_c115c.py`, `_c115a`, `selftest_c148_prerun_fp.py`, `_headcmp_79-6`, `_stageplan`, `_c106e`, `_c114`, `_c114d`, `_c128b`, `_c103`, `_c106c`, `tools/selftest_protocol*.py` (list them with Glob) and the two
   that guard `protocol.check_command` if any (grep `check_command` in `tools/bench/selftest_*.py`). Compare with the `before` logs of 169-a2-2 (`diag_c169_a2_2_before_*.log`); a count that got worse = revert that ONE edit by the
   editor tool, record it, and RETURN. A self-test that was already failing or timing out before the edits is quoted as such, not as a regression (c103 was 0/4 in 169-a2-2's before run).
4. Drain with `py tools/gate_fp.py` per its usage text: fp-100 and fp-99, one call each, citing `selftest_c169_fp98_100.py` and the patch file:line. fp-98, fp-101, fp-102 and every hook entry stay as they are.
5. Facts `tools/bench/diag_c169_a2_3_facts.md` (<= 40 lines, every number with file:line): self-test counts per file before/after, the drain calls and their output, fp-98's reason for staying open (one line), a `skipped:` line.

## Not in this card
No fp-98 change, no X5 change, no T8 change, no tools/hooks/** edit, no recipe, STATUS, INDEX, plan or memory_model edit, no LabVIEW, no new option.
