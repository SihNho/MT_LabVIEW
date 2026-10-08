---
card: 150-a3-6
status: current
date: 2026-10-08
---
# Brief 150-a3-6 - RETRY of 150-a3-5 (s08 made, not run): cut BEFORE the unmeasured frame; offline

Everything in `tools/bench/cards/brief_150-a3-5.md` applies (steps 1-8, return conditions, report name `tools/bench/diag_c150_a3_6_facts.md`; no `--launch`, no tool/hook edit, no s07 file overwritten). Read `tools/bench/diag_c150_a3_5_facts.md` (8b3a3734) first.

## Why the retry, and the ONE change
150-a3-5 stopped at its own maker: the simulator (`tools/stagesim.py:1805-1807`, PD289(f)) will not simulate action 20 `p4_x_n2_order` because its target frame #29869 belongs to FS #29721, whose diagram has never been measured (the real graph reads it with err 1055 and no border, in the s04..s07 graph logs :296). That is a measurement gap, not a plan defect. Actions 1..19 of the whole-remainder cut (ops 166..190) passed every earlier maker check (X0, R, C2).
**Change: cap the cut so that NO action touching frame #29869 / FS #29721 is in s08** - i.e. the longest prefix of the formula cut that ends before action 20 and splits no `of` pair (<= 19 actions). Copy `prep_c150_a3_5_mk.py` -> `prep_c150_a3_6_mk.py` (a one-line cap; say which line), keep START 595.3, all other rules unchanged.
The remaining v18 ops (action 20 on) are NOT in s08; list them (op numbers) and state in one sentence that they need either a measurement of FS #29721's diagram or a later stage - do NOT decide that, do NOT touch `stagesim.py`.

## Then steps 2-8 of brief 150-a3-5 on the capped plan
Rebase, X10 after the rebase, pred with V18E-R' (`prep_c150_a3_6_pred.py` from the 150-a3-1 pred), recipes `stage_d1_ring_p4_s08v18.py` + `_scratch.py`, a sink gate per `wire_indicators` census row, licence by script, dry + prerun PASS, `--scratch-required` rc, invariants (also `diag_c150_a3_5_*` files unchanged except where you supersede them - say which). If the capped plan fails ANOTHER simulator or prerun gate, RETURN with the first failing line verbatim.
Quote: action count, op range, X10 margins at the capped cut, the first op NOT included, and whether the capped cut leaves any `of` pair or frame dependency open across the s08/s09 boundary (read from the sim, no inference).
