---
name: cloud-credit-interactive-sessions-only
description: "The user's $250 Claude Code cloud-session credit (until 2026-11-05) is drawn first only by cloud sessions the user opens interactively (desktop/web/--cloud); cloud ROUTINES (RemoteTrigger) ran on the subscription windows instead — measured 2026-09-29 and 2026-10-01"
metadata:
  node_type: memory
  pinned: false
  originSessionId: b607b493-a66f-4081-b122-a7a95d2c2a67
  modified: 2026-10-02T03:06:50.439Z
type: decision
status: in-force
date: 2026-10-02
source: memory/cloud_credit_interactive_sessions_only.md
---

# The cloud credit is spent by interactive cloud sessions, not by routines

On 2026-09-29 I tested the cloud by creating two one-time ROUTINES through RemoteTrigger. Their nested `claude -p`
calls reported the same subscription 5-hour / weekly utilisation as local calls, and the credit panel still showed
US$250 of US$250 afterwards. I concluded "cloud work draws on the subscription" and the user dropped the cloud plan.

On 2026-10-01 the user pasted blog posts saying the promo credit is consumed first, and then tested it themselves:
they opened a cloud session from the app and saw it use the credit only — *"확실히 클라우드로 세션 시작하니까 클라우드
토큰만 사용하네. 지금 보면 1달러 사용함"*. My earlier conclusion held only for routines.

## How I apply it

- To spend the credit (and spare the subscription), work must run in a cloud session the USER opens (desktop app
  Code tab, claude.ai/code, or `claude --cloud`), not in a routine I schedule.
- Whether `claude -p` calls spawned INSIDE an interactive cloud session also bill to the credit was still unmeasured
  on 2026-10-01; check that before moving the nested-cell benches (decbench, ucbench, matbench, gsearch) to the cloud.
- 2026-10-02: `claude --cloud` from a LOCAL terminal also bills the credit, and nested `claude -p` inside a cloud
  session does too. `--cloud` refuses non-TTY callers, but launching it UNATTENDED works: a .ps1 that runs
  `Start-Transcript; claude --cloud (Get-Content -Raw prompt.txt)`, started with `Start-Process powershell -File` (new
  console window = a TTY); the transcript holds the session id, and RemoteTrigger get_run_log reads the session's log.
  The cloud clones origin at the pushed branch head and pushes results to its own branch.
- The credit panel (app usage card, "클라우드 세션 크레딧") is the direct readout; compare it before and after.
- Lesson about my own testing: a probe that used a different entry point than the one in question is not evidence
  about that entry point — state which path was tested when reporting.
