---
name: rules_apply_shelved_benchmark_first
description: The user's 2026-10-11 decision - the rules/hook apply path with blocking (cand-shellguard) is SHELVED, not switched on; the GPT-vs-Claude benchmark comes first, because that was the purpose of the whole effort
type: project
status: in-force
date: 2026-10-11
source: chat 2026-10-11
---

User 2026-10-11: "사실 이 모든 시작은 GPT와 클로드 둘 사이에 벤치를 돌려보는게 목적이었지. 만약 이게 너무 문제가 될 것 같다면 안하는것도 방법일 것 같기는 해..." → "진행" (on the chat's proposal: shelve the apply device, run the benchmark).

Measured before the decision: 74 of 147 commits in 14 days touched tools/hooks or settings (about 5 a day); every one would have needed candidate -> both debaters -> user -> apply once blocking was on.

- Kept on disk, NOT active: tools/rules_apply.py, tools/rules_protected.json, tools/git_precommit_rules.py, tools/bench/candidates/ (cand-shellguard-01@23fd5380, rejected by both debaters in structure-equal-02 round 13 for revision), tools/bench/rules_baseline_20261010.json (status list only). No ledger, no git hook.
- Still active: the common guard tools/hooks/guardcore.py + adapters, the trusted .codex hooks (live-tested 15/0), the guardcore-fix-20261010.
- Discussion structure-equal-02 ended by the user's decision (/end, 2026-10-11).

- 2026-10-12: REMOVED from the tree (user "그렇게 하자", docs/decisions/claude_main_gpt_debate_peer_only.md); recoverable
  from git history at 87e48c28.

**Why:** the device slows every hook fix by hours while GPT is still read-only; the benchmark decides the subscription by 2026-10-16.
**How to apply:** do not switch the device on without the user; revisit when GPT is given write roles. Related: [[backend_agnostic_project_goal]], [[codex_sessions_run_full_access]].
