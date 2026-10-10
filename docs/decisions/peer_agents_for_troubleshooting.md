---
name: peer-agents-for-troubleshooting
description: "The user wants Codex and Gemini connected to the project directory as read-only research sub-agents that Claude dispatches during troubleshooting, with Claude keeping all judgement and execution"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1ffa4eb9-19ac-4240-b7d7-6ef33fffb8c1
  modified: 2026-08-28T05:33:43.853Z
type: decision
status: in-force
date: 2026-08-28
source: memory/peer_agents_for_troubleshooting.md
---

# Codex and Gemini as read-only sub-agents, Claude as the manager

The user's plan, 2026-08-28: *"지금의 디렉토리에 Codex 및 Gemini를 같이 연결해두고, 너가 관리자로서
트러블슈팅이 필요한 단계에서 하부 에이전트로 부리는거야"* — connect Codex and Gemini to this project
directory and have Claude, as the manager, dispatch them as sub-agents at the points where
troubleshooting is needed. The motivation is discussion, direction-setting, and mutual review.

**Why pointing them at the directory matters.** The usual objection to a peer model is the cost of
transferring context. That objection largely disappears when the agent can read the project's own
curated documents, which is exactly what the two-tier documentation discipline was built for: a cold
agent reads the status document and the skill and is oriented for free. So the setup cost is much
lower than briefing a model by hand.

**The division of labour that keeps it safe.** Claude stays the only execution path that touches
LabVIEW — the project's rule that only one execution path may act at a time is not negotiable, and a
peer agent that "helpfully" runs a VI or edits a file would break it and could reach hardware. Peers
are therefore **read-only**: they search, they read the docs, they attack a hypothesis, and they
write nothing but their answer. Their output is a *hypothesis*, never evidence; it gets confirmed
against the machine or the vendor's own files before it is acted on.

**When to call them** — the trigger the user's own critique established: **immediately before
building something**, not merely before committing to a hypothesis. The expensive mistakes are
construction, not deduction.

Keep the prompt narrow ("here is the error and what I tried, attack this hypothesis") rather than
open-ended ("what should we do with this project"), because a broad question produces mush from a
cold agent while a narrow one produces a checkable claim.

**The quota constraint that must shape any implementation.** The user runs both peers on cheap
subscriptions that can hit their token limit mid-session, and warned: *"토큰 끊겼는데도 대답
기다리다 보면 5시간 그냥 버려버릴수도 있다"* — waiting on an answer that will never come can throw
away hours. So a peer call must never be able to block the work:

- every call gets a **hard timeout** and runs in the background, never in the foreground;
- the wrapper must distinguish *answered* / *timed out* / *quota exhausted*, because a quota error
  means every later call to that agent will fail too — record it and stop calling that agent for the
  rest of the session rather than paying the timeout again each time;
- **fail open**: a peer being unavailable degrades to working without it, never to waiting. The peer
  is an optional accelerator, and Claude's own web search is the fallback.
