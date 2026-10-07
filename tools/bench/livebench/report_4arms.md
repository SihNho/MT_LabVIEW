---
type: bench-report
status: current
date: 2026-10-07
tags: [livebench, runner, agents, rules]
---

# Live bench, 4 arms x 2 cycles (2026-10-06 .. 10-07)

User 2026-10-06: "A 조건, A+1~3 적용 조건, A+1~3 + Karpathy 조건, B 조건 이렇게 벤치 돌려보자. 여기 최적화 결과를
바탕으로 GPT 비교 할 예정임" / "전반적인 플랜의 진척도를 볼 예정" (whole-project progress, not only the ring buffer).

Every arm: own git worktree (V6_bench\<arm>), LabVIEW outputs in claudeDev\bench\<arm>\ only, the same start
(D1_ring_p4s02_20261003_110001.vi md5 84cac487, first purpose = P4 session 3), 2 runner cycles, run one at a time.
Metrics: tools/bench/livebench/<arm>.json (collector lb_collect.py). Harness: tools/bench/livebench/README.md.

| arm | what | wall min | USD | s03 adopted at | cards (PASS) | LabVIEW runs | hand-backs | purpose met |
|---|---|---|---|---|---|---|---|---|
| A | rules S1+E3, purpose flow (Sonnet 5.5 high assignment) | 162 | 82.31 | cycle 2, +152 min | 17 (9) | 15 | 6 | 0/2 |
| B | same rules, legacy flow (Opus judgement dispatches, 6-card cap) | 206 | 96.26 | cycle 1, +62 min | 15 (3) | 52 | - | 0/2 |
| A13 | A + per-function postconditions, test records (advisory), generated docs | 290 | 234.23 | cycle 1, +68 min | 26 (15) | 29 | 6 | 0/2 |
| A13K | A13 + Karpathy's 4 principles in the agent prompts | 197 | 80.67 | cycle 2, +109 min | 19 (10) | 23 | 5 | 1/2 |

Whole-project progress (docs/goalmap.json): no requirement or milestone changed state in any arm. M3 detail: every arm
went from P4 session 2/6 to 3/6 (ops 58 -> 78 of 190); no arm executed session 4.

Not counted: arm A run 1 (CRLF worktree defect, kept as V6_bench\A_run1_20261006_2113: 2 cycles, $125.83, s03 adopted)
and the 12:07 / 12:30 launches that stopped on harness faults (no model cost / killed by the chat's background limit).

## What the numbers say (n = 1 run per arm - read as direction, not proof)

- Same progress everywhere: the arms differ in cost and route, not in result. Run-to-run noise is large (A run 1 vs run 2
  adopted s03 in different cycles with different costs).
- Agent change (A vs B): A cost 14 % less, ran LabVIEW 3.5x less and had a higher card pass rate (53 % vs 20 %); B
  adopted s03 sooner. Not decisive.
- Rules 1-3 (A13 vs A): no progress gain in this run and 2.8x the cost; four material sessions alone cost ~$136
  (collector attributes them by log name - to verify before concluding).
- Karpathy (A13K vs A13): same progress at about one third of A13's cost, close to A's cost; the only arm that met a
  cycle purpose.
- Every arm spent most of its time on the SAME tool faults, in the same order: Error List predictor double count (55 vs
  56), adopt checker reading 'ExecStop' in a docstring echo as a stop, created-object binding when rebasing s04,
  a WhileLoop present only in the simulator, Terminal vs ParameterTerminal class names. These are simulator / checker
  mismatches with real LabVIEW, fixed separately inside each arm and lost at the next arm's reset.
- Guards worked as designed: hand-back by code fired on unexplained failures, out-of-purpose cards (an assignment session
  tried to edit its own guard_assign.py in A and A13K, a card asked for write access to the plan doc) and missing flip
  reports for a gate change. guard_write caught nothing (0 in every arm); launch-gate refusals were 53-64 per arm,
  mostly foreground-LabVIEW-without-timeout friction.

## Harness faults found and fixed during the bench
worktree bed not set (no Error List bed) - over-strict main-tree POST gate - reaper marking inherited main logs - inherited
due state - CRLF checkout vs LF main (contaminated A run 1) - the chat's ~30 min background-task limit killing a child
runner (runs are now launched detached). Still open: inherited violation counts (guard_cycle blocked an A13 launch).
