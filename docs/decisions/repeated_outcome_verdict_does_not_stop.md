---
name: repeated-outcome-verdict-does-not-stop
description: "The user's 2026-09-23 ruling — once they have answered a repeated outcome-review verdict, further repetitions of the same verdict do not stop the runner; the session marks it in STATUS and I report it; only a changed verdict stops the work"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: b5d0cc76-fda8-4724-8899-5a019fc98595
  modified: 2026-09-22T16:14:03.244Z
type: decision
status: in-force
date: 2026-09-22
source: memory/repeated_outcome_verdict_does_not_stop.md
---

# A repeated outcome verdict the user already answered does not stop the runner

The outcome review (every 5 cycles) had returned "no runnable VI, cost not defensible" five times. On 2026-09-20 one
session stopped the runner under the rule "on repetition the work stops for a re-plan with the user" and the user
answered "continue" (Pre-decided 44). On 2026-09-21 the next session, facing the same verdict again, did NOT stop and
escalated in STATUS instead (Pre-decided 83). The Jev contradiction check surfaced the two as an unresolved conflict
and the user ruled:

> **"83번으로 가자."** (2026-09-23)

## How I apply it

- After the user has answered a given outcome verdict, the same verdict recurring is **not** a stop condition: the
  session writes the escalation into STATUS, and I tell the user in my next report. No STOP line, no runner halt.
- The work stops only when the verdict's content changes: a new violation line, or a numbered requirement that
  moved backwards. Then the re-plan question is genuinely new and goes to the user.
- The user prefers to be told, not asked again, about a judgement they have already made. This matches their
  standing preference that the runner finish what it is doing rather than pause for questions.
