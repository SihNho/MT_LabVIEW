---
name: wiki_agent_debate_and_machine_notes
description: "2026-10-10 — the Claude–GPT debate was copied OUT of V6 into the Obsidian-비서 wiki as skill agent-debate (manual start only, user picks read scope, Google Docs, ingest via Sources/); each PC connected to the wiki gets Assistant/Machines/<host>.md"
metadata:
  node_type: memory
  type: project
  originSessionId: 8ed349e2-e5c6-47b5-a07f-e368b50dda85
  modified: 2026-10-10T05:05:28.357Z
type: decision
status: in-force
date: 2026-10-10
source: memory/wiki_agent_debate_and_machine_notes.md
---

The user wanted the V6 debate (see [[claude_gpt_debate_live_gdoc]]) for the LLM wiki and paper writing, **kept separate from
V6**. Built 2026-10-10: `Obsidian-비서/.agents/skills/agent-debate/` (SKILL.md + scripts copied and generalised from
V6 `tools/debate_*.py`; V6 files untouched). Their conditions: no automation (start only when they say), they choose
what the speakers read (whole wiki / specific notes / web / Gemini), no hooks, Google Docs as the live record, finished
debates exported into `Sources/inbox/` then the normal ingest, and it must run on other PCs (Windows).

**Why:** they will mostly run it from another PC; the wiki is Dropbox-synced, so per-PC state is recorded IN the vault —
one `Assistant/Machines/<hostname>.md` per PC, edited only on that PC, used later as the disconnect checklist
(user: "나중에 PC에서 연결 해제할 때도 참조하기 좋잖아"). `Tooling Status.md` lists the PCs.

**How to apply:** changes to the V6 debate do not flow to the wiki copy (and vice versa). Work files go to
`%USERPROFILE%\.agent-debate\` — not AppData (the Claude app virtualises AppData writes; a WMI-detached worker cannot
see them, measured 2026-10-10) and not Dropbox. Pending: moving Tooling Status's P01 '로컬 환경' section into
`Machines/20185292-P01.md` needs the user's approval; no real-model / real-Google-doc run done yet.
