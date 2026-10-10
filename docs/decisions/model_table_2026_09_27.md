---
name: model-table-2026-09-27
description: "The user's 2026-09-27 model decision after the 3-day trial (Fable low material, judgement medium/high A/B, replay benches) — judgement Opus 5.5 high fixed, material Opus 5.5 high, ladders Opus max -> Fable low -> stop/user, firefighter = one Opus max cycle, retrospective on Opus high (it had been burning Fable on the outcome role), fact/prose Opus medium; plus scratch-VI verification after two failures of one scripting function"
metadata:
  pinned: true
type: decision
status: in-force
date: 2026-09-27
source: memory/model_table_2026_09_27.md
---

# Model table in force from 2026-09-27 (user: "테이블대로 적용해서 차기 싸이클 부터는 변경된걸로 돌리자")

The user had taken the weekly-limit reboot deliberately to try stronger models for three days and then asked for a
decision ("어떤 조합이 제일 좋아보임?"). Basis: matbench v1 (material effort: low 5 / medium 7 / high 8 / max 9 of 10),
judgement A/B cycles 89-97 (high slightly better, not decisive), the Fable-low material trial (3x cost, no gain),
cycle 87 (fable/low judgement produced nothing), and the peer cost lines (retrospectives on the fable/medium outcome
role: 37 calls, $196 in a week — the biggest Fable sink, an unnoticed leftover of the 09-18 codex-quota move).

| role | in force |
|---|---|
| judgement session | Opus 5.5 high; ladder high -> max -> Fable low -> stop + decision |
| material session | Opus 5.5 high; card escalation max -> Fable low -> decision |
| cycle firefighter | ONE Opus max cycle, then stop |
| retrospective | Opus 5.5 high (thin not required) |
| fact / prose peers | Opus 5.5 medium, thin |
| outcome review | Fable medium thin, every 5 cycles (kept as the one different-priors reviewer) |
| hypothesis / prior-art / ingest, audit | Opus high / Opus medium / Sonnet (unchanged) |

Also decided the same turn: "도구 결함 관련하여 스크래치 vi 검증 부분도 적용" — after two failures of a stage run on the
same scripting function, the next LabVIEW act is a minimal scratch-VI verification of that function, enforced by the
launch gate, because cycles 95-101 escalated nearly every cycle on tool defects that no model change fixes.

## How I apply it

- Do not re-open the model question per cycle; change it only with a new replay bench or a user decision.
- When a Fable line item appears in the weekly usage, look first for a role that silently moved to Fable (as the
  retrospective did) before blaming the trial.
- Runner code changes take effect only after a relaunch at a cycle boundary (STOP marker, then relaunch), which the
  chat does and announces; peer role changes apply to the next dispatch.
