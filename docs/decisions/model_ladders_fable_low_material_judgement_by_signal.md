---
name: model-ladders-fable-low-material-judgement-by-signal
description: "The user's 2026-09-26 decisions — use the weekly quota before Monday by making Fable 5.1 low the default MATERIAL model until the renewal (revert reminder set), and raise the JUDGEMENT session (Opus high, then Fable low, then Fable medium) only on runner-measured signals (next.json unchanged, judgement-fault retrospective slugs), resetting after a delivery"
metadata:
  node_type: memory
  pinned: false
  originSessionId: 1e5293f3-09a7-4b72-9393-fcba8dd55703
  modified: 2026-09-25T15:45:29.404Z
type: decision
status: superseded
date: 2026-09-25
source: memory/model_ladders_fable_low_material_judgement_by_signal.md
superseded_by: model_table_2026_09_27
---

# Model ladders: Fable low material until Monday; judgement raised by signal (user, 2026-09-26)

> "지금 3일 안에 사용량 다 써야하는데, 당분간 Fable 5.1 low 사용빈도를 높여보는 건 어떻게 생각하는지?"
> "판정 세션은 필요에 따라서 medium 상위 혹은 fable로 교체하는 것도 생각해보는게 어떨지"

I agreed on the data (fable/low firefighter cycles 71/72 delivered where Opus failed twice; a fable/low judgement
cycle 87 produced nothing) and made both mechanical in `cycle_runner.py` (card chat-M1), CLAUDE.md "MODEL LADDERS".

## How I apply it

- Material default = Fable 5.1 low until 2026-09-28 07:00 KST (weekly renewal); a one-time app reminder fires then
  and I compare Fable-vs-Opus material cycles (result cards' `escalation` field) before choosing the default.
- Judgement stays Opus 5.5 medium by default and moves up only on file-measured signals: `next.json` unchanged or
  a judgement-fault slug in the last retrospective; ladder Opus high → Fable low → Fable medium → runner stop with a
  decision item; a delivering cycle resets it. "필요에 따라" always means a logged trigger, never a feeling.
- The user's intent when quota is about to expire: spend it on cycles, weighted toward Fable, rather than let it
  lapse — while keeping the standing "minimise Fable" rule as the steady state after renewal.
- Judgement effort A/B until Monday (user, 2026-09-26: "Opus 5.5도 기본을 medium이 좋을지 high가 좋을지도 판단 필요할듯"):
  no cycle had run judgement at high, so there was no basis to choose. `cycle_runner.py --judge-ab` alternates the
  level-0 effort by cycle parity (odd = medium, even = high) until 2026-09-28 07:00 KST, logs a `JUDGE-AB` line and
  records `effort` in the cycle card; a triggered ladder level overrides it. On Monday I compare minutes, cost,
  deliveries, judgement slugs and unchanged-NEXT counts per effort and propose the default; the user decides.

## Outcome and reversal (user, 2026-09-26 morning: "91 사이클까지 보고 재료 세션은 opus로 변경하자")

After 2.5 cycles with Fable low as the material default (cycles 89-91) the per-cycle cost tripled ($50-55 vs $19),
cycle time doubled (114-125 min vs 65) and the card pass rate did not improve; the failures were the same classes
(missing scripting verb, script bug), which a cheaper model does not fix. The user decided to revert the material
default to Opus 5.5 medium at the end of cycle 91, before the Monday renewal. Lesson: Fable pays only as an
ESCALATION rung on a card Opus already failed twice (cycles 71/72), not as a blanket default; when the user proposes
spending quota on a stronger model, compare cost per delivery after two cycles and say plainly if it is not paying.
The same conversation added two process rules the user approved: (2) any script that MODIFIES a VI through COM goes
through the stage dry-run + offline pre-run gate regardless of its file name (diag_* scripts had bypassed it and
broke a VI three times in cycle 90), and (4) a task card names what it `requires` (ops, donor files, terminals) and
the material session verifies their existence offline FIRST, returning BLOCKED instead of designing around a hole;
a cycle is capped at 6 cards. Wall-time facts behind it: a real measurement run ("leg") costs ~7 min per 120 s
because of LabVIEW restart + bead-pick GUI; peer reviews ~20 min per cycle; cycle close ~15 min.
