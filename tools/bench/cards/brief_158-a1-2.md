# Brief 158-a1-2 (assignment 158-1): PD384(b) only - run-closing checkpoints, offline

Read first: `CLAUDE.md`, `docs/script-writing.md`, `tools/bench/cards/brief_158-a1-1.md` part (b) and the measure steps,
`tools/bench/diag_c158_a1_1_facts.md` (card 158-a1-1 stopped on part (a): no `Nodes[]` row exists for a LoopTunnel inner face,
so part (a) is NOT in this card; do not touch `loop_inner_face_route` or the `cfw` / `connect_nested_v1` act).
Base pins: stagexec 69b1a301, stagekit 0d8f6d25, stagesim eb99c6ba, addrcheck 207beb0d. `tools/bench/prep_c158_a1_1_before.log`
and `tools/bench/sim/ring_p5s02a_c158/before.json` are the stored BEFORE state and stay valid while those pins hold; reuse them,
do not repeat the 884 s baseline run. No LabVIEW, no hook edit, no recipe / plan / pred / licence / P5 file edit. Rule 1a: only how
stage tools ADDRESS a wire and what they PRINT changes.

## What to build (call existing functions, do not copy them)
Part (b) exactly as in brief_158-a1-1.md: `stagexec.checkpoint_ops` (`stagexec.py:2028`) puts the LAST op of each maximal run of
consecutive `move_in` ops in the set (BIND_KINDS ops, op 0 and the last op as now); `fate_lines` (`stagexec.py:2036`) for a run
takes the FATE lines of every `move_in` in the run from the run-closing read compared with the checkpoint read before the run
(format unchanged, `step=<n>` stays); a non-closing `move_in` no longer prints `FATE-UNREAD`; the Executor REFUSES before op 1
(ExecStop CHECKPOINT) a caller-supplied checkpoint set lacking the run-closing op of any `move_in` run.

## Measure
1. After the edit: the same plan-compile sweep as `prep_c158_a1_1_regress.py` (CALL it); every stored plan compiles to the SAME
   ops as `before.json`; suite counts equal `prep_c158_a1_1_before.log:9-21` except stated rule updates.
2. New `tools/bench/selftest_c158_runcheck.py` on recorded data (sim steps under `tools/bench/sim/ring_p5s02a/`): (i) p5s02a
   `checkpoint_ops` = (0,1,3,6,8,9,12,15,16,17); (ii) a set missing 12 or missing 17 is refused before op 1 (dry/sim backend);
   (iii) FATE lines of ops 10-12 come from the op-12 read and still give the six M3 wires; (iv) no FATE-UNREAD for a non-closing
   move_in.
3. Re-pin ONLY md5 strings in pinned self-tests that fail on the new stagexec/stagekit bytes; `selftest_c157_innerface.py`
   case (iv) (old every-move_in list) is UPDATED to the new rule and the change stated. Report counts for c155, c156, c157.
4. Report new md5s of stagexec / stagekit (stagesim, addrcheck, stage_prerun unchanged).

Facts file `tools/bench/diag_c158_a1_2_facts.md` (<= 40 lines, facts only, an `OPEN:` line per unresolved thing).
Return the standard <= 30-line summary. Failure budget 2.
