---
name: backend_agnostic_project_goal
description: "The user's 2026-10-10 goal — the project must continue from ANY session (Claude Code or Codex/GPT) with the same rules, state and safety; subscription choice after 10-16 decided by measured work-unit cost"
metadata:
  node_type: memory
  type: project
  originSessionId: b607b493-a66f-4081-b122-a7a95d2c2a67
  modified: 2026-10-10T08:35:18.359Z
type: decision
status: in-force
date: 2026-10-10
source: memory/backend_agnostic_project_goal.md
---

User 2026-10-10: "개정 후에는 클로드가 되었든 아니면 지피티가 되었든 어떤 세션에서건 동일한 프로젝트를 진행할 수 있었으면 좋겠음" — they may move the main model to GPT and drop Claude to a lower plan. Current plan Max 20x + ChatGPT Plus runs until 2026-10-16; after that one combination is held for a whole month (downgrade/upgrade churn wasted money: the 5x→20x upgrade last month cost >50만원 with little proration). No budget cap and no usage-based auto-stop in any design ("내가 실시간으로 관리"). Motor port COM3 operation stays as rule 1b (no permanent ownership).

Converged Claude–GPT discussion token-efficiency-01 (16 rounds): rules/decisions/state in the repo (docs/rules, docs/decisions, docs/START.md), CLAUDE.md = AGENTS.md short core; one common guard code (tools/hooks/guardcore.py) + per-backend adapters, tested on FAKE targets (no rig disassembly needed); GPT starts with read-only analysis and card proposals; then same-card pair comparison (time, errors, retries, read tokens, weekly % per work unit) decides the subscription. Cards chat-X1 (rules/decisions/start) and chat-X2 (guard core/Codex) built in worktrees, merged after the running cycle.

**Why:** the user does not know which vendor will carry the project next month; the safety rules must not depend on one vendor's harness.
**How to apply:** new rules and decisions go into the repo files, not only into this memory; never add a budget cap; report verification level as "executor path verified / outside the executor only secondary defence". Related: [[claude_gpt_debate_live_gdoc]], [[deliverable_first_hooks_outside_runner]], [[run_mode_economy_performance]].
