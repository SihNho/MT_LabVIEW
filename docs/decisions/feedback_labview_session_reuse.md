---
name: feedback-labview-session-reuse
description: "Don't close/reopen the LabVIEW GUI-automation session between steps — reuse whatever instance is already open"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 52d900cc-eddf-491c-ac00-c5055911beed
  modified: 2026-08-25T04:07:59.461Z
type: decision
status: in-force
date: 2026-08-25
source: memory/feedback_labview_session_reuse.md
---

Don't force-close and relaunch LabVIEW between inspection/edit steps during GUI-automation work on this
project. Reuse the already-open instance (switch files via File > Open or Ctrl+E from within it, close
just the specific VI window if needed) instead of killing the whole LabVIEW.exe process and relaunching.

**Why:** the user corrected this directly (2026-08-25) after several turns of repeatedly
`Stop-Process -Force`-ing LabVIEW and relaunching fresh for each new VI to inspect. Relaunching is
slower (7-9s splash/load time each time) and throws away window-position/zoom-level state for no
benefit, since nothing was ever unsaved/at-risk that required a clean restart.

**How to apply:** when starting to inspect or edit a different VI mid-session, prefer opening it into
the existing LabVIEW instance (e.g. launch a second `LabVIEW.exe <path>` command targeting the same
already-running instance, or use File > Open within the open editor) rather than
`Get-Process LabVIEW | Stop-Process -Force` first. Only close/relaunch if the instance is actually in a
broken state (unresponsive, wrong file loaded with unresolvable stale dialogs) — not as a routine reset.
See [[labview_vi_analysis_skill]] and [[project-v6-parallelization]].
