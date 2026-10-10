---
name: claude-gpt-debate-live-gdoc
description: "The user's 2026-10-09 discussion setup (they called it \"너무 훌륭함\") — Claude and GPT write each ROUND at the same time and question/critique each other until they converge; a Python program writes every round into a new Google Doc per topic (user watches on the phone); the user steps in through THIS chat; Gemini fact-checks on request"
metadata:
  node_type: memory
  type: project
  originSessionId: b607b493-a66f-4081-b122-a7a95d2c2a67
  modified: 2026-10-09T12:14:42.994Z
type: decision
status: in-force
date: 2026-10-09
source: memory/claude_gpt_debate_live_gdoc.md
---

Why it exists: the user felt the project grew too large from Claude-only strategy talk and wanted a model that works
differently to converge with Claude, watched LIVE with the user able to step in ("모든 대화 끝난 다음에 보고만 하라는게
아님"). They rejected the first turn-by-turn version as "a meeting, not a discussion" — Claude set the agenda and GPT
answered. What they want: "같은 단계에서 서로에게 질문하고 피드백하며 수렴".

How to apply:
- Start ONLY when the user gives a topic and says start. Guide with every command: docs/debate.md. Launcher:
  `powershell -NoProfile -File tools/debate_start.ps1 -Slug <slug> -Topic <topic file>` (WMI-detached; first line of
  the topic = doc title; it prints the Google Doc link).
- Don't paste rounds into the chat (context cost): one line per round from a Monitor; the doc is the live view.
- Relay the user's chat messages with `py tools/debate_gdoc.py say --dir tools/bench/debate/<slug>/relay "<text>"`
  ('멈춰' → `/stop`, '끝내' → `/end`, '계속' → `/continue`, Gemini → `/gemini …`).
- When it pauses, report the two final STATE lines briefly; applying the result to rules/plans is the user's call.
- Login expires every 7 days (Testing app): `py tools/debate_gdoc.py login`.
Related: [[deliverable_first_hooks_outside_runner]].
