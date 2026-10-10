---
name: labview-restart-standing-permission
description: The user granted standing permission to restart LabVIEW - no need to ask each time
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-08-29T12:36:29.453Z
type: decision
status: in-force
date: 2026-08-29
source: memory/labview_restart_standing_permission.md
---

# LabVIEW restarts have standing permission — stop asking each time

On 2026-08-29, after Claude asked for permission to restart the shared LabVIEW instance to clear a
VI-Server wedge, the user replied *"재시작 항상 오케이"* — restarting is **always** OK.

This replaces the earlier per-incident etiquette ("a LabVIEW restart clears them — ask the user
first, the instance is shared"). The word "항상" widens it into a standing rule: when a restart of
LabVIEW is the right fix (a wedged VI server, zombie windows of deleted scratch VIs, stale
in-memory state), do it without pausing for approval, and simply report that it was done.

Two boundaries that this permission does NOT change:

- **Save state first, as always.** Everything of value must already be on disk before killing the
  process — which the fleet's standing "save the target" discipline guarantees. A restart discards
  every in-memory edit silently, which is precisely why it works as a cleanup.
- **It is permission to restart LabVIEW, not to touch originals or hardware.** Rule 1 (never save
  an original) and the hardware bans are unaffected. If a Close/Save dialog listing an original
  ever appears during a graceful shutdown, the answer is still Cancel — or avoid the dialogs
  entirely by killing the process, which saves nothing.

Practical note: killing `LabVIEW.exe` outright is usually the cleaner restart here, because a
graceful exit prompts save dialogs for dirty scratch VIs whose files have already been deleted.
