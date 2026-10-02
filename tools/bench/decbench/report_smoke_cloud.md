# decbench report

tag smoke_cloud, par 6, stub no, spent $4.64 (blind $0.00)

| arm | n | invalid | blind mean | mech mean | min/run | usd total | usd/run | turns | tool calls |
|---|---|---|---|---|---|---|---|---|---|
| H | 1 | 0 | None | 1.0 | 0.97 | 0.64 | 0.64 | 8 | 7 |
| SH | 1 | 0 | None | 1.0 | 0.79 | 0.34 | 0.342 | 7 | 6 |
| SMX | 1 | 0 | None | 1.0 | 14.8 | 3.65 | 3.654 | 53 | 51 |

## Arm-runs

| case | arm | rep | usd | min | mech | blind |
|---|---|---|---|---|---|---|
| R4-clean-r2pin | H | 1 | 0.6404 | 0.97 | {"M1": 1.0, "F1": 0.0, "B1": 1.0} | null |
| R4-clean-r2pin | SH | 1 | 0.3416 | 0.79 | {"M1": 1.0, "F1": 0.0, "B1": 1.0} | null |
| R4-clean-r2pin | SMX | 1 | 3.654 | 14.8 | {"M1": 1.0, "F1": 0.0, "B1": 1.0} | null |

## Mechanical vs blind disagreements (|diff| >= 0.5)

- none
