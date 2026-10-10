---
name: labview-knowledge-must-be-portable-across-projects
description: "LabVIEW automation know-how must be written to be exported to the user's other LabVIEW projects and machines — package it as a portable skill, not as project-local notes with hard-coded paths"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 72babae7-a0eb-4591-80eb-3f88511dbec4
  modified: 2026-08-25T19:52:09.073Z
type: decision
status: in-force
date: 2026-08-25
source: memory/labview_knowledge_must_be_portable_across_projects.md
---

# Write the LabVIEW know-how to be exported, not just to be used here

The user runs **more than one LabVIEW project**, and said (2026-08-26) that the findings from this
work are valuable enough to apply elsewhere: *"the instructions should be eventually exported to other
projects and/or other environments in the future."*

So LabVIEW automation knowledge must be authored as **portable, reusable material** rather than as
notes welded to this project. Concretely:

- **Separate the general from the specific.** Techniques that hold for any LabVIEW work — VI Scripting
  recipes, the `New VI Object` terminal contract, decoded error codes, GUI-control laws, wire-colour
  to datatype mappings, palette behaviour — belong in a portable document. Facts that are only true
  here — this rig's file paths, the piezo-stage rule, which VI is the base version, the bead-tracking
  kernel's connector pane — stay project-local.
- **Prefer a skill as the packaging format.** A skill directory carrying its own `SKILL.md` and
  `scripts/` can be copied into another project or machine and works immediately, whereas a root-level
  `.md` file plus a `tools/` script assumes this folder layout. This project already demonstrates the
  pattern with `labview-vi-analysis`.
- **Avoid hard-coded absolute paths** in anything meant to travel. Reference paths relative to the
  skill or the project root, and state environment assumptions (LabVIEW version, OS, screen
  resolution, whether VI Scripting is enabled) explicitly, since they will differ elsewhere.
- **Say what was verified and on what.** A technique confirmed on LabVIEW 2026 at 1920x1080 may behave
  differently on another version or DPI, so record the conditions alongside the claim rather than
  presenting it as universal.

The underlying goal is that each hard-won lesson is paid for once and then reused across every LabVIEW
project the user works on, instead of being rediscovered per project.
