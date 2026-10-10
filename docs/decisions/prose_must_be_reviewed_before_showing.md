---
name: reports-are-written-by-codex-not-proofread
description: "The user finds my Korean wording strange and decided (2026-09-16) that user-facing reports should be WRITTEN by codex (ChatGPT CLI) from my fact list — not written by me and proofread — because \"클로드와 코덱스는 문체가 달라\""
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 97b1695e-68c2-4985-8cac-1ca3097b3b15
  modified: 2026-09-16T08:13:24.407Z
type: decision
status: in-force
date: 2026-09-16
source: memory/prose_must_be_reviewed_before_showing.md
---

# Reports the user reads are written by codex from my facts. I do not write the prose and get it proofread.

## The two instructions, 2026-09-16

First: *"클로드가 말하는 어휘 선택이나 문장이 너무 이상해. AI 워터마크 넣는다고 문장이 난리가 난 것 같은데,
출력해서 보여줄 내용들을 ChatGPT 통해서 검수 받고 보여줬으면 좋겠어."*

I built a proofreading relay (`prose-review`: I write, codex rewrites). The user then corrected the design:

> *"보고는 검수를 받는게 아니라 그냥 chatgpt cli에 의존하는게 좋을 것 같은데? 그냥 클로드와 코덱스는 문체가 달라."*

So proofreading my sentences is the wrong shape — the styles are different at the root, and a rewrite of my
text still carries my sentence shapes. **Codex writes the report; I supply the facts.**

## The rule

- For anything the user will read as a report or explanation — a closing report, a cycle summary, a design
  explanation, a decision they must make — I hand the `reporter` agent a **fact list** (results, numbers, file
  paths, gate outcomes, the question being asked, in bullet form) and it has codex write the Korean report.
  I show that text as-is.
- I still write: one-line direct answers (rule 2b), short mid-work status lines, questions of a sentence or two,
  and anything inside tool calls. The rule is for prose of paragraph length or more.
- Facts are mine and must be exact; wording is codex's. The reporter must not add or drop facts.

## Why

The user reads these to decide things. My wording costs them attention; codex's does not. It is not a
correctness issue — it is a style mismatch the user identified directly, and it applies to every future session.
