---
name: user-wants-learnable-labview-notes
description: "The user wants a teaching-oriented LabVIEW write-up kept in LEARNING.md, separate from the LLM hand-off docs, so they can catch up later on what was done and why"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 72babae7-a0eb-4591-80eb-3f88511dbec4
  modified: 2026-08-25T16:56:35.691Z
type: decision
status: in-force
date: 2026-08-25
source: memory/user_wants_learnable_labview_notes.md
---

# Keep a learnable LabVIEW write-up for the user, not just hand-off notes

The user is usually too busy to follow the work as it happens, and asked (2026-08-26) that Claude
"leave some track and learnable materials in a designated place on the project" so they can learn
afterwards what was done with LabVIEW overall. The designated place in this project is
**`LEARNING.md`** at the project root.

This is a **different audience** from the docs that already exist. `STATUS.md`, `WORKLOG.md`, and
`PLAN_kernel_parallel.md` are written for the next Claude session or another LLM picking the work
up cold — they optimise for resumability. `LEARNING.md` is written for the user as a human learner:
it should explain LabVIEW concepts and techniques (what VI Scripting is, how `New VI Object` works,
why a particular error happened and what it taught us), with enough context that reading it alone
teaches the topic. Prefer short explanations of the *mechanism* over a chronological log of clicks.

The user explicitly capped the cost: **"don't waste too much effort on here."** So append concise
sections as real understanding is gained, rather than producing long polished essays or
restructuring the file each session.
