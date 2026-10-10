---
name: research-fallback-ladder
description: External research must degrade gracefully - Claude runs its own research session when both peer agents are quota-exhausted
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1ffa4eb9-19ac-4240-b7d7-6ef33fffb8c1
  modified: 2026-08-28T13:37:33.517Z
type: decision
status: in-force
date: 2026-08-28
source: memory/research_fallback_ladder.md
---

# Research must never stall on a peer's quota — Claude is the last rung

The user's directive, 2026-08-28, after codex hit its quota mid-session and agy became the only
external researcher: *"agy도 쿼터가 꽉 차서 기다려야 할 수도 있으니, 경우에 따라서는 클로드에서도
세션을 운영할 가능성도 열어놔"* — agy may fill up too, so keep open the option of running research
sessions from Claude itself.

So external research is a **ladder that degrades, never a dependency that blocks**:

1. **One peer per question** — whichever of codex / agy is available. Asking both the same question
   is normally waste, because two models sharing priors can be confidently wrong together; their
   agreement is not verification.
2. **The other peer** when the first is quota-exhausted (the wrapper marks this and the marker file
   must be deleted once quota renews).
3. **Claude's own research** when both are out — direct web search and fetch, or a spawned subagent
   for a genuinely large fan-out. This is not a theoretical fallback: it was already used
   successfully to verify a vendor documentation page that a peer had cited.

The user reinforced the bottom rung explicitly: *"codex 및 agy 둘 다 소진되었다면 클로드라도 외부
조사를 돌려야 한다"* — if both peers are exhausted, Claude must run the external research itself.
The peers are a way to **delegate** the standing "search the web and community before
troubleshooting" rule, never a way to be excused from it. "No peer available" is not a licence to
skip straight to experimenting on the machine.

Waiting for a quota to renew is the one option that is never correct. Whichever rung answers, the
conclusion is still a hypothesis until it is confirmed against the machine or the vendor's own
files — that verification step, not the number of agents consulted, is what makes an answer safe
to act on.
