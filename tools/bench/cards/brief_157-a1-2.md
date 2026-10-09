# Brief 157-a1-2 (assignment 157-1): re-pin two self-tests, then dry + prerun + X10 of plan_ring_p5s02a on the new tool bytes, offline

Read first: `tools/bench/diag_c157_a1_1_facts.md` (card 157-a1-1 built the tool fix; its only suite change was two stagekit md5 pin gates),
`tools/bench/diag_c156_a2_1_facts.md` (the pre-check numbers on the old bytes, the commands, and what the launch gate wants), `CLAUDE.md`,
`docs/script-writing.md`. No LabVIEW, no hook edit, no recipe / plan / pred / licence edit.

## Part 1 - re-pin (the OPEN of card 157-a1-1)
`tools/bench/selftest_c156_passwire.py:161` and `tools/bench/selftest_c155_basecase_frame.py:206` pin stagekit `aec03c6c`. The edit was
PD381(d) and is intended; change ONLY that md5 string in each to the current stagekit md5 (`0d8f6d25...`, md5sum the file, do not copy from
this brief). Re-run both under `bgrun`: expect `selftest_c156_passwire` 20/0 and `selftest_c155_basecase_frame` 21/0. If either shows any
other failing gate, RETURN with the gate line - do not touch more than the pin.

## Part 2 - dry + prerun on the new bytes (stagexec 69b1a301, stagekit 0d8f6d25, stagesim eb99c6ba, addrcheck 207beb0d, stage_prerun 9decb20f)
Same commands as card 156-a2-1 (`diag_c156_a2_1_*.log` first lines), under `py tools/bgrun.py --max-min 10 --log tools/bench/diag_c157_a1_2_<name>.log -- ...`:
1. `py -u tools/stage_prerun.py --dry tools/recipes/stage_d1_ring_p5s02a.py` and the same for `..._scratch.py`.
2. `--prerun` for both. Quote: PASS counts, the X10 line (planned MAIN peak vs the 675 limit; Executor-only), X17, X14, and whether PB is
   PASS-UNVERIFIED. The checkpoint list the run uses must contain 10, 11, 12 (quote it).
3. `--scratch-required tools/recipes/stage_d1_ring_p5s02a.py` (rc 3 is the expected answer).
4. The launch gate on the FULL command, not the bare path (the bare-path `--check-launch` is vacuous, `diag_c156_a2_1_facts.md`): quote what
   the gate says for `py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c157_p5s02a_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02a_scratch.py`
   WITHOUT running it (use the stage_prerun function the guard uses; name the function and line). Expected: refused only for the PB
   PASS-UNVERIFIED reason, released by `DRY-UNVERIFIED-OK: PB frame-keyed cdiff` in the bound card plus `--unverified-card`. State the exact
   label prefix the refusal text asks for.
5. If planned MAIN is above 675: do NOT re-cut. Report the number and the two nearest group boundaries from `plan_ring_p5s02r_all.json`
   (judgement owns PD379(c)).
Also report whether the prior-art review is still valid for the new bytes (the gate's own verdict, not a guess).

## Report `tools/bench/diag_c157_a1_2_facts.md` (<= 40 lines)
Pins before/after, the two self-test counts, dry/prerun/scratch-required/launch-gate lines with file:line, X10 numbers, the label prefix,
md5 of every file changed. `OPEN:` line per unresolved thing. Facts only. Failure budget 2.
