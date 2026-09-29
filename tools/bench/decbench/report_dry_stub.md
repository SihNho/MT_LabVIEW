# decbench report

tag dry_stub, par 10, stub ratelimit, spent $0.00 (blind $0.00)

| arm | n | invalid | blind mean | mech mean | min/run | usd total | usd/run | turns | tool calls |
|---|---|---|---|---|---|---|---|---|---|
| FL | 2 | 0 | 1.0 | 1.0 | 0.01 | 0.0 | 0.0 | 1 | 1 |
| H | 2 | 0 | 1.0 | 1.0 | 0.01 | 0.0 | 0.0 | 1 | 1 |
| MX | 2 | 0 | 1.0 | 1.0 | 0.01 | 0.0 | 0.0 | 1 | 1 |
| PAR | 2 | 0 | 1.0 | 1.0 | 0.01 | 0.0 | 0.0 | 4 | 4 |
| XH | 2 | 0 | 1.0 | 1.0 | 0.01 | 0.0 | 0.0 | 1 | 1 |

## Arm-runs

| case | arm | rep | usd | min | mech | blind |
|---|---|---|---|---|---|---|
| R4-clean-r2pin | FL | 1 | 0.0 | 0.01 | {"M1": 1.0, "F1": 0.0, "B1": 0.0} | {"M1": 1.0, "F1": 0.0, "B1": 0.5} |
| R4-clean-r2pin | H | 1 | 0.0 | 0.01 | {"M1": 1.0, "F1": 0.0, "B1": 0.0} | {"M1": 1.0, "F1": 0.0, "B1": 0.5} |
| R4-clean-r2pin | MX | 1 | 0.0 | 0.01 | {"M1": 1.0, "F1": 0.0, "B1": 0.0} | {"M1": 1.0, "F1": 0.0, "B1": 0.5} |
| R4-clean-r2pin | PAR | 1 | 0.0 | 0.01 | {"M1": 1.0, "F1": 0.0, "B1": 0.0} | {"M1": 1.0, "F1": 0.0, "B1": 0.5} |
| R4-clean-r2pin | XH | 1 | 0.0 | 0.01 | {"M1": 1.0, "F1": 0.0, "B1": 0.0} | {"M1": 1.0, "F1": 0.0, "B1": 0.5} |
| S1-pool-overload | FL | 1 | 0.0 | 0.01 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.5} |
| S1-pool-overload | H | 1 | 0.0 | 0.01 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.5} |
| S1-pool-overload | MX | 1 | 0.0 | 0.01 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.5} |
| S1-pool-overload | PAR | 1 | 0.0 | 0.01 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.5} |
| S1-pool-overload | XH | 1 | 0.0 | 0.01 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.5} |

## Mechanical vs blind disagreements (|diff| >= 0.5)

- S1-pool-overload H r1 B1 mech 0.0 blind 0.5
- S1-pool-overload XH r1 B1 mech 0.0 blind 0.5
- S1-pool-overload MX r1 B1 mech 0.0 blind 0.5
- S1-pool-overload FL r1 B1 mech 0.0 blind 0.5
- S1-pool-overload PAR r1 B1 mech 0.0 blind 0.5
- R4-clean-r2pin H r1 B1 mech 0.0 blind 0.5
- R4-clean-r2pin XH r1 B1 mech 0.0 blind 0.5
- R4-clean-r2pin MX r1 B1 mech 0.0 blind 0.5
- R4-clean-r2pin FL r1 B1 mech 0.0 blind 0.5
- R4-clean-r2pin PAR r1 B1 mech 0.0 blind 0.5
