---
name: chat-compacts-instead-of-handoff
description: "The user's 2026-10-02 rule — do not push them to open a new chat when this chat's context passes 50 %; keep going and let automatic context compaction handle it (the user is often remote and cannot open a new chat); the guard's chat context bound is disabled"
metadata:
  node_type: memory
  pinned: false
  originSessionId: b607b493-a66f-4081-b122-a7a95d2c2a67
  modified: 2026-10-01T16:48:53.026Z
type: decision
status: in-force
date: 2026-10-01
source: memory/chat_compacts_instead_of_handoff.md
---

# Keep the chat going and let it compact — no forced hand-off at 50 %

On 2026-10-02, with this chat at ~525k tokens, I told the user the guard would refuse further sub-agent dispatches
above 500k and recommended moving to a new chat. The user answered: *"세션이 50% 넘으면 새 세션 열도록 강요하지
말고 그냥 문맥 압축하는 방향으로 가자. 내가 당분간 로컬에 접속이 어려움"*. Opening a new chat needs them at the
lab PC; compaction does not.

## How I apply it

- `tools/hooks/guard_session.py` `CHAT_CONTEXT_LIMIT = None` (self-test 27/27); the runner's per-cycle dispatch cap is
  unchanged (it binds runner cycle agents only).
- Never recommend a new chat just because the context is large. Instead keep `docs/chat-handoff.md` and STATUS
  current after each real decision, so an automatic compaction loses nothing.
- If the context bound ever has to come back, it is one constant in guard_session.py — ask the user first.
