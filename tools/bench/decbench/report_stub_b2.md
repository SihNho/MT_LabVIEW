# decbench v1 - decision bench, full run (card chat-B2)

Facts only. 10 known-answer cases x 5 arms x 2 repeats, --par 10. Arms: H = Opus 5.5 high; XH = Opus 5.5 xhigh; MX = Opus 5.5 max; FL = Fable 5.1 low; PAR = PAR (3 Opus high lenses + 1 synthesiser).
Score per arm-run = mean(must_hit) - 0.5 x max(forbidden), floored at 0; bonus mean beside it, never added. blind = one Opus 5.5 high scorer cell per case (answer key + rubric texts, labels shuffled, arm/model hidden); mech = rubric regexes. usd / min = per arm-run (PAR = sum of its 4 cells; min = wall clock of the arm-run).
Spent $0.00 (arm-runs $0.00 + blind scorers $0.00). Valid arm-runs 12, invalid 0.

## Per category x arm

| category | arm | n | blind mean | mech mean | bonus (blind) | usd / run | min / run | repeat spread (blind) |
|---|---|---|---|---|---|---|---|---|
| steering | H | 2 | 1.00 | 1.00 | 0.50 | 0.00 | 0.0 | 0.00 |
| steering | XH | 0 | - | - | - | - | - | - |
| steering | MX | 0 | - | - | - | - | - | - |
| steering | FL | 0 | - | - | - | - | - | - |
| steering | PAR | 2 | 1.00 | 1.00 | 0.50 | 0.00 | 0.0 | 0.00 |
| troubleshooting | H | 2 | 1.00 | 1.00 | 0.50 | 0.00 | 0.0 | 0.00 |
| troubleshooting | XH | 0 | - | - | - | - | - | - |
| troubleshooting | MX | 0 | - | - | - | - | - | - |
| troubleshooting | FL | 0 | - | - | - | - | - | - |
| troubleshooting | PAR | 2 | 1.00 | 1.00 | 0.50 | 0.00 | 0.0 | 0.00 |
| peer review | H | 2 | 1.00 | 1.00 | 0.50 | 0.00 | 0.0 | 0.00 |
| peer review | XH | 0 | - | - | - | - | - | - |
| peer review | MX | 0 | - | - | - | - | - | - |
| peer review | FL | 0 | - | - | - | - | - | - |
| peer review | PAR | 2 | 1.00 | 1.00 | 0.50 | 0.00 | 0.0 | 0.00 |

## All cases x arm (blind r1 ; r2 | mech r1 ; r2 | usd mean | min mean)

| case | H | XH | MX | FL | PAR |
|---|---|---|---|---|---|
| S1-pool-overload | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - |
| S2-display-loop | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - |
| S3-disp-resplit | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.00 &#124; 0.0 | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.00 &#124; 0.0 |
| T1-looseends-pin | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - |
| T2-constvalue-void | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.00 &#124; 0.0 | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.00 &#124; 0.0 |
| T3-handles-gate | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - |
| R1-guisave-foreground | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - |
| R2-fsit-writer | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - |
| R3-chat-synthesis | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.00 &#124; 0.0 | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | 1.00 ; 1.00 &#124; 1.00 ; 1.00 &#124; $0.00 &#124; 0.0 |
| R4-clean-r2pin | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - | - ; - &#124; - ; - &#124; $- &#124; - |

## Per arm totals

| arm | n | blind mean | mech mean | usd total | usd / run | min / run | turns / run | tool calls / run | timeouts |
|---|---|---|---|---|---|---|---|---|---|
| H | 6 | 1.000 | 1.000 | 0.00 | 0.00 | 0.0 | 1.0 | 1.0 | 0 |
| XH | 0 | - | - | 0.00 | - | - | - | - | 0 |
| MX | 0 | - | - | 0.00 | - | - | - | - | 0 |
| FL | 0 | - | - | 0.00 | - | - | - | - | 0 |
| PAR | 6 | 1.000 | 1.000 | 0.00 | 0.00 | 0.0 | 4.0 | 4.0 | 0 |

## Peer review: defect hits (R1-guisave-foreground, R2-fsit-writer, R3-chat-synthesis) and clean-case false alarms (R4-clean-r2pin)

Defect hit = blind must-hit mean of the arm-run (0..1); full hit = every must_hit item scored 1 by the blind scorer; accepted = forbidden item (DEFECT none/minor) committed (blind >= 0.5). False alarm on the clean case = its forbidden item (DEFECT: blocker) committed (blind >= 0.5; mech in brackets).

| arm | defect must-hit mean (blind) | full hits / runs | accepted-as-fine / runs | clean-case false alarms / runs (mech) |
|---|---|---|---|---|
| H | 1.00 | 2 / 2 | 0 / 2 | 0 / 0 (0) |
| XH | - | 0 / 0 | 0 / 0 | 0 / 0 (0) |
| MX | - | 0 / 0 | 0 / 0 | 0 / 0 (0) |
| FL | - | 0 / 0 | 0 / 0 | 0 / 0 (0) |
| PAR | 1.00 | 2 / 2 | 0 / 2 | 0 / 0 (0) |

Per defect case, blind must-hit mean per arm:

| case | H | XH | MX | FL | PAR |
|---|---|---|---|---|---|
| R1-guisave-foreground | - | - | - | - | - |
| R2-fsit-writer | - | - | - | - | - |
| R3-chat-synthesis | 1.00 | - | - | - | 1.00 |

## Discriminating cases (blind score)

within = the largest |r1 - r2| over arms; between = range of the per-arm mean scores. A case whose between is not larger than its within is not distinguishable from repeat noise.

| case | within | between | discriminates | per-arm mean |
|---|---|---|---|---|
| S1-pool-overload | 0.00 | 0.00 | no |  |
| S2-display-loop | 0.00 | 0.00 | no |  |
| S3-disp-resplit | 0.00 | 0.00 | no | H 1.00, PAR 1.00 |
| T1-looseends-pin | 0.00 | 0.00 | no |  |
| T2-constvalue-void | 0.00 | 0.00 | no | H 1.00, PAR 1.00 |
| T3-handles-gate | 0.00 | 0.00 | no |  |
| R1-guisave-foreground | 0.00 | 0.00 | no |  |
| R2-fsit-writer | 0.00 | 0.00 | no |  |
| R3-chat-synthesis | 0.00 | 0.00 | no | H 1.00, PAR 1.00 |
| R4-clean-r2pin | 0.00 | 0.00 | no |  |

Discriminating: none

## Mechanical vs blind disagreements (|mech - blind| >= 0.5 on one item): 20

| case | item | count |
|---|---|---|
| R3-chat-synthesis | B1 | 4 |
| S3-disp-resplit | B1 | 4 |
| S3-disp-resplit | B2 | 4 |
| T2-constvalue-void | B1 | 4 |
| T2-constvalue-void | B2 | 4 |

<details><summary>all 20</summary>

- S3-disp-resplit H r1 B1 mech 0.0 blind 0.5
- S3-disp-resplit H r1 B2 mech 0.0 blind 0.5
- S3-disp-resplit H r2 B1 mech 0.0 blind 0.5
- S3-disp-resplit H r2 B2 mech 0.0 blind 0.5
- S3-disp-resplit PAR r1 B1 mech 0.0 blind 0.5
- S3-disp-resplit PAR r1 B2 mech 0.0 blind 0.5
- S3-disp-resplit PAR r2 B1 mech 0.0 blind 0.5
- S3-disp-resplit PAR r2 B2 mech 0.0 blind 0.5
- T2-constvalue-void H r1 B1 mech 0.0 blind 0.5
- T2-constvalue-void H r1 B2 mech 0.0 blind 0.5
- T2-constvalue-void H r2 B1 mech 0.0 blind 0.5
- T2-constvalue-void H r2 B2 mech 0.0 blind 0.5
- T2-constvalue-void PAR r1 B1 mech 0.0 blind 0.5
- T2-constvalue-void PAR r1 B2 mech 0.0 blind 0.5
- T2-constvalue-void PAR r2 B1 mech 0.0 blind 0.5
- T2-constvalue-void PAR r2 B2 mech 0.0 blind 0.5
- R3-chat-synthesis H r1 B1 mech 0.0 blind 0.5
- R3-chat-synthesis H r2 B1 mech 0.0 blind 0.5
- R3-chat-synthesis PAR r1 B1 mech 0.0 blind 0.5
- R3-chat-synthesis PAR r2 B1 mech 0.0 blind 0.5

</details>

## Validity

- Arm-runs re-run from the start after a rate-limit/overload cell: 0 (none).
- Invalid arm-runs in the table: 0 (none).
- Timeouts (cell cap): 0.
- Arm-runs without a blind score: 0 (none).
- Models seen in cell envelopes (modelUsage): stub.
