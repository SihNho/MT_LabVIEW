---
name: gui-only-when-script-verified-unreachable
description: "The user's hard rule, set 2026-08-31 after six corrections: GUI is permitted ONLY where scripting is VERIFIED unreachable — never as a cost/time judgment call"
metadata:
    pinned: true
type: decision
status: in-force
date: 2026-08-31
source: memory/build_tool_vis_by_scripting_not_clicking.md
---

# GUI only where script is VERIFIED unreachable — the user's hard rule

Set explicitly on 2026-08-31 — *"GUI 활용은 script로 도달 불가능한 경우에만. 이거 적용하자"* — after
the user had to correct GUI-creep **six times** across the project. This replaces every cost-based
judgment ("only two clicks left", "the op takes an hour to build") with a bright line:

**Before any GUI act, one of these must hold, in writing:**
1. The operation is on the **verified-impossible list** (external evidence cited in the skill), or
2. an external search was just run for THIS specific operation and came back negative, and that
   finding was recorded.

Anything else gets scripted, regardless of how much longer it takes this session. Speed comes from
replayable scripts, not from clicks.

## Why the misjudgments kept happening (the pattern to catch)

Every wrong "GUI is required" came from **generalizing an adjacent finding without verifying the
specific case**: `New VI Object`'s class *input* being fixed was stretched to "class constants need
the picker" (false — `ClassSpecifierConstant.Class Name` is a WRITABLE scripting property, and
`Set Type` exists); one right-click habit became "labels need the GUI" (false — `Node.Label` →
`Text` is writable on nodes, including primitives); "Wire Inputs declined" became "branching is
impossible" (false — the branch succeeded and the wire-count check misread it). A claimed limit of
our own tooling is a factual claim needing a search — the things nobody wrote down are exactly the
things most likely believed wrong.

## The verified-impossible list (only these justify GUI, as of 2026-08-31)

- Placing a primitive that is not in `New VI Object`'s style ring (error 1054; NI forums say copy
  from a donor or place by hand).
- Growing a node's terminal count (no VI Server API; peer-checked against NI docs).

Both are per-primitive-TYPE one-time costs once a labeled donor exists (labels now scriptable), so
even these should land in a DONOR/tool, never in a deliverable. The list shrinks; it never grows
without a recorded search.
