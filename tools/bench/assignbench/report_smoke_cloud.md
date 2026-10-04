# assignbench report - smoke_cloud

tag smoke_cloud, par 4, reps 1, stub no, cases 1, arms OM,OH,SM,SH, spent $2.02 (blind $0.00)

Score per arm-run = mean(must_hit) - 0.5 x max(forbidden), floored at 0 (dec_score). M1 = the ACTION line matches the known action (mechanical). blind = one Opus 5.5 high scorer cell per case. usd / min per arm-run.

## Per arm

| arm | model / effort | n | invalid | action match (M1 mech) | forbidden hit (mech) | blind mean | mech mean | usd / run | usd total | min / run |
|---|---|---|---|---|---|---|---|---|---|---|
| OM | claude-opus-5-5 / medium | 1 | 0 | 1.00 | 0.00 | None | 1.0 | 0.667 | 0.67 | 0.23 |
| OH | claude-opus-5-5 / high | 1 | 0 | 1.00 | 0.00 | None | 1.0 | 0.673 | 0.67 | 0.27 |
| SM | claude-sonnet-5-5 / medium | 1 | 0 | 0.00 | 0.00 | None | 0.5 | 0.337 | 0.34 | 0.14 |
| SH | claude-sonnet-5-5 / high | 1 | 0 | 1.00 | 0.00 | None | 1.0 | 0.341 | 0.34 | 0.2 |

## Action match by known action class (M1 mech, all reps)

| known action | cases | OM | OH | SM | SH |
|---|---|---|---|---|---|
| CLOSE | 1 | 1.00 (1) | 1.00 (1) | 0.00 (1) | 1.00 (1) |

## Per case x arm (answered ACTION per rep ; blind score per rep ; usd mean ; min mean)

| case | known | OM | OH | SM | SH |
|---|---|---|---|---|---|
| A21-c143-purpose-met | CLOSE | CLOSE ; ? ; $0.67 ; 0.2 | CLOSE ; ? ; $0.67 ; 0.3 | ISSUE ; ? ; $0.34 ; 0.1 | CLOSE ; ? ; $0.34 ; 0.2 |

## Mechanical vs blind disagreements (|diff| >= 0.5)

- none

## Known answers (with evidence)

- **A21-c143-purpose-met** (CLOSE): CLOSE: the purpose (P4 session 2 scratch adopted, session-3 prep beside it) is met - 143-3 ADOPTED the s02 file (84cac487) and 143-6 PASSed the session-3 prep 8/0 (dry + prerun). The session-3 LabVIEW card is the next cycle's first act; issuing it now is an acceptable extension, not required. Evidence: tools/bench/cards/result_143-3.json:13; tools/bench/cards/result_143-6.json:1; STATUS.md:62.
