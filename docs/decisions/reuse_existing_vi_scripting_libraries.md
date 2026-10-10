---
name: reuse-existing-vi-scripting-libraries
description: "Build the VI Scripting layer on erdosmiller/lv-scripting (the user's choice) rather than hand-building primitives; other public libraries evaluated and why they were not chosen"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 72babae7-a0eb-4591-80eb-3f88511dbec4
  modified: 2026-08-25T18:41:22.354Z
type: decision
status: in-force
date: 2026-08-25
source: memory/reuse_existing_vi_scripting_libraries.md
---

# Build on `erdosmiller/lv-scripting`; don't hand-build the primitive layer

The user pointed out (2026-08-26) that the "VI Scripting primitive layer" this project was about to
build by hand already exists as open source, and that Claude should **analyse and reuse existing
implementations before wiring anything from scratch**. This overrides the earlier plan of
bootstrapping a driver VI through the LabVIEW GUI, which is slow and error-prone.

**Decision (user, 2026-08-26): `erdosmiller/lv-scripting` is the chosen foundation** — "erdosmiller
seems to best fit our need." The user also noted the search need not be considered exhaustive, so
better options may still surface; treat this as the working choice, not a closed question.

Why it fits: MIT licensed, targets LabVIEW 2015+, pure G with no undocumented APIs and no external
runtime, ships 13 progressive examples, and installs as a VIPM package — and **VIPM (JKI VI Package
Manager) is already installed on this machine**. Installing it writes into the production LabVIEW
installation, so it needs the user's go-ahead rather than being done unattended.

The alternatives, and why they were not chosen:

- **`CyantusLYX/labview_mcp`** has the most directly relevant SubVIs (`get_object_terminals` then
  `connect_objects(src, src_term, dst, dst_term)` is the pattern worth learning), but its repository
  states its licence as "[To be specified]", which means all rights reserved by default — so its code
  must not be vendored. It also requires the DQMH framework (not installed) plus a Go + Python + COM
  stack.
- **`Zuehlke/labview-mcp`** is MIT and matches this machine's LabVIEW (26.3.1f1 = 2026 Q3), but rides
  NI's private, undocumented `lvai.LVAI` gRPC interface with no version policy, its **edit** RPC
  "consistently fails" by the author's own account, and it cannot handle VIs containing project-local
  subVIs — which the tracking VIs are built from. Its **read** path (VI → AIXML text) is still
  attractive, because it would expose block-diagram wiring as text, which byte extraction can never do.
- **`JanGoebel/labview_assistant`** — MCP server plus scripting functions; not yet evaluated in depth.

The general lesson to carry: **before building infrastructure, search for an existing implementation**,
and hand-build only the primitives that turn out to be genuinely missing or incompatible.
