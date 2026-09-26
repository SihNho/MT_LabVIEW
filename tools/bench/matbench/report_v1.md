# matbench v1 - Opus 5.5 effort ladder (card chat-N3)

Mechanical scores only (score.py score_cell_v1). Cell = score / minutes / usd, repeats r1 ; r2. Detail: results_v1.json.

| task | claude-opus-5-5/low | claude-opus-5-5/medium | claude-opus-5-5/high | claude-opus-5-5/max |
|---|---|---|---|---|
| T1 | 0 / 0.29 min / $0.58 ; 0 / 0.29 min / $0.56 | 0 / 1.28 min / $0.93 ; 0 / 0.77 min / $0.72 | 0 / 1.4 min / $1.11 ; 0 / 0.99 min / $1.06 | 1 / 5.23 min / $2.57 ; 1 / 7.43 min / $3.25 |
| T2 | 1 / 0.73 min / $0.79 ; 0 / 0.82 min / $0.81 | 1 / 1.4 min / $1.18 ; 1 / 0.92 min / $0.89 | 1 / 2.16 min / $1.52 ; 1 / 2.17 min / $1.73 | 0 / 7.52 min / $3.24 ; 1 / 8.85 min / $3.77 |
| T3 | 0 / 1.57 min / $1.11 ; 0 / 1.45 min / $1.11 | 0 / 5.62 min / $1.36 ; 1 / 1.94 min / $1.29 | 1 / 3.31 min / $1.95 ; 1 / 3.28 min / $1.94 | 1 / 9.12 min / $3.94 ; 1 / 6.45 min / $2.76 |
| T5 | 1 / 2.55 min / $1.37 ; 1 / 2.43 min / $1.04 | 1 / 3.73 min / $1.76 ; 1 / 3.47 min / $1.68 | 1 / 5.46 min / $2.31 ; 1 / 4.96 min / $2.09 | 1 / 11.97 min / $5.86 ; 1 / 12.49 min / $4.68 |
| T6 | 1 / 0.47 min / $0.54 ; 1 / 0.53 min / $0.56 | 1 / 0.63 min / $0.65 ; 1 / 0.6 min / $0.62 | 1 / 1.05 min / $0.80 ; 1 / 0.81 min / $0.72 | 1 / 4.24 min / $1.71 ; 1 / 2.97 min / $1.34 |

| condition | cells | score sum | mean score | mean partial | mean minutes | total usd | timeouts | dispatches |
|---|---|---|---|---|---|---|---|---|
| claude-opus-5-5/low (material) | 10 | 5 | 0.500 | 0.835 | 1.11 | 8.48 | 0 | 0 |
| claude-opus-5-5/medium (material) | 10 | 7 | 0.700 | 0.840 | 2.04 | 11.08 | 0 | 0 |
| claude-opus-5-5/high (material) | 10 | 8 | 0.800 | 0.860 | 2.56 | 15.24 | 0 | 0 |
| claude-opus-5-5/max (material) | 10 | 9 | 0.900 | 0.935 | 7.63 | 33.11 | 0 | 0 |

## Repeat variance per task

within = the largest score (minutes) range between the two repeats of one condition; between = range of the per-condition mean scores. A between-range not larger than the within-range is not distinguishable from repeat noise.

| task | within score range | within minutes range | between mean-score range | per-condition mean score |
|---|---|---|---|---|
| T1 | 0 | 2.2 | 1.0 | low 0, medium 0, high 0, max 1 |
| T2 | 1 | 1.33 | 0.5 | low 0.5, medium 1, high 1, max 0.5 |
| T3 | 1 | 3.68 | 1.0 | low 0, medium 0.5, high 1, max 1 |
| T5 | 0.0 | 0.52 | 0.0 | low 1, medium 1, high 1, max 1 |
| T6 | 0 | 1.27 | 0.0 | low 1, medium 1, high 1, max 1 |

## Facts

Per condition (mean score / mean minutes / total usd): low 0.500 / 1.11 / $8.48; medium 0.700 / 2.04 / $11.08; high 0.800 / 2.56 / $15.24; max 0.900 / 7.63 / $33.11. Tasks whose between-condition score range exceeds the within-condition repeat range: T1; tasks with the same mean score under every effort: T5, T6. T3 uid group ['25240','25344','25382'] hit per cell: low r1 miss, low r2 miss, medium r1 miss, medium r2 hit, high r1 hit, high r2 hit, max r1 hit, max r2 hit. v0 Fable cells under the v1 scorer (mean score / mean minutes / total usd): fable/low 1.000 / 3.48 / $17.59; fable/medium 0.800 / 2.76 / $19.29.

## Validity notes (measured)

- T4 DROPPED from v1 (brief item 2: 'if still BLOCKED after one fix attempt, drop'). Fix applied: every tracked file of the T4 worktree set to its last-commit time (matbench.restore_mtimes; priorart_cycle14.log now 2026-09-20 20:19, older than the card commit minus guard_cycle's 30 h window, selftest G10), files copied from the card commit 33ea0b3 set to that commit's time. Verification cell (Opus 5.5/medium, runs_T4env/T4_c1_r1, 1.1 min) was still BLOCKED, now by two other mtime gates: stop_record rejects the FIXED line because docs/d1-loop12-17-split-plan.md (commit time 22:32) is older than the prior-art review (23:47), and guard_cycle.py:497 refuses the recipe because its commit time 00:14 is newer than that review. Commit times are not the original edit times, so no commit-time stamping can reproduce the order the real gates saw.
- T5 is scored v1-style: score = t5_struct jaccard of the produced plan's wiring delta vs the reference plan (1 when equal), computed per cell in its own worktree (matbench.post). The empty plan scores 0.0 (t5_struct.log).
- T1 is scored v1-style: the behaviour group (result card cost.labview_runs == 0 and no allowed logged command naming LabVIEW.exe) replaced the wording group; every v1 and every re-scored v0 T1 card has labview_runs 0. '9 of 11' is partial-only. The workaround rule (status PASS, or artefacts listed while the FlatSequence group is missed) flagged T1 medium r1 and high r1 (offline group maps written as artefacts); both also missed the FlatSequence group, so the score is 0 either way.
- Scorer fix during v1: the timeout flag was a substring test on the whole cell log; both T5 high cells QUOTED 'BGRUN TIMEOUT' in their result text and were flagged TIMEOUT although bgrun ended rc=0 after 331 s / 301 s. v1 now matches only a line starting 'BGRUN TIMEOUT'. The table above is the re-score with that fix.
- LabVIEW pids new during batches T2 (26144), T3 (25880), T5 (13684), T6 (23860) belong to the live cycle-94 runner in the main checkout: tools/bench/diag_c94_abba.py (BGRUN START 11:24:43, a multi-leg real run) prints 'pid': 26144, 25880, 9652, 13684 in tools/bench/diag_c94_abba.log; its leg6 started at 12:22 inside the T6 batch window 12:18-12:23 (the log had not yet printed that leg's pid when this report was written). Replay cells: 994 logged tool calls, 0 cell_guard refusals, 0 commands naming LabVIEW.exe.
- Cells ran with --permission-mode acceptEdits under the replay card (labview none, peers []); dispatches 0 in every cell. n = 2 per task x condition; a task whose between-condition score range does not exceed its within-condition repeat range is not separable from repeat noise at this n.
- Cost: 40 cells, $67.91 cumulative (guard $120 never reached, nothing skipped); wall 72 min for the batch (bgrun 4339 s).

## Notes per run below score 1

- T1 claude-opus-5-5/low r1: missed: facts_any ['FlatSequence', 'flat-sequence', 'frame-move'] | partial-only missed: partial_only ['9 of 11', '9/11']
- T1 claude-opus-5-5/low r2: missed: facts_any ['FlatSequence', 'flat-sequence', 'frame-move'] | partial-only missed: partial_only ['9 of 11', '9/11']
- T1 claude-opus-5-5/medium r1: workaround (designed around the missing verb). missed: facts_any ['FlatSequence', 'flat-sequence', 'frame-move'] | partial-only missed: partial_only ['9 of 11', '9/11']
- T1 claude-opus-5-5/medium r2: missed: facts_any ['FlatSequence', 'flat-sequence', 'frame-move'] | partial-only missed: partial_only ['9 of 11', '9/11']
- T1 claude-opus-5-5/high r1: workaround (designed around the missing verb). missed: facts_any ['FlatSequence', 'flat-sequence', 'frame-move'] | partial-only missed: partial_only ['9 of 11', '9/11']
- T1 claude-opus-5-5/high r2: missed: facts_any ['FlatSequence', 'flat-sequence', 'frame-move'] | partial-only missed: partial_only ['9 of 11', '9/11']
- T2 claude-opus-5-5/low r2: missed: facts_any ['N[74]', 'index out of range', 'Nodes[] order', 'index shift']
- T2 claude-opus-5-5/max r1: missed: facts_any ['N[74]', 'index out of range', 'Nodes[] order', 'index shift']
- T3 claude-opus-5-5/low r1: missed: facts_any ['25240', '25344', '25382']
- T3 claude-opus-5-5/low r2: missed: facts_all ['1 source', 'one source', '1 sink']; facts_any ['25240', '25344', '25382']
- T3 claude-opus-5-5/medium r1: missed: facts_any ['25240', '25344', '25382']
- LabVIEW pids T1: before [24452] after [] new []
- LabVIEW pids T2: before [] after [26144] new [26144]
- LabVIEW pids T3: before [26144] after [25880] new [25880]
- LabVIEW pids T5: before [25880] after [13684] new [13684]
- LabVIEW pids T6: before [13684] after [23860] new [23860]

## v0 Fable cells re-scored with the v1 scorer (runs/ of chat-N2, one repeat each)

| task | fable/low | fable/medium |
|---|---|---|
| T1 | 1 / 2.99 min / $3.90 | 0 / 3.24 min / $3.25 |
| T2 | 1 / 3.21 min / $3.12 | 1 / 3.72 min / $4.55 |
| T3 | 1 / 3.75 min / $2.96 | 1 / 4.13 min / $3.87 |
| T5 | 1 / 5.83 min / $5.03 | 1 / 1.72 min / $5.34 |
| T6 | 1 / 1.64 min / $2.57 | 1 / 0.98 min / $2.28 |

| condition | cells | score sum | mean score | mean minutes | total usd |
|---|---|---|---|---|---|
| fable/low | 5 | 5 | 1.000 | 3.48 | 17.59 |
| fable/medium | 5 | 4 | 0.800 | 2.76 | 19.29 |
- v0 T1 fable/medium: workaround (designed around the missing verb). missed: facts_any ['FlatSequence', 'flat-sequence', 'frame-move'] | partial-only missed: partial_only ['9 of 11', '9/11']
