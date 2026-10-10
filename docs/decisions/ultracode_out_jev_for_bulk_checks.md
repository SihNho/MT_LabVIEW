---
name: ultracode-out-jev-for-bulk-checks
description: "The user's 2026-09-30 decision after the ultracode benches — ultracode (parallel multi-agent Workflow) is not used in this project; cross-document judgement goes to a single Opus, bulk per-item checks go to a Jev loop with script aggregation, mechanical checks to plain Python"
metadata:
  node_type: memory
  pinned: false
  originSessionId: b607b493-a66f-4081-b122-a7a95d2c2a67
  modified: 2026-09-29T17:51:09.883Z
type: decision
status: in-force
date: 2026-09-29
source: memory/ultracode_out_jev_for_bulk_checks.md
---

# Ultracode is out; the division of labour is single Opus / Jev loop / Python (user, 2026-09-30: "좋아")

Measured basis: on the "find contradictions between project documents" task (9 known answers) one ultracode run
spawned 53 sub-agents, used over 13 million tokens in one hour and was killed at the 60-minute cap with no answer,
while single Opus sessions solved the same task in 2–8 minutes for about $1–4 (7–9 of 9 found). On a smaller
counting task all arms scored 10/10 and ultracode cost about 4x single Opus high. The likely reason is structural:
our judgement work needs several documents read together, and splitting it into pieces makes it harder and adds
split/merge cost.

When I proposed "revisit ultracode for checking hundreds of independent items", the user pointed out that Jev is the
better tool there — which matches their 2026-09-23 direction (Jev verifies individual items as typed questions in a
loop, the LLM only sums up).

## How I apply it

| work | who does it |
|---|---|
| judgement or review that needs several documents read together | a single Opus (high, max when needed) |
| hundreds of well-defined per-item checks | a Jev loop plus script aggregation, accuracy measured on a labelled set first |
| purely mechanical checks (file exists, line exists) | a Python script |
| ultracode | not used |

- Do not offer ultracode as an option to the judgement agent or to the runner; the pending "judgement agent picks
  effort/ultracode per card" structure keeps effort choice only.
- Reopen only with a new measurement on a task that splits naturally into independent parts AND cannot be phrased as
  a typed Jev question.
