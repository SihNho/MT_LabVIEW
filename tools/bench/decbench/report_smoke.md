# decbench report

tag smoke, par 10, stub no, spent $10.23 (blind $0.15)

| arm | n | invalid | blind mean | mech mean | min/run | usd total | usd/run | turns | tool calls |
|---|---|---|---|---|---|---|---|---|---|
| FL | 1 | 0 | 1.0 | 1.0 | 0.53 | 2.29 | 2.288 | 4 | 3 |
| H | 1 | 0 | 1.0 | 1.0 | 0.97 | 1.04 | 1.044 | 9 | 8 |
| MX | 1 | 0 | 1.0 | 1.0 | 4.99 | 2.0 | 2.001 | 18 | 17 |
| PAR | 1 | 0 | 1.0 | 1.0 | 1.58 | 3.63 | 3.634 | 29 | 25 |
| XH | 1 | 0 | 1.0 | 1.0 | 1.27 | 1.11 | 1.113 | 9 | 8 |

## Arm-runs

| case | arm | rep | usd | min | mech | blind |
|---|---|---|---|---|---|---|
| T2-guardpeer-jevlog | FL | 1 | 2.2878 | 0.53 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 0.5} |
| T2-guardpeer-jevlog | H | 1 | 1.0443 | 0.97 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 0.5} |
| T2-guardpeer-jevlog | MX | 1 | 2.0008 | 4.99 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 0.0} |
| T2-guardpeer-jevlog | PAR | 1 | 3.634 | 1.58 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 0.0} |
| T2-guardpeer-jevlog | XH | 1 | 1.1134 | 1.27 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 0.5} |

## Mechanical vs blind disagreements (|diff| >= 0.5)

- T2-guardpeer-jevlog H r1 B2 mech 1.0 blind 0.5
- T2-guardpeer-jevlog XH r1 B2 mech 1.0 blind 0.5
- T2-guardpeer-jevlog MX r1 B2 mech 1.0 blind 0.0
- T2-guardpeer-jevlog FL r1 B2 mech 1.0 blind 0.5
- T2-guardpeer-jevlog PAR r1 B2 mech 1.0 blind 0.0
