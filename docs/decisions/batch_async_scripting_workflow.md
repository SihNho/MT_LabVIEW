---
name: batch-async-scripting-workflow
description: "The user wants scripting-driver VIs to run as parallel fire-and-forget batches (reentrant shared clones), not one blocking run at a time"
metadata: 
  node_type: memory
  originSessionId: 1ffa4eb9-19ac-4240-b7d7-6ef33fffb8c1
  modified: 2026-08-27T02:08:36.165Z
type: decision
status: in-force
date: 2026-08-27
source: memory/batch_async_scripting_workflow.md
---

# Scripting drivers should support fire-many-inspect-later, not one run at a time

While using the KernelBuilder scripting driver (2026-08-27), the user said running it one-at-a-time
is inconvenient: they want to *"동시에 scripting으로 wiring 여러개 한 번에 끝내고 나중에 점검하는
형태"* — fire several scripting/wiring jobs at once and inspect the results afterwards — and asked
whether that needs renamed copies of the VI or whether one VI can run in several windows.

The answer they researched and endorsed (correct LabVIEW technique): **no renamed copies** — make
the driver VI **Reentrant with shared clones** (VI Properties > Execution), and launch instances
asynchronously (Open VI Reference with option 0x40 + Start Asynchronous Call with
Wait Until Done = False, or equivalently from Python COM: `GetVIReference(path, "", False, 0x40)`
returns an independent clone reference per call).

Caveats that must be respected when applying this to VI-Scripting workloads:
- VI Scripting *edit* operations largely serialize through LabVIEW's UI thread / root loop, so
  clones give fire-and-forget semantics (the real win) more than true speedup.
- **Never point two concurrent clones at the same target VI** — concurrent programmatic edits of
  one VI risk corruption. One clone per target copy.

Standing takeaway for any future driver VI built for this user: design it for batch use from the
start — reentrant (shared clones), config on the front panel (see driver-vi-inputs-as-controls),
and a scriptable launch path (COM/CLI) so N jobs can be dispatched unattended and inspected later.
