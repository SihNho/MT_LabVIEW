---
name: hardware-do-not-run-the-motor-superseded
description: "SUPERSEDED 2026-09-16 — the motor ban applied to an earlier period; see hardware_operation_permission.md, which says to operate the motors while the rig is disassembled"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 2b7a154c-b779-4f1a-8095-9dd814570b41
  modified: 2026-09-16T03:04:28.019Z
type: decision
status: superseded
date: 2026-09-16
source: memory/hardware_do_not_run_the_motor.md
superseded_by: hardware_operation_permission
---

# Superseded — do not act on this file

This memory recorded the user's 2026-08-27 instruction *"우선 모터 가동은 절대 하지 않는 선에서 계속 처리해"*
(carry on without ever running the motor), which narrowed an earlier and broader hardware permission.

**On 2026-09-16 the user reversed it for the current period**, saying that the motors and machines — motor
operation and motor reading included — must be operated *before* the rig is reassembled, and that they will
announce reassembly themselves.

The live rule is in **`hardware_operation_permission.md`**. Read that instead.

What survives from here: the ASI piezo stage is the one instrument whose ban was never about scheduling. It can
collide and physically break the rig, and the full-hardware permission of 2026-09-13 was explicitly conditioned on
the piezo being detached.
