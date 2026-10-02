# decbench - Sonnet 5.5 vs Opus 5.5, cloud run (Linux port, 2026-10-02)

Facts only. 10 known-answer cases x 3 arms x 2 repeats, --par 6. Arms: H = Opus 5.5 high; SH = Sonnet 5.5 high; SMX = Sonnet 5.5 max.
Score per arm-run = mean(must_hit) - 0.5 x max(forbidden), floored at 0; bonus mean beside it, never added. blind = one Opus 5.5 high scorer cell per case (answer key + rubric texts, labels shuffled, arm/model hidden); mech = rubric regexes. usd / min = per arm-run (PAR = sum of its 4 cells; min = wall clock of the arm-run).
Spent $64.99 (arm-runs $63.41 + blind scorers $1.57). Valid arm-runs 60, invalid 0.

## Per category x arm

| category | arm | n | blind mean | mech mean | bonus (blind) | usd / run | min / run | repeat spread (blind) |
|---|---|---|---|---|---|---|---|---|
| steering | H | 6 | 0.67 | 0.67 | 0.50 | 0.81 | 1.0 | 0.00 |
| steering | SH | 6 | 0.38 | 0.50 | 0.42 | 0.37 | 0.6 | 0.08 |
| steering | SMX | 6 | 0.67 | 0.67 | 0.50 | 2.96 | 10.3 | 0.00 |
| troubleshooting | H | 6 | 0.67 | 0.42 | 0.67 | 0.60 | 1.3 | 0.17 |
| troubleshooting | SH | 6 | 0.42 | 0.50 | 0.17 | 0.31 | 0.8 | 0.33 |
| troubleshooting | SMX | 6 | 0.88 | 0.67 | 0.75 | 2.39 | 10.5 | 0.08 |
| peer review | H | 8 | 0.67 | 0.73 | 0.50 | 0.47 | 0.9 | 0.12 |
| peer review | SH | 8 | 0.52 | 0.58 | 0.44 | 0.26 | 0.6 | 0.00 |
| peer review | SMX | 8 | 0.98 | 0.83 | 0.88 | 1.62 | 6.9 | 0.04 |

## All cases x arm (blind r1 ; r2 | mech r1 ; r2 | usd mean | min mean)

| case | H | SH | SMX |
|---|---|---|---|
| S1-pool-overload | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.99 &#124; 1.3 | 0.00 ; 0.25 &#124; 0.00 ; 1.00 &#124; $0.47 &#124; 0.7 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $3.41 &#124; 11.4 |
| S2-display-loop | 0.00 ; 0.00 &#124; 0.00 ; 0.00 &#124; $0.77 &#124; 0.9 | 0.00 ; 0.00 &#124; 0.00 ; 0.00 &#124; $0.36 &#124; 0.7 | 0.00 ; 0.00 &#124; 0.00 ; 0.00 &#124; $3.30 &#124; 11.8 |
| S3-disp-resplit | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.68 &#124; 0.8 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.29 &#124; 0.5 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $2.16 &#124; 7.7 |
| T1-looseends-pin | 0.25 ; 0.25 &#124; 0.50 ; 0.00 &#124; $0.73 &#124; 1.8 | 0.50 ; 0.50 &#124; 0.50 ; 0.00 &#124; $0.36 &#124; 1.2 | 0.50 ; 0.75 &#124; 0.50 ; 0.50 &#124; $4.14 &#124; 19.1 |
| T2-constvalue-void | 0.75 ; 1.00 &#124; 0.50 ; 0.50 &#124; $0.56 &#124; 1.0 | 0.00 ; 0.75 &#124; 0.00 ; 1.00 &#124; $0.32 &#124; 0.7 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $1.21 &#124; 5.3 |
| T3-handles-gate | 0.75 ; 1.00 &#124; 0.50 ; 0.50 &#124; $0.51 &#124; 1.1 | 0.25 ; 0.50 &#124; 1.00 ; 0.50 &#124; $0.25 &#124; 0.5 | 1.00 ; 1.00 &#124; 0.50 ; 0.50 &#124; $1.81 &#124; 7.0 |
| R1-guisave-foreground | 0.00 ; 0.50 &#124; 0.00 ; 0.50 &#124; $0.75 &#124; 1.5 | 0.00 ; 0.00 &#124; 0.00 ; 0.00 &#124; $0.30 &#124; 0.7 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $1.47 &#124; 5.9 |
| R2-fsit-writer | 0.75 ; 0.75 &#124; 1.00 ; 1.00 &#124; $0.45 &#124; 0.7 | 0.25 ; 0.25 &#124; 0.50 ; 0.50 &#124; $0.27 &#124; 0.6 | 1.00 ; 1.00 &#124; 0.50 ; 0.50 &#124; $1.53 &#124; 5.6 |
| R3-chat-synthesis | 0.67 ; 0.67 &#124; 0.67 ; 0.67 &#124; $0.36 &#124; 0.6 | 0.83 ; 0.83 &#124; 0.67 ; 1.00 &#124; $0.29 &#124; 0.6 | 1.00 ; 0.83 &#124; 1.00 ; 0.67 &#124; $0.98 &#124; 4.1 |
| R4-clean-r2pin | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.32 &#124; 0.8 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.17 &#124; 0.6 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $2.50 &#124; 12.0 |

## Per arm totals

| arm | n | blind mean | mech mean | usd total | usd / run | min / run | turns / run | tool calls / run | timeouts |
|---|---|---|---|---|---|---|---|---|---|
| H | 20 | 0.667 | 0.617 | 12.21 | 0.61 | 1.1 | 8.8 | 7.8 | 0 |
| SH | 20 | 0.446 | 0.533 | 6.17 | 0.31 | 0.7 | 8.7 | 7.6 | 0 |
| SMX | 20 | 0.854 | 0.733 | 45.04 | 2.25 | 9.0 | 41.5 | 40.4 | 0 |

## Peer review: defect hits (R1-guisave-foreground, R2-fsit-writer, R3-chat-synthesis) and clean-case false alarms (R4-clean-r2pin)

Defect hit = blind must-hit mean of the arm-run (0..1); full hit = every must_hit item scored 1 by the blind scorer; accepted = forbidden item (DEFECT none/minor) committed (blind >= 0.5). False alarm on the clean case = its forbidden item (DEFECT: blocker) committed (blind >= 0.5; mech in brackets).

| arm | defect must-hit mean (blind) | full hits / runs | accepted-as-fine / runs | clean-case false alarms / runs (mech) |
|---|---|---|---|---|
| H | 0.56 | 0 / 6 | 0 / 6 | 0 / 2 (0) |
| SH | 0.36 | 0 / 6 | 0 / 6 | 0 / 2 (0) |
| SMX | 0.97 | 5 / 6 | 0 / 6 | 0 / 2 (0) |

Per defect case, blind must-hit mean per arm:

| case | H | SH | SMX |
|---|---|---|---|
| R1-guisave-foreground | 0.25 | 0.00 | 1.00 |
| R2-fsit-writer | 0.75 | 0.25 | 1.00 |
| R3-chat-synthesis | 0.67 | 0.83 | 0.92 |

## Discriminating cases (blind score)

within = the largest |r1 - r2| over arms; between = range of the per-arm mean scores. A case whose between is not larger than its within is not distinguishable from repeat noise.

| case | within | between | discriminates | per-arm mean |
|---|---|---|---|---|
| S1-pool-overload | 0.25 | 0.88 | yes | H 1.00, SH 0.12, SMX 1.00 |
| S2-display-loop | 0.00 | 0.00 | no | H 0.00, SH 0.00, SMX 0.00 |
| S3-disp-resplit | 0.00 | 0.00 | no | H 1.00, SH 1.00, SMX 1.00 |
| T1-looseends-pin | 0.25 | 0.38 | yes | H 0.25, SH 0.50, SMX 0.62 |
| T2-constvalue-void | 0.75 | 0.62 | no | H 0.88, SH 0.38, SMX 1.00 |
| T3-handles-gate | 0.25 | 0.62 | yes | H 0.88, SH 0.38, SMX 1.00 |
| R1-guisave-foreground | 0.50 | 1.00 | yes | H 0.25, SH 0.00, SMX 1.00 |
| R2-fsit-writer | 0.00 | 0.75 | yes | H 0.75, SH 0.25, SMX 1.00 |
| R3-chat-synthesis | 0.17 | 0.25 | yes | H 0.67, SH 0.83, SMX 0.92 |
| R4-clean-r2pin | 0.00 | 0.00 | no | H 1.00, SH 1.00, SMX 1.00 |

Discriminating: S1-pool-overload, T1-looseends-pin, T3-handles-gate, R1-guisave-foreground, R2-fsit-writer, R3-chat-synthesis

## Mechanical vs blind disagreements (|mech - blind| >= 0.5 on one item): 63

| case | item | count |
|---|---|---|
| R2-fsit-writer | B1 | 4 |
| R2-fsit-writer | M1 | 4 |
| R2-fsit-writer | M2 | 4 |
| R3-chat-synthesis | B1 | 5 |
| R3-chat-synthesis | M2 | 3 |
| R4-clean-r2pin | B1 | 4 |
| S1-pool-overload | B1 | 4 |
| S1-pool-overload | F1 | 2 |
| S1-pool-overload | M2 | 1 |
| S1-pool-overload | M3 | 1 |
| S2-display-loop | M1 | 1 |
| S3-disp-resplit | B2 | 1 |
| T1-looseends-pin | B1 | 5 |
| T1-looseends-pin | F2 | 2 |
| T1-looseends-pin | M1 | 2 |
| T1-looseends-pin | M2 | 2 |
| T2-constvalue-void | B1 | 1 |
| T2-constvalue-void | F1 | 1 |
| T2-constvalue-void | M1 | 1 |
| T2-constvalue-void | M2 | 2 |
| T3-handles-gate | B1 | 4 |
| T3-handles-gate | F1 | 4 |
| T3-handles-gate | M1 | 2 |
| T3-handles-gate | M2 | 3 |

<details><summary>all 63</summary>

- S1-pool-overload H r2 B1 mech 1.0 blind 0.0
- S1-pool-overload SH r1 F1 mech 0.0 blind 1.0
- S1-pool-overload SH r2 M2 mech 1.0 blind 0.5
- S1-pool-overload SH r2 M3 mech 1.0 blind 0.0
- S1-pool-overload SH r2 F1 mech 0.0 blind 0.5
- S1-pool-overload SH r2 B1 mech 1.0 blind 0.0
- S1-pool-overload SMX r1 B1 mech 1.0 blind 0.0
- S1-pool-overload SMX r2 B1 mech 1.0 blind 0.0
- S2-display-loop SMX r1 M1 mech 1.0 blind 0.5
- S3-disp-resplit H r2 B2 mech 0.0 blind 1.0
- T1-looseends-pin H r1 M1 mech 1.0 blind 0.5
- T1-looseends-pin H r1 B1 mech 0.0 blind 0.5
- T1-looseends-pin H r2 M1 mech 1.0 blind 0.5
- T1-looseends-pin H r2 F2 mech 1.0 blind 0.0
- T1-looseends-pin H r2 B1 mech 1.0 blind 0.5
- T1-looseends-pin SH r2 M2 mech 0.0 blind 0.5
- T1-looseends-pin SH r2 F2 mech 1.0 blind 0.5
- T1-looseends-pin SH r2 B1 mech 1.0 blind 0.5
- T1-looseends-pin SMX r1 B1 mech 0.0 blind 0.5
- T1-looseends-pin SMX r2 M2 mech 0.0 blind 0.5
- T1-looseends-pin SMX r2 B1 mech 1.0 blind 0.5
- T2-constvalue-void H r1 M2 mech 0.0 blind 0.5
- T2-constvalue-void H r2 M2 mech 0.0 blind 1.0
- T2-constvalue-void SH r1 F1 mech 0.0 blind 1.0
- T2-constvalue-void SH r1 B1 mech 1.0 blind 0.0
- T2-constvalue-void SH r2 M1 mech 1.0 blind 0.5
- T3-handles-gate H r1 M1 mech 0.0 blind 1.0
- T3-handles-gate H r1 M2 mech 1.0 blind 0.5
- T3-handles-gate H r1 B1 mech 1.0 blind 0.0
- T3-handles-gate H r2 F1 mech 1.0 blind 0.0
- T3-handles-gate SH r1 M1 mech 1.0 blind 0.5
- T3-handles-gate SH r1 M2 mech 1.0 blind 0.0
- T3-handles-gate SH r1 B1 mech 1.0 blind 0.0
- T3-handles-gate SH r2 M2 mech 1.0 blind 0.0
- T3-handles-gate SH r2 F1 mech 1.0 blind 0.0
- T3-handles-gate SH r2 B1 mech 1.0 blind 0.0
- T3-handles-gate SMX r1 F1 mech 1.0 blind 0.0
- T3-handles-gate SMX r1 B1 mech 1.0 blind 0.5
- T3-handles-gate SMX r2 F1 mech 1.0 blind 0.0
- R2-fsit-writer H r1 M1 mech 1.0 blind 0.5
- R2-fsit-writer H r1 B1 mech 0.0 blind 1.0
- R2-fsit-writer H r2 M1 mech 1.0 blind 0.5
- R2-fsit-writer H r2 B1 mech 0.0 blind 1.0
- R2-fsit-writer SH r1 M1 mech 1.0 blind 0.0
- R2-fsit-writer SH r1 M2 mech 0.0 blind 0.5
- R2-fsit-writer SH r2 M1 mech 1.0 blind 0.0
- R2-fsit-writer SH r2 M2 mech 0.0 blind 0.5
- R2-fsit-writer SH r2 B1 mech 0.0 blind 1.0
- R2-fsit-writer SMX r1 M2 mech 0.0 blind 1.0
- R2-fsit-writer SMX r2 M2 mech 0.0 blind 1.0
- R2-fsit-writer SMX r2 B1 mech 0.0 blind 1.0
- R3-chat-synthesis H r1 B1 mech 1.0 blind 0.0
- R3-chat-synthesis H r2 B1 mech 1.0 blind 0.0
- R3-chat-synthesis SH r1 M2 mech 0.0 blind 0.5
- R3-chat-synthesis SH r1 B1 mech 1.0 blind 0.0
- R3-chat-synthesis SH r2 M2 mech 1.0 blind 0.5
- R3-chat-synthesis SH r2 B1 mech 0.0 blind 0.5
- R3-chat-synthesis SMX r2 M2 mech 0.0 blind 0.5
- R3-chat-synthesis SMX r2 B1 mech 1.0 blind 0.0
- R4-clean-r2pin H r1 B1 mech 1.0 blind 0.5
- R4-clean-r2pin H r2 B1 mech 1.0 blind 0.5
- R4-clean-r2pin SH r1 B1 mech 1.0 blind 0.5
- R4-clean-r2pin SH r2 B1 mech 1.0 blind 0.5

</details>

## Validity

- Arm-runs re-run from the start after a rate-limit/overload cell: 0 (none).
- Invalid arm-runs in the table: 0 (none).
- Timeouts (cell cap): 0.
- Arm-runs without a blind score: 0 (none).
- Models seen in cell envelopes (modelUsage): claude-haiku-4-5-20251001, claude-opus-5-5, claude-sonnet-5-5.

## Cloud H vs v1 H (reproducibility; same cases, prompts, rubrics, scorer model)

v1 = results_full.json (Windows, 2026-09-29/30, scorer saw 10 answers per case: 5 arms x 2). cloud = this run (Linux container, scorer saw 6 answers per case: 3 arms x 2). Produced by compare_h.py.

| case | v1 H blind r1 ; r2 | cloud H blind r1 ; r2 | v1 H mech mean | cloud H mech mean | v1 usd / run | cloud usd / run | v1 min / run | cloud min / run |
|---|---|---|---|---|---|---|---|---|
| S1-pool-overload | 1.00 ; 1.00 | 1.00 ; 1.00 | 1.00 | 1.00 | 0.96 | 0.99 | 1.2 | 1.3 |
| S2-display-loop | 1.00 ; 1.00 | 0.00 ; 0.00 | 1.00 | 0.00 | 0.85 | 0.77 | 1.6 | 0.9 |
| S3-disp-resplit | 1.00 ; 1.00 | 1.00 ; 1.00 | 1.00 | 1.00 | 0.87 | 0.68 | 1.8 | 0.8 |
| T1-looseends-pin | 0.00 ; 0.75 | 0.25 ; 0.25 | 0.00 | 0.25 | 0.87 | 0.73 | 2.4 | 1.8 |
| T2-constvalue-void | 1.00 ; 1.00 | 0.75 ; 1.00 | 1.00 | 0.50 | 0.85 | 0.56 | 2.4 | 1.0 |
| T3-handles-gate | 0.50 ; 0.50 | 0.75 ; 1.00 | 1.00 | 0.50 | 0.67 | 0.51 | 2.0 | 1.1 |
| R1-guisave-foreground | 0.00 ; 0.00 | 0.00 ; 0.50 | 0.25 | 0.25 | 0.84 | 0.75 | 2.3 | 1.5 |
| R2-fsit-writer | 1.00 ; 0.75 | 0.75 ; 0.75 | 1.00 | 1.00 | 0.66 | 0.45 | 1.9 | 0.7 |
| R3-chat-synthesis | 0.50 ; 0.83 | 0.67 ; 0.67 | 0.67 | 0.67 | 0.59 | 0.36 | 1.4 | 0.6 |
| R4-clean-r2pin | 1.00 ; 1.00 | 1.00 ; 1.00 | 1.00 | 1.00 | 0.65 | 0.32 | 1.3 | 0.8 |
| **all** (n 20 / 20) | 0.742 | 0.667 | 0.792 | 0.617 | 0.78 | 0.61 | 1.8 | 1.1 |

- H blind mean: v1 0.742, cloud 0.667 (difference -0.075). H mech mean: v1 0.792, cloud 0.617.
- The largest per-case change is S2-display-loop: v1 H 1.00 ; 1.00 (blind and mech), cloud H 0.00 ; 0.00 (blind and mech; mech forbidden item hit in both repeats). SH and SMX also score 0.00 ; 0.00 on S2 in this run.
- Cloud H cost / run is $0.61 vs $0.78 in v1, and 1.1 vs 1.8 min / run.

## Run facts and environment differences from v1

- Wall-clock of the full run: 03:23:43 to 04:08:31 UTC (44.8 min), --par 6, --guard-usd 90 (the guard never fired: arm-runs total $63.41).
- Spend: full run $64.99 (arm-runs $63.41 + 10 blind scorers $1.57); smoke (R4-clean-r2pin x H/SH/SMX x 1, no blind) $4.63 (H $0.64, SH $0.34, SMX $3.65); total $69.62.
- Port changes (decbench.py only for the run; scoring code untouched): `claude.exe` -> `claude`; the dec_guard hook command `py` -> `sys.executable`; TEMP defaulted to tempfile.gettempdir(); timeout kill via process group (os.killpg) instead of taskkill; matbench.labview_pids stubbed to [] on Linux (no tasklist). Arms SH / SMX added to ARMS. report_v1.py gained --arms / --title (defaults unchanged).
- The repository was unshallowed (git fetch --unshallow) so the case base commits exist for the worktrees.
- Every one of the 60 arm-run cell logs starts with "Ignoring N permissions.allow entries from .claude/settings.json: this workspace has not been trusted" (N = 20 or 21 depending on the base commit) (Claude Code 2.1.287, Linux container). The worktree's own project hooks invoke `py` and Windows paths and fail (non-blocking) on Linux; the dec_guard PreToolUse hook ran and logged every call (calls.jsonl).
- Cells also report claude-haiku-4-5-20251001 in modelUsage (the CLI's auxiliary model); arm models as configured.
- Invalid cells: none (0 rate-limit / overload re-runs, 0 timeouts, 0 arm-runs without a blind score).
