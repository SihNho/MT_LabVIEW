---
name: claude_main_gpt_debate_peer_only
description: The user's 2026-10-12 decision after the X10 benchmark - Claude stays the main model for all project work; GPT is used only as a discussion agent and peer reviewer, as today
type: project
status: in-force
date: 2026-10-12
source: chat 2026-10-12
---

User 2026-10-12, after tools/bench/matbench/report_x10.md (Claude opus-5-5/high 8/10 vs GPT gpt-6.1-sol/high 4/10 on
matbench T1-T6, GPT partly handicapped by tooling): "그러면 지피티는 그냥 지금 구조대로 토론 에이전트 및 피어리뷰로만 쓰고
클로드를 메인으로 하자. 그러면 사실 지피티와 공용 훅 사용할 필요도 없음."

- Supersedes the working goal of [[backend_agnostic_project_goal]] (any session, Claude or Codex, carries the project):
  GPT does not take material, assignment or judgement roles. Discussions (docs/debate.md) and peer reviews stay.
- Subscription: the benchmark gave no reason to move the main work to GPT (chat recommendation: keep Claude Max 20x,
  ChatGPT Plus for discussions); the user decides the plan after 2026-10-16.
- Rollback, user 2026-10-12 "그렇게 하자" on the chat's A/B/C split:
  - ROLLED BACK (GPT-only, no gain for Claude): scope-cwd-fix (c4efa1ec code: tools/scope_header.py, tools/hooks/
    guard_bash.py, tools/hooks/guardcore.py, docs/guardcore.md back to c4efa1ec^, tools/bench/selftest_scope_cwd.py
    removed; its records stay in tools/bench/debate/scope-cwd-fix/); the GPT bench cell worktree ..\V6_bench\gpt_cell;
    the shelved apply-path device (tools/rules_apply.py, rules_protected.json, git_precommit_rules.py, bench/candidates/,
    their self-tests, rules_baseline_20261010.json - in git history at 87e48c28); the rule "hook/rule changes need both
    agents' agreement" - hooks are again fixed by the chat, which tells the user (as before 2026-10-10).
  - KEPT (helps Claude alone): docs/rules + docs/decisions + docs/START.md + the short CLAUDE.md (start context 42.7k ->
    ~3k tokens); guard_bash false-positive fixes (labview-none scripts need no timeout; `.py` file names not read as a
    launch) and the quoted-absolute-path catch (a real hole); discussion relay fixes.
  - KEPT for GPT in discussions (it runs with full access): .codex/hooks.json + tools/hooks/guardcore.py + adapters.
  - The user's own ~/.codex/matbench.config.toml profile was not touched; the user may delete it.

**Why:** the benchmark showed no case for GPT as the main worker; dual-backend safety costs time on every hook change.
**How to apply:** route all cards to Claude; open a Claude-GPT discussion only when the user asks or the runner's
outcome/stuck triggers fire; GPT sessions stay read-only by instruction.
