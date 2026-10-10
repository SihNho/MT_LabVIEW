---
name: bank-gui-control-knowledge-after-each-success
description: "Every time a GUI target is finally hit after misclicks, write down the reusable way to find it — code, a locating rule, a menu path — so GUI control compounds instead of being re-derived each session"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 72babae7-a0eb-4591-80eb-3f88511dbec4
  modified: 2026-08-25T17:07:31.118Z
type: decision
status: in-force
date: 2026-08-25
source: memory/bank_gui_control_knowledge_after_each_success.md
---

# Bank the clue every time a GUI target is finally found

The user's standing instruction on this LabVIEW project (2026-08-26): *"if you are continuously
mis-clicking on the terminals or loops or else, after getting to the right point, you should leave
some clues that will help you do the GUI control eventually. Could be code, could be some standard
for finding the correct position, could be some rules, anything."*

The failure mode this corrects is **re-derivation**. A session spends ten round-trips homing in on a
4-pixel terminal, succeeds, and then records only *that the step was done* — so the next session pays
the same ten round-trips. The cost never falls. The user wants GUI control to **compound**: each
painful lookup should leave behind an artefact that makes the next one cheap.

So whenever a target is finally hit after misses, immediately capture the *reusable* part, in
whichever form fits:

- **Code** — a new action in `tools/lv_gui.ps1` that locates the thing programmatically (for example
  sampling pixel colours down a node's left edge to find terminal rows, rather than eyeballing them).
- **A locating rule** — the arithmetic that converts what you can see into a click target, such as
  screen coordinate = window origin + image coordinate, or terminal rows being at fixed fractions of
  a node's height.
- **A recorded path** — an exact menu or palette route that was expensive to discover, written out in
  full so it is followed rather than re-explored.

Store durable technique in `tools/lv_gui.ps1`'s header and the project's GUI playbook, not buried in
a dated worklog entry, because the point is that a future session finds it without reading history.
Prefer window-relative or rule-based coordinates over absolute screen pixels, since absolute values
go stale as soon as a window moves.
