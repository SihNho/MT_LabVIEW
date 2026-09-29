# decbench v1 - decision bench, full run (card chat-B2)

Facts only. 10 known-answer cases x 5 arms x 2 repeats, --par 10. Arms: H = Opus 5.5 high; XH = Opus 5.5 xhigh; MX = Opus 5.5 max; FL = Fable 5.1 low; PAR = PAR (3 Opus high lenses + 1 synthesiser).
Score per arm-run = mean(must_hit) - 0.5 x max(forbidden), floored at 0; bonus mean beside it, never added. blind = one Opus 5.5 high scorer cell per case (answer key + rubric texts, labels shuffled, arm/model hidden); mech = rubric regexes. usd / min = per arm-run (PAR = sum of its 4 cells; min = wall clock of the arm-run).
Spent $179.78 (arm-runs $177.66 + blind scorers $2.12). Valid arm-runs 100, invalid 0.

## Per category x arm

| category | arm | n | blind mean | mech mean | bonus (blind) | usd / run | min / run | repeat spread (blind) |
|---|---|---|---|---|---|---|---|---|
| steering | H | 6 | 1.00 | 1.00 | 0.50 | 0.90 | 1.5 | 0.00 |
| steering | XH | 6 | 0.67 | 0.83 | 0.33 | 1.24 | 2.4 | 0.67 |
| steering | MX | 6 | 1.00 | 1.00 | 0.50 | 2.07 | 4.9 | 0.00 |
| steering | FL | 6 | 1.00 | 0.94 | 0.33 | 1.47 | 0.7 | 0.00 |
| steering | PAR | 6 | 0.50 | 0.81 | 0.58 | 3.48 | 2.8 | 0.33 |
| troubleshooting | H | 6 | 0.62 | 0.67 | 0.33 | 0.80 | 2.3 | 0.25 |
| troubleshooting | XH | 6 | 0.54 | 0.58 | 0.58 | 1.19 | 3.1 | 0.08 |
| troubleshooting | MX | 6 | 0.71 | 0.50 | 0.67 | 2.72 | 8.7 | 0.25 |
| troubleshooting | FL | 6 | 0.50 | 0.50 | 0.38 | 1.46 | 0.8 | 0.50 |
| troubleshooting | PAR | 6 | 0.50 | 0.42 | 0.50 | 3.58 | 3.4 | 0.00 |
| peer review | H | 8 | 0.64 | 0.73 | 0.38 | 0.68 | 1.7 | 0.15 |
| peer review | XH | 8 | 0.93 | 0.92 | 0.62 | 1.01 | 2.2 | 0.06 |
| peer review | MX | 8 | 0.98 | 0.90 | 0.69 | 2.09 | 5.9 | 0.04 |
| peer review | FL | 8 | 0.68 | 0.67 | 0.38 | 1.40 | 0.7 | 0.06 |
| peer review | PAR | 8 | 0.92 | 0.92 | 0.62 | 2.85 | 2.5 | 0.00 |

## All cases x arm (blind r1 ; r2 | mech r1 ; r2 | usd mean | min mean)

| case | H | XH | MX | FL | PAR |
|---|---|---|---|---|---|
| S1-pool-overload | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.96 &#124; 1.2 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $1.30 &#124; 2.2 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $2.25 &#124; 5.4 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $1.50 &#124; 0.7 | 0.00 ; 0.00 &#124; 0.67 ; 1.00 &#124; $3.56 &#124; 3.2 |
| S2-display-loop | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.85 &#124; 1.6 | 1.00 ; 0.00 &#124; 1.00 ; 1.00 &#124; $1.33 &#124; 2.7 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $2.15 &#124; 5.4 | 1.00 ; 1.00 &#124; 1.00 ; 0.67 &#124; $1.54 &#124; 0.8 | 1.00 ; 0.00 &#124; 1.00 ; 0.67 &#124; $3.54 &#124; 3.0 |
| S3-disp-resplit | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.87 &#124; 1.8 | 1.00 ; 0.00 &#124; 1.00 ; 0.00 &#124; $1.10 &#124; 2.2 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $1.82 &#124; 3.7 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $1.36 &#124; 0.6 | 1.00 ; 1.00 &#124; 1.00 ; 0.50 &#124; $3.33 &#124; 2.3 |
| T1-looseends-pin | 0.00 ; 0.75 &#124; 0.00 ; 0.00 &#124; $0.87 &#124; 2.4 | 0.00 ; 0.00 &#124; 0.00 ; 0.00 &#124; $1.37 &#124; 3.4 | 0.50 ; 0.00 &#124; 0.00 ; 0.00 &#124; $3.56 &#124; 11.8 | 0.00 ; 0.75 &#124; 0.00 ; 0.50 &#124; $1.55 &#124; 0.9 | 0.00 ; 0.00 &#124; 0.00 ; 0.00 &#124; $4.07 &#124; 4.1 |
| T2-constvalue-void | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.85 &#124; 2.4 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $1.19 &#124; 3.0 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $2.31 &#124; 7.6 | 1.00 ; 0.25 &#124; 1.00 ; 0.50 &#124; $1.55 &#124; 1.0 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $3.59 &#124; 3.0 |
| T3-handles-gate | 0.50 ; 0.50 &#124; 1.00 ; 1.00 &#124; $0.67 &#124; 2.0 | 0.75 ; 0.50 &#124; 0.50 ; 1.00 &#124; $1.00 &#124; 2.8 | 1.00 ; 0.75 &#124; 0.50 ; 0.50 &#124; $2.29 &#124; 6.8 | 0.50 ; 0.50 &#124; 0.50 ; 0.50 &#124; $1.30 &#124; 0.5 | 0.50 ; 0.50 &#124; 0.50 ; 0.00 &#124; $3.07 &#124; 3.0 |
| R1-guisave-foreground | 0.00 ; 0.00 &#124; 0.00 ; 0.50 &#124; $0.84 &#124; 2.3 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $1.42 &#124; 3.0 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $2.78 &#124; 7.9 | 0.00 ; 0.00 &#124; 0.00 ; 0.00 &#124; $1.29 &#124; 0.7 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $3.29 &#124; 4.0 |
| R2-fsit-writer | 1.00 ; 0.75 &#124; 1.00 ; 1.00 &#124; $0.66 &#124; 1.9 | 0.75 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.87 &#124; 1.7 | 1.00 ; 1.00 &#124; 1.00 ; 0.50 &#124; $1.64 &#124; 3.9 | 0.75 ; 1.00 &#124; 1.00 ; 1.00 &#124; $1.49 &#124; 0.8 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $2.91 &#124; 2.3 |
| R3-chat-synthesis | 0.50 ; 0.83 &#124; 0.67 ; 0.67 &#124; $0.59 &#124; 1.4 | 0.83 ; 0.83 &#124; 0.67 ; 0.67 &#124; $0.84 &#124; 1.8 | 1.00 ; 0.83 &#124; 1.00 ; 0.67 &#124; $1.29 &#124; 3.0 | 0.83 ; 0.83 &#124; 0.67 ; 0.67 &#124; $1.37 &#124; 0.5 | 0.67 ; 0.67 &#124; 0.67 ; 0.67 &#124; $2.47 &#124; 1.4 |
| R4-clean-r2pin | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.65 &#124; 1.3 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.92 &#124; 2.3 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $2.66 &#124; 8.9 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $1.44 &#124; 0.8 | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $2.71 &#124; 2.2 |

## Per arm totals

| arm | n | blind mean | mech mean | usd total | usd / run | min / run | turns / run | tool calls / run | timeouts |
|---|---|---|---|---|---|---|---|---|---|
| H | 20 | 0.742 | 0.792 | 15.62 | 0.78 | 1.8 | 9.7 | 8.7 | 0 |
| XH | 20 | 0.733 | 0.792 | 22.66 | 1.13 | 2.5 | 15.7 | 14.6 | 0 |
| MX | 20 | 0.904 | 0.808 | 45.49 | 2.27 | 6.4 | 28.8 | 27.7 | 0 |
| FL | 20 | 0.721 | 0.700 | 28.79 | 1.44 | 0.7 | 6.8 | 5.7 | 0 |
| PAR | 20 | 0.667 | 0.733 | 65.11 | 3.26 | 2.8 | 42.4 | 38.2 | 0 |

## Peer review: defect hits (R1-guisave-foreground, R2-fsit-writer, R3-chat-synthesis) and clean-case false alarms (R4-clean-r2pin)

Defect hit = blind must-hit mean of the arm-run (0..1); full hit = every must_hit item scored 1 by the blind scorer; accepted = forbidden item (DEFECT none/minor) committed (blind >= 0.5). False alarm on the clean case = its forbidden item (DEFECT: blocker) committed (blind >= 0.5; mech in brackets).

| arm | defect must-hit mean (blind) | full hits / runs | accepted-as-fine / runs | clean-case false alarms / runs (mech) |
|---|---|---|---|---|
| H | 0.51 | 1 / 6 | 0 / 6 | 0 / 2 (0) |
| XH | 0.90 | 3 / 6 | 0 / 6 | 0 / 2 (0) |
| MX | 0.97 | 5 / 6 | 0 / 6 | 0 / 2 (0) |
| FL | 0.57 | 1 / 6 | 0 / 6 | 0 / 2 (0) |
| PAR | 0.89 | 4 / 6 | 0 / 6 | 0 / 2 (0) |

Per defect case, blind must-hit mean per arm:

| case | H | XH | MX | FL | PAR |
|---|---|---|---|---|---|
| R1-guisave-foreground | 0.00 | 1.00 | 1.00 | 0.00 | 1.00 |
| R2-fsit-writer | 0.88 | 0.88 | 1.00 | 0.88 | 1.00 |
| R3-chat-synthesis | 0.67 | 0.83 | 0.92 | 0.83 | 0.67 |

## Discriminating cases (blind score)

within = the largest |r1 - r2| over arms; between = range of the per-arm mean scores. A case whose between is not larger than its within is not distinguishable from repeat noise.

| case | within | between | discriminates | per-arm mean |
|---|---|---|---|---|
| S1-pool-overload | 0.00 | 1.00 | yes | H 1.00, XH 1.00, MX 1.00, FL 1.00, PAR 0.00 |
| S2-display-loop | 1.00 | 0.50 | no | H 1.00, XH 0.50, MX 1.00, FL 1.00, PAR 0.50 |
| S3-disp-resplit | 1.00 | 0.50 | no | H 1.00, XH 0.50, MX 1.00, FL 1.00, PAR 1.00 |
| T1-looseends-pin | 0.75 | 0.38 | no | H 0.38, XH 0.00, MX 0.25, FL 0.38, PAR 0.00 |
| T2-constvalue-void | 0.75 | 0.38 | no | H 1.00, XH 1.00, MX 1.00, FL 0.62, PAR 1.00 |
| T3-handles-gate | 0.25 | 0.38 | yes | H 0.50, XH 0.62, MX 0.88, FL 0.50, PAR 0.50 |
| R1-guisave-foreground | 0.00 | 1.00 | yes | H 0.00, XH 1.00, MX 1.00, FL 0.00, PAR 1.00 |
| R2-fsit-writer | 0.25 | 0.12 | no | H 0.88, XH 0.88, MX 1.00, FL 0.88, PAR 1.00 |
| R3-chat-synthesis | 0.33 | 0.25 | no | H 0.67, XH 0.83, MX 0.92, FL 0.83, PAR 0.67 |
| R4-clean-r2pin | 0.00 | 0.00 | no | H 1.00, XH 1.00, MX 1.00, FL 1.00, PAR 1.00 |

Discriminating: S1-pool-overload, T3-handles-gate, R1-guisave-foreground

## Mechanical vs blind disagreements (|mech - blind| >= 0.5 on one item): 106

| case | item | count |
|---|---|---|
| R1-guisave-foreground | M1 | 1 |
| R2-fsit-writer | B1 | 6 |
| R2-fsit-writer | M1 | 3 |
| R2-fsit-writer | M2 | 1 |
| R3-chat-synthesis | B1 | 6 |
| R3-chat-synthesis | M1 | 1 |
| R3-chat-synthesis | M2 | 6 |
| R4-clean-r2pin | B1 | 10 |
| S1-pool-overload | B1 | 5 |
| S1-pool-overload | F1 | 2 |
| S1-pool-overload | M1 | 1 |
| S1-pool-overload | M2 | 2 |
| S1-pool-overload | M3 | 2 |
| S2-display-loop | B1 | 2 |
| S2-display-loop | F1 | 2 |
| S2-display-loop | M1 | 3 |
| S2-display-loop | M2 | 1 |
| S2-display-loop | M3 | 2 |
| S3-disp-resplit | B2 | 2 |
| S3-disp-resplit | F1 | 1 |
| S3-disp-resplit | M2 | 1 |
| T1-looseends-pin | B1 | 8 |
| T1-looseends-pin | F2 | 2 |
| T1-looseends-pin | M1 | 7 |
| T1-looseends-pin | M2 | 2 |
| T2-constvalue-void | B1 | 1 |
| T2-constvalue-void | F1 | 1 |
| T2-constvalue-void | M1 | 1 |
| T3-handles-gate | B1 | 9 |
| T3-handles-gate | F1 | 7 |
| T3-handles-gate | M2 | 8 |

<details><summary>all 106</summary>

- S1-pool-overload XH r1 B1 mech 1.0 blind 0.0
- S1-pool-overload XH r2 B1 mech 0.0 blind 0.5
- S1-pool-overload MX r1 B1 mech 1.0 blind 0.0
- S1-pool-overload PAR r1 M2 mech 1.0 blind 0.0
- S1-pool-overload PAR r1 M3 mech 1.0 blind 0.0
- S1-pool-overload PAR r1 F1 mech 0.0 blind 1.0
- S1-pool-overload PAR r1 B1 mech 1.0 blind 0.5
- S1-pool-overload PAR r2 M1 mech 1.0 blind 0.5
- S1-pool-overload PAR r2 M2 mech 1.0 blind 0.5
- S1-pool-overload PAR r2 M3 mech 1.0 blind 0.5
- S1-pool-overload PAR r2 F1 mech 0.0 blind 1.0
- S1-pool-overload PAR r2 B1 mech 1.0 blind 0.5
- S2-display-loop H r2 B1 mech 1.0 blind 0.0
- S2-display-loop XH r2 M1 mech 1.0 blind 0.5
- S2-display-loop XH r2 M2 mech 1.0 blind 0.0
- S2-display-loop XH r2 M3 mech 1.0 blind 0.0
- S2-display-loop XH r2 F1 mech 0.0 blind 0.5
- S2-display-loop FL r2 M1 mech 0.0 blind 1.0
- S2-display-loop PAR r2 M1 mech 1.0 blind 0.0
- S2-display-loop PAR r2 M3 mech 1.0 blind 0.0
- S2-display-loop PAR r2 F1 mech 0.0 blind 0.5
- S2-display-loop PAR r2 B1 mech 1.0 blind 0.5
- S3-disp-resplit XH r2 F1 mech 0.0 blind 1.0
- S3-disp-resplit FL r2 B2 mech 0.0 blind 1.0
- S3-disp-resplit PAR r2 M2 mech 0.0 blind 1.0
- S3-disp-resplit PAR r2 B2 mech 0.0 blind 1.0
- T1-looseends-pin H r1 M1 mech 0.0 blind 0.5
- T1-looseends-pin H r1 B1 mech 0.0 blind 1.0
- T1-looseends-pin H r2 M2 mech 0.0 blind 0.5
- T1-looseends-pin H r2 F2 mech 1.0 blind 0.0
- T1-looseends-pin XH r1 M1 mech 1.0 blind 0.5
- T1-looseends-pin XH r1 B1 mech 0.0 blind 0.5
- T1-looseends-pin XH r2 M1 mech 1.0 blind 0.5
- T1-looseends-pin XH r2 B1 mech 0.0 blind 0.5
- T1-looseends-pin MX r1 F2 mech 1.0 blind 0.0
- T1-looseends-pin MX r2 M1 mech 1.0 blind 0.5
- T1-looseends-pin MX r2 B1 mech 0.0 blind 0.5
- T1-looseends-pin FL r1 M1 mech 1.0 blind 0.5
- T1-looseends-pin FL r1 B1 mech 0.0 blind 0.5
- T1-looseends-pin FL r2 M2 mech 0.0 blind 0.5
- T1-looseends-pin FL r2 B1 mech 0.0 blind 1.0
- T1-looseends-pin PAR r1 M1 mech 1.0 blind 0.5
- T1-looseends-pin PAR r1 B1 mech 0.0 blind 1.0
- T1-looseends-pin PAR r2 M1 mech 1.0 blind 0.5
- T1-looseends-pin PAR r2 B1 mech 1.0 blind 0.0
- T2-constvalue-void FL r2 M1 mech 1.0 blind 0.0
- T2-constvalue-void FL r2 F1 mech 1.0 blind 0.5
- T2-constvalue-void FL r2 B1 mech 1.0 blind 0.5
- T3-handles-gate H r1 M2 mech 1.0 blind 0.0
- T3-handles-gate H r1 B1 mech 1.0 blind 0.0
- T3-handles-gate H r2 M2 mech 1.0 blind 0.0
- T3-handles-gate H r2 B1 mech 1.0 blind 0.0
- T3-handles-gate XH r1 M2 mech 1.0 blind 0.5
- T3-handles-gate XH r1 F1 mech 1.0 blind 0.0
- T3-handles-gate XH r1 B1 mech 1.0 blind 0.5
- T3-handles-gate XH r2 M2 mech 1.0 blind 0.0
- T3-handles-gate XH r2 B1 mech 1.0 blind 0.0
- T3-handles-gate MX r1 F1 mech 1.0 blind 0.0
- T3-handles-gate MX r2 M2 mech 1.0 blind 0.5
- T3-handles-gate MX r2 F1 mech 1.0 blind 0.0
- T3-handles-gate MX r2 B1 mech 1.0 blind 0.5
- T3-handles-gate FL r1 M2 mech 1.0 blind 0.0
- T3-handles-gate FL r1 F1 mech 1.0 blind 0.0
- T3-handles-gate FL r1 B1 mech 1.0 blind 0.0
- T3-handles-gate FL r2 M2 mech 1.0 blind 0.0
- T3-handles-gate FL r2 F1 mech 1.0 blind 0.0
- T3-handles-gate FL r2 B1 mech 1.0 blind 0.0
- T3-handles-gate PAR r1 M2 mech 1.0 blind 0.0
- T3-handles-gate PAR r1 F1 mech 1.0 blind 0.0
- T3-handles-gate PAR r1 B1 mech 1.0 blind 0.0
- T3-handles-gate PAR r2 F1 mech 1.0 blind 0.0
- T3-handles-gate PAR r2 B1 mech 1.0 blind 0.0
- R1-guisave-foreground H r2 M1 mech 1.0 blind 0.0
- R2-fsit-writer H r1 B1 mech 0.0 blind 1.0
- R2-fsit-writer H r2 M1 mech 1.0 blind 0.5
- R2-fsit-writer XH r1 M1 mech 1.0 blind 0.5
- R2-fsit-writer XH r1 B1 mech 0.0 blind 1.0
- R2-fsit-writer XH r2 B1 mech 0.0 blind 1.0
- R2-fsit-writer MX r1 B1 mech 0.0 blind 1.0
- R2-fsit-writer MX r2 M2 mech 0.0 blind 1.0
- R2-fsit-writer MX r2 B1 mech 0.0 blind 1.0
- R2-fsit-writer FL r1 M1 mech 1.0 blind 0.5
- R2-fsit-writer FL r2 B1 mech 0.0 blind 1.0
- R3-chat-synthesis H r1 M1 mech 1.0 blind 0.5
- R3-chat-synthesis H r2 M2 mech 0.0 blind 0.5
- R3-chat-synthesis H r2 B1 mech 1.0 blind 0.0
- R3-chat-synthesis XH r1 M2 mech 0.0 blind 0.5
- R3-chat-synthesis XH r1 B1 mech 1.0 blind 0.0
- R3-chat-synthesis XH r2 M2 mech 0.0 blind 0.5
- R3-chat-synthesis XH r2 B1 mech 1.0 blind 0.0
- R3-chat-synthesis MX r1 B1 mech 1.0 blind 0.5
- R3-chat-synthesis MX r2 M2 mech 0.0 blind 0.5
- R3-chat-synthesis MX r2 B1 mech 1.0 blind 0.0
- R3-chat-synthesis FL r1 M2 mech 0.0 blind 0.5
- R3-chat-synthesis FL r2 M2 mech 0.0 blind 0.5
- R3-chat-synthesis PAR r2 B1 mech 1.0 blind 0.0
- R4-clean-r2pin H r1 B1 mech 1.0 blind 0.5
- R4-clean-r2pin H r2 B1 mech 1.0 blind 0.5
- R4-clean-r2pin XH r1 B1 mech 1.0 blind 0.5
- R4-clean-r2pin XH r2 B1 mech 1.0 blind 0.5
- R4-clean-r2pin MX r1 B1 mech 1.0 blind 0.5
- R4-clean-r2pin MX r2 B1 mech 1.0 blind 0.5
- R4-clean-r2pin FL r1 B1 mech 1.0 blind 0.5
- R4-clean-r2pin FL r2 B1 mech 1.0 blind 0.5
- R4-clean-r2pin PAR r1 B1 mech 1.0 blind 0.5
- R4-clean-r2pin PAR r2 B1 mech 1.0 blind 0.5

</details>

## Validity

- Arm-runs re-run from the start after a rate-limit/overload cell: 0 (none).
- Invalid arm-runs in the table: 0 (none).
- Timeouts (cell cap): 0.
- Arm-runs without a blind score: 0 (none).
- Models seen in cell envelopes (modelUsage): claude-fable-5-1, claude-opus-5-5.
