---
card: 161-a1-2
status: current
date: 2026-10-10
---
# Brief 161-a1-2 (assignment 161-1) - OFFLINE test debt left by 161-a1-1: re-pin one stale self-test, make the s4 self-test call the shared checkpoint rule, finish the suite re-runs

`labview: none`, no `--launch`, no `tools/hooks` edit, no env bypass. Read `tools/bench/diag_c161_a1_1_facts.md` (all of it) and `docs/script-writing.md`.
`tools/stagexec.py` is a4df7e15 (card 161-a1-1; do NOT edit it here). `stagesim` 95a162ba, `stagekit` 0b5bb678, `stage_prerun` 7605116f stay unchanged.

## Decision already taken (judgement PD393(a), applied by the assignment session) - do not ask
The rule is literally "every `delete_wire` op is a required checkpoint". p5s02b compiles delete_wire at ops 1, 4 and 8, so the set is (0,1,2,3,4,5,7,8,9,10): three extra reads, not two.
That is accepted here; the X10 MAIN <= 675 re-measure belongs to the next card (prerun). Nothing in this card touches the p5s02b pred / licence / EL / recipes.

## Do
1. `tools/bench/selftest_c157_innerface.py:72`: its `PINS` still pin `stagesim eb99c6ba` (stale since 160-a1-1; stagesim is 95a162ba). First MEASURE the current md5 of each pinned file
   (stagesim, addrcheck, plan_ring_p5s02a.json, step_15) and quote them; re-pin ONLY the md5s that differ, and the docstring line 28. Re-run the self-test; quote the pass/fail counts (previous: 12/1).
2. `tools/bench/selftest_stagexec_s4.py:163` hand-copies the old rule (BIND|last) on `plan_ring_p4_s01`. Replace the copy by a call to the shared rule in `tools/stagexec.py`
   (`checkpoint_ops` / `required_checkpoints`; read their signatures, do not guess) so the test no longer encodes the rule a second time (docs/script-writing.md). Run it BEFORE and AFTER the edit
   (the before-run is the measured B2 refusal of 161-a1-1's OPEN); quote counts both times. If after the edit a case fails for a reason other than the checkpoint set, report the line - do not loosen it.
3. Run `tools/bench/selftest_c156_b2_2_invcheck.py` (re-pinned to a4df7e15 by 161-a1-1) and quote pass/fail.
4. After steps 1-3, re-run `py tools/bench/selftest_c161_delckpt.py` (expect 11/0) and quote it.
5. Say whether `guard_peer` still blocks a following build-class command: quote the refusal verbatim if it does, or say "no block seen" (do not fake a command to find out; if a normal command of yours is refused, quote that). If it still blocks on a LOG
   that your re-run replaced with a passing one, report the block only; a peer review is owed only if the block names a failing record that stays failing. Hook false positive: `py tools/gate_fp.py log ...`.
6. Background anything slow under `py tools/bgrun.py --material --max-min N --log ... -- ...`.

## Report `tools/bench/diag_c161_a1_2_facts.md` (<= 30 lines, facts only)
current md5 of each pinned file; self-test counts before/after for c157_innerface, stagexec_s4, invcheck, delckpt; any block quoted; md5 UNCHANGED: stagexec a4df7e15, stagesim 95a162ba, stagekit 0b5bb678, stage_prerun 7605116f; `OPEN:` lines.
