---
name: cycles-run-in-fresh-sessions-via-runner
description: "The user's 2026-09-17 decision on the long-session problem — every cycle runs in a FRESH judgement session spawned by a script (cycle runner, claude -p, Opus at effort max), never carried on in the same conversation; the interactive chat is for talking with the user only"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 97b1695e-68c2-4985-8cac-1ca3097b3b15
  modified: 2026-09-17T10:45:42.741Z
type: decision
status: in-force
date: 2026-09-17
source: memory/cycles_run_in_fresh_sessions_via_runner.md
---

# One cycle = one fresh session, spawned by a runner — Opus max for judgement

On 2026-09-17 the user asked why the session had grown so long. The causes were that I kept running new cycles
inside the same conversation after the retrospective (against CLAUDE.md §3 "session = one cycle"), and that
material sessions came back one judgement question at a time. I offered two ways to enforce "one session per
cycle": the user opens a new session each cycle, or a script does it. The user chose the script:

> **"2번으로 가자. Opus max"**

## What this means

- **A cycle runner** (`tools/cycle_runner.py`) loops: spawn a fresh `claude -p` judgement session that reads only
  STATUS.md and the current plan, runs one cycle, writes the retrospective and STATUS NEXT, and exits; the runner
  checks the exit and NEXT, then spawns the next one. Each session starts from an empty context, so per-turn cost
  stays flat and the loop runs unattended overnight.
- **The judgement model in those sessions is Opus at effort max**, not Fable (standing cost rule). Fable is not
  the default judge of a cycle.
- **Stop conditions belong to the runner**: a STOP marker in STATUS.md written by the user, the same failure two
  cycles in a row, and the usage-limit rule (resume at renewal + 2 min).
- **The interactive chat window no longer executes cycles.** It is for talking with the user: answer questions
  from STATUS and the latest retrospective, and redirect the runner by editing STATUS NEXT or STOP. So it must not
  grow long again.
- A session gate hook (`guard_session.py`, PreToolUse on Agent) refuses new material dispatches once the
  retrospective has run in that session, and above a dispatch cap (8 per session), so a session cannot quietly
  carry a second cycle even if the rule is forgotten.
- Plans carry a "pre-decided" section so material sessions apply decisions already made instead of returning
  them as questions.
