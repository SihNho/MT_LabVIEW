---
name: opus-55-pinned-effort-high-not-max
description: "The user's 2026-09-23 decision — pin Claude Opus 5.5 by explicit model id for judgement, review and material sessions, and run judgement at effort HIGH (not max) because above high the gain is small and the cost triples; requires Claude Code ≥ 2.1.280"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1e5293f3-09a7-4b72-9393-fcba8dd55703
  modified: 2026-09-23T06:59:03.026Z
type: decision
status: in-force
date: 2026-09-23
source: memory/opus_55_pinned_effort_high_not_max.md
---

# Opus 5.5 pinned by id; judgement at effort high, not max

On 2026-09-23 the user pointed at a discussion (news.hada.io/topic?id=34142) reporting that reasoning effort above
"high" gives little and can hurt, and then asked about moving to Opus 5.5. The measured basis in that thread was the
Artificial Analysis index for Opus 5.5: low 42 / medium 51 / high 54 / xhigh 56 / max 58 points at $0.55 / $1.34 /
$1.82 / $3.46 / $5.98 per task — the "quality drops" part was anecdote (reasoning-budget exhaustion on simple tasks),
the cost cliff was measurement. The user agreed to the order I proposed: update the CLI, verify the model answers,
then change the settings. Their rig state was "experiment starting", so no LabVIEW was used for any of it.

What was changed (commit b4127fd):

- `tools/cycle_runner.py`: `--model` default `claude-opus-5-5`, `--effort` default `high` (was alias `opus` / `max`,
  the user's 2026-09-17 "Opus max" decision, now superseded by them).
- `tools/peer.ps1`: role `hypothesis` = `claude-opus-5-5` / `xhigh` (was opus/max); role `priorart` = 5.5 / high.
- `tools/prior_art_review.py` default model 5.5; `.claude/agents/material.md`, `log-reader.md`,
  `motor-limit-checker.md` `model: claude-opus-5-5`.
- Claude Code CLI updated 2.1.250 → 2.1.280 (5.5 is refused below 2.1.280).

**Amended the same afternoon** ("오케이 테이블대로 반영하자", commit e160be0) after checking Anthropic's docs: Opus 5.5
does not share Opus 5's effort scale — its **medium** is the default and scores as Opus 5's **max** on the
Artificial Analysis index. The user also found 700-second reviews too long. Table in force: judgement medium ·
prior-art medium · material medium · hypothesis review high · log-reader low. First runner cycle is compared with
cycle 65; a slot whose retries or review count get worse goes back up one notch, nothing else changes.

## How I apply it

- Never use the bare alias `opus` in runner, peer or agent settings: it resolved to `claude-opus-5` and an alias
  change would silently move the cost/quality baseline. Pin the id.
- Default effort for judgement and material sessions is high. Reserve xhigh for the adversarial failed-prediction
  review; do not put max anywhere without the user asking.
- The next runner cycle after this change is the comparison against cycle 65 (opus-5/max, 80 min, $48.08): report
  time, cost, review count and retrospective slugs side by side.
