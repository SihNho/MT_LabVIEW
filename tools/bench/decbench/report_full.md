# decbench report

tag full, par 10, stub no, spent $179.78 (blind $2.12)

| arm | n | invalid | blind mean | mech mean | min/run | usd total | usd/run | turns | tool calls |
|---|---|---|---|---|---|---|---|---|---|
| FL | 20 | 0 | 0.721 | 0.7 | 0.725 | 28.79 | 1.439 | 6.75 | 5.65 |
| H | 20 | 0 | 0.742 | 0.792 | 1.827 | 15.62 | 0.781 | 9.7 | 8.65 |
| MX | 20 | 0 | 0.904 | 0.808 | 6.445 | 45.49 | 2.275 | 28.75 | 27.7 |
| PAR | 20 | 0 | 0.667 | 0.733 | 2.844 | 65.11 | 3.255 | 42.35 | 38.2 |
| XH | 20 | 0 | 0.733 | 0.792 | 2.507 | 22.66 | 1.133 | 15.65 | 14.6 |

## Arm-runs

| case | arm | rep | usd | min | mech | blind |
|---|---|---|---|---|---|---|
| R1-guisave-foreground | FL | 1 | 1.2131 | 0.62 | {"M1": 0.0, "M2": 0.0, "F1": 0.0, "B1": 0.0} | {"M1": 0.0, "M2": 0.0, "F1": 0.0, "B1": 0.0} |
| R1-guisave-foreground | FL | 2 | 1.3678 | 0.7 | {"M1": 0.0, "M2": 0.0, "F1": 0.0, "B1": 0.0} | {"M1": 0.0, "M2": 0.0, "F1": 0.0, "B1": 0.0} |
| R1-guisave-foreground | H | 1 | 0.815 | 2.05 | {"M1": 0.0, "M2": 0.0, "F1": 0.0, "B1": 0.0} | {"M1": 0.0, "M2": 0.0, "F1": 0.0, "B1": 0.0} |
| R1-guisave-foreground | H | 2 | 0.8583 | 2.56 | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "B1": 0.0} | {"M1": 0.0, "M2": 0.0, "F1": 0.0, "B1": 0.0} |
| R1-guisave-foreground | MX | 1 | 2.5981 | 7.32 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| R1-guisave-foreground | MX | 2 | 2.9612 | 8.52 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| R1-guisave-foreground | PAR | 1 | 3.4903 | 3.9 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| R1-guisave-foreground | PAR | 2 | 3.0937 | 4.19 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| R1-guisave-foreground | XH | 1 | 1.4597 | 3.38 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| R1-guisave-foreground | XH | 2 | 1.3828 | 2.72 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| R2-fsit-writer | FL | 1 | 1.4142 | 0.72 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 0.5, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| R2-fsit-writer | FL | 2 | 1.5631 | 0.94 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| R2-fsit-writer | H | 1 | 0.6486 | 2.3 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| R2-fsit-writer | H | 2 | 0.6636 | 1.6 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 0.5, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| R2-fsit-writer | MX | 1 | 1.7797 | 4.71 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| R2-fsit-writer | MX | 2 | 1.4904 | 3.03 | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| R2-fsit-writer | PAR | 1 | 2.8371 | 2.18 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| R2-fsit-writer | PAR | 2 | 2.9903 | 2.33 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| R2-fsit-writer | XH | 1 | 0.8641 | 2.02 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0} | {"M1": 0.5, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| R2-fsit-writer | XH | 2 | 0.868 | 1.44 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| R3-chat-synthesis | FL | 1 | 1.3212 | 0.47 | {"M1": 1.0, "M2": 0.0, "M3": 1.0, "F1": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 0.5, "M3": 1.0, "F1": 0.0, "B1": 0.0} |
| R3-chat-synthesis | FL | 2 | 1.4171 | 0.58 | {"M1": 1.0, "M2": 0.0, "M3": 1.0, "F1": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 0.5, "M3": 1.0, "F1": 0.0, "B1": 0.0} |
| R3-chat-synthesis | H | 1 | 0.5792 | 1.42 | {"M1": 1.0, "M2": 0.0, "M3": 1.0, "F1": 0.0, "B1": 0.0} | {"M1": 0.5, "M2": 0.0, "M3": 1.0, "F1": 0.0, "B1": 0.0} |
| R3-chat-synthesis | H | 2 | 0.5958 | 1.34 | {"M1": 1.0, "M2": 0.0, "M3": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 0.5, "M3": 1.0, "F1": 0.0, "B1": 0.0} |
| R3-chat-synthesis | MX | 1 | 1.4039 | 3.66 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "B1": 0.5} |
| R3-chat-synthesis | MX | 2 | 1.1693 | 2.28 | {"M1": 1.0, "M2": 0.0, "M3": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 0.5, "M3": 1.0, "F1": 0.0, "B1": 0.0} |
| R3-chat-synthesis | PAR | 1 | 2.4844 | 1.39 | {"M1": 1.0, "M2": 0.0, "M3": 1.0, "F1": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 0.0, "M3": 1.0, "F1": 0.0, "B1": 0.0} |
| R3-chat-synthesis | PAR | 2 | 2.4471 | 1.39 | {"M1": 1.0, "M2": 0.0, "M3": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 0.0, "M3": 1.0, "F1": 0.0, "B1": 0.0} |
| R3-chat-synthesis | XH | 1 | 0.7594 | 1.9 | {"M1": 1.0, "M2": 0.0, "M3": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 0.5, "M3": 1.0, "F1": 0.0, "B1": 0.0} |
| R3-chat-synthesis | XH | 2 | 0.9238 | 1.69 | {"M1": 1.0, "M2": 0.0, "M3": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 0.5, "M3": 1.0, "F1": 0.0, "B1": 0.0} |
| R4-clean-r2pin | FL | 1 | 1.3073 | 0.47 | {"M1": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "F1": 0.0, "B1": 0.5} |
| R4-clean-r2pin | FL | 2 | 1.5812 | 1.07 | {"M1": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "F1": 0.0, "B1": 0.5} |
| R4-clean-r2pin | H | 1 | 0.669 | 1.44 | {"M1": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "F1": 0.0, "B1": 0.5} |
| R4-clean-r2pin | H | 2 | 0.631 | 1.16 | {"M1": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "F1": 0.0, "B1": 0.5} |
| R4-clean-r2pin | MX | 1 | 2.8882 | 9.25 | {"M1": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "F1": 0.0, "B1": 0.5} |
| R4-clean-r2pin | MX | 2 | 2.4368 | 8.58 | {"M1": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "F1": 0.0, "B1": 0.5} |
| R4-clean-r2pin | PAR | 1 | 2.6599 | 1.9 | {"M1": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "F1": 0.0, "B1": 0.5} |
| R4-clean-r2pin | PAR | 2 | 2.7673 | 2.45 | {"M1": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "F1": 0.0, "B1": 0.5} |
| R4-clean-r2pin | XH | 1 | 0.8286 | 1.85 | {"M1": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "F1": 0.0, "B1": 0.5} |
| R4-clean-r2pin | XH | 2 | 1.0095 | 2.68 | {"M1": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "F1": 0.0, "B1": 0.5} |
| S1-pool-overload | FL | 1 | 1.48 | 0.67 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} |
| S1-pool-overload | FL | 2 | 1.5284 | 0.75 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} |
| S1-pool-overload | H | 1 | 1.0366 | 1.22 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} |
| S1-pool-overload | H | 2 | 0.8852 | 1.16 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} |
| S1-pool-overload | MX | 1 | 2.076 | 4.77 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} |
| S1-pool-overload | MX | 2 | 2.4164 | 6.11 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} |
| S1-pool-overload | PAR | 1 | 3.5784 | 3.26 | {"M1": 0.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} | {"M1": 0.0, "M2": 0.0, "M3": 0.0, "F1": 1.0, "F2": 0.0, "B1": 0.5} |
| S1-pool-overload | PAR | 2 | 3.5357 | 3.07 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} | {"M1": 0.5, "M2": 0.5, "M3": 0.5, "F1": 1.0, "F2": 0.0, "B1": 0.5} |
| S1-pool-overload | XH | 1 | 1.3887 | 2.33 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} |
| S1-pool-overload | XH | 2 | 1.2047 | 2.03 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.5} |
| S2-display-loop | FL | 1 | 1.5446 | 0.69 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} |
| S2-display-loop | FL | 2 | 1.5447 | 0.9 | {"M1": 0.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} |
| S2-display-loop | H | 1 | 0.8653 | 1.6 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} |
| S2-display-loop | H | 2 | 0.8447 | 1.57 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} |
| S2-display-loop | MX | 1 | 2.2922 | 5.46 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} |
| S2-display-loop | MX | 2 | 2.0036 | 5.34 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} |
| S2-display-loop | PAR | 1 | 3.4119 | 2.37 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} |
| S2-display-loop | PAR | 2 | 3.6717 | 3.62 | {"M1": 1.0, "M2": 0.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} | {"M1": 0.0, "M2": 0.0, "M3": 0.0, "F1": 0.5, "F2": 0.0, "B1": 0.5} |
| S2-display-loop | XH | 1 | 1.1507 | 2.23 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 1.0} |
| S2-display-loop | XH | 2 | 1.5039 | 3.17 | {"M1": 1.0, "M2": 1.0, "M3": 1.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} | {"M1": 0.5, "M2": 0.0, "M3": 0.0, "F1": 0.5, "F2": 0.0, "B1": 0.0} |
| S3-disp-resplit | FL | 1 | 1.4037 | 0.6 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} |
| S3-disp-resplit | FL | 2 | 1.3109 | 0.55 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 0.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} |
| S3-disp-resplit | H | 1 | 0.8047 | 1.9 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} |
| S3-disp-resplit | H | 2 | 0.936 | 1.69 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} |
| S3-disp-resplit | MX | 1 | 1.6239 | 3.29 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} |
| S3-disp-resplit | MX | 2 | 2.0146 | 4.15 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} |
| S3-disp-resplit | PAR | 1 | 3.3944 | 2.15 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} |
| S3-disp-resplit | PAR | 2 | 3.2614 | 2.43 | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "B1": 0.0, "B2": 0.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} |
| S3-disp-resplit | XH | 1 | 0.9823 | 2.56 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 0.0, "B2": 1.0} |
| S3-disp-resplit | XH | 2 | 1.2223 | 1.81 | {"M1": 0.0, "M2": 0.0, "F1": 0.0, "B1": 0.0, "B2": 0.0} | {"M1": 0.0, "M2": 0.0, "F1": 1.0, "B1": 0.0, "B2": 0.0} |
| T1-looseends-pin | FL | 1 | 1.5376 | 0.89 | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "F2": 1.0, "B1": 0.0} | {"M1": 0.5, "M2": 0.0, "F1": 0.0, "F2": 1.0, "B1": 0.5} |
| T1-looseends-pin | FL | 2 | 1.5526 | 0.98 | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} | {"M1": 1.0, "M2": 0.5, "F1": 0.0, "F2": 0.0, "B1": 1.0} |
| T1-looseends-pin | H | 1 | 0.8933 | 2.35 | {"M1": 0.0, "M2": 0.0, "F1": 0.0, "F2": 1.0, "B1": 0.0} | {"M1": 0.5, "M2": 0.0, "F1": 0.0, "F2": 1.0, "B1": 1.0} |
| T1-looseends-pin | H | 2 | 0.8514 | 2.38 | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "F2": 1.0, "B1": 0.0} | {"M1": 1.0, "M2": 0.5, "F1": 0.0, "F2": 0.0, "B1": 0.0} |
| T1-looseends-pin | MX | 1 | 4.1632 | 14.52 | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "F2": 1.0, "B1": 0.0} | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "F2": 0.0, "B1": 0.0} |
| T1-looseends-pin | MX | 2 | 2.9611 | 9.07 | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "F2": 1.0, "B1": 0.0} | {"M1": 0.5, "M2": 0.0, "F1": 0.0, "F2": 1.0, "B1": 0.5} |
| T1-looseends-pin | PAR | 1 | 3.8014 | 3.95 | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "F2": 1.0, "B1": 0.0} | {"M1": 0.5, "M2": 0.0, "F1": 0.0, "F2": 1.0, "B1": 1.0} |
| T1-looseends-pin | PAR | 2 | 4.3482 | 4.33 | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "F2": 1.0, "B1": 1.0} | {"M1": 0.5, "M2": 0.0, "F1": 0.0, "F2": 1.0, "B1": 0.0} |
| T1-looseends-pin | XH | 1 | 1.4862 | 3.98 | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "F2": 1.0, "B1": 0.0} | {"M1": 0.5, "M2": 0.0, "F1": 0.0, "F2": 1.0, "B1": 0.5} |
| T1-looseends-pin | XH | 2 | 1.2515 | 2.74 | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "F2": 1.0, "B1": 0.0} | {"M1": 0.5, "M2": 0.0, "F1": 0.0, "F2": 1.0, "B1": 0.5} |
| T2-constvalue-void | FL | 1 | 1.5858 | 1.0 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 0.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 0.0} |
| T2-constvalue-void | FL | 2 | 1.5157 | 0.93 | {"M1": 1.0, "M2": 1.0, "F1": 1.0, "B1": 1.0, "B2": 0.0} | {"M1": 0.0, "M2": 1.0, "F1": 0.5, "B1": 0.5, "B2": 0.0} |
| T2-constvalue-void | H | 1 | 0.8473 | 2.28 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 0.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 0.0} |
| T2-constvalue-void | H | 2 | 0.8492 | 2.5 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 0.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 0.0} |
| T2-constvalue-void | MX | 1 | 2.3554 | 7.8 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 1.0} |
| T2-constvalue-void | MX | 2 | 2.269 | 7.36 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 1.0} |
| T2-constvalue-void | PAR | 1 | 3.4768 | 3.01 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 1.0} |
| T2-constvalue-void | PAR | 2 | 3.7128 | 3.04 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 1.0} |
| T2-constvalue-void | XH | 1 | 1.287 | 3.25 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 1.0} |
| T2-constvalue-void | XH | 2 | 1.0893 | 2.84 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0, "B2": 1.0} |
| T3-handles-gate | FL | 1 | 1.2974 | 0.49 | {"M1": 1.0, "M2": 1.0, "F1": 1.0, "B1": 1.0} | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "B1": 0.0} |
| T3-handles-gate | FL | 2 | 1.299 | 0.48 | {"M1": 1.0, "M2": 1.0, "F1": 1.0, "B1": 1.0} | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "B1": 0.0} |
| T3-handles-gate | H | 1 | 0.6507 | 2.2 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "B1": 0.0} |
| T3-handles-gate | H | 2 | 0.6908 | 1.83 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "B1": 0.0} |
| T3-handles-gate | MX | 1 | 2.4462 | 7.0 | {"M1": 1.0, "M2": 1.0, "F1": 1.0, "B1": 1.0} | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} |
| T3-handles-gate | MX | 2 | 2.1431 | 6.68 | {"M1": 1.0, "M2": 1.0, "F1": 1.0, "B1": 1.0} | {"M1": 1.0, "M2": 0.5, "F1": 0.0, "B1": 0.5} |
| T3-handles-gate | PAR | 1 | 3.1163 | 2.8 | {"M1": 1.0, "M2": 1.0, "F1": 1.0, "B1": 1.0} | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "B1": 0.0} |
| T3-handles-gate | PAR | 2 | 3.0265 | 3.12 | {"M1": 1.0, "M2": 0.0, "F1": 1.0, "B1": 1.0} | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "B1": 0.0} |
| T3-handles-gate | XH | 1 | 1.0092 | 2.53 | {"M1": 1.0, "M2": 1.0, "F1": 1.0, "B1": 1.0} | {"M1": 1.0, "M2": 0.5, "F1": 0.0, "B1": 0.5} |
| T3-handles-gate | XH | 2 | 0.9924 | 3.0 | {"M1": 1.0, "M2": 1.0, "F1": 0.0, "B1": 1.0} | {"M1": 1.0, "M2": 0.0, "F1": 0.0, "B1": 0.0} |

## Mechanical vs blind disagreements (|diff| >= 0.5)

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
