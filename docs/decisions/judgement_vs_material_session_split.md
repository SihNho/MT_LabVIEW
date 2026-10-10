---
name: judgement-vs-material-session-split
description: "Split sessions by JUDGEMENT vs MATERIAL and put the scarce top model only on judgement — the user's cost decision of 2026-09-15, including the failure budget and the short-judgement-session rule"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 6959fd57-add7-402e-9ed9-9a94ff2b4d5f
  modified: 2026-09-15T04:38:16.019Z
type: decision
status: in-force
date: 2026-09-15
source: memory/judgement_vs_material_session_split.md
---

On 2026-09-15 the user compared token costs directly and concluded that **Opus at high effort is far cheaper than
Fable at low effort**, then set the working rule: *"정말 필수적으로 고차원적인 판단이 필요한 경우에만 Fable 사용하고
Fable이 판단할 재료들은 opus 혹은 하위 모델로 세션을 잡는게 거의 필수처럼 보이는데?"* — and confirmed it as a rule.

Note this INVERTS the earlier framing in `fable_usage_cost_control.md`, where the expensive model did the judgement
and a cheap model did mechanical work. The corrected structure is the same idea seen from the cost side: the scarce
model is spent ONLY on judgement, and a cheaper-but-capable model (Opus) prepares the material it judges. Opus is not
"the lower tier" here — it is the material-preparation tier, which is where most of the wall-clock time actually goes.

## What counts as MATERIAL (separate session, Opus high by default)

- Measuring LabVIEW API facts: property-ID short-name censuses, class hierarchy checks, reading a VI's terminal names.
- Writing and running recipes that follow an already-verified pattern; grepping logs; updating INDEX / NAMES / STATUS.
- Dispatching peer reviews and collecting their answers (dispatch and collection are material, not judgement).
- Extracting bare facts from a failed run: which gate failed, with which values.

## What counts as JUDGEMENT (the scarce model, or Opus max while Fable budget is exhausted)

- Design decisions and choosing what to accept from a peer review.
- Whether a change violates rule 1a (does it alter the original's computation?).
- Diagnosing a failure when hypotheses genuinely diverge.
- Designing the discriminating experiment: what measurement would separate the candidates.

## Two rules that make the split actually cheaper

1. **Failure budget of 2 for a material session.** Two failed builds and it stops, writes the logs and state down,
   and hands the problem to a judgement session. The motivating case: `OpCaseFrames_v0` looked like a closed-spec
   repeat of a verified pattern and still failed five times — a material session grinding through that is more
   expensive than the judgement it was avoiding.
2. **Judgement sessions stay SHORT.** A judgement session that has grown to 78% of its context window defeats the
   purpose, because every turn re-reads the whole thing. Load only STATUS.md, the relevant plan document, and a
   summary of the failing log — never the material session's full history.

## Current budget state

Fable's budget was exhausted for the week of 2026-09-15, so **judgement runs on Opus max** in the meantime. The split
itself still applies: it is about which session does what, not about which model is available this week.
