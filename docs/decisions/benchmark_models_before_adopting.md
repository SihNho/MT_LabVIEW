---
name: benchmark-models-before-adopting
description: "The user's 2026-09-26 direction — before switching the MATERIAL session's model (Opus vs Fable low/medium) for real cycles, run a proper offline benchmark on replayed past cards with known answers, because material sessions judge and generate, not just execute; cycle-level cost/pass comparisons are not a fair test"
metadata:
  pinned: false
type: decision
status: in-force
date: 2026-09-26
source: memory/benchmark_models_before_adopting.md
---

# Benchmark a model on replayed cards before adopting it for material sessions (user, 2026-09-26)

After the Fable-low material trial (cycles 89-91) showed no gain at 3x cost, I proposed a card-parity A/B inside
live cycles. The user asked for something stronger first:

> "본격 러닝 전에 적절한 비교가 있을지? 재료 세션이 사실 판단 및 생성까지 관여하잖아. 관여하는 범위가 큰데 적절한
> 테스트가 필요해보임" → "벤치 하네스 진행하도록"

## How I apply it

- A model/effort change for material sessions is decided by a REPLAY BENCH: past task cards whose correct outcome is
  now known (a missing verb to report as BLOCKED, a diagnosis with a known file:line, an offline P2 check, a stage
  plan that must simulate to diff 0, a log extraction), each run in a git worktree at the commit before the card,
  LabVIEW forbidden (simulator dry-run only), fixed time and dispatch caps, scored mechanically against the answer
  table (facts present, BLOCKED right, plan diff 0, minutes, cost, dispatches), with a thin peer only for the
  ambiguous rubric items. Harness pattern = the earlier GUI-executor bench (bench-* agents).
- Live-cycle comparisons (cost per cycle, pass rate) are reported as context, never as the decision basis, because
  task difficulty differs cycle to cycle.
- What the replay bench cannot test (reacting to unexpected COM/LabVIEW results) is measured afterwards by card-parity
  A/B inside live cycles, only if the bench is inconclusive.
- Same logic for the escalation ladder rungs: the user asked whether Fable low is enough for a firefighter recall or
  whether medium is needed; data on escalated cards (result-card `escalation`) decides, not a feeling.

## Result and decision (2026-09-26 13:0x, user: "승인")

matbench v1 (5 tasks x 2 repeats, Opus 5.5 low/medium/high/max, $68): score sums 5 / 7 / 8 / 9 of 10, mean minutes
1.1 / 2.0 / 2.6 / 7.6, usd $8 / $11 / $15 / $33. Effort changed the score only on the uid-precision task (T3: high and
max 2/2) and on "report the missing verb" (T1: max only). Fable low re-scored 5/5 (n=1) at ~1.2x high's cost. The user
approved: MATERIAL default = Opus 5.5 HIGH; intra-cycle escalation = Opus max -> Fable low -> user. Fable medium is
dropped from the ladder (no gain over low in v0/v1). Replay-bench numbers, not cycle costs, were the basis.
