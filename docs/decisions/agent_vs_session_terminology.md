---
name: agent-vs-session-terminology
description: "The user's 2026-09-29 terminology — \"에이전트/agent\" is a Claude instance spawned by the runner or the chat (judgement agent, material agent, log-reader, peer); \"세션/session\" means only a new conversation window with the user"
metadata:
  node_type: memory
  pinned: false
  originSessionId: aa054aba-9e4f-48b1-9e24-88ad783da19a
  modified: 2026-09-29T09:03:01.074Z
type: decision
status: in-force
date: 2026-09-29
source: memory/agent_vs_session_terminology.md
---

On 2026-09-29, after a detour caused by my using "session" for both the runner's per-cycle judgement instance and
the user's chat window, the user fixed the vocabulary: "이제는 헷갈리지 않도록 에이전트와 세션을 확실히 구분해서 말할게.
세션은 새로운 대화창으로".

## How I apply it

- In reports and questions to the user: "판단 에이전트", "작업 에이전트", "로그 요약 에이전트", "피어 리뷰 에이전트" for
  anything the runner or I spawn; "세션" / "대화 세션" / "새 대화창" only for a conversation window with the user.
- The runner itself is a Python script, not an agent — call it "러너 (스크립트)".
- Internal code and docs keep their existing words (CYCLE_SESSION, "judgement session" in CLAUDE.md); do not
  mass-rename (see the no-coined-terms memory); translate when speaking to the user.
