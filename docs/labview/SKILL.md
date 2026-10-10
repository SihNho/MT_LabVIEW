---
name: labview-automation
description: Automate LabVIEW programmatically - edit block diagrams with VI Scripting, and drive the LabVIEW GUI reliably when scripting cannot reach. Use whenever a task involves creating, editing, wiring or inspecting a LabVIEW .vi; enabling loop parallelism; dropping subVIs; adding structures or constants; decoding VI Scripting errors (1057/1059); or clicking anything inside the LabVIEW editor. Also use when choosing a VI Scripting library, or when GUI automation of LabVIEW is misclicking, hitting the wrong window, or failing to wire terminals.
---

# LabVIEW Automation

**PORTABLE SKILL — copy this whole directory into any LabVIEW project.** Nothing here is
project-specific. **Verified on:** LabVIEW 2026 (26.3.1f1, Q3), Windows 10, 1920×1080, single
display, VI Scripting enabled — re-verify colours/pixel offsets on any other setup.

This file is the INDEX. The technique lives one layer down — open the reference for the topic you
are actually doing, in full:

| you are about to… | read |
|---|---|
| create/wire/inspect diagram objects by script; pick a library; follow the wiring protocol; design ops | [references/vi-scripting.md](references/vi-scripting.md) |
| drive LabVIEW from Python/COM: run VIs, set controls, save, diagnose hangs/silent failures | [references/com-driving.md](references/com-driving.md) |
| click anything in the editor: Quick Drop, class picker, wiring by hand, resize, menus, screenshots | [references/gui-recipes.md](references/gui-recipes.md) |
| read `.vi` files offline; find where NI installs things; persist IMAQ images bit-exactly | [references/files-and-formats.md](references/files-and-formats.md) |

## Rule 0 — prefer code over clicking, always

1. **VI Scripting** (enable in Tools ▸ Options ▸ VI Server) via an installed library — do not
   hand-build primitives. Measured: a task costing **31–40 GUI tool calls is ONE scripting call**.
2. Only two operations have NO scripting path (externally verified): **placing a primitive outside
   `New VI Object`'s style ring** and **growing a node's terminal count**. Everything else that
   looks unscriptable has turned out scriptable — search before declaring a third.
3. A click into a DELIVERABLE repeats on every rebuild; a click into a TOOL is paid once. When a
   scripted path exists in principle, build the tool — "only a few clicks left" is how the tool
   never gets built.

## The five laws that bite hardest (details in the references)

- **Verify by effect, never by return code or wire count.** Silent decline is the normal failure
  mode; a successful BRANCH adds no Wire object; `ExecState` 0→1 is the unforgeable signal.
- **Names are the API and they are exact bytes** — labels contain real newlines and trailing
  spaces. Keep and consult the project's verified-name registry before every wiring call.
- **Open the panel before editing, save before closing, and never cold-load a broken-saved VI
  headless** (recompile spin). After **error 2** (memory full): restart FIRST — a Ctrl+S in that
  state can write a stale file.
- **Menus, wiring mode, palettes and Context Help leave LabVIEW modal — every later COM call hangs
  until `Esc`.** A hang with no dialog is usually this, not a wedge.
- **Trust the foreground TITLE PIXELS, not the focus call's return** — keystrokes have landed in
  other applications. Verify, then type.

## Safety

- **Never modify an original `.vi`.** Work on copies. A `*` in the title is not a disk change —
  only Save is. If an original goes dirty: close WITHOUT saving, verify checksum (`-Action md5`).
  Answer **Don't Save** to every save prompt on an original, and audit saved-version bytes after
  sessions that opened originals (`19 00 80 00` = LV2019, `26 00 80 00` = LV2026 — a newer save is
  irreversible).
- **Copy the whole dependency folder** before opening a VI with subVIs (else "Find the VI Named X"
  cascades).
- **One execution path at a time** — never two automations, or automation + human, on one LabVIEW.
- On a machine wired to real hardware: confirm before driving anything, and know which instruments
  must never be actuated.
