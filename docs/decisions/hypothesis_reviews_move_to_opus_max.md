---
name: hypothesis-reviews-move-to-opus-max
description: "The user's 2026-09-17 direction on peer-review cost — GPT/codex usage is higher than expected, so hypothesis (failed-prediction) reviews are to be tried on a Claude sub-session under codex's exact constraints, using Opus at effort MAX (not Fable), with web search enabled; codex stays for the outcome review and as the second opinion; switch only after a measured comparison"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 97b1695e-68c2-4985-8cac-1ca3097b3b15
  modified: 2026-09-17T05:56:04.087Z
type: decision
status: superseded
date: 2026-09-17
source: memory/hypothesis_reviews_move_to_opus_max.md
superseded_by: codex_roles_move_to_claude
---

# Hypothesis reviews: Opus at max effort, under codex's constraints — measured before the switch

On 2026-09-17 the user noticed codex (GPT) usage was "생각보다 적지 않은데" and asked whether the hypothesis
peer reviews could be handed to a Claude sub-session — *"메인 세션 말고 서브세션 cli 통해서 코덱스가 받는 제약과
동일 조건으로"* — i.e. the same read-only sandbox, adversarial preamble, timeout, archive and gates.

Two follow-ups fixed the model: Fable at low effort would not save cost (tokens are dominated by the files the
reviewer reads; Fable's per-token price is higher; low effort weakens exactly the "find the other explanation"
work), and on Opus the user said **"opus는 high 보다 더 높게 잡아도 문제 없을 것 같은데"** — so the reviewer is
**Opus at effort max**.

## The agreed shape

- **Hypothesis (failed-prediction) reviews → `peer.ps1 -Agent claude -Model opus -Effort max`**, with **web
  search enabled** for that role (the day's decisive codex refutations were all vendor-document citations, and the
  Claude peer's "no web" was a configuration, not a capability).
- **codex stays** for (a) the outcome review — the layer that must not share our priors (user decision
  2026-09-15) — and (b) a second opinion whenever a Claude review passes a claim about *our own tools*
  ("impossible", "no creator"), because a same-family reviewer shares the blind spot.
- **Switch only on numbers:** the next five failed predictions go to BOTH reviewers; compare defect found /
  seconds / cost from the archive's own cost lines. CLAUDE.md's rule that a Claude peer cannot discharge a failed
  prediction (user decision D3, 2026-09-15) is amended only after that comparison, not before.
- Fable is not used for reviews (standing cost rule).
