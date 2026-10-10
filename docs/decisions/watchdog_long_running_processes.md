---
name: watchdog-long-running-processes
description: "Any single blocking process must be supervised - past a time threshold, actively verify (dialog check, screenshot) instead of waiting"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1ffa4eb9-19ac-4240-b7d7-6ef33fffb8c1
  modified: 2026-08-28T12:34:14.464Z
type: decision
status: in-force
date: 2026-08-28
source: memory/watchdog_long_running_processes.md
---

# A single process running too long demands verification, not patience

The user's correction, 2026-08-28, after twice watching a LabVIEW COM call sit blocked behind a
hidden modal dialog for 15+ minutes: *"지금도 엄청 단일 프로세스를 15분 넘게 돌리고 있는 것 같은데.
아무래도 단일 프로세스가 일정 시간 이상 돌아갈 때 검증이 필요한 것 같아"* — when a single process
runs beyond a threshold, verification is required.

The failure pattern this targets: a blocking call (LabVIEW `Run` over COM being the canonical case)
whose expected duration is under a minute silently hangs behind a modal dialog, and the session
"waits for the notification" while nothing can ever complete. Backgrounding the command is not
enough — backgrounding only frees the conversation; the process itself still needs a supervisor.

Standing behaviour:

- **Know the expected duration** of any blocking call before starting it (LabVIEW Op runs: seconds).
- **Past ~2-3x the expected duration, actively verify**: check for modal dialogs
  (`lv_gui.ps1 -Action dialogs`), screenshot the blocker, dismiss it, and treat the run as failed —
  rather than waiting for a notification that cannot arrive.
- **Prefer building the watchdog into the tool** (e.g. gscript's run helper polls for dialogs while
  the COM call blocks in a worker thread and auto-recovers) over ad-hoc vigilance, which fades.
- A hard timeout that merely kills the client is the *last* resort — it loses the diagnosis; the
  dialog screenshot IS the diagnosis.

This generalizes the project's earlier lesson that every apparent LabVIEW "wedge" was a hidden
modal dialog: the dialogs are a known, enumerable failure mode, so supervision can and should be
automatic.
