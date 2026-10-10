---
name: labview-automation
description: Automate LabVIEW programmatically - edit block diagrams with VI Scripting, and drive the LabVIEW GUI reliably when scripting cannot reach. Use whenever a task involves creating, editing, wiring or inspecting a LabVIEW .vi; enabling loop parallelism; dropping subVIs; adding structures or constants; decoding VI Scripting errors (1057/1059); or clicking anything inside the LabVIEW editor. Also use when choosing a VI Scripting library, or when GUI automation of LabVIEW is misclicking, hitting the wrong window, or failing to wire terminals.
---

# LabVIEW Automation - moved to docs/labview/

The technique now lives in the repository so that ANY session (Claude Code or Codex) reads the same text
(card chat-X1, user 2026-10-10). The files were moved verbatim; line numbers are unchanged.

Read, in full, before any LabVIEW work:

1. `docs/labview/SKILL.md` - the index and Rule 0 (prefer code over clicking), then the reference for the topic:
2. `docs/labview/references/vi-scripting.md` - create/wire/inspect diagram objects by script, libraries, ops
3. `docs/labview/references/com-driving.md` - drive LabVIEW from Python/COM, save, hangs and silent failures
4. `docs/labview/references/gui-recipes.md` - clicking in the editor when scripting cannot reach
5. `docs/labview/references/files-and-formats.md` - `.vi` files offline, NI install paths, IMAQ persistence

The helper scripts stay here: `scripts/lv_gui.ps1`, `scripts/uitars_grounder.py` (the project's own copies are
`tools/lv_gui.ps1` and `tools/uitars_grounder.py`). Project rules for LabVIEW work: `docs/rules/labview-execution.md`.
