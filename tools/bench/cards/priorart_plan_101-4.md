# Card 101-4 - edit of tools/recipes/stage_d1_disp.py before its one authorised re-run (rung 1 of card 101-3)

The recipe (reviewed as `novel` in archive/peer/2026-09-26-priorart-c100-6-disp-stage.md, released for sha ab062905e941)
ran r3 and r4 in cycle 101. r4 stopped at op 4 (move_in #8775, a DigitalNumericConstant) with STEP-DIFF
dangling_sim_only [8753] (tools/bench/stage_d1_disp_r4.log:89-90). The card asks for ONE more run in RECORD MODE.

## What changed in the recipe (nothing else)
1. `stagexec.Executor(PLAN, be, checkpoints=cps, record=True)`:
   - cps = every binding op (create/tunnel/add_sr, stagexec.BIND_KINDS) + ops 4, 5, 12 + the last op.
     This is the existing PD193(a) checkpoint mechanism (card 86-4, stagexec.Executor docstring; used by the L2-A1 run
     tools/bench/stage_d1_l2a1_86-5.log, peak 638 MB). Reason: every-op whole-VI reads cost ~3.4 MB each
     (tools/bench/meter_l2a1_86c.log METER SUMMARY, error 2 at 695 MB) and r4 was at 594.6 MB after op 4 of 47
     (tools/bench/stage_d1_disp_r4.log:88), so a read after every op would cross MEMSTOP 700.
   - record=True is NEW in stagexec (card 101-4): a STEP-DIFF is appended to Executor.diffs and the run continues on the
     unsaved scratch; binding/addressing/op-error/MEMSTOP stops still stop, Executor.cur names the op. Self-test
     tools/bench/selftest_stagexec_c101-4.log 76/0 (T39-T39d).
2. After the run: if any diff -> every diff is printed (op, ids, ops since the last read, new entries), the E3
   computation_diff of the LAST checkpoint read is printed as information (pure Python, no extra LabVIEW read), ExecState
   is read, E1 FAILS fatally and NOTHING is saved. If no diff -> the unchanged W1 / E2 / E3 / save path.
3. The E3 cdiff code moved into a helper `cdiff()` (same statements as before, stagexec.lv_run :2004-2008 origin).
4. Stage task label "card 101-4"; docstring states the above.

## Change since review archive/peer/2026-09-27-priorart-c101-4-disp-record.md (novel, sha a3b93ec1f3d0)
The pre-run failed X6 (tools/bench/stage_d1_disp_prerun6.log: "uids [(600, 82)]"). The slice bound `[:600]` in a
fact-formatting line equals a node uid of the input graph. The three slice bounds in the new record-mode fact lines
(`[:600]`, `[:900]`, `[:1200]`) now all read `[:CUT]` (CUT = 10 ** 3, already defined at the top of the recipe). Nothing
else changed. Offline checks of these bytes (tools/bench/diag_c101b_syntax3.log): the file parses, is 120 lines, has no
unbound name, and passes stage_prerun.lint (X6) with uids [] and names [].

## The plan it executes
tools/bench/sim/disp/plan_disp.json re-simulated (md5 b535071e...) from the unchanged stageplan_disp_r4_open.json with
one stagesim model change: `only_source` (tools/stagesim.py only_source_fate / _apply_only_source): a moved CONSTANT that
was the only source of a single-sink cut wire takes the wire along (r4 #8775 -> 8753 read unwired); a node source keeps
the sourceless half-wire (diag_c71_l7_1a_tunnels.log:60,64,70). Replay vs r4 k1-k4 equal (tools/bench/diag_c101b_resim.log).
