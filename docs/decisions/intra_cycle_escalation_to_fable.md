---
name: intra-cycle-escalation-to-fable
description: "The user's 2026-09-25 rule — inside a cycle, a material card that takes too long or fails repeatedly on Opus is re-issued to Fable 5.1 low, then Fable 5.1 medium, then handed to the user; two rungs per card, same flags, and the result card records the rung so Opus-vs-Fable outcomes become data"
metadata:
  node_type: memory
  pinned: false
  originSessionId: 1e5293f3-09a7-4b72-9393-fcba8dd55703
  modified: 2026-09-25T13:12:07.610Z
type: decision
status: in-force
date: 2026-09-25
source: memory/intra_cycle_escalation_to_fable.md
---

# Intra-cycle escalation: Opus → Fable low → Fable medium → user (2026-09-25)

While cycle 85 spent 105 minutes on Opus building two missing scripting verbs, the user asked:

> "한 싸이클 내부에서도 특정 프로세스가 과하게 오래 걸리거나 반복적으로 실패할 경우 Fable 5.1 낮음 (그래도 안된다면
> Fable 5.1 중간) 높여보는 것이 유효할지"

I agreed (cycles 71/72 on fable/low had delivered L7-1b after two Opus failures) and built it the same turn:
agents `material-fable-low.md` / `material-fable-medium.md`, `escalation` and `retry_of_card` fields in the task
and result schemas, the rule in `tools/cycle_prompt.md` and CLAUDE.md.

## How I apply it

- Trigger = a card FAIL with its failure budget spent, or its `budget.minutes` exceeded. Not "it feels slow".
- Rung 1 Fable low, rung 2 Fable medium, then the item goes to `decisions_pending.json`; never a third rung and
  never a third Opus try of the same card.
- The escalated card keeps the same goal, pass list, flags, rules and peers; only the agent changes.
- This is bounded Fable use, not a relaxation of the standing "minimise Fable" rule.
