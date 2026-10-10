---
name: codex-roles-move-to-claude
description: "The user's 2026-09-18 direction — Codex's weekly quota is nearly gone (9 % left), so the roles Codex played (fact search, failed-prediction review, outcome review, user-facing reports) are to be run on Claude sessions instead, with Fable named as the model"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: b5d0cc76-fda8-4724-8899-5a019fc98595
  modified: 2026-09-18T06:46:29.719Z
type: decision
status: in-force
date: 2026-09-18
source: memory/codex_roles_move_to_claude.md
---

# Codex's roles move to Claude — the user's quota decision of 2026-09-18

The user checked their Codex (ChatGPT CLI) usage and found only 9 % of the weekly limit left:

> *"Codex 잔여량이 생각보다 얼마 남지 않음. 주간 한도 9% 남았음. 아무래도 Codex가 수행중인 역할을 fable로
> 구동하는게 어떨까 싶음."*

Until then Codex was the external voice in this project: the adversarial arm of every failed-prediction review
(dispatched `-Dual` with an Opus/max Claude peer since 2026-09-17), every API/command fact search with the web,
the five-cycle outcome review ("was any of this worth doing?", deliberately never a Claude peer because it shares
our priors), and the writer of user-facing reports (chosen for its prose style).

## What this changes

- Those roles run on Claude sub-sessions from now on; the user named **Fable** as the model. My proposed split,
  offered for their confirmation: hypothesis reviews on the already-measured Opus/max peer alone (no more
  `-Dual`), fact searches and report writing on Fable at low effort with web search, the outcome review on
  Fable at medium — with the remaining Codex quota kept for that outcome review if the user prefers.
- The gate rule "only a codex/gemini exchange can discharge a failed prediction" (`guard_peer.py`, decision D3)
  has to be amended accordingly — the five-comparison trial it was waiting on has effectively run.
- Fable calls carry a fixed cost from the project's rule files being loaded (about $1.5–3 per call measured on
  2026-09-18); peer roles that do not need the rules should use a thin prompt without them.
- Gemini (agy) remains the fallback external voice when a genuinely independent opinion is needed.
