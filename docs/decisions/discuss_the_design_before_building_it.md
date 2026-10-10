---
name: discuss-the-design-before-building-it
description: "When the user raises an idea as a question (\"이런 게 필요하지 않은지\"), that is an invitation to discuss the design — not an instruction to implement it; I built the prior-art review in one turn with zero design discussion and the user called it out"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 1c79eb01-7150-4a78-9689-e6d4f34f7800
  modified: 2026-09-15T10:08:43.865Z
type: decision
status: in-force
date: 2026-09-15
source: memory/discuss_the_design_before_building_it.md
---

# A question about whether something is needed is not a request to build it

On 2026-09-15 the user proposed adding a review layer, phrased as a question:

> *"기존 분석한 도큐먼트 및 코드를 참조하여 현재의 방향을 피어리뷰 하는 세션이 필요하지 않은지"*

Within a single turn I wrote a memory, wrote `tools/prior_art_review.py`, wrote a plan file, and dispatched the
first review. The user's response was exact:

> *"어떤 식으로 피어리뷰 잡을건지 디스커션 하나도 없었어"*

Every design decision in that tool was mine, made silently: who reviews it (I picked codex, though the claude peer
is the project's "does this match our files" auditor and is arguably the better fit), what evidence it receives,
when it fires, what questions it asks, what its verdicts mean, and — the biggest one — **its scope**. The user
asked for a review of *the current DIRECTION* against prior analysis; I built a prior-art check on *the next
build*. That narrowing was never stated, let alone agreed.

## The rule

When the user raises an idea as a question, or says "…하지 않은지", "…필요할 것 같은데", "생각이 듦" — **put the
design choices on the table first**: the two or three real forks, my recommendation for each, and what each costs.
Build after they choose. Speed is not the thing being optimised here; their design input is, and it is the input I
cannot generate myself.

This is distinct from an instruction. "이걸 고치도록", "진행해", "C로 가자" are decisions and should be executed
without a round trip. The tell is the question mark and the hedged verb, not the topic.

## Why it matters beyond politeness

Building first destroys the option. Once the tool exists and has run, the discussion becomes "should we keep this?"
rather than "what should this be?", and the design I happened to pick becomes the default by inertia. The user is
the one holding the rig knowledge, the cost constraints and the priorities — the exact inputs a design needs.

## 2026-09-24 addition — finish the whole structure discussion before dispatching builds

During a multi-item structure discussion the user said "먼저 적용 하고 2번 안건으로 가자", I dispatched two material
builds, and two turns later a cross-cutting topic came up (a standard inter-session protocol with flags). The user:
"아니, 그런데 지금은 규약 다듬기 먼저 해야하지 않아?" — the builds had to be stopped and parked. When a discussion is
still open and a later item can change how everything is built (protocols, message formats, gates), dispatch only
documentation of decisions; start builds once the discussion's cross-cutting items are settled, and say so.
