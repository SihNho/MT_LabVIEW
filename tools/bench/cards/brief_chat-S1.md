# brief chat-S1 — the judgement agent chooses effort (and ultracode) per card (user 2026-09-29)

User decisions (chat 2026-09-29): "판단에이전트가 모델을 결정하는 것 관련: 제안한 구조로 진행해보자" · "그렇게 진행하면
좋겠음" · usage limits all retired ("사용량은 내가 실시간으로 체크하고 매뉴얼하게 통제") · ultracode: no agent-count cap,
but "ultracode 에이전트를 복수로 띄우지 않는 것은 동의함" (one ultracode run live at a time) · not for peer reviews ·
model changes on the decision bench are ON HOLD (decbench too weak) — this structure is how variation is allowed instead.
Rig 실험중: NO LabVIEW. Runner stays stopped. Offline tooling only.

## What to build
1. **Card fields** (`docs/protocol/` task/1 + result/1 schemas, `tools/protocol.py` validate):
   task/1 optional `exec: {"effort": "high"|"xhigh"|"max", "mode": "single"|"ultracode", "reason": "<why>"}`;
   default = high/single when absent (today's behaviour). result/1 echoes `exec` plus measured `minutes`, `usd` if
   known, so effort-vs-outcome data accumulates.
2. **Routing:** effort is fixed per agent definition, so add `.claude/agents/material-xhigh.md` (claude-opus-5-5, effort
   xhigh; same body as material.md) next to `material.md` (high) and `material-opus-max.md` (max). For `mode:
   ultracode`: PROBE how a material card can run as ultracode (agent frontmatter `effort: ultracode`? a `claude -p
   --effort ultracode` cell under bgrun as tools/bench/ucbench does?). Pick the working route, document it, self-test it.
3. **Guard** (`tools/hooks/guard_session.py`): a CARD dispatch whose `exec` does not match the subagent_type
   (e.g. exec.effort max via `material`) is refused with the right agent name; `exec` without a `reason` is refused;
   at most ONE ultracode run live at a time (track like the pipeline's live list); peer reviews never ultracode
   (peer.ps1 roles unchanged). No usage/cost ceilings (retired by the user).
4. **Judgement prompt** (`tools/cycle_prompt.md` and the judgement agent's instructions): one short section — the
   judgement agent may set `exec` per card with a reason; model swaps (Opus↔Fable) and model-table changes go to
   `tools/bench/decisions_pending.json`, never decided by the agent. The escalation ladder (material → opus-max →
   fable-low) is unchanged.
5. **CLAUDE.md**: one amendment line in §3 (model ladders) citing the user's words above.
6. Self-tests: protocol schema cases, guard cases (match/mismatch, missing reason, second ultracode refused, chat vs
   cycle scope), existing selftest_guard_session 27/27 stays green. No runner restart, no git commit.

Return result/1: files changed, self-test counts, the ultracode route chosen and its probe evidence, `open:`.
