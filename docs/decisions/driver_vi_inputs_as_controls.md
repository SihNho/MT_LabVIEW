---
name: driver-vi-inputs-as-controls
description: "When building driver/scripting VIs, expose inputs as front-panel controls rather than block-diagram constants — the user's standing design preference"
metadata: 
  node_type: memory
  originSessionId: 1ffa4eb9-19ac-4240-b7d7-6ef33fffb8c1
  modified: 2026-08-27T01:03:18.814Z
type: decision
status: in-force
date: 2026-08-27
source: memory/driver_vi_inputs_as_controls.md
---

# Driver VI inputs should be front-panel controls, not diagram constants

While approving the COM-automation pivot for `KernelBuilder_v1.vi` (2026-08-27), the user gave this
as a standing design note: *"kernelbuilder 만들때 input을 상수값이 아닌 control로 두면 나중에
사용하기 더 편할거야"* — when building KernelBuilder(-style VIs), put the inputs in as controls
rather than constant values; it is much more convenient to use later.

Why this matters in practice, learned the hard way in the same project: a `.vi` is a compiled
binary with no text form, so every configuration value that lives as a **diagram constant** can only
be changed by editing the block diagram — which, under GUI automation, costs 5–15 tool calls per
edit (double-click, select-all, retype, verify by tip strip). The same value exposed as a
**front-panel control** can be set in one call from outside LabVIEW (`SetControlValue` via the
ActiveX/COM server, or interactively by the user), turned into a config file trivially, and read
back (`GetControlValue`) for verification without screenshots.

Apply this whenever creating or extending a scripting driver, test harness, or any VI whose
behaviour is meant to be steered per run: target paths, name lists, coordinates, option flags —
all as labelled front-panel controls (with the connector pane left unwired unless needed).
Constants are only for values that are genuinely fixed forever. Existing constants can be migrated
with right-click → "Change to Control".
