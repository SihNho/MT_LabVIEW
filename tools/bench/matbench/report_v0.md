# matbench v0 - material-model replay (card chat-N2)

Mechanical scores only (score.py). Cell = score (partial) / minutes / usd. Detail: results_v0.json.

| task | claude-opus-5-5/medium | fable/low | fable/medium |
|---|---|---|---|
| T1 | 0 (0.40) / 0.58 min / $0.67 | 0 (0.60) / 2.99 min / $3.90 | 0 (0.00) / 3.24 min / $3.25 |
| T2 | 1 (1.00) / 1.52 min / $1.13 | 1 (1.00) / 3.21 min / $3.12 | 1 (1.00) / 3.72 min / $4.55 |
| T3 | 0 (0.80) / 2.71 min / $1.56 | 1 (1.00) / 3.75 min / $2.96 | 1 (1.00) / 4.13 min / $3.87 |
| T4 | 0 (0.75) / 1.0 min / $0.93 | 0 (0.25) / 3.55 min / $3.61 | 0 (0.25) / 1.98 min / $2.32 |
| T5 | 1 (1.00) / 3.11 min / $1.48 | 1 (1.00) / 5.83 min / $5.03 | 1 (1.00) / 1.72 min / $5.34 |
| T6 | 1 (1.00) / 0.79 min / $1.00 | 1 (1.00) / 1.64 min / $2.57 | 1 (1.00) / 0.98 min / $2.28 |

| condition | score | partial | minutes | usd | timeouts | dispatches |
|---|---|---|---|---|---|---|
| claude-opus-5-5/medium (material) | 3/6 | 4.95 | 9.7 | 6.76 | 0 | 0 |
| fable/low (material-fable-low) | 4/6 | 4.85 | 21.0 | 21.20 | 0 | 0 |
| fable/medium (material-fable-medium) | 4/6 | 4.25 | 15.8 | 21.61 | 0 | 0 |

## Validity notes (measured)

- T4 is ENVIRONMENT-INVALID in v0: all 6 T4 cells (2 batches) ended BLOCKED by the replay worktree, not by the task. Batch 1 (runs_invalid/T4_env_v0): recipe md5 7fb6223f at base != card 1098a443 and the gate releases (prior-art FIXED, outcome review) were committed WITH the card. Batch 2 (runs/T4_c*): guard_cycle.py:404-419 refused the pre-run because tools/bench/priorart_cycle14.log (a dead 2026-09-16 dispatch, no BGRUN END) got the checkout mtime, and the gate keys on mtime. All 3 models named that cause; failure budget 2 spent, not rerun.
- T5's truth metric (end computation_diff rows == the reference's) is DEGENERATE on this base: the reference ends on the 15 rows the base graph already has (stagesim first_divergent n=0 'base'), so an empty plan meets it. t5_struct.py compares the wiring delta instead: reference = 15 edges added / 17 removed; the empty plan scores jaccard 0.0; all three produced plans are structurally EQUAL to the reference (jaccard 1.0).
- T1's facts_all group ['no LabVIEW run', 'nothing opened', 'not opened', '0 LabVIEW'] was hit by no cell although none ran LabVIEW (cards say e.g. 'nothing built, nothing run', 'no LabVIEW'); the group's wording, not the behaviour, decided it.
- T1 c2 'workaround' flag fired because the card listed an unrun diagnostic script (tools/bench/diag_c89_t0map.py) while missing the FlatSequence group; its score was 0 on missed groups either way.
- LabVIEW pids that appeared during batches T3 (25904) and T4-rerun (9300) belong to the live cycle-92 runner in the main checkout (tools/bench/diag_c92_clfn_thread.log BGRUN START 08:52:30, diag_c92b_anythread.log 09:08:33, inside those batch windows). Replay cells: 540 logged tool calls, 0 cell_guard refusals, no allowed command that executes gscript/stagekit/COM/lv_gui/peer (only grep/ls/sed naming them).
- First v0 launch (08:41) was KILLED after T1 because cell_guard scanned every .py NAMED in a command (grep/wc) and refused 2 harmless reads; fixed to scan only .py in execution position (selftest G6) and relaunched; the killed cells were deleted, not scored.
- Cells run with --permission-mode acceptEdits (cycle_runner.py:1008 shape): some Bash forms (md5sum on claudeDev paths, bgrun with a long foreground timeout) were refused by the permission layer, the same for every condition.

T5 structure vs reference (t5_struct.py, not a score group): c0 equal=True jaccard=1.0; c1 equal=True jaccard=1.0; c2 equal=True jaccard=1.0

## Notes per 0-score run

- T1 c0 (claude-opus-5-5/medium): missed: facts_all ['no LabVIEW run', 'nothing opened', 'not opened', '0 LabVIEW']; facts_any ['FlatSequence', 'flat-sequence', 'frame-move']; facts_any ['9 of 11', '9/11']
- T1 c1 (fable/low): missed: facts_all ['no LabVIEW run', 'nothing opened', 'not opened', '0 LabVIEW']; facts_any ['9 of 11', '9/11']
- T1 c2 (fable/medium): workaround (designed around the missing verb). missed: facts_all ['no LabVIEW run', 'nothing opened', 'not opened', '0 LabVIEW']; facts_any ['FlatSequence', 'flat-sequence', 'frame-move']; facts_any ['9 of 11', '9/11']
- T3 c0 (claude-opus-5-5/medium): missed: facts_any ['25240', '25344', '25382']
- T4 c0 (claude-opus-5-5/medium): missed: facts_any ['X1']
- T4 c1 (fable/low): missed: facts_all ['8/0', 'PASS 8']; facts_any ['graph_k_80_owners']; facts_any ['X1']
- T4 c2 (fable/medium): missed: facts_all ['8/0', 'PASS 8']; facts_any ['graph_k_80_owners']; facts_any ['X1']
- LabVIEW pids T6: before [23988] after [23988] new []
- LabVIEW pids T1: before [25728] after [25728] new []
- LabVIEW pids T2: before [25728] after [25728] new []
- LabVIEW pids T3: before [25728] after [25904] new [25904]
- LabVIEW pids T5: before [] after [] new []
- LabVIEW pids T4: before [] after [9300] new [9300]
