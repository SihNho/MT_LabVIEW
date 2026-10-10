---
name: gemini-roles-delegated-to-claude
description: "Gemini CLI (agy) — retired 2026-09-22 for its headless command auto-deny, then BROUGHT BACK by the user on 2026-10-01 as the FIRST arm of web fact questions (gemini-3.1-pro-high, Opus fallback) after a benchmark showed it more accurate on LabVIEW topics; every other role stays on Claude"
metadata:
  node_type: memory
  pinned: false
  originSessionId: b5d0cc76-fda8-4724-8899-5a019fc98595
  modified: 2026-10-01T03:13:54.104Z
type: decision
status: in-force
date: 2026-10-01
source: memory/gemini_roles_delegated_to_claude.md
---

# Gemini: web fact questions first, everything else on Claude

**2026-09-22:** a material session found that `agy` run headless auto-denies its own "command" permission and
returns nothing; the user ruled *"Gemini 역할도 claude에게 위임."* and every Gemini role went to Claude sub-sessions.

**2026-09-29 → 10-01:** the user heard Gemini is much better at web search and asked whether to use it again. Measured
(`tools/bench/gsearch/report_g1.md`, `report_g2.md`): on 8 LabVIEW-topic known-answer questions x 2,
gemini-3.1-pro-high scored 13 correct / 3 partly / 0 wrong vs Opus fact medium 7/8/1 and high 6/9/1, but it cited a
primary ni.com source only 4/16 times (Opus 16/16) and was slower (median 143 s vs 99 s). Making it work headless
took three fixes: run agy from an empty temp directory (it had read our own repo once), give it a web-only brief
instead of AGENTS.md (which told it to read STATUS.md), and the user's hand-set `"deny":["command(*)"]` in
`~/.gemini/antigravity-cli/settings.json` (the permission classifier refused to let me edit that file). The user then
approved: *"이렇게 변경하고 진행하자"*.

## How I apply it

- `peer.ps1 -Kind fact` with no `-Agent` = gemini-3.1-pro-high first (600 s), automatic fallback to the claude fact
  role (Opus 5.5 medium) on error/timeout/empty answer.
- Before an answer drives expensive work (a LabVIEW build), re-check with an explicit `-Agent claude -Kind fact` to get
  primary sources — gemini's answers are usually right but often carry no checkable URL.
- Hypothesis reviews, prior-art, audits and anything that must read our files stay on Claude; Gemini cannot read the
  repository by design.
- If the user's `deny command(*)` rule disappears from the agy settings file, headless gemini calls abort again — check
  that file first when gemini starts failing. agy rewrites the file's formatting on its own; that is harmless.
