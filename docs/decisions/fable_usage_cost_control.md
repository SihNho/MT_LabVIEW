---
name: fable-usage-cost-control
description: "Minimise Fable usage and push work onto Opus sub-sessions — the user's standing cost rule (2026-09-14, re-issued and widened 2026-09-16 even after upgrading the subscription)"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 97b1695e-68c2-4985-8cac-1ca3097b3b15
  modified: 2026-09-16T07:51:10.067Z
type: decision
status: in-force
date: 2026-09-16
source: memory/fable_usage_cost_control.md
---

# Fable is the scarce resource. Spend it on judgement only; everything else goes to Opus sub-sessions.

## The rule, in the user's words

2026-09-14: Fable usage was burning *"말도 안되게 빠른"* after a 13-hour session — control it.

2026-09-16, **after upgrading the subscription**, re-issued and widened:

> *"Fable의 사용량을 최대한 줄이고, 필요하다면 하부 세션을 늘려서라도 opus 비중을 높이는 게 좋음."*

So an upgrade does **not** relax the rule. The direction is unconditional: **minimise Fable, and if raising the
Opus share means spawning more sub-sessions, spawn them.** Session count is not the cost the user is watching;
Fable tokens are.

## What it means in practice

- **A Fable session is a JUDGEMENT session and nothing else**: design decisions, what to accept from a review,
  rule-1a calls, diagnosis when hypotheses genuinely diverge, designing the discriminating experiment. It reads
  STATUS.md, the plan document and a failure summary — and stays short.
- **Everything else is MATERIAL and goes to Opus** (high effort by default): writing and running recipes and
  diagnostics, reading logs, grepping, patching code, dispatching peers and collecting answers, STATUS/INDEX
  bookkeeping, extracting facts from a failed run.
- **Prefer more Opus sub-sessions over doing it here.** When a judgement session finds itself about to write a
  recipe, read a long log, or patch a wrapper, that is the signal to hand off — even if the handoff costs an
  extra session.
- **The failure I made on 2026-09-16, which triggered the re-issue:** a Fable session did the whole cycle —
  recipes, log reads, a 26-wrapper patch, peer dispatches — in one context. That is the pattern to stop.

## Why (the user's reasoning, 2026-09-15)

Opus at high effort is far cheaper than Fable at low; Fable's judgement is only worth paying for when the
question genuinely needs it. Material preparation is where most wall-clock time goes, so that is where the cheap
model belongs. Splitting also keeps judgement sessions short, which is what makes them good.
